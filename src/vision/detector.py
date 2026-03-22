"""
Nutrition data detector - filters images that don't contain nutrition information.

This prevents processing product fronts, marketing images, or invalid uploads.
"""
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from src.vision.model_interface import VisionModel
from src.vision.prompts import get_detection_prompt

logger = logging.getLogger(__name__)


class NutritionDataDetector:
    """Detects whether an image contains nutrition data."""
    
    def __init__(self, vision_model: VisionModel):
        """
        Initialize detector.
        
        Args:
            vision_model: Vision model for image analysis
        """
        self.vision_model = vision_model
    
    def has_nutrition_data(self, image_path: Path) -> Dict[str, Any]:
        """
        Check if image contains nutrition data.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dict with keys:
                - has_data: bool
                - confidence: str (high/medium/low)
                - reason: str
        """
        logger.info(f"Detecting nutrition data in: {image_path.name}")
        
        prompt = get_detection_prompt()
        response = self.vision_model.analyze_image(image_path, prompt)
        
        if not response:
            logger.warning(f"No response from vision model for {image_path.name}")
            return {
                "has_data": False,
                "confidence": "low",
                "reason": "Vision model failed to respond"
            }
        
        # Parse JSON response (handle markdown code blocks)
        try:
            # Strip markdown code blocks if present
            clean_response = self._clean_json_response(response)
            result = json.loads(clean_response)
            
            # Validate required fields
            has_data = result.get("has_nutrition_data", False)
            confidence = result.get("confidence", "low")
            reason = result.get("reason", "No reason provided")
            
            logger.info(f"{image_path.name}: has_data={has_data}, confidence={confidence}")
            
            return {
                "has_data": has_data,
                "confidence": confidence,
                "reason": reason
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse detection response: {e}")
            logger.debug(f"Raw response: {response}")
            
            # Fallback: check if response contains positive indicators
            response_lower = response.lower()
            has_positive = any(word in response_lower for word in ["true", "yes", "contains", "nutrition"])
            
            return {
                "has_data": has_positive,
                "confidence": "low",
                "reason": f"JSON parse failed, used fallback heuristic"
            }
    
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
