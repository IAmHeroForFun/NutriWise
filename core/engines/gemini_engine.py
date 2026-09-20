import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

JSON_SCHEMA_TEMPLATE = """
{
  "overall_summary": "Brief summary of today's whole-day personalized plan",
  "meals": {
    "breakfast": [
      {
        "food_name": "Exact Name from Catalog",
        "clinical_rationale": "1 concise sentence explaining why this food is beneficial for the user's health condition or weather",
        "health_benefits": ["Benefit 1", "Benefit 2"],
        "source_citation": "Source Title from Catalog",
        "page_number": 1
      }
    ],
    "snack": [
      {
        "food_name": "Exact Name from Catalog",
        "clinical_rationale": "Why this snack provides sustained energy",
        "health_benefits": ["Benefit 1"],
        "source_citation": "Source Title",
        "page_number": 1
      }
    ],
    "lunch": [
      {
        "food_name": "Exact Name from Catalog",
        "clinical_rationale": "Why this food forms a balanced midday meal",
        "health_benefits": ["Benefit 1"],
        "source_citation": "Source Title",
        "page_number": 1
      }
    ],
    "dinner": [
      {
        "food_name": "Exact Name from Catalog",
        "clinical_rationale": "Why this food aids evening digestion and restorative sleep",
        "health_benefits": ["Benefit 1"],
        "source_citation": "Source Title",
        "page_number": 1
      }
    ]
  }
}
"""

def generate_grounded_plan(profile, candidate_foods, weather_info, season, target_meal=None):
    """
    Calls Gemini API with candidate foods and book citations to curate
    a strictly grounded dietary plan for the entire day matching the user's profile, weather, and conditions.
    
    Returns a dict with curated meals and citations, or None if API unavailable.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
    if not api_key:
        logger.info("GEMINI_API_KEY not configured. Using deterministic engine.")
        return None

    model = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # Prepare compact, token-efficient candidates catalog grounded in DB
    catalog = []
    for f in candidate_foods:
        source_title = f.source.title if f.source else "Nutritional Reference"
        excerpt = f.original_text.replace('\n', ' ')[:250] if f.original_text else f.summary[:200]
        catalog.append({
            "name": f.name,
            "category": f.category,
            "ingredients": f.ingredients,
            "source": source_title,
            "page": f.page_number,
            "excerpt": excerpt
        })

    system_instruction = (
        "You are NutriWise Clinical Dietitian. You curate balanced, health-promoting daily meals. "
        "CRITICAL GROUNDING RULE: You MUST ONLY select dishes and cite ingredients from the provided CANDIDATE FOODS catalog. "
        "DO NOT invent dishes, external recipes, or medical claims. Every recommendation must cite the exact source title and page number. "
        "Ensure recommendations actively support the user's health conditions and suit the current weather and season. "
        "Respond ONLY with a valid JSON object matching the requested schema."
    )

    meal_types = [target_meal] if target_meal else ['breakfast', 'snack', 'lunch', 'dinner']

    prompt = (
        f"USER PROFILE:\n"
        f"- Diet: {profile.diet_type}\n"
        f"- Health Conditions: {', '.join(profile.conditions) if profile.conditions else 'None'}\n"
        f"- Allergies to Avoid (already filtered): {', '.join(profile.allergies) if profile.allergies else 'None'}\n"
        f"- Liked Ingredients: {', '.join(profile.liked_ingredients) if profile.liked_ingredients else 'Any'}\n"
        f"- Disliked Ingredients: {', '.join(profile.disliked_ingredients) if profile.disliked_ingredients else 'None'}\n"
        f"- Location: {profile.location_city or 'Local'}\n"
        f"- Weather: {weather_info.get('temp', 'Moderate')}°C, {weather_info.get('description', 'Clear')}, Category: {weather_info.get('category', 'NORMAL')}\n"
        f"- Season: {season}\n\n"
        f"MEALS TO PLAN: {meal_types}\n\n"
        f"AVAILABLE CANDIDATE FOODS FROM UPLOADED BOOKS (Grounding Catalog):\n"
        f"{json.dumps(catalog, indent=1)}\n\n"
        f"INSTRUCTIONS:\n"
        f"Curate 2 to 4 complementary foods for each requested meal slot to form a balanced, complete daily regimen.\n"
        f"Ensure no food is repeated across meals.\n"
        f"Format your response strictly as JSON matching this schema:\n"
        f"{JSON_SCHEMA_TEMPLATE}\n"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_instruction + "\n\n" + prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    models_to_try = []
    for m in [model, 'gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-flash-latest', 'gemini-2.5-flash-lite']:
        if m and m not in models_to_try:
            models_to_try.append(m)

    for m in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        try:
            response = requests.post(url, json=payload, timeout=25)
            if response.status_code == 200:
                data = response.json()
                raw_text = data['candidates'][0]['content']['parts'][0]['text']
                result_json = json.loads(raw_text)
                return result_json
            elif response.status_code in [503, 404, 429]:
                logger.warning(f"Model {m} returned {response.status_code}, trying next model...")
                continue
            else:
                logger.warning(f"Gemini API returned status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error calling Gemini model {m}: {str(e)}")
            continue

    return None
