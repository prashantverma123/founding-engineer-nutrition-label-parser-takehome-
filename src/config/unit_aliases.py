"""
Unit normalization mappings.
"""

UNIT_ALIASES = {
    # Weight units
    'g': 'g',
    'gram': 'g',
    'grams': 'g',
    'gm': 'g',
    'mg': 'mg',
    'milligram': 'mg',
    'milligrams': 'mg',
    'mcg': 'µg',
    'µg': 'µg',
    'ug': 'µg',
    'microgram': 'µg',
    'micrograms': 'µg',
    'kg': 'kg',
    'kilogram': 'kg',
    'kilograms': 'kg',
    
    # Volume units
    'ml': 'ml',
    'milliliter': 'ml',
    'milliliters': 'ml',
    'l': 'l',
    'liter': 'l',
    'liters': 'l',
    
    # International units
    'iu': 'IU',
    'i.u.': 'IU',
    
    # Percentages
    '%': '%',
    'percent': '%',
    'pct': '%',
    
    # Other
    'cal': 'cal',
    'kcal': 'kcal',
    'calories': 'cal',
}


def normalize_unit(raw_unit: str) -> str:
    """
    Normalize a raw unit string to standard form.
    Returns standard unit if found, otherwise returns cleaned raw unit.
    """
    if not raw_unit:
        return ''
    
    # Clean and lowercase
    clean_unit = raw_unit.lower().strip()
    
    # Remove periods and spaces
    clean_unit = clean_unit.replace('.', '').replace(' ', '')
    
    # Look up in aliases
    if clean_unit in UNIT_ALIASES:
        return UNIT_ALIASES[clean_unit]
    
    # Return as-is if not found
    return raw_unit.strip()
