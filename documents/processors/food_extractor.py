import re
from core.models import Food, FoodBenefit, FoodAllergen, FoodCondition

CANONICAL_FOODS = {
    # Grain
    'rice': ('Rice', 'grain'),
    'wheat': ('Wheat', 'grain'),
    'roti': ('Roti', 'grain'),
    'chapati': ('Chapati', 'grain'),
    'oat': ('Oats', 'grain'),
    'oats': ('Oats', 'grain'),
    'oatmeal': ('Oats', 'grain'),
    'millet': ('Millet', 'grain'),
    'millets': ('Millet', 'grain'),
    'jowar': ('Jowar', 'grain'),
    'bajra': ('Bajra', 'grain'),
    'barley': ('Barley', 'grain'),
    'atta': ('Atta', 'grain'),
    'maize': ('Maize', 'grain'),
    'poha': ('Poha', 'grain'),
    'upma': ('Upma', 'grain'),
    'idli': ('Idli', 'grain'),
    'dosa': ('Dosa', 'grain'),
    'khichdi': ('Khichdi', 'grain'),
    'pongal': ('Pongal', 'grain'),
    'biryani': ('Biryani', 'grain'),
    'pulao': ('Pulao', 'grain'),
    'paratha': ('Paratha', 'grain'),
    'bread': ('Bread', 'grain'),
    'quinoa': ('Quinoa', 'grain'),
    'suji': ('Suji', 'grain'),
    # Pulse
    'dal': ('Dal', 'pulse'),
    'moong': ('Moong Dal', 'pulse'),
    'masoor': ('Masoor Dal', 'pulse'),
    'chana': ('Chana Dal', 'pulse'),
    'rajma': ('Rajma', 'pulse'),
    'lentil': ('Lentils', 'pulse'),
    'lentils': ('Lentils', 'pulse'),
    'urad': ('Urad Dal', 'pulse'),
    'toor': ('Toor Dal', 'pulse'),
    'arhar': ('Arhar Dal', 'pulse'),
    'chickpea': ('Chickpeas', 'pulse'),
    'chickpeas': ('Chickpeas', 'pulse'),
    'lobiya': ('Lobiya', 'pulse'),
    'soybean': ('Soybean', 'pulse'),
    'soybeans': ('Soybean', 'pulse'),
    'tofu': ('Tofu', 'pulse'),
    'besan': ('Besan', 'pulse'),
    # Vegetable
    'spinach': ('Spinach', 'vegetable'),
    'palak': ('Spinach', 'vegetable'),
    'carrot': ('Carrots', 'vegetable'),
    'carrots': ('Carrots', 'vegetable'),
    'tomato': ('Tomato', 'vegetable'),
    'tomatoes': ('Tomato', 'vegetable'),
    'onion': ('Onions', 'vegetable'),
    'onions': ('Onions', 'vegetable'),
    'brinjal': ('Brinjal', 'vegetable'),
    'baingan': ('Brinjal', 'vegetable'),
    'bitter gourd': ('Bitter Gourd', 'vegetable'),
    'karela': ('Bitter Gourd', 'vegetable'),
    'pumpkin': ('Pumpkin', 'vegetable'),
    'bottle gourd': ('Bottle Gourd', 'vegetable'),
    'lauki': ('Bottle Gourd', 'vegetable'),
    'capsicum': ('Capsicum', 'vegetable'),
    'cabbage': ('Cabbage', 'vegetable'),
    'cauliflower': ('Cauliflower', 'vegetable'),
    'potato': ('Potatoes', 'vegetable'),
    'potatoes': ('Potatoes', 'vegetable'),
    'aloo': ('Potatoes', 'vegetable'),
    'methi': ('Methi', 'vegetable'),
    'drumstick': ('Drumstick', 'vegetable'),
    'moringa': ('Drumstick', 'vegetable'),
    'beetroot': ('Beetroot', 'vegetable'),
    'radish': ('Radish', 'vegetable'),
    'turnip': ('Turnip', 'vegetable'),
    'okra': ('Okra', 'vegetable'),
    'bhindi': ('Okra', 'vegetable'),
    'cucumber': ('Cucumber', 'vegetable'),
    'zucchini': ('Zucchini', 'vegetable'),
    'mushroom': ('Mushrooms', 'vegetable'),
    'mushrooms': ('Mushrooms', 'vegetable'),
    'sweet potato': ('Sweet Potato', 'vegetable'),
    'peas': ('Peas', 'vegetable'),
    'pea': ('Peas', 'vegetable'),
    'matar': ('Peas', 'vegetable'),
    'corn': ('Corn', 'vegetable'),
    'bhutta': ('Corn', 'vegetable'),
    # Fruit
    'banana': ('Banana', 'fruit'),
    'bananas': ('Banana', 'fruit'),
    'apple': ('Apples', 'fruit'),
    'apples': ('Apples', 'fruit'),
    'mango': ('Mango', 'fruit'),
    'mangoes': ('Mango', 'fruit'),
    'papaya': ('Papaya', 'fruit'),
    'guava': ('Guava', 'fruit'),
    'orange': ('Orange', 'fruit'),
    'oranges': ('Orange', 'fruit'),
    'pomegranate': ('Pomegranate', 'fruit'),
    'amla': ('Amla', 'fruit'),
    'pear': ('Pears', 'fruit'),
    'pears': ('Pears', 'fruit'),
    'grape': ('Grapes', 'fruit'),
    'grapes': ('Grapes', 'fruit'),
    'watermelon': ('Watermelon', 'fruit'),
    'coconut': ('Coconut', 'fruit'),
    'lemon': ('Lemon', 'fruit'),
    'lime': ('Lime', 'fruit'),
    'kiwi': ('Kiwi', 'fruit'),
    'pineapple': ('Pineapple', 'fruit'),
    'fig': ('Fig', 'fruit'),
    'figs': ('Fig', 'fruit'),
    'dates': ('Dates', 'fruit'),
    # Dairy
    'milk': ('Milk', 'dairy'),
    'curd': ('Curd', 'dairy'),
    'yogurt': ('Curd', 'dairy'),
    'paneer': ('Paneer', 'dairy'),
    'ghee': ('Ghee', 'dairy'),
    'buttermilk': ('Buttermilk', 'dairy'),
    'lassi': ('Lassi', 'dairy'),
    'cheese': ('Cheese', 'dairy'),
    'whey': ('Whey', 'dairy'),
    'raita': ('Raita', 'dairy'),
    'chaas': ('Chaas', 'dairy'),
    'kheer': ('Kheer', 'dairy'),
    # Nuts / Seeds
    'almond': ('Almonds', 'nut_seed'),
    'walnut': ('Walnuts', 'nut_seed'),
    'cashew': ('Cashews', 'nut_seed'),
    'peanut': ('Peanuts', 'nut_seed'),
    'pistachio': ('Pistachios', 'nut_seed'),
    'groundnut': ('Peanuts', 'nut_seed'),
    'sesame': ('Sesame Seeds', 'nut_seed'),
    'flaxseed': ('Flaxseed', 'nut_seed'),
    'chia': ('Chia Seeds', 'nut_seed'),
}

