
import os
from datetime import datetime, timezone
from typing import Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from supabase import Client, create_client


# --------------------------------------------------
# 1. Environment Configuration
# --------------------------------------------------

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

APP_NAME = "Aabhaas Public Alert API"

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY", ""
).strip()
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "").strip()


# --------------------------------------------------
# 2. Supabase Connection
# --------------------------------------------------

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    supabase: Optional[Client] = None
else:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
    )


def require_database() -> Client:
    """Return the Supabase client or report a configuration error."""

    if supabase is None:
        raise HTTPException(
            status_code=503,
            detail="Database is not configured.",
        )

    return supabase


# --------------------------------------------------
# 3. FastAPI Application and CORS
# --------------------------------------------------

app = FastAPI(
    title=APP_NAME,
    version="0.1.0",
)

origins_raw = os.getenv(
    "PUBLIC_WEBSITE_ORIGINS",
    "https://aabhaas-public-alerts.onrender.com",
)

origins = [
    origin.strip().rstrip("/")
    for origin in origins_raw.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Key"],
)


# --------------------------------------------------
# 4. Data Models
# --------------------------------------------------

Source = Literal["AI_MODEL", "IOT_SENSOR", "MANUAL"]

Severity = Literal["LOW", "MODERATE", "HIGH", "CRITICAL"]

RiskCategory = Literal[
    "Very Low",
    "Low",
    "Moderate",
    "High",
    "Very High",
]


class AlertCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    severity: Severity
    message: str = Field(min_length=5, max_length=2000)
    location: str = Field(min_length=2, max_length=200)
    source: Source
    risk_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
    )
    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
    )
    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
    )


class AlertResolve(BaseModel):
    resolution_note: str = Field(
        default="Resolved by authorized administrator",
        max_length=1000,
    )


class DashboardStatusUpdate(BaseModel):
    risk_score: float = Field(ge=0, le=100)
    category: RiskCategory
    location: str = Field(min_length=2, max_length=200)
    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
    )
    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
    )
    source: str = Field(
        default="AI_MODEL",
        max_length=50,
    )
    message: str = Field(max_length=1000)


# --------------------------------------------------
# 5. Admin Authentication
# --------------------------------------------------

def require_admin(x_admin_key: Optional[str]) -> None:
    """Verify the administrator's API key."""

    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Admin API is not configured.",
        )

    if not x_admin_key or x_admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing admin key.",
        )


# --------------------------------------------------
# 6. Health Check
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": APP_NAME,
        "database_configured": supabase is not None,
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }


# --------------------------------------------------
# 7. Dashboard Status API
# --------------------------------------------------

@app.post("/api/dashboard/status")
def update_dashboard_status(
    payload: DashboardStatusUpdate,
    x_admin_key: Optional[str] = Header(default=None),
):
    """
    Create or update the single current dashboard status.

    Only an authorized dashboard or administrator can update it.
    """

    require_admin(x_admin_key)
    db = require_database()

    row = {
        "id": 1,
        "risk_score": payload.risk_score,
        "category": payload.category,
        "location": payload.location,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "source": payload.source,
        "message": payload.message,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    result = (
        db.table("dashboard_status")
        .upsert(row, on_conflict="id")
        .execute()
    )

    return {
        "status": "ok",
        "dashboard_status": (
            result.data[0] if result.data else row
        ),
    }


@app.get("/api/dashboard/status")
def get_dashboard_status():
    """Retrieve the latest dashboard risk status."""

    db = require_database()

    result = (
        db.table("dashboard_status")
        .select("*")
        .eq("id", 1)
        .limit(1)
        .execute()
    )

    return {
        "dashboard_status": (
            result.data[0] if result.data else None
        )
    }


# --------------------------------------------------
# 8. Get Current Active Alert
# --------------------------------------------------

@app.get("/api/alerts/active")
def get_active_alert():
    db = require_database()

    result = (
        db.table("alerts")
        .select("*")
        .eq("status", "ACTIVE")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    return {
        "alert": result.data[0] if result.data else None
    }


# --------------------------------------------------
# 9. Get Alert History
# --------------------------------------------------

@app.get("/api/alerts/history")
def get_alert_history(
    limit: int = Query(default=20, ge=1, le=100),
):
    db = require_database()

    result = (
        db.table("alerts")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return {
        "alerts": result.data
    }


# --------------------------------------------------
# 10. Create a New Alert
# --------------------------------------------------

@app.post("/api/alerts")
def create_alert(
    payload: AlertCreate,
    x_admin_key: Optional[str] = Header(default=None),
):
    """
    Resolve existing active alerts and create a new active alert.
    This endpoint requires administrator authentication.
    """

    require_admin(x_admin_key)
    db = require_database()

    now = datetime.now(timezone.utc).isoformat()

    # Resolve any previous active alert.
    db.table("alerts").update(
        {
            "status": "RESOLVED",
            "resolved_at": now,
            "resolution_note": (
                "Automatically superseded by a newer alert"
            ),
        }
    ).eq("status", "ACTIVE").execute()

    # Prepare the new alert.
    row = payload.model_dump()

    row.update(
        {
            "status": "ACTIVE",
            "created_at": now,
            "resolved_at": None,
            "resolution_note": None,
        }
    )

    result = (
        db.table("alerts")
        .insert(row)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Alert could not be saved.",
        )

    return {
        "alert": result.data[0]
    }


# --------------------------------------------------
# 11. Resolve an Existing Alert
# --------------------------------------------------

@app.post("/api/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: str,
    payload: AlertResolve,
    x_admin_key: Optional[str] = Header(default=None),
):
    require_admin(x_admin_key)
    db = require_database()

    now = datetime.now(timezone.utc).isoformat()

    result = (
        db.table("alerts")
        .update(
            {
                "status": "RESOLVED",
                "resolved_at": now,
                "resolution_note": payload.resolution_note,
            }
        )
        .eq("id", alert_id)
        .eq("status", "ACTIVE")
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Active alert not found.",
        )

    return {
        "alert": result.data[0]
    }

