from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import auth, enquiry, fleet, membership, payment, blog, user, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if settings.DEBUG:
        await init_db()  # Auto-create tables in dev. Use Alembic in production.
    if settings.SENTRY_DSN:
        import sentry_sdk
        sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.2)
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title="Oneness Aviation API",
    description="Backend API for Oneness Aviation — private charter and ferry flight platform",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,    # Hide Swagger in production
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api"

app.include_router(auth.router,               prefix=API_PREFIX)
app.include_router(user.router,               prefix=API_PREFIX)
app.include_router(enquiry.router,            prefix=API_PREFIX)
app.include_router(fleet.router,              prefix=API_PREFIX)
app.include_router(membership.router,         prefix=API_PREFIX)
app.include_router(payment.router,            prefix=API_PREFIX)
app.include_router(blog.router,               prefix=API_PREFIX)
app.include_router(blog.faq_router,           prefix=API_PREFIX)
app.include_router(blog.testimonial_router,   prefix=API_PREFIX)
app.include_router(admin.router,              prefix=API_PREFIX)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}
