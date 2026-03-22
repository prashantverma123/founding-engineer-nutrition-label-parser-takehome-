"""
Output schema definitions and validation.
"""
from typing import List

OUTPUT_COLUMNS = [
    'product_image',
    'source_section',
    'nutrient_name_raw',
    'nutrient_name_standard',
    'amount_raw',
    'amount',
    'unit_raw',
    'unit',
    'serving_context',
    'parsing_method',
    'confidence',
    'notes'
]


def validate_nutrient_record_dict(record: dict) -> bool:
    """Validate that a nutrient record dictionary has all required columns."""
    return all(col in record for col in OUTPUT_COLUMNS)
