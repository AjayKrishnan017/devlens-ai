from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


# ---------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------

app = FastAPI(
    title="DevLens AI",
    description=(
        "AI-powered code intelligence platform combining "
        "static analysis, complexity analysis, security checks, "
        "and machine-learning-based defect-risk estimation."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------

origins = [
    # Local React development
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # Production Vercel frontend
    "https://devlens-ai-cyan.vercel.app",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "DevLens AI",
        "version": "1.0.0",
        "status": "running",
        "description": (
            "AI-powered code intelligence and "
            "defect-risk analysis platform"
        ),
    }


# ---------------------------------------------------------
# Health Endpoint
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "DevLens AI API",
        "version": "1.0.0",
    }


# ---------------------------------------------------------
# API Routes
# ---------------------------------------------------------

app.include_router(
    router,
    prefix="/api/v1",
    tags=["Analysis"],
)