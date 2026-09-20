from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from datetime import date
import requests

from .models import Food, UserProfile, RecommendationResult
from .forms import RegisterForm
from .engines import (
    hard_filters, scoring_engine, meal_combiner,
    season_engine, weather_engine, ingredient_matcher,
    gemini_engine, auto_learner
)

def landing(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    total_foods = Food.objects.count()
    return render(request, 'landing.html', {'total_foods': total_foods})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Welcome! Let's set up your personalized profile.")
            return redirect('core:onboarding')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    if request.method == 'POST':
        u = request.POST.get('username', '').strip()
        p = request.POST.get('password', '').strip()
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect('core:dashboard')
        messages.error(request, "Invalid username or password.")
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('core:landing')

@login_required
def onboarding(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Step 1: Basic Stats
        profile.age = int(request.POST.get('age')) if request.POST.get('age') else None
        profile.height_cm = float(request.POST.get('height_cm')) if request.POST.get('height_cm') else None
        profile.weight_kg = float(request.POST.get('weight_kg')) if request.POST.get('weight_kg') else None
        profile.activity_level = request.POST.get('activity_level', 'moderate')

        # Step 2: Diet Type
        profile.diet_type = request.POST.get('diet_type', 'vegetarian')

        # Step 3: Health Conditions
        profile.conditions = request.POST.getlist('conditions')

        # Step 4: Allergies
        profile.allergies = request.POST.getlist('allergies')

        # Step 5: Dislikes
        dis_foods = request.POST.getlist('disliked_foods')
        dis_ings = request.POST.getlist('disliked_ingredients')
        custom_dis = [x.strip().lower() for x in request.POST.get('disliked_custom', '').split(',') if x.strip()]
        profile.disliked_foods = dis_foods
        profile.disliked_ingredients = list(set(dis_ings + custom_dis))

        # Step 6: Likes
        liked_f = request.POST.getlist('liked_foods')
        liked_i = request.POST.getlist('liked_ingredients')
        custom_lik = [x.strip().lower() for x in request.POST.get('liked_custom', '').split(',') if x.strip()]
        profile.liked_foods = liked_f
        profile.liked_ingredients = list(set(liked_i + custom_lik))

        # Step 7: Location
        lat_val = request.POST.get('latitude', '').strip()
        lon_val = request.POST.get('longitude', '').strip()
        if lat_val and lon_val:
            try:
                profile.latitude = float(lat_val)
                profile.longitude = float(lon_val)
                profile.location_auto_detected = True
            except ValueError:
                pass
        profile.location_city = request.POST.get('location_city', '').strip()
        profile.location_state = request.POST.get('location_state', '').strip()

        profile.onboarding_complete = True
        profile.save()

        # Invalidate existing cached recommendation for today to reflect updated preferences
        RecommendationResult.objects.filter(user=request.user, generated_date=date.today()).delete()

        messages.success(request, "Your diet profile has been configured!")
        return redirect('core:dashboard')

    return render(request, 'onboarding.html', {'profile': profile})

@login_required
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.onboarding_complete:
        messages.info(request, "Please complete your health profile first.")
        return redirect('core:onboarding')

    today = date.today()
    cached = RecommendationResult.objects.filter(user=request.user, generated_date=today).first()
    
    # Only regenerate if explicitly requested via ?refresh=1
    if cached and request.GET.get('refresh') == '1':
        cached.delete()
        cached = None

    if cached:
        plan = cached.result_json
    else:
        plan = _generate_plan(profile)
        RecommendationResult.objects.create(
            user=request.user,
            generated_date=today,
            result_json=plan
        )

    season_meta = season_engine.get_season_info(plan.get('season'))
    return render(request, 'dashboard.html', {
        'profile': profile,
        'plan': plan,
        'season_meta': season_meta,
    })

def _generate_plan(profile):
    season = season_engine.get_current_season()
    weather = weather_engine.get_weather_category(profile)
    safe_foods = hard_filters.apply_hard_filters(profile)

    # Filter out foods marked cant_make
    cant_make_ids = set(profile.cant_make or [])
    available_foods = [f for f in safe_foods if f.id not in cant_make_ids]

    plan = {
        'date': str(date.today()),
        'season': season,
        'weather': weather,
        'meals': {},
        'featured_combos': {},
        'source_mode': 'deterministic_rule',
        'overall_summary': ''
    }

    # 1. First, populate safe matching candidate foods partitioned by meal slot
    foods_by_name = {f.name.lower(): f for f in available_foods}
    for meal_type in ['breakfast', 'snack', 'lunch', 'dinner']:
        meal_candidates = [f for f in available_foods if meal_type in (f.meal_types or [])]
        if len(meal_candidates) < 3:
            meal_candidates = available_foods
        ranked = scoring_engine.rank_foods(meal_candidates, profile, meal_type, season, weather['category'])
        plan['meals'][meal_type] = [_serialize_food(item) for item in ranked]

    # 2. Try Grounded Gemini AI to curate top featured combos and distill knowledge
    api_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
    if api_key:
        try:
            ai_result = gemini_engine.generate_grounded_plan(profile, available_foods, weather, season)
            if ai_result and 'meals' in ai_result:
                # Distill new knowledge into local database permanently
                auto_learner.distill_ai_knowledge(ai_result, foods_by_name, profile)

                all_recommended_foods = []
                for meal_type, items in ai_result['meals'].items():
                    combo_items = []
                    combo_foods = []
                    featured_names = set()

                    for item in items:
                        fname = item.get('food_name', '')
                        food = foods_by_name.get(fname.lower())
                        if food:
                            combo_foods.append(food)
                            all_recommended_foods.append(food)
                            featured_names.add(food.name.lower())
                            serialized = _serialize_food({
                                'food': food,
                                'score': 95,
                                'reasons': [item.get('clinical_rationale', f"Curated for {profile.diet_type}")],
                                'is_ai_grounded': True,
                                'clinical_rationale': item.get('clinical_rationale', '')
                            })
                            combo_items.append(serialized)

                    if combo_items:
                        plan['featured_combos'][meal_type] = combo_items
                        auto_learner.learn_meal_pattern(meal_type, combo_foods, weather, season, profile)

                        # Promote featured foods to top of meal's full catalog
                        current_meal_list = plan['meals'].get(meal_type, [])
                        promoted = []
                        remaining = []
                        for dish in current_meal_list:
                            if dish['name'].lower() in featured_names:
                                dish['is_featured'] = True
                                promoted.append(dish)
                            else:
                                remaining.append(dish)
                        plan['meals'][meal_type] = promoted + remaining

                if plan['featured_combos']:
                    plan['source_mode'] = 'gemini_grounded'
                    plan['overall_summary'] = ai_result.get('overall_summary', '')
                    auto_learner.register_recommendation_exposure(profile.user, all_recommended_foods)
        except Exception:
            pass

    # 3. Build Health & Key Ingredients Intelligence
    ingredients_hub = {}
    user_conditions = {str(c).strip().lower() for c in (profile.conditions or [])}

    for food in available_foods:
        food_conditions = [c.condition_name.title() for c in food.conditions.all() if c.recommendation_type == 'RECOMMENDED']
        food_benefits = [b.benefit for b in food.benefits.all()]

        for ing in (food.ingredients or []):
            ing_clean = str(ing).strip().lower()
            if len(ing_clean) < 3:
                continue
            if ing_clean not in ingredients_hub:
                ingredients_hub[ing_clean] = {
                    'name': ing_clean.title(),
                    'dishes': [],
                    'benefits': set(),
                    'conditions': set(),
                    'is_vital': False
                }
            ingredients_hub[ing_clean]['dishes'].append({
                'id': food.id,
                'name': food.name,
                'category': food.category,
                'source': food.source.title if food.source else 'Published Reference'
            })
            for b in food_benefits[:2]:
                ingredients_hub[ing_clean]['benefits'].add(b)
            for c in food_conditions:
                ingredients_hub[ing_clean]['conditions'].add(c)
                if c.lower() in user_conditions:
                    ingredients_hub[ing_clean]['is_vital'] = True

    # Convert sets to lists and sort by relevance
    sorted_ingredients = []
    for ing_key, data in ingredients_hub.items():
        data['benefits'] = list(data['benefits'])[:2]
        data['conditions'] = list(data['conditions'])[:3]
        data['dish_count'] = len(data['dishes'])
        sorted_ingredients.append(data)

    # Sort: ingredients addressing user conditions first, then by dish count
    sorted_ingredients.sort(key=lambda x: (x['is_vital'], x['dish_count']), reverse=True)
    plan['health_ingredients'] = sorted_ingredients

    return plan

def _serialize_food(item):
    food = item['food']
    return {
        'id': food.id,
        'name': food.name,
        'summary': food.summary,
        'category': food.category,
        'ingredients': food.ingredients,
        'score': item['score'],
        'reasons': item['reasons'],
        'is_ai_grounded': item.get('is_ai_grounded', False),
        'clinical_rationale': item.get('clinical_rationale', ''),
        'benefits': [b.benefit for b in food.benefits.all()[:2]],
        'citation': {
            'source_title': food.source.title if food.source else "Authoritative Reference",
            'source_type': food.source.get_source_type_display() if food.source else "Book",
            'author': food.source.author if food.source else "",
            'page': food.page_number,
            'chapter': food.chapter,
            'source_url': food.source_url,
            'original_text': food.original_text[:600] if food.original_text else "",
        }
    }

@login_required
def food_detail(request, pk):
    food = get_object_or_404(Food.objects.prefetch_related('benefits', 'allergens', 'conditions'), pk=pk)
    return render(request, 'food_detail.html', {'food': food})

@login_required
def food_alternatives(request, pk):
    food = get_object_or_404(Food, pk=pk)
    profile = request.user.profile
    alts = ingredient_matcher.find_alternatives(food, profile)
    return render(request, 'alternatives.html', {
        'original_food': food,
        'alternatives': alts['shared_ingredient_alternatives'],
        'ingredient_uses': alts['ingredient_uses'],
    })

@login_required
def mark_cant_make(request, pk):
    if request.method == 'POST':
        profile = request.user.profile
        cant_list = list(profile.cant_make or [])
        if pk not in cant_list:
            cant_list.append(pk)
            profile.cant_make = cant_list
            profile.save()
            # Reinforcement penalty in auto_learner
            auto_learner.record_user_feedback(request.user, pk, 'reject')
            # Regenerate daily plan without this food
            RecommendationResult.objects.filter(user=request.user, generated_date=date.today()).delete()
        return JsonResponse({'status': 'ok', 'food_id': pk})
    return JsonResponse({'error': 'POST required'}, status=400)

@login_required
def food_feedback(request, pk):
    """
    Records positive reinforcement ('like', 'cooked') or negative ('reject')
    into UserFoodAffinity to adapt scoring engine for the user.
    """
    if request.method == 'POST':
        action = request.POST.get('action', 'like')
        boost = auto_learner.record_user_feedback(request.user, pk, action)
        return JsonResponse({'status': 'ok', 'food_id': pk, 'score_boost': boost})
    return JsonResponse({'error': 'POST required'}, status=400)

@login_required
def api_recommendations(request):
    profile = request.user.profile
    plan = _generate_plan(profile)
    return JsonResponse(plan)

@login_required
def api_reverse_geocode(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    if not lat or not lon:
        return JsonResponse({'error': 'Coordinates required'}, status=400)

    api_key = getattr(settings, 'OPENWEATHER_API_KEY', '').strip()

    # 1. Try OpenWeather if API key exists
    if api_key:
        try:
            url = "https://api.openweathermap.org/geo/1.0/reverse"
            r = requests.get(url, params={'lat': lat, 'lon': lon, 'limit': 1, 'appid': api_key}, timeout=5)
            data = r.json()
            if data and isinstance(data, list):
                loc = data[0]
                return JsonResponse({
                    'city': loc.get('name', ''),
                    'state': loc.get('state', ''),
                    'country': loc.get('country', '')
                })
        except Exception:
            pass

    # 2. Free public reverse geocoding fallback (BigDataCloud client-side free reverse API, no key required)
    try:
        url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
        r = requests.get(url, params={'latitude': lat, 'longitude': lon, 'localityLanguage': 'en'}, timeout=5)
        data = r.json()
        city = data.get('city') or data.get('locality') or data.get('principalSubdivision') or ''
        state = data.get('principalSubdivision') or ''
        country = data.get('countryCode') or 'IN'
        if city:
            return JsonResponse({'city': city, 'state': state, 'country': country})
    except Exception:
        pass

    return JsonResponse({'city': 'Local Region', 'state': '', 'country': 'IN'})
