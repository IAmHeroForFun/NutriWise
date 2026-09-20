# 07 — Weather & Season → Food Chain

## Why Both Matter

Weather and season both influence which foods are most appropriate at any given moment, but they come from different sources and change at different speeds.

| | Season | Weather |
|---|---|---|
| Source | Current month (no API needed) | Live OpenWeather API |
| How often it changes | Monthly | Hourly |
| Score bonus | +15 | +10 |
| Food field | `food.seasons` | `food.weather_categories` |
| Example (September) | `monsoon` | `RAINY` (if raining today) |

---

## Step 1 — How Foods Get Weather & Season Tags

When admin uploads a book and clicks ▶ Process, the food extractor scans each paragraph for weather and season keywords.

### Season Keywords → `food.seasons`

| Keywords in book text | Assigned season |
|---|---|
| "summer", "hot season", "heat", "body heat" | `summer` |
| "monsoon", "rainy season", "rains" | `monsoon` |
| "winter", "cold season", "chilly" | `winter` |
| "spring", "moderate weather" | `spring` |
| "autumn", "fall" | `autumn` |

### Weather Keywords → `food.weather_categories`

| Keywords in book text | Assigned category |
|---|---|
| "hot weather", "cooling", "body heat", "thirst" | `HOT`, `VERY_HOT` |
| "monsoon", "rainy", "humid", "wet" | `RAINY`, `HUMID` |
| "cold weather", "warming", "winter cold" | `COOL`, `COLD` |
| No weather keywords / "all seasons" | `[]` (neutral) |

### Book Text Example

> *"Buttermilk is an excellent cooling drink during summer and hot weather. It helps reduce body heat and aids digestion."*

Extractor detects: `buttermilk` near `cooling`, `summer`, `hot weather`
- `seasons = ["summer"]`
- `weather_categories = ["HOT", "VERY_HOT"]`

> *"Moong Dal Khichdi is particularly comforting during the rainy season and cold monsoon evenings."*

Extractor detects: `khichdi` near `rainy`, `monsoon`
- `seasons = ["monsoon"]`
- `weather_categories = ["RAINY", "HUMID"]`

---

## Step 2 — Season Engine (Monthly)

```python
MONTH_TO_SEASON = {
    1: "winter",   2: "winter",
    3: "spring",   4: "spring",
    5: "summer",   6: "summer",
    7: "monsoon",  8: "monsoon",  9: "monsoon",
    10: "autumn",  11: "autumn",
    12: "winter"
}
```

Called once per dashboard request. No API. Just `date.today().month`.

---

## Step 3 — Weather Engine (Live API)

Calls OpenWeather API once per day. Result cached in `RecommendationResult`.

```
Input: user's lat/lng (preferred) OR city name (fallback)
Output: {category: "RAINY", temp: 31.2, humidity: 82, location: "Mumbai"}

Mapping:
  weather code 500–531  → RAINY
  humidity > 75%        → HUMID
  temp ≥ 35°C          → VERY_HOT
  temp ≥ 28°C          → HOT
  temp ≥ 20°C          → NORMAL
  temp ≥ 12°C          → COOL
  temp < 12°C          → COLD
```

---

## Step 4 — Scoring Engine Uses Both

```python
# Season bonus (+15)
if current_season in food.seasons:
    score += 15
    reasons.append(f"Great for {current_season} season")

# Weather bonus (+10)
if weather_category in food.weather_categories:
    score += 10
    reasons.append(f"Suits {weather_category.lower()} weather")
```

Foods with **empty** `weather_categories` (`[]`) are treated as **neutral** → 0 bonus, but still shown.

---

## Worked Example — Mumbai, September 2026

**Context:**
- Month: September → Season: `monsoon`
- Temperature: 31°C, Humidity: 82%, Light rain
- Weather Category: `RAINY` (rain code takes priority)

**Food pool after hard filters (vegetarian, no allergies):**

| Food | `seasons` | `weather_categories` | Season +15? | Weather +10? | Score |
|---|---|---|---|---|---|
| Moong Dal Khichdi | `["monsoon"]` | `["RAINY","HUMID"]` | ✓ +15 | ✓ +10 | 75+ |
| Ginger Tea | `["monsoon","winter"]` | `["RAINY","COLD"]` | ✓ +15 | ✓ +10 | 65+ |
| Buttermilk | `["summer"]` | `["HOT","VERY_HOT"]` | ✗ | ✗ | 50+ |
| Plain Steamed Rice | `[]` | `[]` | ✗ neutral | ✗ neutral | 48+ |
| Mango Lassi | `["summer"]` | `["HOT","VERY_HOT"]` | ✗ | ✗ | 40+ |

→ Khichdi and Ginger Tea float to top. Buttermilk (summer food) ranks lower.

---

## Step 5 — What the User Sees

Weather banner is always shown at the top of the dashboard:

```
┌──────────────────────────────────────────────┐
│  🌧 Mumbai · 31°C · Light Rain · RAINY       │
│  🌿 Season: Monsoon                          │
└──────────────────────────────────────────────┘
```

Each food card shows weather/season as explicit reasons:

```
🍲 Moong Dal Khichdi               Score: 75/100
  ✓ Compatible with your diet
  ✓ Good for lunch
  ✓ Great for monsoon season        ← season engine
  ✓ Suits rainy weather             ← weather engine
  ✓ Recommended for diabetes        ← condition engine
```

---

## Edge Cases

| Situation | Behaviour |
|---|---|
| User has no location set | Weather engine returns `NORMAL`, no weather reason shown on cards |
| OpenWeather API fails | Returns `NORMAL` (safe fallback), no crash |
| Food has no `seasons` or `weather_categories` | Gets 0 bonus for context — still shows in results |
| All foods are "neutral" (no tags set) | No context bonuses → scoring relies on diet/condition/meal/likes only |
| Multiple conditions match both season and weather | Both bonuses stack → total +25 from context signals |
