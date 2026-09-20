# NutriWise — User & Administrator Operations Guide

Welcome to the comprehensive operational guide for **NutriWise**. This manual provides step-by-step instructions for everyday users navigating their personalized daily diet plans, as well as administrators managing knowledge ingestion, book libraries, and the autonomous learning engine.

---

# Part 1: End-User Guide

## 1. Getting Started & Account Registration
1. Navigate to the NutriWise home page (`/`).
2. Click **Get Started** or **Register** in the top navigation bar.
3. Choose a username, enter your email address, and set a secure password.
4. Upon successful registration, you are logged in automatically and redirected to the **7-Step Onboarding Wizard**.

---

## 2. Completing the 7-Step Onboarding Wizard

NutriWise tailors every meal to your unique biology, medical needs, and kitchen reality. The onboarding wizard takes under 2 minutes:

| Step | Title | What to Provide | Why It Matters |
|---|---|---|---|
| **Step 1** | **Biometrics** | Age, Height (cm), Weight (kg), and Activity Level (*Sedentary*, *Light*, *Moderate*, *Active*). | Calculates energy requirements and metabolic baseline. |
| **Step 2** | **Dietary Type** | Select one: **Vegan**, **Vegetarian**, or **Non-Vegetarian**. | Serves as a binary hard filter; vegan users will never see dairy or eggs. |
| **Step 3** | **Health Conditions** | Check all that apply: *Diabetes*, *Hypertension*, *High Cholesterol*, *PCOS*, *Thyroid*, *Anemia*, *Digestive Health*, *Weight Loss* (or *None*). | Prioritizes foods clinically indicated for your condition and eliminates contraindicated (`AVOID`) items. |
| **Step 4** | **Allergies** | Select severe allergens: *Peanut*, *Gluten*, *Dairy*, *Tree Nut*, *Soy*, *Egg*, *Shellfish* (or *No allergies*). | **Zero-Tolerance Hard Filter**: Dishes containing matching allergens are strictly removed. |
| **Step 5** | **Disliked Foods** | Check common foods/ingredients you dislike or type custom ingredients to exclude. | Custom exclusions prevent recommendations you do not enjoy eating. |
| **Step 6** | **Liked Foods** | Select your favorite staples, pulses, and vegetables. | Awards bonus ranking points (+10 for favorite foods, +5 for liked ingredients). |
| **Step 7** | **Location & Weather** | Click **📍 Detect My Location** (browser geolocation) or type your city manually. | Syncs live weather from OpenWeather to recommend cooling foods in summer/heat or warming foods in rain/cold. |

Once submitted, your profile is stored, and your first personalized daily meal plan is generated and cached.

---

## 3. Navigating Your Daily Dashboard (`/dashboard/`)

Your dashboard is organized for clarity, transparency, and speed:

```
┌────────────────────────────────────────────────────────────────────────┐
│  ☀️ Mumbai: 31.2°C, Rainy · Category: RAINY          🌧️ Monsoon Season  │
├────────────────────────────────────────────────────────────────────────┤
│  [All Meals View]                [Key Ingredients & Health Hub]        │
└────────────────────────────────────────────────────────────────────────┘
```

### Context Banners
- **Weather Banner**: Shows your live local temperature, conditions (e.g. *Clear*, *Rainy*, *Heatwave*), and thermal category.
- **Season Banner**: Displays the active Indian culinary season (*Monsoon*, *Winter*, *Summer*, *Spring*, *Autumn*).

### Two-Tier Meal Architecture
Every meal time is divided into two intuitive tiers:
1. **Tier 1: Recommended Featured Picks (`⭐ Recommended Pick`)**
   - Curated synergistic combinations selected by Grounded Gemini AI or the Auto-Learner engine (e.g. `Breakfast: Upma + Banana + Milk` or `Lunch: Pulao + Dal + Raita`).
   - Promoted right to the top of each meal section.
2. **Tier 2: Full Categorized Catalog**
   - Below the featured picks, the full list of all safe foods matching that meal time is available in descending score order.
   - **Realistic Culinary Partitioning**:
     - 🌅 **Breakfast**: 17 morning items (Upma, Dosa, Paratha, Oats, Milk, Curd, Breakfast Fruits). Heavy curries and biryanis are excluded.
     - ☕ **Snack**: 25 light bites (Apples, Banana, Buttermilk, Coconut, Corn, Cucumber, Nuts).
     - 🍛 **Lunch**: 40 hearty dishes (Rice, Roti, Biryani, Dal, Rajma, Paneer, Spinach, Subzis, Raita).
     - 🌙 **Dinner**: 36 restorative items (Roti, Khichdi, Dal, Cooked Vegetables, Soothing Milk, Kheer).

---

## 4. Viewing Verified Book Citations
Unlike chatbots that invent unverified health claims, every single food card in NutriWise is verifiable:
1. On any food card, look for the book citation box:
   ```
   📖 The Indian Pantry · Page 42
   Read verified book citation →
   ```
2. Click **Read verified book citation →**.
3. A modal opens displaying the **Book Title**, **Author**, **Chapter**, **Page Number**, and the **Original Medical Text** extracted from the author's work.

---

## 5. What If You Can't Make a Dish? ("Can't make this? 🔄")
If a recommended dish requires an ingredient you don't have in your kitchen:
1. Click **Can't make? 🔄** on the food card.
2. You will be redirected to the **Ingredient Alternatives** page (`/food/<id>/alternatives/`).
3. The engine scans your pantry staples and displays:
   - **Dishes with Shared Ingredients**: Sorted by overlap count (e.g., if you cannot make *Moong Dal Soup*, it suggests *Moong Dal Khichdi* which shares 3 ingredients).
   - **Creative Single-Ingredient Uses**: Shows other delicious ways to use leftover ingredients in your kitchen.
