"""
Amount validation module - catches hallucinations and impossible values.

This is our main defense against LLM hallucinations.
"""
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Reasonable ranges for common nutrients (amount per serving)
# Format: nutrient_standard -> (min, max, unit)
REASONABLE_RANGES = {
    # Macronutrients (grams)
    'protein': (0, 100, 'g'),
    'total_fat': (0, 100, 'g'),
    'saturated_fat': (0, 50, 'g'),
    'trans_fat': (0, 10, 'g'),
    'total_carbohydrate': (0, 150, 'g'),
    'dietary_fiber': (0, 50, 'g'),
    'total_sugars': (0, 100, 'g'),
    'added_sugars': (0, 100, 'g'),
    
    # Minerals (milligrams)
    'sodium': (0, 5000, 'mg'),
    'calcium': (0, 2000, 'mg'),
    'iron': (0, 100, 'mg'),
    'potassium': (0, 5000, 'mg'),
    'magnesium': (0, 1000, 'mg'),
    'zinc': (0, 100, 'mg'),
    
    # Vitamins (milligrams)
    'vitamin_c': (0, 2000, 'mg'),
    'vitamin_b1': (0, 100, 'mg'),
    'vitamin_b2': (0, 100, 'mg'),
    'vitamin_b3': (0, 100, 'mg'),
    'vitamin_b6': (0, 200, 'mg'),
    'vitamin_b12': (0, 10, 'mg'),
    
    # Vitamins (micrograms)
    'vitamin_d': (0, 5000, 'µg'),
    'vitamin_d3': (0, 5000, 'µg'),
    
    # Other
    'calories': (0, 1000, 'cal'),
    'cholesterol': (0, 500, 'mg'),
}


class AmountValidator:
    """Validates parsed nutrient amounts for reasonableness."""
    
    def validate_amount(
        self,
        nutrient_standard: str,
        amount: Optional[float],
        unit: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that an amount is reasonable for the given nutrient.
        
        This is our main defense against LLM hallucinations.
        
        Args:
            nutrient_standard: Standardized nutrient name
            amount: Parsed amount value
            unit: Unit of measurement
        
        Returns:
            Tuple of (is_valid, warning_message)
        """
        # Null amounts are invalid
        if amount is None:
            return False, "Amount is null"
        
        # Negative amounts are impossible
        if amount < 0:
            return False, f"Negative amount: {amount}"
        
        # Zero is suspicious but not invalid
        if amount == 0:
            return True, f"Zero amount (may be 'Not a significant source')"
        
        # Check against known reasonable ranges
        if nutrient_standard in REASONABLE_RANGES:
            min_val, max_val, expected_unit = REASONABLE_RANGES[nutrient_standard]
            
            # Check unit matches expected
            if unit and unit != expected_unit:
                if not self._units_compatible(unit, expected_unit):
                    return True, f"Unexpected unit '{unit}' (expected '{expected_unit}')"
            
            # Check if amount is in reasonable range
            if amount < min_val or amount > max_val:
                return False, f"Amount {amount}{unit} outside reasonable range [{min_val}-{max_val}{expected_unit}]"
        
        # Unknown nutrient or amount is reasonable
        return True, None
    
    def _units_compatible(self, unit1: str, unit2: str) -> bool:
        """Check if two units are compatible."""
        compatible_sets = [
            {'g', 'grams', 'gram'},
            {'mg', 'milligrams', 'milligram'},
            {'µg', 'mcg', 'ug', 'micrograms', 'microgram'},
            {'cal', 'calories', 'kcal'},
        ]
        
        unit1_lower = unit1.lower()
        unit2_lower = unit2.lower()
        
        for compatible_set in compatible_sets:
            if unit1_lower in compatible_set and unit2_lower in compatible_set:
                return True
        
        return unit1_lower == unit2_lower
