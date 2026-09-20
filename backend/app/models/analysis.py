from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    code: str = Field(
        ...,
        min_length=1,
        description="Python source code to analyze"
    )


class AnalysisResponse(BaseModel):
    success: bool
    report: dict