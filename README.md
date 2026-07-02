# Oneness Aviation — Backend API

**FastAPI · PostgreSQL · Redis · Razorpay · Python 3.12**

Complete REST API backend for the Oneness Aviation private charter and ferry flight platform.

---

## Project Structure

```
oneness-backend/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Environment settings
│   ├── database.py              # SQLAlchemy async engine + session
│   ├── models/
│   │   ├── user.py              # User + UserRole enum
│   │   ├── enquiry.py           # Enquiry + CharterRequest
│   │   ├── aircraft.py          # Aircraft + AircraftCategory + AirportDistance
│   │   ├── membership.py        # Membership + MembershipPlan
│   │   ├── payment.py           # Payment (Razorpay)
│   │   └── blog.py              # BlogPost + FAQ + Testimonial
│   ├── schemas/
│   │   ├── auth.py              # Register, Login, Token schemas
│   │   ├── user.py              # UserResponse, UserUpdate
│   │   ├── enquiry.py           # Enquiry + Charter schemas
│   │   ├── fleet.py             # Aircraft + Estimator schemas
│   │   ├── membership.py        # Membership + Plan schemas
│   │   ├── payment.py           # Payment schemas
│   │   └── blog.py              # Blog + FAQ + Testimonial schemas
│   ├── routers/
│   │   ├── auth.py              # /api/auth/*
│   │   ├── user.py              # /api/users/*
│   │   ├── enquiry.py           # /api/enquiries/*
│   │   ├── fleet.py             # /api/fleet/*
│   │   ├── membership.py        # /api/memberships/*
│   │   ├── payment.py           # /api/payments/*
│   │   ├── blog.py              # /api/blog/*, /api/faq/*, /api/testimonials/*
│   │   └── admin.py             # /api/admin/*
│   ├── services/
│   │   ├── auth_service.py      # JWT, hashing, login logic
│   │   ├── email_service.py     # FastAPI-Mail + Jinja2 templates
│   │   ├── fleet_service.py     # Aircraft CRUD + cost estimator
│   │   └── payment_service.py   # Razorpay integration
│   ├── middleware/
│   │   └── dependencies.py      # get_current_user, require_admin
│   ├── utils/
│   │   ├── s3.py                # AWS S3 / Cloudflare R2 uploads
│   │   └── pdf.py               # ReportLab invoice generation
│   └── templates/
│       └── email/
│           ├── enquiry_confirmation.html
│           ├── admin_enquiry_notification.html
│           ├── charter_confirmation.html
│           ├── membership_welcome.html
│           ├── payment_receipt.html
│           └── password_reset.html
├── alembic/                     # Database migrations
├── scripts/
│   └── seed.py                  # Seed DB with fleet, plans, FAQs, testimonials
├── tests/
│   ├── conftest.py              # Pytest fixtures (in-memory SQLite)
│   ├── test_auth.py
│   ├── test_enquiry.py
│   ├── test_fleet.py
│   └── test_blog.py
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── pytest.ini
```

---

## Quick Start (Local Development)

### Option A — Docker (recommended, zero setup)

```bash
# 1. Clone and enter the project
cd oneness-backend

# 2. Copy env file
cp .env.example .env
# Edit .env and fill in MAIL_*, RAZORPAY_* values

# 3. Start everything (API + PostgreSQL + Redis)
docker compose up --build

# 4. In a new terminal, seed the database
docker compose exec api python -m scripts.seed
```

API is now running at **http://localhost:8000**
Swagger docs at **http://localhost:8000/docs**

---

### Option B — Manual (without Docker)

#### Prerequisites
- Python 3.12+
- PostgreSQL 14+
- Redis 7+

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — fill in DATABASE_URL, SECRET_KEY, mail settings, Razorpay keys

# 4. Create database
createdb oneness_db              # or use pgAdmin / DBeaver

# 5. Run database migrations
alembic upgrade head

# 6. Seed initial data
python -m scripts.seed

# 7. Start the server
uvicorn app.main:app --reload
```

API runs at **http://localhost:8000**

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values.

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection | `postgresql+asyncpg://user:pass@localhost/oneness_db` |
| `SECRET_KEY` | JWT signing key (min 32 chars) | `your-super-secret-key-here` |
| `MAIL_USERNAME` | SMTP email address | `fly@onenessaviation.com` |
| `MAIL_PASSWORD` | App password (not login password) | `abcd efgh ijkl mnop` |
| `RAZORPAY_KEY_ID` | Razorpay test/live key | `rzp_test_xxxx` |
| `RAZORPAY_KEY_SECRET` | Razorpay secret | `xxxxxxxxxxxx` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379` |
| `ADMIN_EMAIL` | Email that receives enquiry notifications | `admin@onenessaviation.com` |

---

## API Endpoints Reference

### Auth — `/api/auth`
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login → returns JWT |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/forgot-password` | Send password reset email |
| POST | `/api/auth/reset-password` | Reset password with token |