DEFAULT_COMPOSITE_INGREDIENTS = {
    'Khichdi': ['rice', 'moong dal', 'ghee', 'turmeric', 'cumin'],
    'Biryani': ['rice', 'spices', 'ghee', 'onion'],
    'Pulao': ['rice', 'vegetables', 'ghee', 'spices'],
    'Idli': ['rice', 'urad dal'],
    'Dosa': ['rice', 'urad dal'],
    'Poha': ['flattened rice', 'onion', 'mustard seed', 'turmeric', 'coriander'],
    'Upma': ['suji', 'mustard seed', 'curry leaves', 'onion'],
    'Paratha': ['atta', 'ghee'],
    'Raita': ['curd', 'cucumber', 'cumin'],
    'Kheer': ['rice', 'milk', 'cardamom'],
}

DEFAULT_FOOD_MEAL_TYPES = {
    # Breakfast & Morning Items
    'Upma': ['breakfast', 'snack'],
    'Dosa': ['breakfast', 'dinner'],
    'Paratha': ['breakfast', 'lunch'],
    'Bread': ['breakfast', 'snack'],
    'Oats': ['breakfast', 'snack'],
    'Milk': ['breakfast', 'snack', 'dinner'],
    'Curd': ['breakfast', 'lunch'],
    'Cheese': ['breakfast', 'snack'],
    'Chia Seeds': ['breakfast', 'snack'],

    # Fruits (primarily Morning Breakfast & Snack)
    'Banana': ['breakfast', 'snack'],
    'Apples': ['breakfast', 'snack'],
    'Dates': ['breakfast', 'snack'],
    'Fig': ['breakfast', 'snack'],
    'Mango': ['breakfast', 'snack'],
    'Orange': ['breakfast', 'snack'],
    'Papaya': ['breakfast', 'snack'],
    'Pomegranate': ['breakfast', 'snack'],
    'Grapes': ['snack'],
    'Guava': ['snack'],
    'Kiwi': ['snack'],
    'Pears': ['snack'],
    'Pineapple': ['snack'],
    'Watermelon': ['snack'],

    # Beverages & Light Snacks
    'Buttermilk': ['snack', 'lunch'],
    'Coconut': ['snack', 'lunch'],
    'Corn': ['snack', 'lunch'],
    'Cucumber': ['snack', 'lunch', 'dinner'],
    'Lemon': ['snack', 'lunch'],
    'Kheer': ['snack', 'lunch', 'dinner'],

    # Main Staples (Lunch & Dinner)
    'Rice': ['lunch', 'dinner'],
    'Roti': ['lunch', 'dinner'],
    'Atta': ['lunch', 'dinner'],
    'Wheat': ['lunch', 'dinner'],
    'Bajra': ['lunch', 'dinner'],
    'Barley': ['lunch', 'dinner'],
    'Jowar': ['lunch', 'dinner'],
    'Maize': ['lunch', 'dinner'],
    'Millet': ['lunch', 'dinner'],
    'Quinoa': ['lunch', 'dinner'],
    'Pulao': ['lunch', 'dinner'],
    'Biryani': ['lunch', 'dinner'],

    # Pulses & Dals (Lunch & Dinner)
    'Dal': ['lunch', 'dinner'],
    'Lentils': ['lunch', 'dinner'],
    'Rajma': ['lunch', 'dinner'],
    'Paneer': ['lunch', 'dinner'],

    # Vegetables & Accompaniments (Lunch & Dinner)
    'Beetroot': ['lunch', 'dinner'],
    'Bottle Gourd': ['lunch', 'dinner'],
    'Brinjal': ['lunch', 'dinner'],
    'Capsicum': ['lunch', 'dinner'],
    'Carrots': ['lunch', 'dinner'],
    'Cauliflower': ['lunch', 'dinner'],
    'Methi': ['lunch', 'dinner'],
    'Mushrooms': ['lunch', 'dinner'],
    'Okra': ['lunch', 'dinner'],
    'Onions': ['lunch', 'dinner'],
    'Peas': ['lunch', 'dinner'],
    'Potatoes': ['lunch', 'dinner'],
    'Pumpkin': ['lunch', 'dinner'],
    'Spinach': ['lunch', 'dinner'],
    'Tomato': ['lunch', 'dinner'],
    'Ghee': ['lunch', 'dinner'],
    'Raita': ['lunch', 'dinner'],
}

