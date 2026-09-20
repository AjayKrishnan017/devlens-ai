from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


app = FastAPI(
    title="DevLens AI",
    description="AI-powered code intelligence and defect-risk analysis platform",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "DevLens AI",
        "version": "1.0.0",
        "status": "running",
    }


app.include_router(
    router,
    prefix="/api/v1",
    tags=["Analysis"],
)