"""
Core data models for nutrition label parsing pipeline.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class ParsingMethod(Enum):
    RULE_BASED = "rule_based"
    LLM_FALLBACK = "llm_fallback"
    FAILED = "failed"


class SourceSection(Enum):
    NUTRITION_FACTS = "nutrition_facts"
    SUPPLEMENT_FACTS = "supplement_facts"
    SERVING_SIZE = "serving_size"
    INGREDIENTS = "ingredients"
    UNKNOWN = "unknown"


class Confidence(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class OCRResult:
    """Raw OCR output from an image."""
    image_path: str
    raw_text: str
    lines: List[str]
    success: bool
    error: Optional[str] = None


@dataclass
class SectionBlock:
    """A detected section within OCR text."""
    section_type: SourceSection
    text: str
    line_numbers: List[int]
    confidence: Confidence


@dataclass
class NutrientRecord:
    """Represents a single nutrient extracted from an image."""
    product_image: str
    nutrient_name_raw: str
    nutrient_name_standard: str
    amount_raw: str
    amount: Optional[float]
    unit_raw: str
    unit: str
    serving_context: str
    parsing_method: str
    confidence: str
    notes: str
    source_section: str = "vision_extraction"
    daily_value_percent: Optional[str] = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
            'product_image': self.product_image,
            'nutrient_name_raw': self.nutrient_name_raw,
            'nutrient_name_standard': self.nutrient_name_standard,
            'amount_raw': self.amount_raw,
            'amount': self.amount,
            'unit_raw': self.unit_raw,
            'unit': self.unit,
            'serving_context': self.serving_context,
            'parsing_method': self.parsing_method,
            'confidence': self.confidence,
            'notes': self.notes
        }


@dataclass
class ParsedCandidate:
    """A candidate nutrient line extracted from text."""
    raw_line: str
    nutrient_name_raw: Optional[str] = None
    amount_raw: Optional[str] = None
    unit_raw: Optional[str] = None
    parsed: bool = False
    confidence: Confidence = Confidence.LOW


@dataclass
class ParseDecision:
    """Tracking information about parsing decisions."""
    image_path: str
    total_lines: int
    section_blocks: List[SectionBlock]
    candidates_extracted: int
    rule_based_parsed: int
    llm_fallback_used: int
    failed_to_parse: int
    ambiguity_notes: List[str] = field(default_factory=list)


@dataclass
class ProductParseResult:
    """Complete parsing result for a product image."""
    image_path: str
    ocr_result: OCRResult
    sections: List[SectionBlock]
    nutrient_records: List[NutrientRecord]
    parse_decision: ParseDecision
    success: bool
    error: Optional[str] = None
