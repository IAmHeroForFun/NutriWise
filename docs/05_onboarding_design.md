# 05 — User Onboarding Design

## Overview

The onboarding is a **single HTML page** with **7 steps** navigated by JavaScript (no page reloads).
A progress bar at the top shows which step the user is on.
On the final step, submitting the form saves all data to `UserProfile` and redirects to the dashboard.

```
Step 1 ── Step 2 ── Step 3 ── Step 4 ── Step 5 ── Step 6 ── Step 7
Basic      Diet      Health    Allergies  Dislikes  Likes     Location
Info       Type      Conditions
```

---

## Step 1 — Basic Information

**Fields:**
- Age (number, 10–100, required)
- Height in cm (number, optional)
- Weight in kg (number, optional)
- Activity level (dropdown):
  - Sedentary (mostly sitting)
  - Light (walking occasionally)
  - Moderate (regular exercise) ← default
  - Active (intense exercise)

**Saved to:** `UserProfile.age`, `height_cm`, `weight_kg`, `activity_level`

---

## Step 2 — Diet Type

**UI:** 3 large radio cards with icon + name + description

| Option | Value | Description |
|---|---|---|
| 🌱 Vegan | `vegan` | No animal products (no meat, dairy, eggs) |
| 🥛 Vegetarian | `vegetarian` | Dairy/eggs allowed, no meat ← default |
| 🍗 Non-Vegetarian | `non-vegetarian` | All foods including meat, poultry, seafood |

**Engine effect:** Hard Filter #1 — diet incompatible foods removed entirely

**Saved to:** `UserProfile.diet_type`

---

## Step 3 — Health Conditions *(select all that apply)*

**UI:** Checkbox cards with emoji + label. "None of the above" deselects all.

| Label | Value |
|---|---|
| 🩸 Diabetes | `diabetes` |
| ❤️ Hypertension (high blood pressure) | `hypertension` |
| 🫀 High Cholesterol | `cholesterol` |
| ⚖️ Weight Management | `weight_loss` |
| 💉 Anemia (iron deficiency) | `anemia` |
| 🦋 Thyroid condition | `thyroid` |
| 🌸 PCOD / PCOS | `pcos` |
| 🫃 Digestive issues / IBS | `digestive` |

**Engine effect:**
- Foods marked `AVOID` for user's condition → **Hard Filter** (removed)
- Foods marked `RECOMMENDED` for user's condition → **+20 score bonus**

**Saved to:** `UserProfile.conditions` (JSON array)

---

## Step 4 — Allergies *(select all that apply)*

**UI:** Checkbox cards (styled with warning/red). "No allergies" deselects all.

| Label | Value |
|---|---|
| 🥜 Peanuts / Groundnuts | `peanut` |
| 🌾 Gluten (wheat, barley) | `gluten` |
| 🥛 Dairy (milk, paneer, curd) | `dairy` |
| 🌰 Tree nuts (cashew, almond, walnut) | `tree_nut` |
| 🫘 Soy / Soybean | `soy` |
| 🥚 Eggs | `egg` |
| 🦐 Shellfish (prawn, crab) | `shellfish` |

**Engine effect:** **Hard Filter** — any food containing this allergen is removed entirely

**Saved to:** `UserProfile.allergies` (JSON array)

---

## Step 5 — Foods / Ingredients You Dislike *(select all that apply)*

**UI:** Checkbox cards (styled with neutral/grey). Also a free-text field.

**Common checkboxes:**

| Label | Stored as | Matched against |
|---|---|---|
| Bitter Gourd (Karela) | `disliked_foods` | Food name |
| Brinjal (Baingan) | `disliked_foods` | Food name |
| Onion | `disliked_ingredients` | Ingredient list |
| Garlic | `disliked_ingredients` | Ingredient list |
| Cauliflower | `disliked_foods` | Food name |
| Okra (Bhindi) | `disliked_foods` | Food name |
| Coconut | `disliked_ingredients` | Ingredient list |
| Ghee | `disliked_ingredients` | Ingredient list |