4. Marking a food as "Can't make" excludes it from future daily plans so you don't see it again.

---

## 6. Exploring the Health & Key Ingredients Hub
Click the **Key Ingredients & Health Hub** tab in the dashboard navigation:
- **Search Bar**: Type any ingredient (e.g., *Turmeric*, *Spinach*, *Ginger*, *Cumin*).
- **Therapeutic Rationale**: Learn why this ingredient is clinically recommended for your specific conditions.
- **Recipe Directory**: View every single dish in your library that incorporates that ingredient.

---

## 7. Updating Your Profile
Whenever your health status, location, or taste preferences change:
1. Click **Profile** in the navigation bar.
2. Update your conditions, allergies, or location.
3. Save changes. The system automatically recalculates and refreshes your daily recommendations.

---

# Part 2: Administrator Guide

The administrator manages the ingestion of medical reference books, monitors extracted culinary data, and audits autonomous learning patterns.

## 1. Accessing the Django Admin Panel
1. Navigate to `/admin/` in your browser.
2. Sign in with your administrator credentials.

---

## 2. Ingesting New Books & Sources (`documents.Source`)
NutriWise can ingest knowledge from three distinct formats:
- **PDF Ebooks**: Nutrition manuals, clinical guidelines, research papers.
- **EPUB Ebooks**: Digital cookbooks, dietary guides.
- **Web URLs**: Authoritative health portals, clinical monographs.

### How to Upload and Ingest a Book:
1. In the admin dashboard, click **Sources** under the **DOCUMENTS** section (or visit `/admin/documents/source/add/`).
2. Fill in the document metadata:
   - **Title**: Exact book title (e.g., *Healing Foods*).
   - **Source type**: Select `PDF`, `EPUB`, or `WEBSITE`.
   - **Author**: Author name (e.g., *Dr. Shikha Sharma*).
   - **File**: Upload the `.pdf` or `.epub` file (up to 50 MB).
   - If `WEBSITE`, leave the file blank and enter the full `http(s)://` URL.
3. Click **Save**. The source is created with status **UPLOADED**.
4. On the Sources list page, click the blue **▶ Process Now** button next to the uploaded document.

### What Happens During Processing:
1. The appropriate processor runs (`pdf_processor.py`, `epub_processor.py`, or `web_processor.py`).
2. **Noise Cleansing**: The extractor automatically rejects:
   - Tables of contents and indexes
   - Exam practice questions, revision notes, and marks
   - Food spoilage and microbiology chapters
3. **Canonical Resolution**: Maps names to standardized food entities (e.g. *baingan* ➔ *Brinjal*, *lauki* ➔ *Bottle Gourd*).
4. **Clinical Indication Extraction**: Parses therapeutic statements to create `FoodBenefit` and `FoodCondition` records.
5. **Deterministic Meal Slots**: Assigns realistic culinary meal slots (`DEFAULT_FOOD_MEAL_TYPES`).
6. The source status changes to **DONE**, displaying the total count of extracted foods (e.g., `✓ Extracted 24 food records`).

---

## 3. Managing Food Records (`core.Food`)
1. In the admin dashboard, click **Foods** under **CORE**.
2. Search for any food by name, or filter by category and diet type.
3. Opening a food record reveals:
   - **Ingredients List**: JSON array of culinary ingredients.
   - **Meal Types**: Which meal slots this dish is eligible for (`breakfast`, `snack`, `lunch`, `dinner`).
   - **Seasons & Weather**: Contextual suitability tags.
   - **Stacked Inlines**:
     - **Food Benefits**: Sourced clinical health benefits.
     - **Food Allergens**: Cross-referenced allergens (`peanut`, `gluten`, `dairy`, etc.).
     - **Food Conditions**: Clinical indications (`RECOMMENDED`, `AVOID`, `LIMIT`) with source reasons.
4. **Deduplication Principle**: If a food appears in multiple books, NutriWise updates and enriches the existing record with new citations and benefits rather than creating duplicate entries.

---

## 4. Auditing the Autonomous Auto-Learner
NutriWise features self-learning backend engines that learn from AI curations and user actions:

### `LearnedMealPattern`
- Located in `/admin/core/learnedmealpattern/`.
- Records synergistic food combinations (e.g., `Upma + Banana + Milk`) alongside the weather, season, and diet type under which the pairing was successful.
- Tracks `occurrence_count` and empirical `success_rating`.

### `UserFoodAffinity`
- Located in `/admin/core/userfoodaffinity/`.
- Tracks each user's interaction frequency with specific dishes.
- Adjusts scoring dynamically over time so frequently chosen meals are favored while preventing recommendation fatigue.

---

## 5. Cache Management & Testing New Sources
When you upload a new book or modify an existing food, you may want to verify that new dishes appear on user dashboards immediately:
- NutriWise uses a **Cache-First** strategy: once a daily plan is generated, it is cached in `RecommendationResult` for that calendar day.
- To force an immediate regeneration for a user:
  1. In the admin panel, go to **Recommendation results** (`/admin/core/recommendationresult/`).
  2. Select and delete the cached result for today's date.
  3. The next time the user opens `/dashboard/`, the engine will re-run the full ranking and AI curation pipeline, incorporating all newly added foods.
