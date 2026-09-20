from fastapi import APIRouter, HTTPException

from app.models.analysis import AnalysisRequest
from app.services.health_engine import HealthEngine


router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "online",
        "service": "DevLens AI"
    }


@router.post("/analyze")
def analyze_code(request: AnalysisRequest):
    try:
        engine = HealthEngine(request.code)
        report = engine.analyze()

        if not report.get("success"):
            raise HTTPException(
                status_code=400,
                detail=report.get(
                    "error",
                    "Code analysis failed."
                )
            )

        return {
            "success": True,
            "report": report
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Internal analysis error: {str(error)}"
        )