SEASON_KEYWORDS = {
    'summer': ['summer', 'hot season', 'heat', 'cooling', 'body heat', 'thirst', 'hot days', 'summer months'],
    'monsoon': ['monsoon', 'rainy season', 'rainy', 'rains', 'wet season', 'humid season', 'damp'],
    'winter': ['winter', 'cold season', 'cold weather', 'chilly', 'warming', 'cold days', 'winter months'],
    'spring': ['spring', 'spring season', 'moderate weather', 'fresh'],
    'autumn': ['autumn', 'fall season', 'post-monsoon', 'sharad'],
}

WEATHER_KEYWORDS = {
    'HOT': ['hot weather', 'cooling', 'reduce heat', 'heat wave', 'warm days', 'thirst'],
    'VERY_HOT': ['extreme heat', 'scorching', 'very hot', 'heat exhaustion'],
    'RAINY': ['monsoon', 'rainy', 'rain', 'rains', 'wet weather'],
    'HUMID': ['humid', 'humidity', 'muggy', 'sticky', 'damp'],
    'COOL': ['cool weather', 'mild cold', 'cool days'],
    'COLD': ['cold weather', 'winter cold', 'chilly', 'warming', 'keep body warm', 'heats the body'],
}

MEAL_KEYWORDS = {
    'breakfast': ['breakfast', 'morning meal', 'morning', 'start of day', 'early morning', 'tiffin'],
    'lunch': ['lunch', 'midday', 'afternoon', 'main meal', 'noon'],
    'dinner': ['dinner', 'evening meal', 'night', 'supper', 'light dinner'],
    'snack': ['snack', 'between meals', 'mid-morning', 'evening snack', 'tea-time', 'light bite'],
}