**Free-text field:** "Other foods or ingredients you dislike (comma-separated)"
→ Everything from this field goes into `disliked_ingredients`

**Engine effect:** **Hard Filter** — disliked food name OR any food containing disliked ingredient is removed

**Saved to:** `UserProfile.disliked_foods`, `UserProfile.disliked_ingredients`

---

## Step 6 — Foods / Ingredients You Like *(select all that apply)*

**UI:** Checkbox cards (styled with green). Also a free-text field.

**Common checkboxes:**

| Label | Value | Stored as |
|---|---|---|
| 🍚 Rice / Pulao | `rice` | `liked_foods` |
| 🫓 Roti / Chapati | `roti` | `liked_foods` |
| 🫘 Moong Dal | `moong dal` | `liked_foods` |
| 🫘 Chana / Chickpea | `chana` | `liked_foods` |
| 🥬 Spinach (Palak) | `spinach` | `liked_ingredients` |
| 🧀 Paneer | `paneer` | `liked_foods` |
| 🍌 Banana | `banana` | `liked_foods` |
| 🌰 Almonds | `almond` | `liked_ingredients` |
| 🌾 Oats | `oat` | `liked_foods` |
| 🌾 Millet (Bajra/Jowar) | `millet` | `liked_foods` |

**Free-text field:** "Other foods or ingredients you enjoy (comma-separated)"
→ Goes into `liked_ingredients`

**Engine effect:**
- Liked food name match → **+10 score bonus** + shows "⭐ One of your favourites" reason
- Food contains liked ingredient → **+5 score bonus** + shows "Contains ingredients you enjoy" reason

**Saved to:** `UserProfile.liked_foods`, `UserProfile.liked_ingredients`

---

## Step 7 — Location *(auto-detect + manual override)*

### UI States

**State A — Default (page loads):**
- "📍 Detect My Location" button visible
- Manual city text input also visible and usable immediately

**State B — Detecting:**
- Button text changes to "⏳ Detecting..."
- Button disabled
- Manual input still usable

**State C — Detection succeeded:**
- Green banner: "✓ Detected: Mumbai, Maharashtra"
- "Not your city? Change →" link to clear and re-show manual input
- Hidden fields `latitude`, `longitude`, `location_city` populated

**State D — Detection failed / permission denied:**
- Amber banner: "⚠ Could not detect location. Please enter manually."
- Manual city input auto-focused

**State E — Manual entry:**
- User types city name
- `latitude` and `longitude` left blank (weather engine uses city name string)

### Technical Flow
1. User clicks "📍 Detect My Location"
2. Browser calls `navigator.geolocation.getCurrentPosition()`
3. JS gets `{latitude, longitude}` from browser
4. JS sends AJAX GET to `/api/reverse-geocode/?lat=X&lon=Y`
5. Django calls OpenWeather Geocoding API → returns `{city, state}`
6. JS populates hidden fields and shows city name in success banner
7. On form submit → all fields (lat, lng, city) sent to Django

### What gets saved
| Scenario | `latitude` | `longitude` | `location_city` | `location_auto_detected` |
|---|---|---|---|---|
| Auto-detect success | 19.076090 | 72.877426 | "Mumbai" | True |
| Manual entry | null | null | "Chennai" | False |
| Detection failed, manual | null | null | "Delhi" | False |

---

## Form Submission

All 7 steps submit in a **single POST request** to `/profile/`.

The view saves everything in one call:
```python
profile.age = request.POST.get("age")
profile.conditions = request.POST.getlist("conditions")
profile.allergies = request.POST.getlist("allergies")
profile.disliked_foods = request.POST.getlist("disliked_foods")
# ... etc.
profile.onboarding_complete = True
profile.save()
return redirect("dashboard")
```

After completing onboarding, the user is redirected to `/dashboard/`.

## Dashboard Redirect Logic

```python
# dashboard view
if not profile.onboarding_complete:
    return redirect("onboarding")  # force onboarding first
```
