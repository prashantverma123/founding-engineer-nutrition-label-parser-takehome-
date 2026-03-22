"""
Nutrient name aliases mapping raw OCR text to standard names.
"""

NUTRIENT_ALIASES = {
    # Macronutrients
    'protein': 'protein',
    'total fat': 'total_fat',
    'fat': 'total_fat',
    'saturated fat': 'saturated_fat',
    'trans fat': 'trans_fat',
    'polyunsaturated fat': 'polyunsaturated_fat',
    'monounsaturated fat': 'monounsaturated_fat',
    'cholesterol': 'cholesterol',
    'total carbohydrate': 'total_carbohydrate',
    'carbohydrate': 'total_carbohydrate',
    'carbohydrates': 'total_carbohydrate',
    'dietary fiber': 'dietary_fiber',
    'fiber': 'dietary_fiber',
    'total sugars': 'total_sugars',
    'sugars': 'total_sugars',
    'added sugars': 'added_sugars',
    'sugar alcohol': 'sugar_alcohol',
    'sugar alcohols': 'sugar_alcohol',
    
    # Vitamins - Fat Soluble
    'vitamin a': 'vitamin_a',
    'retinol': 'vitamin_a',
    'beta carotene': 'beta_carotene',
    'vitamin d': 'vitamin_d',
    'vitamin d3': 'vitamin_d3',
    'cholecalciferol': 'vitamin_d3',
    'vitamin e': 'vitamin_e',
    'alpha tocopherol': 'vitamin_e',
    'tocopherol': 'vitamin_e',
    'vitamin k': 'vitamin_k',
    
    # Vitamins - Water Soluble
    'vitamin c': 'vitamin_c',
    'ascorbic acid': 'vitamin_c',
    'vitamin b1': 'vitamin_b1',
    'thiamin': 'vitamin_b1',
    'thiamine': 'vitamin_b1',
    'thiamine mononitrate': 'vitamin_b1',
    'vitamin b2': 'vitamin_b2',
    'riboflavin': 'vitamin_b2',
    'vitamin b3': 'vitamin_b3',
    'niacin': 'vitamin_b3',
    'niacinamide': 'vitamin_b3',
    'vitamin b5': 'vitamin_b5',
    'pantothenic acid': 'vitamin_b5',
    'vitamin b6': 'vitamin_b6',
    'pyridoxine': 'vitamin_b6',
    'pyridoxine hcl': 'vitamin_b6',
    'pyridoxine hydrochloride': 'vitamin_b6',
    'vitamin b7': 'vitamin_b7',
    'biotin': 'vitamin_b7',
    'vitamin b9': 'vitamin_b9',
    'folate': 'vitamin_b9',
    'folic acid': 'vitamin_b9',
    'vitamin b12': 'vitamin_b12',
    'cobalamin': 'vitamin_b12',
    'cyanocobalamin': 'vitamin_b12',
    
    # Minerals
    'calcium': 'calcium',
    'iron': 'iron',
    'magnesium': 'magnesium',
    'phosphorus': 'phosphorus',
    'potassium': 'potassium',
    'sodium': 'sodium',
    'zinc': 'zinc',
    'copper': 'copper',
    'manganese': 'manganese',
    'selenium': 'selenium',
    'chromium': 'chromium',
    'molybdenum': 'molybdenum',
    'iodine': 'iodine',
    'chloride': 'chloride',
    
    # Other nutrients
    'calories': 'calories',
    'energy': 'calories',
    'caffeine': 'caffeine',
    'omega-3': 'omega_3',
    'omega-6': 'omega_6',
    'dha': 'dha',
    'epa': 'epa',
    'choline': 'choline',
}


def normalize_nutrient_name(raw_name: str) -> str:
    """
    Normalize a raw nutrient name to standard form.
    Returns standard name if found, otherwise returns cleaned raw name.
    """
    if not raw_name:
        return 'unknown'
    
    # Clean and lowercase
    clean_name = raw_name.lower().strip()
    
    # Remove common punctuation
    clean_name = clean_name.replace('(', '').replace(')', '').replace(',', '')
    
    # Look up in aliases
    if clean_name in NUTRIENT_ALIASES:
        return NUTRIENT_ALIASES[clean_name]
    
    # Return slugified version
    return clean_name.replace(' ', '_').replace('-', '_')
