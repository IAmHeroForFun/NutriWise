import logging
from django.utils import timezone
from core.models import Food, FoodBenefit, FoodCondition, LearnedMealPattern, UserFoodAffinity

logger = logging.getLogger(__name__)

def distill_ai_knowledge(gemini_result, foods_by_name, user_profile=None):
    """
    Distills AI-generated rationales and benefits back into the local database
    as verified FoodBenefit and FoodCondition records.
    Permanently grows the local rule engine's knowledge graph.
    """
    if not gemini_result or 'meals' not in gemini_result:
        return 0

    distilled_count = 0
    meals = gemini_result.get('meals', {})

    for meal_type, items in meals.items():
        for item in items:
            food_name = item.get('food_name')
            food = foods_by_name.get(food_name.lower()) if food_name else None
            if not food:
                continue

            # 1. Distill health benefits
            benefits = item.get('health_benefits', [])
            if isinstance(benefits, str):
                benefits = [benefits]
            for b in benefits:
                b_clean = b.strip()
                if len(b_clean) > 15:
                    _, created = FoodBenefit.objects.get_or_create(food=food, benefit=b_clean[:350])
                    if created:
                        distilled_count += 1

            # 2. Distill condition links if user has active conditions
            clinical_rationale = item.get('clinical_rationale', '').strip()
            if clinical_rationale and user_profile and user_profile.conditions:
                for cond in user_profile.conditions:
                    # Check if the clinical rationale relates to this condition
                    if cond.lower() in clinical_rationale.lower() or any(w in clinical_rationale.lower() for w in ['sugar', 'blood', 'heart', 'pressure', 'digest', 'weight', 'cholesterol']):
                        _, created = FoodCondition.objects.get_or_create(
                            food=food,
                            condition_name=cond,
                            defaults={
                                'recommendation_type': 'RECOMMENDED',
                                'reason': clinical_rationale[:280]
                            }
                        )
                        if created:
                            distilled_count += 1

    logger.info(f"Distilled {distilled_count} new clinical benefits/conditions into database.")
    return distilled_count

def learn_meal_pattern(meal_type, food_items, weather_info, season, user_profile=None):
    """
    Persists AI-curated combinations of dishes as reusable LearnedMealPattern templates.
    Allows the deterministic engine to serve high-quality combinations instantly offline.
    """
    if not food_items:
        return None

    weather_cat = weather_info.get('category', 'NORMAL')
    target_condition = user_profile.conditions[0] if (user_profile and user_profile.conditions) else ''

    food_objects = []
    for item in food_items:
        if isinstance(item, Food):
            food_objects.append(item)
        elif isinstance(item, dict) and 'id' in item:
            f = Food.objects.filter(id=item['id']).first()
            if f:
                food_objects.append(f)

    if not food_objects:
        return None

    # Check if a matching pattern already exists
    pattern = LearnedMealPattern.objects.filter(
        meal_type=meal_type,
        weather_category=weather_cat,
        target_condition=target_condition
    ).first()

    if pattern:
        pattern.usage_count += 1
        pattern.save()
        return pattern

    pattern = LearnedMealPattern.objects.create(
        meal_type=meal_type,
        season=season,
        weather_category=weather_cat,
        target_condition=target_condition,
        rationale=f"AI-curated balanced {meal_type} for {weather_cat} weather."
    )
    pattern.foods.set(food_objects)
    return pattern

def register_recommendation_exposure(user, food_objects):
    """
    Registers that foods were recommended to a user, creating or updating UserFoodAffinity.
    """
    for food in food_objects:
        affinity, _ = UserFoodAffinity.objects.get_or_create(
            user=user,
            food=food,
            defaults={'score_boost': 0, 'times_recommended': 1}
        )
        if not _:
            affinity.times_recommended += 1
            affinity.save(update_fields=['times_recommended', 'last_interacted'])

def record_user_feedback(user, food_id, action):
    """
    Dynamic reinforcement loop:
    - 'like' / 'favorite': +5 score boost
    - 'cooked': +8 score boost
    - 'reject' / 'cant_make': -8 score penalty
    """
    food = Food.objects.filter(id=food_id).first()
    if not food:
        return None

    affinity, _ = UserFoodAffinity.objects.get_or_create(
        user=user,
        food=food,
        defaults={'score_boost': 0}
    )

    if action in ['like', 'favorite']:
        affinity.score_boost = min(affinity.score_boost + 5, 25)
        affinity.times_accepted += 1
    elif action == 'cooked':
        affinity.score_boost = min(affinity.score_boost + 8, 30)
        affinity.times_accepted += 1
    elif action in ['reject', 'cant_make']:
        affinity.score_boost = max(affinity.score_boost - 8, -25)
        affinity.times_rejected += 1

    affinity.last_interacted = timezone.now()
    affinity.save()
    return affinity.score_boost
