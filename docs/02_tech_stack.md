# 02 — Technology Stack

## Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.14 / 3.11+ | Runtime language |
| Django | 5.1+ / 4.2+ | Web framework — views, models, admin, auth |
| SQLite | Built-in | Local development database (zero config) |
| psycopg2-binary | Latest | PostgreSQL adapter (production only) |
| python-dotenv | Latest | Load `.env` environment variables |
| requests | Latest | HTTP calls — OpenWeather and Gemini API |
| PyMuPDF (fitz) | Latest | Extract text and chapters from PDF ebooks |
| ebooklib | Latest | Extract text and structural chapters from EPUB ebooks |
| BeautifulSoup4 | Latest | Parse HTML and strip boilerplate from websites & EPUBs |
| Pillow | Latest | Image handling (OCR support) |
| pytesseract | Latest | OCR for scanned PDF pages (fallback) |

---

## Frontend
| Technology | Purpose |
|---|---|
| HTML5 | Semantic structure and accessibility |
| CSS3 | Custom styling with deep green palette, card grids, badges, modals |
| Vanilla JavaScript | 7-step onboarding wizard, geolocation, AJAX citation modal, live ingredient search |

*Zero frontend frameworks (no React, Vue, or npm dependencies) — lightning-fast server-side rendering via Django templates.*

---

## Database
| Environment | Database | Config |
|---|---|---|
| Local development | SQLite | Auto-configured, local file: `db.sqlite3` |
| Production | PostgreSQL via Supabase | Connection string set in `.env` (`DB_HOST`, `DB_NAME`, etc.) |

---

## External APIs & Services
| Service | Provider | Tier | Purpose |
|---|---|---|---|
| **Dietary Curation (RAG)** | Google Gemini API (`v1beta`) | Free tier | Grounded complementary meal curation from candidate books |
| **Current Weather** | OpenWeather API | Free tier (1,000 calls/day) | Live ambient temperature, humidity, and weather conditions |
| **Reverse Geocoding** | OpenWeather Geocoding API | Free tier | Coordinates (lat/lon) → City and State resolution |
| **Geolocation** | Browser Native Geolocation API | Free (client-side) | One-click user coordinate detection |

---

## Local Environment
```
Python venv (/mnt/Work/projects/hackday1.0/venv/)
├── All dependencies installed inside venv
├── Django dev server (python manage.py runserver)
└── SQLite database (db.sqlite3)
```

---

## Production Environment
```
Hosting: Railway / Render / VPS
Database: Supabase PostgreSQL (port 5432)
Static files: collected via collectstatic to staticfiles/
Process: gunicorn dietary_app.wsgi --log-file -
```

---

## Requirements File (`requirements.txt`)
```
django>=4.2
python-dotenv
requests
beautifulsoup4
PyMuPDF
ebooklib
Pillow
pytesseract
```
