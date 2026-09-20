CATEGORY_ROLES = {
    'grain': 'carb',
    'pulse': 'protein',
    'vegetable': 'vegetable',
    'fruit': 'fruit_or_nut',
    'nut_seed': 'fruit_or_nut',
    'dairy': 'protein',
    'spice': 'flavour',
    'oil': 'cooking',
}

MEAL_STRUCTURES = {
    'breakfast': ['carb', 'protein', 'fruit_or_nut'],
    'snack': ['fruit_or_nut', 'protein'],
    'lunch': ['carb', 'protein', 'vegetable'],
    'dinner': ['carb', 'protein', 'vegetable'],
}

def build_meal(ranked_foods, meal_type, used_food_ids=None):
    """
    Returns all dishes suited for this time of the day, sorted by score with role prioritization.
    """
    needed_roles = list(MEAL_STRUCTURES.get(meal_type, ['carb', 'protein', 'vegetable']))
    selected_items = []
    added_ids = set()

    # First pass: prioritize structural role balance to the top
    for role in needed_roles:
        for item in ranked_foods:
            food = item['food']
            if food.id in added_ids:
                continue
            food_role = CATEGORY_ROLES.get(food.category, 'any')
            if food_role == role:
                selected_items.append(item)
                added_ids.add(food.id)
                break

    # Second pass: append all remaining scored foods compatible with this meal slot
    for item in ranked_foods:
        food = item['food']
        if food.id not in added_ids:
            # Check if food is suitable for this meal slot (or unconstrained)
            if not food.meal_types or meal_type in food.meal_types:
                selected_items.append(item)
                added_ids.add(food.id)

    return selected_items, added_ids
