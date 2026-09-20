from django.db import models
from django.contrib.auth.models import User
from documents.models import Source

class Food(models.Model):
    name = models.CharField(max_length=255, unique=True)
    regional_names = models.TextField(blank=True, help_text="Common Indian or vernacular names")
    summary = models.TextField(blank=True, help_text="Source description of this food item")
    category = models.CharField(max_length=100, blank=True, help_text="grain, pulse, vegetable, fruit, dairy, nut_seed, spice, oil")
    
    # Structured tags
    ingredients = models.JSONField(default=list, blank=True)
    diet_types = models.JSONField(default=list, blank=True, help_text="['vegan', 'vegetarian', 'non-vegetarian']")
    meal_types = models.JSONField(default=list, blank=True, help_text="['breakfast', 'lunch', 'dinner', 'snack']")
    seasons = models.JSONField(default=list, blank=True, help_text="['summer', 'monsoon', 'winter', 'spring', 'autumn']")
    weather_categories = models.JSONField(default=list, blank=True, help_text="['HOT', 'VERY_HOT', 'COOL', 'COLD', 'HUMID', 'RAINY']")
    preparation_methods = models.TextField(blank=True)

    # Source Citations
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True, related_name='foods')
    page_number = models.IntegerField(null=True, blank=True)
    chapter = models.CharField(max_length=255, blank=True)
    source_url = models.TextField(blank=True)
    original_text = models.TextField(blank=True, help_text="Direct excerpt citation from the book/website")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def ingredient_overlap(self, other_food):
        """Returns the count of shared ingredients between two foods."""
        if not self.ingredients or not other_food.ingredients:
            return 0
        s1 = {str(i).strip().lower() for i in self.ingredients if str(i).strip()}
        s2 = {str(i).strip().lower() for i in other_food.ingredients if str(i).strip()}
        return len(s1 & s2)

class FoodBenefit(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='benefits')
    benefit = models.TextField()

    def __str__(self):
        return f"{self.food.name} - {self.benefit[:60]}"

class FoodAllergen(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='allergens')
    allergen = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.food.name} contains {self.allergen}"

class FoodCondition(models.Model):
    REC_CHOICES = [
        ('RECOMMENDED', 'Recommended'),
        ('AVOID', 'Avoid'),
        ('LIMIT', 'Limit'),
    ]
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='conditions')
    condition_name = models.CharField(max_length=100)
    recommendation_type = models.CharField(max_length=20, choices=REC_CHOICES)
    reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.food.name} - {self.condition_name} ({self.recommendation_type})"

class UserProfile(models.Model):
    DIET_CHOICES = [
        ('vegan', 'Vegan'),
        ('vegetarian', 'Vegetarian'),
        ('non-vegetarian', 'Non-Vegetarian'),
    ]
    ACTIVITY_CHOICES = [
        ('sedentary', 'Sedentary'),
        ('light', 'Light'),
        ('moderate', 'Moderate'),
        ('active', 'Active'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Step 1: Basic Stats
    age = models.IntegerField(null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, default='moderate')

    # Step 2: Diet Type
    diet_type = models.CharField(max_length=50, choices=DIET_CHOICES, default='vegetarian')

    # Step 3: Health Conditions
    conditions = models.JSONField(default=list, blank=True)

    # Step 4: Allergies
    allergies = models.JSONField(default=list, blank=True)

    # Step 5: Dislikes
    disliked_foods = models.JSONField(default=list, blank=True)
    disliked_ingredients = models.JSONField(default=list, blank=True)
    disliked_categories = models.JSONField(default=list, blank=True)

    # Step 6: Likes
    liked_foods = models.JSONField(default=list, blank=True)
    liked_ingredients = models.JSONField(default=list, blank=True)

    # Step 7: Location & Live Weather
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_city = models.CharField(max_length=100, blank=True)
    location_state = models.CharField(max_length=100, blank=True)
    location_auto_detected = models.BooleanField(default=False)

    # Inaccessible or substitute marked foods
    cant_make = models.JSONField(default=list, blank=True)
    onboarding_complete = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username} ({self.diet_type})"

class RecommendationResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    generated_date = models.DateField()
    result_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_date', '-created_at']

    def __str__(self):
        return f"Plan for {self.user.username} on {self.generated_date}"


class LearnedMealPattern(models.Model):
    """
    Auto-learned meal combinations discovered by Gemini from uploaded books.
    Persisted to enrich the deterministic engine and provide fast offline templates.
    """
    meal_type = models.CharField(max_length=20)  # breakfast, snack, lunch, dinner
    season = models.CharField(max_length=20, blank=True)
    weather_category = models.CharField(max_length=20, blank=True)
    target_condition = models.CharField(max_length=100, blank=True)
    foods = models.ManyToManyField(Food, related_name='learned_patterns')
    rationale = models.TextField(blank=True)
    citation_source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True)
    usage_count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Learned {self.meal_type} Pattern ({self.target_condition or 'General'})"


class UserFoodAffinity(models.Model):
    """
    Tracks dynamic reinforcement learning score boosts per user and food.
    Updated on recommendations, acceptances (likes/cooked), and swaps.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_affinities')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    score_boost = models.IntegerField(default=0)  # e.g., +5, +10, -10
    times_recommended = models.IntegerField(default=1)
    times_accepted = models.IntegerField(default=0)
    times_rejected = models.IntegerField(default=0)
    last_interacted = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'food')

    def __str__(self):
        return f"{self.user.username} -> {self.food.name} (Boost: {self.score_boost})"
