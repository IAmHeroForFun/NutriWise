from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Food, UserProfile, FoodAllergen, FoodCondition
from core.engines import hard_filters, scoring_engine, meal_combiner, season_engine, ingredient_matcher
from datetime import date

class EngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass123')
        self.profile = UserProfile.objects.create(
            user=self.user,
            diet_type='vegetarian',
            allergies=['peanut'],
            conditions=['diabetes'],
            disliked_foods=['bitter gourd'],
            disliked_ingredients=['onion'],
            liked_foods=['khichdi'],
            liked_ingredients=['spinach'],
            location_city='Mumbai',
            onboarding_complete=True
        )

        self.khichdi = Food.objects.create(
            name='Moong Dal Khichdi',
            category='grain',
            ingredients=['moong dal', 'rice', 'turmeric', 'spinach'],
            diet_types=['vegetarian', 'non-vegetarian'],
            meal_types=['lunch', 'dinner'],
            seasons=['monsoon'],
            weather_categories=['RAINY']
        )
        FoodCondition.objects.create(food=self.khichdi, condition_name='diabetes', recommendation_type='RECOMMENDED')

        self.peanut_snack = Food.objects.create(
            name='Peanut Chikki',
            category='nut_seed',
            ingredients=['peanut', 'jaggery'],
            diet_types=['vegetarian'],
            meal_types=['snack'],
            seasons=['winter']
        )
        FoodAllergen.objects.create(food=self.peanut_snack, allergen='peanut')

        self.onion_dish = Food.objects.create(
            name='Onion Pakoda',
            category='vegetable',
            ingredients=['onion', 'besan', 'oil'],
            diet_types=['vegetarian'],
            meal_types=['snack']
        )

    def test_hard_filters_allergy_and_dislikes(self):
        safe_foods = hard_filters.apply_hard_filters(self.profile)
        safe_names = [f.name for f in safe_foods]

        self.assertIn('Moong Dal Khichdi', safe_names)
        self.assertNotIn('Peanut Chikki', safe_names, "Peanut allergy food should be excluded")
        self.assertNotIn('Onion Pakoda', safe_names, "Disliked onion ingredient should be excluded")

    def test_scoring_bonuses(self):
        score_res = scoring_engine.score_food(self.khichdi, self.profile, 'lunch', 'monsoon', 'RAINY')
        self.assertGreaterEqual(score_res['score'], 80)
        reasons_text = " ".join(score_res['reasons'])
        self.assertIn('Recommended for Diabetes', reasons_text)
        self.assertIn('One of your favourites', reasons_text)
        self.assertIn('Suits rainy weather', reasons_text)

    def test_ingredient_matcher_alternatives(self):
        soup = Food.objects.create(
            name='Spinach Moong Dal Soup',
            category='pulse',
            ingredients=['moong dal', 'spinach', 'ginger'],
            diet_types=['vegetarian'],
            meal_types=['dinner']
        )
        alts = ingredient_matcher.find_alternatives(soup, self.profile)
        shared_dishes = [item['food'].name for item in alts['shared_ingredient_alternatives']]
        self.assertIn('Moong Dal Khichdi', shared_dishes)
