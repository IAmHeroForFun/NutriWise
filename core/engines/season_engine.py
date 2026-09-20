from datetime import date

MONTH_TO_SEASON = {
    1: 'winter', 2: 'winter',
    3: 'spring', 4: 'spring',
    5: 'summer', 6: 'summer',
    7: 'monsoon', 8: 'monsoon', 9: 'monsoon',
    10: 'autumn', 11: 'autumn',
    12: 'winter',
}

SEASON_METADATA = {
    'summer': {'name': 'Summer (Grishma)', 'emoji': '☀️', 'desc': 'Focus on cooling, hydrating, and easily digestible foods.'},
    'monsoon': {'name': 'Monsoon (Varsha)', 'emoji': '🌧️', 'desc': 'Focus on warm, fresh, and gut-soothing preparations.'},
    'winter': {'name': 'Winter (Shishira)', 'emoji': '❄️', 'desc': 'Focus on hearty, nourishing, warming dishes with wholesome fats.'},
    'spring': {'name': 'Spring (Vasant)', 'emoji': '🌸', 'desc': 'Focus on lighter grains, bitter greens, and gentle detox foods.'},
    'autumn': {'name': 'Autumn (Sharad)', 'emoji': '🍂', 'desc': 'Focus on balancing sweet and bitter tastes, avoiding excessive spices.'},
}

def get_current_season(dt=None):
    """Returns current Indian dietary season."""
    if dt is None:
        dt = date.today()
    return MONTH_TO_SEASON.get(dt.month, 'monsoon')

def get_season_info(season_key=None):
    """Returns detailed season information."""
    if not season_key:
        season_key = get_current_season()
    return SEASON_METADATA.get(season_key, {
        'name': season_key.title(),
        'emoji': '🌿',
        'desc': 'Balanced wholesome daily nutrition.'
    })
