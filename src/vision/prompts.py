"""
Structured prompts for nutrition label extraction.

Anti-hallucination strategies:
1. Strict output format (JSON)
2. Explicit "return empty if no data" instruction
3. "Do NOT invent" warnings
4. Request for confidence self-assessment
"""

NUTRITION_DETECTION_PROMPT = """Analyze this image and determine if it contains nutrition information.

Look for:
- Nutrition Facts panels
- Supplement Facts tables
- Nutrition Information sections
- Lists of nutrients with amounts (Protein, Vitamins, Minerals, etc.)

IMPORTANT: Marketing text mentioning vitamins (like "Contains Vitamin B") is NOT nutrition data.
Only images with actual nutritional values (amounts + units) should be considered valid.

Return ONLY a JSON object in this exact format:
{
  "has_nutrition_data": true or false,
  "confidence": "high" or "medium" or "low",
  "reason": "brief explanation of why you think this"
}

Example valid nutrition data:
- "Protein 24g"
- "Vitamin C 60mg"
- A table with nutrient names and amounts

Example NOT valid nutrition data:
- Product front label with no nutrition info
- Marketing text only
- Ingredient lists without amounts

Return only the JSON, no other text."""


NUTRITION_EXTRACTION_PROMPT = """Extract ALL nutritional information from this image.

CRITICAL ANTI-HALLUCINATION RULES:
1. ONLY extract data you can CLEARLY SEE in the image
2. If a nutrient is not visible, DO NOT include it
3. If an amount is unclear, use 0
4. DO NOT invent or estimate values
5. If you see ZERO nutrients, return "NONE"

COMPACT OUTPUT FORMAT (uses 80% fewer tokens than JSON):
Return data as pipe-delimited lines. Each nutrient on one line.

Format:
NUTRIENTS:
Vitamin C|vitamin_c|60|mg|1|
Calcium|calcium|200|mg|1|20
Protein|protein|24|g|1|

SERVING:
2 capsules|30

CONFIDENCE:
high

AMBIGUITIES:
unclear label for vitamin E

Field order per nutrient line: raw_name|standard_name|amount|unit|per_serving|daily_value_pct
- raw_name: exact text from image
- standard_name: vitamin_c, protein, calcium, vitamin_b12, vitamin_d, iron, zinc, etc.
- amount: numeric value only
- unit: g, mg, mcg, µg, IU, cal, kJ
- per_serving: 1 for yes, 0 for no (per 100g)
- daily_value_pct: percentage number or leave empty if not shown

If NO nutrition data found, return just: NONE

Do not add extra explanations. Follow format exactly."""


def get_detection_prompt() -> str:
    """Get nutrition data detection prompt."""
    return NUTRITION_DETECTION_PROMPT


def get_extraction_prompt() -> str:
    """Get nutrition extraction prompt."""
    return NUTRITION_EXTRACTION_PROMPT
