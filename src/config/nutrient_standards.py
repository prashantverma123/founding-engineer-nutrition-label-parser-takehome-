"""
Standard nutrient names and known nutrients list.
Used for validation and confidence scoring.
"""

KNOWN_NUTRIENTS = {
    'protein',
    'total_fat',
    'saturated_fat',
    'trans_fat',
    'polyunsaturated_fat',
    'monounsaturated_fat',
    'cholesterol',
    'total_carbohydrate',
    'dietary_fiber',
    'total_sugars',
    'added_sugars',
    'sugar_alcohol',
    'vitamin_a',
    'beta_carotene',
    'vitamin_d',
    'vitamin_d3',
    'vitamin_e',
    'vitamin_k',
    'vitamin_c',
    'vitamin_b1',
    'vitamin_b2',
    'vitamin_b3',
    'vitamin_b5',
    'vitamin_b6',
    'vitamin_b7',
    'vitamin_b9',
    'vitamin_b12',
    'calcium',
    'iron',
    'magnesium',
    'phosphorus',
    'potassium',
    'sodium',
    'zinc',
    'copper',
    'manganese',
    'selenium',
    'chromium',
    'molybdenum',
    'iodine',
    'chloride',
    'calories',
    'caffeine',
    'omega_3',
    'omega_6',
    'dha',
    'epa',
    'choline',
}


def is_known_nutrient(nutrient_standard: str) -> bool:
    """Check if a standardized nutrient name is in the known set."""
    return nutrient_standard.lower() in KNOWN_NUTRIENTS
