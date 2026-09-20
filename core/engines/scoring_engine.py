WEIGHTS = {
    'diet_compatible': 20,       # Base compatibility guarantee
    'meal_compatible': 20,       # Fits meal slot (e.g. breakfast)
    'health_recommended': 20,    # Explicitly RECOMMENDED in books for condition
    'season_suitable': 15,       # Matches current Indian season
    'weather_suitable': 10,      # Matches current weather (rain/cooling/warming)
    'liked_food': 10,            # User explicitly marked as favourite
    'liked_ingredient': 5,       # Contains an ingredient the user enjoys
}

def score_food(food, profile, meal_type, season, weather_cat):
    """
    Computes deterministic 0-100 score and explicit explanation reasons.
    """
    score = WEIGHTS['diet_compatible']
    reasons = ["Compatible with your diet"]

    # 1. Meal slot compatibility
    if meal_type in (food.meal_types or []):
        score += WEIGHTS['meal_compatible']
        reasons.append(f"Good for {meal_type.title()}")

    # 2. Medical condition bonuses
    user_conditions = {str(c).strip().lower() for c in (profile.conditions or []) if str(c).strip()}
    if user_conditions:
        rec_conditions = [
            c_obj.condition_name.replace('_', ' ').title()
            for c_obj in food.conditions.all()
            if c_obj.condition_name.strip().lower() in user_conditions and c_obj.recommendation_type == 'RECOMMENDED'
        ]
        if rec_conditions:
            score += WEIGHTS['health_recommended']
            reasons.append(f"Recommended for {', '.join(rec_conditions)}")

    # 3. Season compatibility
    if season in (food.seasons or []):
        score += WEIGHTS['season_suitable']
        reasons.append(f"Great for {season.title()} season")

    # 4. Weather compatibility
    if weather_cat and weather_cat != 'NORMAL':
        if weather_cat in (food.weather_categories or []):
            score += WEIGHTS['weather_suitable']
            reasons.append(f"Suits {weather_cat.lower()} weather")

    # 5. Liked food bonus
    user_liked_foods = [str(f).strip().lower() for f in (profile.liked_foods or []) if str(f).strip()]
    food_name_lower = food.name.strip().lower()
    if any(lf in food_name_lower or food_name_lower in lf for lf in user_liked_foods):
        score += WEIGHTS['liked_food']
        reasons.append("⭐ One of your favourites")

    # 6. Liked ingredients bonus
    user_liked_ings = [str(i).strip().lower() for i in (profile.liked_ingredients or []) if str(i).strip()]
    if user_liked_ings and food.ingredients:
        f_ings_lower = [str(i).strip().lower() for i in food.ingredients]
        matched_ings = [
            li.title() for li in user_liked_ings
            if any(li in fi for fi in f_ings_lower) or li in food.name.lower()
        ]
        if matched_ings:
            score += WEIGHTS['liked_ingredient']
            reasons.append(f"Contains {', '.join(matched_ings[:2])}")

    # 7. Auto-learned affinity from past AI interactions and feedback
    if profile and getattr(profile, 'user_id', None):
        try:
            from core.models import UserFoodAffinity
            affinity = UserFoodAffinity.objects.filter(user_id=profile.user_id, food=food).first()
            if affinity and affinity.score_boost != 0:
                score += affinity.score_boost
                if affinity.score_boost > 0:
                    reasons.append(f"🧠 Auto-learned preference (+{affinity.score_boost} pts)")
        except Exception:
            pass

    return {
        'food': food,
        'score': max(0, min(100, score)),
        'reasons': reasons
    }

def rank_foods(foods, profile, meal_type, season, weather_cat):
    """
    Ranks a list of candidate foods by total score descending.
    """
    scored = [score_food(f, profile, meal_type, season, weather_cat) for f in foods]
    return sorted(scored, key=lambda x: x['score'], reverse=True)
