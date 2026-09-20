import requests
from django.conf import settings

WEATHER_CATEGORIES_META = {
    'VERY_HOT': {'label': 'Very Hot', 'emoji': '🔥', 'tip': 'Stay hydrated with cooling liquids.'},
    'HOT': {'label': 'Hot', 'emoji': '☀️', 'tip': 'Favour light meals and natural coolers.'},
    'COOL': {'label': 'Cool', 'emoji': '🌤️', 'tip': 'Enjoy gentle warming spices and teas.'},
    'COLD': {'label': 'Cold', 'emoji': '❄️', 'tip': 'Favour warm stews, soups, and healthy fats.'},
    'HUMID': {'label': 'Humid', 'emoji': '💧', 'tip': 'Favour light, dry, and easily digestible meals.'},
    'RAINY': {'label': 'Rainy', 'emoji': '🌧️', 'tip': 'Warm, freshly cooked foods with ginger and cumin.'},
    'NORMAL': {'label': 'Pleasant', 'emoji': '🌿', 'tip': 'Well-balanced wholesome home meals.'},
}

def get_weather_category(profile):
    """
    Fetches real-time weather from OpenWeather API using lat/lon or city.
    Returns: dict with category, temp, humidity, description, location, auto_detected, tip, emoji
    """
    api_key = getattr(settings, 'OPENWEATHER_API_KEY', '').strip()
    default_resp = {
        'category': 'NORMAL',
        'temp': None,
        'humidity': None,
        'description': 'Normal',
        'location': profile.location_city or 'Your City',
        'auto_detected': profile.location_auto_detected,
        'emoji': '🌿',
        'tip': WEATHER_CATEGORIES_META['NORMAL']['tip']
    }

    if not api_key:
        return default_resp

    params = {'appid': api_key, 'units': 'metric'}
    if profile.latitude and profile.longitude:
        params['lat'] = float(profile.latitude)
        params['lon'] = float(profile.longitude)
    elif profile.location_city:
        city_query = profile.location_city.strip()
        params['q'] = f"{city_query},IN" if "," not in city_query else city_query
    else:
        return default_resp

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code != 200:
            return default_resp
        data = resp.json()

        temp = round(data['main']['temp'], 1)
        humidity = data['main']['humidity']
        weather_id = data['weather'][0]['id'] if data.get('weather') else 800
        desc = data['weather'][0]['description'].title() if data.get('weather') else 'Pleasant'
        loc_name = data.get('name') or profile.location_city or 'Current Location'

        # Determine category based on deterministic rules
        if 500 <= weather_id <= 531 or 200 <= weather_id <= 232 or 300 <= weather_id <= 321:
            category = 'RAINY'
        elif humidity > 75:
            category = 'HUMID'
        elif temp >= 35:
            category = 'VERY_HOT'
        elif temp >= 28:
            category = 'HOT'
        elif temp >= 20:
            category = 'NORMAL'
        elif temp >= 12:
            category = 'COOL'
        else:
            category = 'COLD'

        meta = WEATHER_CATEGORIES_META.get(category, WEATHER_CATEGORIES_META['NORMAL'])

        return {
            'category': category,
            'temp': temp,
            'humidity': humidity,
            'description': desc,
            'location': loc_name,
            'auto_detected': profile.location_auto_detected,
            'emoji': meta['emoji'],
            'tip': meta['tip']
        }
    except Exception:
        return default_resp