CONDITION_KEYWORDS = {
    'diabetes': ['blood sugar', 'glycemic', 'insulin', 'diabetic', 'diabetes', 'glucose'],
    'hypertension': ['blood pressure', 'hypertension', 'sodium', 'cardiovascular', 'heart health', 'bp'],
    'cholesterol': ['cholesterol', 'ldl', 'hdl', 'lipid', 'triglyceride'],
    'weight_loss': ['weight loss', 'obesity', 'low calorie', 'low fat', 'burn fat', 'overweight', 'slimming'],
    'anemia': ['anemia', 'anaemia', 'hemoglobin', 'haemoglobin', 'iron deficiency', 'iron-rich'],
    'thyroid': ['thyroid', 'hypothyroid', 'hyperthyroid', 'goiter'],
    'pcos': ['pcos', 'pcod', 'polycystic', 'hormonal'],
    'digestive': ['digestive', 'digestion', 'ibs', 'gut health', 'bloating', 'constipation', 'stomach'],
}

ALLERGEN_MAP = {
    'peanut': ['peanut', 'groundnut'],
    'gluten': ['wheat', 'barley', 'rye', 'maida', 'atta', 'bread', 'semolina', 'suji'],
    'dairy': ['milk', 'curd', 'yogurt', 'paneer', 'ghee', 'cheese', 'butter', 'lactose', 'whey'],
    'tree_nut': ['cashew', 'almond', 'walnut', 'pistachio'],
    'soy': ['soy', 'soybean', 'tofu'],
    'egg': ['egg', 'eggs'],
    'shellfish': ['prawn', 'shrimp', 'crab', 'lobster', 'shellfish'],
}

AVOID_WORDS = ['avoid', 'should not', 'do not eat', 'harmful for', 'contraindicated', 'not recommended', 'bad for']
LIMIT_WORDS = ['limit', 'moderate', 'in small amounts', 'reduce', 'minimize', 'minimise', 'sparingly']
BENEFIT_WORDS = ['good for', 'beneficial', 'helps', 'recommended', 'rich in', 'source of', 'provides', 'improves', 'reduces', 'prevents', 'supports', 'aids', 'boosts', 'ideal for', 'essential for']

REJECT_SECTION_PATTERNS = [
    r'\btable of contents\b',
    r'\bcontents\n',
    r'\bindex\n',
    r'\bbibliography\b',
    r'\bfood spoilage\b',
    r'\bspoilage occurs\b',
    r'\bmicro-organisms\b',
    r'\bunfit to eat\b',
    r'\bfood safety\b',
    r'\bfood hygiene\b',
    r'\buse by date\b',
    r'\bexam practice\b',
    r'\bexam questions\b',
    r'\btest your knowledge\b',
    r'\brevision notes\b',
    r'\banswers to questions\b',
    r'\b\(?\d+\s*marks?\)?',
    r'\bidentify one\b',
]

def extract_foods(pages, source):
    """
    Parses clean pages/sections and creates/updates Food domain records.
    Returns total count of foods processed.
    """
    count = 0
    for page in pages:
        text = page.get('text', '')
        blocks = _find_food_blocks(text)
        for block in blocks:
            food = _build_food_record(block, page, source)
            if food:
                count += 1
    return count

def _find_food_blocks(text):
    blocks = []
    t_lower = text.lower()

    # Reject non-food sections (e.g. food spoilage chapters, exam pages, TOCs)
    if any(re.search(pat, t_lower[:300]) for pat in REJECT_SECTION_PATTERNS):
        return blocks

    paragraphs = re.split(r'\n{2,}', text)
    for para in paragraphs:
        para = para.strip()
        if len(para) < 35:
            continue
        # Skip figure captions, table titles, exam questions
        first_line = para.split('\n')[0].strip().lower()
        if re.match(r'^(t\s+)?(figure|fig\.|table|diagram|source|photo)\b', first_line):
            continue
        if any(re.search(pat, first_line) for pat in REJECT_SECTION_PATTERNS):
            continue

        detected = _detect_food_name(para)
        if detected:
            food_name, category = detected
            blocks.append({
                'food_name': food_name,
                'category': category,
                'text': para
            })
    return blocks

