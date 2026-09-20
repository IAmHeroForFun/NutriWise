# Dietary Recommendation Web App — Project Documentation

**Project:** NutriWise (hackday1.0)  
**Type:** Web Application (Django + Python 3.14)  
**Goal:** Source-grounded, rule-driven dietary recommendation system with Gemini AI curation and autonomous learning  
**Status:** **100% Implemented, Verified & Production Ready**  

---

## Document Index

| # | File | Description |
|---|---|---|
| 1 | [01_project_overview.md](./01_project_overview.md) | What the app is, core principles, roles, transparency disclaimers |
| 2 | [02_tech_stack.md](./02_tech_stack.md) | Every technology used (Django, PyMuPDF, ebooklib, Gemini API, OpenWeather) |
| 3 | [03_architecture.md](./03_architecture.md) | System architecture, RAG grounding, data flow, cache-first serving |
| 4 | [04_database_schema.md](./04_database_schema.md) | Django models (`Food`, `UserProfile`, `LearnedMealPattern`, `UserFoodAffinity`) |
| 5 | [05_onboarding_design.md](./05_onboarding_design.md) | 7-step user onboarding form — all fields, UI states |
| 6 | [06_recommendation_engine.md](./06_recommendation_engine.md) | Hard filters, scoring weights, Gemini RAG curator, auto-learner, meal partitioning |
| 7 | [07_weather_food_chain.md](./07_weather_food_chain.md) | How weather + season affect food rankings — full chain |
| 8 | [08_data_pipeline.md](./08_data_pipeline.md) | Ingestion pipeline, TOC/noise cleansing, canonical foods, composite ingredients |
| 9 | [09_build_checklist.md](./09_build_checklist.md) | Complete implementation checklist across all 9 build phases |
| 10 | [10_deployment.md](./10_deployment.md) | Production deployment — Supabase PostgreSQL + hosting |
| 11 | [USER_AND_ADMIN_GUIDE.md](./USER_AND_ADMIN_GUIDE.md) | Complete user operations & administrator source ingestion manual |
| 12 | [LIGHTSAIL_DOCKER_HOSTING_GUIDE.md](./LIGHTSAIL_DOCKER_HOSTING_GUIDE.md) | Step-by-step AWS Lightsail Docker deployment + Let's Encrypt SSL setup |

---

## Core Decisions (Quick Reference)

| Component | Choice | Rationale |
|---|---|---|
| **Backend** | Django 5.1 (Python 3.14) | Robust ORM, built-in admin, clean view architecture |
| **Frontend** | Vanilla HTML5 + Modern CSS + JS | Zero build step, fast loading, responsive |
| **Local Database** | SQLite (`db.sqlite3`) | Zero configuration, instantaneous local development |
| **Production Database** | Supabase PostgreSQL or Persistent Docker Volume | Switchable via `DB_HOST` in `.env` |
| **AI Curation** | Google Gemini API (RAG Grounded) | Curates synergistic daily meals using *only* candidate foods from uploaded books |
| **Model Fallbacks** | `gemini-3.6-flash` → `3.5` → `latest` → `2.5-lite` | Bypasses 503 high-demand errors seamlessly |
| **Auto-Learning** | Knowledge Distillation & Pattern Learning | Permanently distills new clinical insights and meal combinations into SQLite |
| **Data Ingestion** | PyMuPDF + ebooklib + BeautifulSoup | Ingests PDFs, EPUBs, and web pages with noise/TOC filtering |
| **Caching Protocol** | Cache-First (`RecommendationResult`) | Serves dashboard in < 15ms with 0 external API calls on reload |
| **Weather Integration** | OpenWeather API | Geolocation-driven thermal categorization |

---

## The One-Line Summary

> User completes an onboarding health profile → deterministic filters shield clinical safety → grounded Gemini AI curates complementary daily meals from uploaded books → backend auto-learns new patterns → dashboard serves instant cached plans with exact citations.
