"""
Nutrition data extractor using vision models.

Extracts structured nutrition information with hallucination prevention.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.vision.model_interface import VisionModel
from src.vision.prompts import get_extraction_prompt
from src.models.entities import NutrientRecord
from src.validation.validator import AmountValidator
from src.config.nutrient_aliases import normalize_nutrient_name
from src.config.unit_aliases import normalize_unit

logger = logging.getLogger(__name__)


class NutritionExtractor:
    """Extracts nutrition data from images using vision models."""
    
    def __init__(self, vision_model: VisionModel):
        """
        Initialize extractor.
        
        Args:
            vision_model: Vision model for image analysis
        """
        self.vision_model = vision_model
        self.validator = AmountValidator()
    
    def extract(self, image_path: Path) -> Dict[str, Any]:
        """
        Extract nutrition data from image.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dict with:
                - nutrients: List[NutrientRecord]
                - serving_info: Dict
                - confidence: str
                - ambiguities: List[str]
                - raw_response: str (for debugging)
        """
        logger.info(f"Extracting nutrition data from: {image_path.name}")
        
        prompt = get_extraction_prompt()
        response = self.vision_model.analyze_image(image_path, prompt)
        
        if not response:
            logger.error(f"No response from vision model for {image_path.name}")
            return {
                "nutrients": [],
                "serving_info": {},
                "confidence": "low",
                "ambiguities": ["Vision model failed to respond"],
                "raw_response": ""
            }
        
        # Parse compact pipe-delimited response
        try:
            parsed_data = self._parse_compact_response(response)
            
            if parsed_data is None:
                logger.error(f"Failed to parse compact response for {image_path.name}")
                return {
                    "nutrients": [],
                    "serving_info": {},
                    "confidence": "low",
                    "ambiguities": ["Failed to parse compact format"],
                    "raw_response": response
                }
            
            nutrients = self._parse_nutrients_compact(
                parsed_data["nutrients"], 
                image_path.name
            )
            
            return {
                "nutrients": nutrients,
                "serving_info": parsed_data.get("serving_info", {}),
                "confidence": parsed_data.get("confidence", "medium"),
                "ambiguities": parsed_data.get("ambiguities", []),
                "raw_response": response
            }
            
        except Exception as e:
            logger.error(f"Failed to parse extraction response: {e}")
            logger.debug(f"Raw response: {response[:500]}")
            
            return {
                "nutrients": [],
                "serving_info": {},
                "confidence": "low",
                "ambiguities": [f"Parse failed: {str(e)}"],
                "raw_response": response
            }
    
    def _parse_compact_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse compact pipe-delimited response format.
        
        Format:
        NUTRIENTS:
        Vitamin C|vitamin_c|60|mg|1|
        Calcium|calcium|200|mg|1|20
        
        SERVING:
        2 capsules|30
        
        CONFIDENCE:
        high
        
        AMBIGUITIES:
        unclear text
        
        Args:
            response: Raw compact response
        
        Returns:
            Dict with parsed data or None if failed
        """
        # Check for NONE response
        if response.strip() == "NONE":
            return {
                "nutrients": [],
                "serving_info": {},
                "confidence": "high",
                "ambiguities": []
            }
        
        result = {
            "nutrients": [],
            "serving_info": {},
            "confidence": "medium",
            "ambiguities": []
        }
        
        current_section = None
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Section headers
            if line.startswith("NUTRIENTS:"):
                current_section = "nutrients"
                continue
            elif line.startswith("SERVING:"):
                current_section = "serving"
                continue
            elif line.startswith("CONFIDENCE:"):
                current_section = "confidence"
                continue
            elif line.startswith("AMBIGUITIES:"):
                current_section = "ambiguities"
                continue
            
            # Parse content based on current section
            if current_section == "nutrients":
                parts = line.split('|')
                if len(parts) >= 5:
                    result["nutrients"].append({
                        "raw_name": parts[0],
                        "standard_name": parts[1],
                        "amount": parts[2],
                        "unit": parts[3],
                        "per_serving": parts[4],
                        "daily_value": parts[5] if len(parts) > 5 and parts[5] else None
                    })
            
            elif current_section == "serving":
                parts = line.split('|')
                if len(parts) >= 2:
                    result["serving_info"] = {
                        "serving_size": parts[0],
                        "servings_per_container": parts[1]
                    }
            
            elif current_section == "confidence":
                result["confidence"] = line.lower()
            
            elif current_section == "ambiguities":
                result["ambiguities"].append(line)
        
        return result
    
    def _parse_nutrients_compact(self, nutrients_data: List[Dict], image_name: str) -> List[NutrientRecord]:
        """
        Parse compact nutrient data into NutrientRecord objects.
        
        Args:
            nutrients_data: List of compact nutrient dicts
            image_name: Name of source image
        
        Returns:
            List of validated NutrientRecord objects
        """
        records = []
        
        for nutrient in nutrients_data:
            try:
                raw_name = nutrient["raw_name"]
                standard_name = nutrient["standard_name"]
                amount_str = nutrient["amount"]
                unit = nutrient["unit"]
                per_serving = nutrient["per_serving"] == "1"
                daily_value = nutrient.get("daily_value")
                
                # Parse amount
                try:
                    amount = float(amount_str)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid amount '{amount_str}' for {raw_name}")
                    continue
                
                # Normalize names and units
                standard_name_normalized = normalize_nutrient_name(standard_name)
                unit_normalized = normalize_unit(unit)
                
                # Validate amount
                is_valid, validation_note = self.validator.validate_amount(
                    standard_name_normalized,
                    amount,
                    unit_normalized
                )
                
                # Build notes list
                validation_notes = []
                if not is_valid and validation_note:
                    validation_notes.append(f"VALIDATION FAILED: {validation_note}")
                elif validation_note:
                    validation_notes.append(validation_note)
                
                # Determine confidence
                confidence = self._determine_confidence(
                    amount,
                    unit_normalized,
                    validation_notes,
                    ""  # No extraction notes in compact format
                )
                
                # Combine notes
                all_notes = "; ".join(validation_notes) if validation_notes else ""
                
                record = NutrientRecord(
                    product_image=image_name,
                    nutrient_name_raw=raw_name,
                    nutrient_name_standard=standard_name_normalized,
                    amount_raw=amount_str,
                    amount=amount,
                    unit_raw=unit,
                    unit=unit_normalized,
                    serving_context="per_serving" if per_serving else "per_100g",
                    daily_value_percent=daily_value,
                    parsing_method="vision_llm",
                    confidence=confidence,
                    notes=all_notes
                )
                
                records.append(record)
                
            except Exception as e:
                logger.warning(f"Failed to parse nutrient {nutrient}: {e}")
                continue
        
        return records
    
    def _parse_nutrients(self, nutrients_data: List[Dict], image_name: str) -> List[NutrientRecord]:
        """
        Parse and validate nutrient data.
        
        Applies:
        - Nutrient name normalization
        - Unit normalization
        - Amount validation (hallucination detection)
        - Confidence scoring
        
        Args:
            nutrients_data: List of nutrient dicts from LLM
            image_name: Source image name
        
        Returns:
            List of validated NutrientRecord objects
        """
        records = []
        
        for nutrient in nutrients_data:
            try:
                # Extract fields
                nutrient_name_raw = nutrient.get("nutrient_name_raw", "")
                nutrient_name_standard = nutrient.get("nutrient_name_standard", "")
                amount_raw = nutrient.get("amount")
                unit_raw = nutrient.get("unit", "")
                notes = nutrient.get("notes", "")
                
                if not nutrient_name_raw:
                    logger.warning("Skipping nutrient with no name")
                    continue
                
                # Normalize nutrient name
                if not nutrient_name_standard:
                    nutrient_name_standard = normalize_nutrient_name(nutrient_name_raw)
                
                # Convert amount to float
                amount = None
                if amount_raw is not None:
                    try:
                        amount = float(amount_raw)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid amount for {nutrient_name_raw}: {amount_raw}")
                        notes = f"{notes}; Invalid amount: {amount_raw}".strip("; ")
                
                # Normalize unit
                unit = normalize_unit(unit_raw) if unit_raw else ""
                
                # Validate amount (anti-hallucination)
                validation_notes = []
                if amount is not None:
                    is_valid, warning = self.validator.validate_amount(
                        nutrient_name_standard,
                        amount,
                        unit
                    )
                    
                    if not is_valid:
                        # Flag as hallucination
                        validation_notes.append(f"VALIDATION FAILED: {warning}")
                        logger.warning(f"Possible hallucination: {nutrient_name_raw} {amount}{unit} - {warning}")
                    elif warning:
                        validation_notes.append(warning)
                
                # Determine confidence
                confidence = self._determine_confidence(
                    amount,
                    unit,
                    validation_notes,
                    notes
                )
                
                # Combine notes
                all_notes = "; ".join(filter(None, [notes] + validation_notes))
                
                # Determine serving context
                serving_context = "per serving" if nutrient.get("per_serving", True) else "per 100g/100ml"
                
                # Create record
                record = NutrientRecord(
                    product_image=image_name,
                    source_section="vision_extraction",
                    nutrient_name_raw=nutrient_name_raw,
                    nutrient_name_standard=nutrient_name_standard,
                    amount_raw=str(amount_raw) if amount_raw is not None else "",
                    amount=amount,
                    unit_raw=unit_raw,
                    unit=unit,
                    serving_context=serving_context,
                    parsing_method="vision_model",
                    confidence=confidence,
                    notes=all_notes
                )
                
                records.append(record)
                
            except Exception as e:
                logger.error(f"Error parsing nutrient: {e}")
                continue
        
        logger.info(f"Extracted {len(records)} nutrients from {image_name}")
        return records
    
    def _determine_confidence(
        self,
        amount: Optional[float],
        unit: str,
        validation_notes: List[str],
        extraction_notes: str
    ) -> str:
        """
        Determine confidence level for a nutrient record.
        
        Args:
            amount: Parsed amount
            unit: Normalized unit
            validation_notes: Validation warnings
            extraction_notes: Notes from extraction
        
        Returns:
            Confidence level: "high", "medium", or "low"
        """
        # Start with high confidence
        score = 3
        
        # Penalize if no amount
        if amount is None:
            score -= 2
        
        # Penalize if no unit
        if not unit:
            score -= 1
        
        # Penalize if validation failed
        if validation_notes and any("VALIDATION FAILED" in note for note in validation_notes):
            score -= 2
        
        # Penalize if extraction noted uncertainty
        if extraction_notes and any(word in extraction_notes.lower() for word in ["unclear", "uncertain", "possibly"]):
            score -= 1
        
        # Map score to confidence
        if score >= 2:
            return "high"
        elif score >= 1:
            return "medium"
        else:
            return "low"
    
    def _is_truncated_json(self, response: str) -> bool:
        """
        Check if JSON response appears truncated.
        
        Args:
            response: Cleaned JSON string
        
        Returns:
            True if response appears truncated
        """
        response = response.strip()
        
        # Check for common truncation indicators
        truncation_indicators = [
            # Unterminated strings
            response.endswith('"'),
            # Missing closing braces
            response.count('{') > response.count('}'),
            # Missing closing brackets
            response.count('[') > response.count(']'),
            # Ends with comma (incomplete object/array)
            response.endswith(','),
            # Ends mid-property name
            response.endswith('_'),
        ]
        
        return any(truncation_indicators)
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean JSON response by removing markdown code blocks.
        
        Gemini often wraps JSON in ```json ... ``` blocks.
        
        Args:
            response: Raw response string
        
        Returns:
            Cleaned JSON string
        """
        # Remove markdown code blocks
        response = response.strip()
        
        # Check for ```json prefix
        if response.startswith("```json"):
            response = response[7:]  # Remove ```json
        elif response.startswith("```"):
            response = response[3:]  # Remove ```
        
        # Remove trailing ```
        if response.endswith("```"):
            response = response[:-3]
        
        return response.strip()