def _detect_food_name(text):
    text_lower = text.lower()
    first_line = text_lower.split('\n')[0].strip()

    # Strip chapter number prefixes (e.g. '1. The Troublesome Tomato' -> 'the troublesome tomato')
    clean_first_line = re.sub(r'^\d+[\.\)]\s*', '', first_line)

    # 1. Match against prominent heading/first line
    for kw, (canonical, category) in CANONICAL_FOODS.items():
        if re.search(rf'\b{re.escape(kw)}\b', clean_first_line):
            return canonical, category

    # 2. Match against very first sentence ONLY if prominent subject
    first_sentence = re.split(r'[.!?\n]', text_lower)[0].strip()
    if len(first_sentence) < 150:
        for kw, (canonical, category) in CANONICAL_FOODS.items():
            # Matches: 'Rice is...', 'Tomato provides...', 'In the case of peas...', 'diversity of rice...'
            pattern = rf'(?:^|\b(?:the|in the case of|celebrate|about|history of|fresh|cooked|eating|make|making)\s+){re.escape(kw)}\b'
            if re.search(pattern, first_sentence):
                return canonical, category

    return None

def _extract_summary(food_name, text):
    sentences = re.split(r'(?<=[.!?\n])\s+', text.strip())
    clean_sentences = []
    food_kw = food_name.lower()

    for s in sentences:
        s_clean = s.strip()
        s_lower = s_clean.lower()
        # Sentence must have substance and no exam/TOC noise
        if len(s_clean) < 25 or len(s_clean) > 350:
            continue
        if any(re.search(pat, s_lower) for pat in REJECT_SECTION_PATTERNS):
            continue
        # Clean linebreaks within sentence
        s_clean = re.sub(r'\s+', ' ', s_clean)
        
        # Prioritize sentences that explicitly discuss this food
        if food_kw in s_lower or any(part in s_lower for part in food_kw.split()):
            clean_sentences.append(s_clean)
            if len(clean_sentences) >= 2:
                break

    if clean_sentences:
        return " ".join(clean_sentences)[:450]
    
    # Fallback to first coherent sentence if food is the chapter topic
    for s in sentences:
        s_clean = re.sub(r'\s+', ' ', s.strip())
        if len(s_clean) > 30 and not any(re.search(pat, s_clean.lower()) for pat in REJECT_SECTION_PATTERNS):
            return s_clean[:450]

    return f"{food_name} is a nutrient-dense food featured in authentic culinary and dietary literature."

def _extract_ingredients(food_name, text):
    t_lower = text.lower()
    ingredients = set()

    # 1. Check explicit ingredients section
    header_match = re.search(r'(?:ingredients|what you need|made with|components)\s*[:\-]\s*(.*?)(?:\n\n|\.\s+|$)', t_lower, re.DOTALL)
    if header_match:
        section = header_match.group(1)
        raw_items = re.split(r'[,;\n•\*\-]', section)
        for item in raw_items:
            clean = item.strip()
            if 2 < len(clean) < 35 and not any(ch in clean for ch in ['©', '<', '>']):
                ingredients.add(clean)

    # 2. If composite dish and no ingredients found, use standard base ingredients
    if not ingredients and food_name in DEFAULT_COMPOSITE_INGREDIENTS:
        return sorted(DEFAULT_COMPOSITE_INGREDIENTS[food_name])

    # 3. For single-ingredient foods, the food itself is the primary ingredient
    if not ingredients:
        return [food_name.lower()]

    return sorted(list(ingredients))

def _detect_seasons(text):
    t_lower = text.lower()
    seasons = [s for s, kws in SEASON_KEYWORDS.items() if any(re.search(rf'\b{re.escape(k)}\b', t_lower) for k in kws)]
    return seasons or ['summer', 'monsoon', 'winter', 'spring', 'autumn']

def _detect_weather_categories(text):
    t_lower = text.lower()
    cats = [w for w, kws in WEATHER_KEYWORDS.items() if any(k in t_lower for k in kws)]
    return cats

