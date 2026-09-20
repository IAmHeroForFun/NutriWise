from core.models import Food

def apply_hard_filters(profile):
    """
    Applies non-negotiable deterministic exclusions:
    1. Diet type (vegan, vegetarian, non-vegetarian)
    2. Allergies (e.g. peanuts, dairy, gluten)
    3. Health conditions marked AVOID
    4. Disliked specific foods
    5. Disliked ingredients
    6. Disliked whole categories
    Returns: List of safe Food objects
    """
    foods = Food.objects.prefetch_related('allergens', 'conditions', 'benefits').all()

    # 1. Diet Type Filter
    ALLOWED_DIETS = {
        'vegan': {'vegan'},
        'vegetarian': {'vegan', 'vegetarian'},
        'non-vegetarian': {'vegan', 'vegetarian', 'non-vegetarian'},
    }
    user_allowed = ALLOWED_DIETS.get(profile.diet_type, {'vegetarian'})
    safe_foods = [f for f in foods if any(d in user_allowed for d in f.diet_types)]

    # 2. Allergy Filter
    user_allergies = {str(a).strip().lower() for a in (profile.allergies or []) if str(a).strip()}
    if user_allergies:
        safe_foods = [
            f for f in safe_foods
            if not any(allergen_obj.allergen.strip().lower() in user_allergies for allergen_obj in f.allergens.all())
        ]

    # 3. Medical Conditions (AVOID)
    user_conditions = {str(c).strip().lower() for c in (profile.conditions or []) if str(c).strip()}
    if user_conditions:
        safe_foods = [
            f for f in safe_foods
            if not any(
                c_obj.condition_name.strip().lower() in user_conditions and c_obj.recommendation_type == 'AVOID'
                for c_obj in f.conditions.all()
            )
        ]

    # 4. Disliked Foods (Exact name match)
    disliked_food_names = {str(d).strip().lower() for d in (profile.disliked_foods or []) if str(d).strip()}
    if disliked_food_names:
        safe_foods = [f for f in safe_foods if f.name.strip().lower() not in disliked_food_names]

    # 5. Disliked Ingredients (Ingredient substring match)
    disliked_ingredients = [str(i).strip().lower() for i in (profile.disliked_ingredients or []) if str(i).strip()]
    if disliked_ingredients:
        filtered = []
        for f in safe_foods:
            f_ings_lower = [str(ing).strip().lower() for ing in (f.ingredients or [])]
            # Exclude if any disliked ingredient appears in food's ingredients
            has_disliked = any(
                any(dis_ing in ing for ing in f_ings_lower) or any(dis_ing in f.name.lower() for dis_ing in disliked_ingredients)
                for dis_ing in disliked_ingredients
            )
            if not has_disliked:
                filtered.append(f)
        safe_foods = filtered

    # 6. Disliked Categories
    disliked_cats = {str(c).strip().lower() for c in (profile.disliked_categories or []) if str(c).strip()}
    if disliked_cats:
        safe_foods = [f for f in safe_foods if f.category.strip().lower() not in disliked_cats]

    return safe_foods
