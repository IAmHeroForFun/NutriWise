from core.engines.hard_filters import apply_hard_filters

def find_alternatives(food, profile, top_n=5):
    """
    Finds substitute dishes sharing key ingredients from the authoritative knowledge base.
    Also suggests alternate usages of those ingredients.
    """
    safe_pool = apply_hard_filters(profile)
    candidate_foods = [f for f in safe_pool if f.id != food.id]

    my_ingredients = {str(i).strip().lower() for i in (food.ingredients or []) if str(i).strip()}

    scored_alternatives = []
    if my_ingredients:
        for candidate in candidate_foods:
            cand_ings = {str(ci).strip().lower() for ci in (candidate.ingredients or []) if str(ci).strip()}
            shared = my_ingredients & cand_ings
            if shared:
                scored_alternatives.append({
                    'food': candidate,
                    'shared': sorted([s.title() for s in shared]),
                    'overlap_count': len(shared),
                })
        scored_alternatives.sort(key=lambda x: x['overlap_count'], reverse=True)

    # Per-ingredient alternative dishes (for top 4 ingredients)
    ingredient_uses = {}
    for ing in list(my_ingredients)[:4]:
        matches = []
        for candidate in candidate_foods:
            cand_ings = [str(ci).strip().lower() for ci in (candidate.ingredients or [])]
            if any(ing in ci for ci in cand_ings) or ing in candidate.name.lower():
                matches.append(candidate)
        if matches:
            ingredient_uses[ing.title()] = matches[:3]

    return {
        'original_food': food,
        'shared_ingredient_alternatives': scored_alternatives[:top_n],
        'ingredient_uses': ingredient_uses,
    }