### User Profile — `/api/users`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/users/me` | ✓ | Get my profile |
| PUT | `/api/users/me` | ✓ | Update name/phone |
| POST | `/api/users/me/change-password` | ✓ | Change password |
| DELETE | `/api/users/me` | ✓ | Delete account |

### Enquiries — `/api/enquiries`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/enquiries/contact` | Optional | Submit contact form |
| POST | `/api/enquiries/charter` | Optional | Submit charter request |
| GET | `/api/enquiries/my` | Optional | My enquiry history |

### Fleet — `/api/fleet`
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/fleet` | List aircraft (filter: category, passengers_min) |
| GET | `/api/fleet/categories` | List categories with counts |
| GET | `/api/fleet/{slug}` | Single aircraft detail |
| POST | `/api/fleet/estimate` | Flight cost estimate |

### Membership — `/api/memberships`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/memberships/plans` | — | List all membership plans |
| GET | `/api/memberships/my` | ✓ | My current membership |
| POST | `/api/memberships/purchase/create-order` | ✓ | Create Razorpay order |
| POST | `/api/memberships/purchase/verify` | ✓ | Verify payment + activate |

### Payments — `/api/payments`
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/payments/create-order` | ✓ | Create payment order |
| POST | `/api/payments/verify` | ✓ | Verify payment signature |
| POST | `/api/payments/webhook` | — | Razorpay webhook handler |
| GET | `/api/payments/history` | ✓ | My payment history |

### Blog & Resources — `/api/blog`, `/api/faq`, `/api/testimonials`
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/blog` | Paginated blog list (filter: category, tag) |
| GET | `/api/blog/categories` | Blog categories with counts |
| GET | `/api/blog/{slug}` | Full blog post detail |
| GET | `/api/faq` | All FAQs (filter: category) |
| GET | `/api/testimonials` | All active testimonials |

### Admin — `/api/admin` (Admin role required)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/dashboard/stats` | Dashboard KPIs |
| GET | `/api/admin/enquiries` | All enquiries with search/filter |
| PATCH | `/api/admin/enquiries/{id}/status` | Update enquiry status |
| GET | `/api/admin/charter-requests` | All charter requests |
| PATCH | `/api/admin/charter-requests/{id}/status` | Update charter status |
| POST | `/api/admin/fleet` | Add aircraft |
| PUT | `/api/admin/fleet/{id}` | Edit aircraft |
| PATCH | `/api/admin/fleet/{id}/availability` | Toggle availability |
| DELETE | `/api/admin/fleet/{id}` | Soft-delete aircraft |
| POST | `/api/admin/blog` | Create blog post |
| PUT | `/api/admin/blog/{id}` | Edit blog post |
| PATCH | `/api/admin/blog/{id}/publish` | Publish/unpublish |
| DELETE | `/api/admin/blog/{id}` | Delete blog post |
| GET | `/api/admin/users` | List all users |

---

## Running Tests

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-asyncio httpx aiosqlite

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific file
pytest tests/test_auth.py -v
```

Tests use an **in-memory SQLite database** — no PostgreSQL needed for testing.

---

## Database Migrations (Production)

```bash
# After changing any model, generate a migration
alembic revision --autogenerate -m "describe your change"

# Apply migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1
```

---

## Frontend Integration

In your React frontend, set the base URL:

```js
// src/lib/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

// Attach JWT token to all requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
```

Add to your `.env` in the React project:
```
VITE_API_URL=http://localhost:8000
```

---

## Seed Data

After running `python -m scripts.seed`, you'll have:

- **14 aircraft** (all categories: light jets, midsize, heavy, ULR, helicopters)
- **5 aircraft categories**
- **28 airport routes** (domestic + international)
- **3 membership plans** (Silver, Gold, Platinum) with real pricing
- **10 FAQs**
- **6 testimonials**
- **1 admin user** — `admin@onenessaviation.com` / `Admin@Oneness2024!`

⚠️ **Change the admin password immediately after first login.**

---

## Production Checklist

- [ ] Set `DEBUG=false` in `.env`
- [ ] Change `SECRET_KEY` to a random 64-character string
- [ ] Change admin password after first login
- [ ] Set `FRONTEND_URL` to your actual domain
- [ ] Configure real SMTP credentials (not Gmail for production — use SendGrid/Brevo)
- [ ] Switch Razorpay from test mode (`rzp_test_`) to live (`rzp_live_`)
- [ ] Configure AWS S3 or Cloudflare R2 for file uploads
- [ ] Set `SENTRY_DSN` for error monitoring
- [ ] Point Razorpay webhook URL to `https://yourdomain.com/api/payments/webhook`
- [ ] Run `alembic upgrade head` before starting the server
- [ ] Run `python -m scripts.seed` once to populate initial data

---

Built for Oneness Aviation by Tushar Samaniya
