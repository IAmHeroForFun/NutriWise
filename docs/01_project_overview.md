# 01 — Project Overview

## What Is This App?

NutriWise is an intelligent, **source-grounded dietary recommendation web app** that curates personalized whole-day meal plans based on:
- The user's diet type, health conditions, allergies, and ingredient preferences
- Verified knowledge extracted from uploaded nutritional books, medical references, and dietary publications
- Current season and real-time weather at the user's location
- Autonomous pattern learning from user feedback and past successful combinations

---

## What Makes It Different?

Unlike black-box chatbots that hallucinate unverified health advice or generic recipes, NutriWise enforces **strict clinical grounding**:

1. **100% Sourced**: Every recommended dish is extracted directly from authoritative books uploaded by the administrator.
2. **Zero Hallucination Constraint**: When generative AI (Gemini) curates daily meals, it operates under a strict RAG protocol where it is only permitted to select from candidate foods extracted from the books and must cite the exact book and page number.
3. **Autonomous Learning Engine**: Clinical rationales and synergistic food pairings are distilled permanently into the local database (`FoodBenefit`, `FoodCondition`, `LearnedMealPattern`), making the system continuously smarter without recurring API calls.
4. **Transparent Citations**: Every food card displays why it was recommended and allows the user to open a verified excerpt modal citing the source book, chapter, and page number.
5. **Deterministic Safety Shield**: Hard clinical filters guarantee that no food with allergens, contraindicated medical conditions, or disliked ingredients ever reaches the user.

---

## Core Principles

1. **Books are Authoritative**: Extracted knowledge goes live immediately without tedious manual entry.
2. **Clinical Safety First**: Hard filters run before AI curation, guaranteeing zero allergy or medical contraindication exposure.
3. **Cache-First Performance**: Once a daily plan is generated, subsequent visits load in < 15ms directly from the local database with 0 external API calls.
4. **Full Transparency**: Every recommendation includes a verified source citation and clinical rationale.
5. **User Privacy**: Personal health conditions and preferences remain securely stored in the local database.

---

## User & Admin Capabilities

### Admin
- Uploads PDF and EPUB ebooks or provides research website URLs.
- Clicks `▶ Process Now` to run the multi-stage ingestion, noise-cleansing, and canonical entity resolution pipeline.
- Manages food items, verified clinical benefits, and conditions in the Django admin interface.

### User
- Completes a 7-step onboarding wizard with automatic browser geolocation detection.
- Views a personalized daily diet plan partitioned into realistic culinary meal times (Breakfast, Snack, Lunch, Dinner).
- Explores top-promoted `⭐ Recommended Picks` alongside the complete categorized catalog of safe dishes.
- Explores the **Health & Key Ingredients Hub** to discover therapeutic ingredients and the dishes containing them.
- Clicks **Can't make this? 🔄** to discover ingredient-matched alternative recipes.

---

## Scope & Disclaimers

- General dietary and nutritional guidance grounded in published literature — **not medical diagnosis or treatment advice**.
- Uses free-tier Google Gemini API as a grounded curation assistant with automatic multi-model fallback and local caching.
