from django.contrib import admin
from .models import (
    Food, FoodBenefit, FoodAllergen, FoodCondition, UserProfile,
    RecommendationResult, LearnedMealPattern, UserFoodAffinity
)

class FoodBenefitInline(admin.TabularInline):
    model = FoodBenefit
    extra = 1

class FoodAllergenInline(admin.TabularInline):
    model = FoodAllergen
    extra = 1

class FoodConditionInline(admin.TabularInline):
    model = FoodCondition
    extra = 1

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'get_source', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'regional_names', 'summary', 'ingredients']
    inlines = [FoodBenefitInline, FoodAllergenInline, FoodConditionInline]

    def get_source(self, obj):
        return obj.source.title if obj.source else "-"
    get_source.short_description = "Source"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'diet_type', 'location_city', 'onboarding_complete', 'updated_at']
    list_filter = ['diet_type', 'onboarding_complete', 'location_auto_detected']
    search_fields = ['user__username', 'location_city', 'conditions', 'allergies']

@admin.register(RecommendationResult)
class RecommendationResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'generated_date', 'created_at']
    list_filter = ['generated_date']
    search_fields = ['user__username']

@admin.register(LearnedMealPattern)
class LearnedMealPatternAdmin(admin.ModelAdmin):
    list_display = ['meal_type', 'target_condition', 'weather_category', 'usage_count', 'created_at']
    list_filter = ['meal_type', 'season', 'weather_category']
    search_fields = ['target_condition', 'rationale']

@admin.register(UserFoodAffinity)
class UserFoodAffinityAdmin(admin.ModelAdmin):
    list_display = ['user', 'food', 'score_boost', 'times_recommended', 'times_accepted', 'times_rejected', 'last_interacted']
    list_filter = ['score_boost', 'last_interacted']
    search_fields = ['user__username', 'food__name']