def _detect_meal_types(food_name, text):
    if food_name in DEFAULT_FOOD_MEAL_TYPES:
        return list(DEFAULT_FOOD_MEAL_TYPES[food_name])
    t_lower = text.lower()
    meals = [m for m, kws in MEAL_KEYWORDS.items() if any(k in t_lower for k in kws)]
    return meals or ['lunch', 'dinner']

def _infer_diet_types(category, ingredients):
    has_dairy = any(any(d in str(ing).lower() for d in ALLERGEN_MAP['dairy']) for ing in ingredients) or category == 'dairy'
    if category in ['grain', 'pulse', 'vegetable', 'fruit', 'nut_seed', 'spice', 'oil']:
        if not has_dairy:
            return ['vegan', 'vegetarian', 'non-vegetarian']
        return ['vegetarian', 'non-vegetarian']
    elif category == 'dairy':
        return ['vegetarian', 'non-vegetarian']
    return ['non-vegetarian']

def _build_food_record(block, page, source):
    food_name = block['food_name']
    text = block['text']
    category = block['category']

    summary = _extract_summary(food_name, text)
    ingredients = _extract_ingredients(food_name, text)
    seasons = _detect_seasons(text)
    weather_cats = _detect_weather_categories(text)
    meal_types = _detect_meal_types(food_name, text)
    diet_types = _infer_diet_types(category, ingredients)

    food, created = Food.objects.get_or_create(
        name__iexact=food_name,
        defaults={'name': food_name}
    )

    # Only set/update summary if newly created or if existing is a short default
    if created or len(food.summary) < 50:
        food.summary = summary
        food.original_text = text[:1000]
        food.source = source
        food.page_number = page.get('page_number')
        food.chapter = page.get('chapter', '')
        food.source_url = page.get('url', '')

    food.category = category
    food.ingredients = ingredients
    food.diet_types = diet_types
    food.meal_types = meal_types
    food.seasons = seasons
    food.weather_categories = weather_cats
    food.save()

    _extract_benefits(food, text)
    _extract_conditions(food, text)
    _extract_allergens(food, ingredients)

    return food

def _extract_benefits(food, text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    food_kw = food.name.lower()

    for s in sentences:
        s_clean = re.sub(r'\s+', ' ', s.strip())
        s_lower = s_clean.lower()
        if len(s_clean) < 25 or len(s_clean) > 300:
            continue
        # Skip exam questions, marks, and non-food content
        if any(re.search(pat, s_lower) for pat in REJECT_SECTION_PATTERNS):
            continue
        # Must contain benefit indicator and explicitly reference the food
        if any(b in s_lower for b in BENEFIT_WORDS):
            if food_kw in s_lower or any(part in s_lower for part in food_kw.split() if len(part) > 3):
                FoodBenefit.objects.get_or_create(food=food, benefit=s_clean)

def _extract_conditions(food, text):
    t_lower = text.lower()
    food_kw = food.name.lower()
    
    # Must explicitly mention this food
    if food_kw not in t_lower and not any(part in t_lower for part in food_kw.split() if len(part) > 3):
        return

    for cond, kws in CONDITION_KEYWORDS.items():
        if any(k in t_lower for k in kws):
            rec_type = 'RECOMMENDED'
            if any(a in t_lower for a in AVOID_WORDS):
                rec_type = 'AVOID'
            elif any(l in t_lower for l in LIMIT_WORDS):
                rec_type = 'LIMIT'
            
            # Find specific sentence mentioning the condition and food
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if any(k in s.lower() for k in kws)]
            clean_s = [s for s in sentences if not any(re.search(pat, s.lower()) for pat in REJECT_SECTION_PATTERNS)]
            reason_text = clean_s[0] if clean_s else f"{food.name} is noted in dietary reference for {cond}."
            
            FoodCondition.objects.get_or_create(
                food=food,
                condition_name=cond,
                defaults={'recommendation_type': rec_type, 'reason': reason_text[:280]}
            )

def _extract_allergens(food, ingredients):
    for allergen, triggers in ALLERGEN_MAP.items():
        for ing in ingredients:
            if any(t in ing.lower() for t in triggers):
                FoodAllergen.objects.get_or_create(food=food, allergen=allergen)
                break
