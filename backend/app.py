from datetime import date as EventDate

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from backend.loader import load_contractors
from backend.recommender import (
    CALENDAR_START,
    CALENDAR_END,
    recommend,
)


app = FastAPI(title="Подбор подрядчиков")
contractors = load_contractors()

# Разрешаем подключение локального интерфейса.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        allow_inf_nan=False,
    )

    city: str = Field(min_length=1)
    date: EventDate = Field(
        ge=CALENDAR_START,
        le=CALENDAR_END,
    )
    event_format: str = Field(min_length=1)
    category: str = Field(min_length=1)
    budget_kzt: float = Field(gt=0, strict=True)
    duration_hours: float | None = Field(
        default=None,
        gt=0,
        strict=True,
    )
    language: str | None = Field(default=None, min_length=1)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "profiles": len(contractors),
    }


@app.get("/options")
def options():
    return {
        "cities": sorted({
            c["city"] for c in contractors
        }),
        "categories": sorted({
            value
            for c in contractors
            for value in c["categories"]
        }),
        "event_formats": sorted({
            value
            for c in contractors
            for value in c["event_formats"]
        }),
        "languages": sorted({
            value
            for c in contractors
            for value in c["languages"]
        }),
        "date_min": CALENDAR_START.isoformat(),
        "date_max": CALENDAR_END.isoformat(),
    }


@app.post("/recommend")
def recommend_contractors(request: RecommendationRequest):
    try:
        return recommend(
            contractors,
            request.model_dump(mode="json"),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error