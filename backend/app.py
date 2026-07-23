"""
=============================================================
  AI-Based Customer Lifetime Value (CLV) Prediction System
  File: backend/app.py
  Purpose: FastAPI REST API  —  /predict, /customers, /stats
=============================================================
  Run:  uvicorn backend.app:app --reload  (from project root)
        OR
        cd backend && uvicorn app:app --reload
=============================================================
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import pickle
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent
MODEL_PATH  = BASE_DIR / "model" / "clv_model.pkl"
SCALER_PATH = BASE_DIR / "model" / "scaler.pkl"
DATA_PATH   = BASE_DIR / "data"  / "customers.csv"

# ── App Setup ──────────────────────────────────────────────
app = FastAPI(
    title       = "CLV Prediction API",
    description = "AI-powered Customer Lifetime Value prediction system",
    version     = "1.0.0",
)

# Allow all origins so the HTML file can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)

# ── Global State ───────────────────────────────────────────
model  = None
scaler = None
df     = None

# ── Startup: Load Model & Data ─────────────────────────────
@app.on_event("startup")
async def load_artifacts():
    global model, scaler, df
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        with open(SCALER_PATH, "rb") as f:
            scaler = pickle.load(f)
        df = pd.read_csv(DATA_PATH)
        print("[OK] Model, scaler, and dataset loaded successfully.")
    except FileNotFoundError as e:
        print(f"[ERR] Missing file: {e}")
        print("   Run `python model/train_model.py` first to generate artifacts.")

# ── Schemas ────────────────────────────────────────────────
class CustomerInput(BaseModel):
    age                : int   = Field(..., ge=18, le=100,  description="Customer age in years")
    purchase_frequency : int   = Field(..., ge=1,  le=365,  description="Number of purchases per year")
    avg_order_value    : float = Field(..., ge=1,           description="Average order value in USD")
    recency            : int   = Field(..., ge=0,  le=730,  description="Days since last purchase")
    tenure             : int   = Field(..., ge=1,  le=360,  description="Months as a customer")

class PredictionResponse(BaseModel):
    predicted_clv   : float
    segment         : str
    segment_color   : str
    segment_emoji   : str
    monthly_value   : float
    annual_value    : float
    input_summary   : dict

# ── Helpers ────────────────────────────────────────────────
def classify_segment(clv: float) -> tuple[str, str, str]:
    """Return (segment_label, hex_color, emoji)."""
    if clv < 1500:
        return "Low Value", "#ef4444", "Low"
    elif clv < 6000:
        return "Medium Value", "#f59e0b", "Mid"
    else:
        return "High Value", "#10b981", "High"

# ── POST /predict ──────────────────────────────────────────
@app.post("/predict", response_model=PredictionResponse, summary="Predict CLV for a customer")
async def predict_clv(customer: CustomerInput):
    """
    Accepts customer feature data and returns:
    - Predicted CLV (Customer Lifetime Value) in USD
    - Customer segment: Low / Medium / High Value
    - Monthly and annual estimated value
    """
    if model is None or scaler is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run train_model.py first."
        )

    # Build feature vector (order must match training order)
    features = [[
        customer.age,
        customer.purchase_frequency,
        customer.avg_order_value,
        customer.recency,
        customer.tenure,
    ]]

    features_scaled = scaler.transform(features)
    raw_clv         = model.predict(features_scaled)[0]
    clv             = max(0.0, round(float(raw_clv), 2))

    segment, color, emoji = classify_segment(clv)
    monthly_value         = round(clv / max(customer.tenure, 1), 2)
    annual_value          = round(monthly_value * 12, 2)

    return PredictionResponse(
        predicted_clv  = clv,
        segment        = segment,
        segment_color  = color,
        segment_emoji  = emoji,
        monthly_value  = monthly_value,
        annual_value   = annual_value,
        input_summary  = customer.model_dump(),
    )

# ── GET /customers ─────────────────────────────────────────
@app.get("/customers", summary="Get sample customer dataset")
async def get_customers(limit: int = 50, offset: int = 0):
    """Returns paginated customer records from the training dataset."""
    if df is None:
        raise HTTPException(status_code=503, detail="Dataset not loaded.")
    subset = df.iloc[offset : offset + limit]
    return {
        "total"     : len(df),
        "limit"     : limit,
        "offset"    : offset,
        "customers" : subset.to_dict(orient="records"),
    }

# ── GET /stats ─────────────────────────────────────────────
@app.get("/stats", summary="Get dataset summary statistics")
async def get_stats():
    """Returns summary statistics for the dashboard overview cards and chart."""
    if df is None:
        raise HTTPException(status_code=503, detail="Dataset not loaded.")

    low    = df[df["CLV"] < 1500]
    medium = df[(df["CLV"] >= 1500) & (df["CLV"] < 6000)]
    high   = df[df["CLV"] >= 6000]

    def safe_mean(subset):
        return round(subset["CLV"].mean(), 2) if len(subset) > 0 else 0.0

    seg_dist = {
        "Low Value"    : len(low),
        "Medium Value" : len(medium),
        "High Value"   : len(high),
    }

    return {
        "total_customers"    : int(len(df)),
        "avg_clv"            : round(float(df["CLV"].mean()), 2),
        "max_clv"            : round(float(df["CLV"].max()), 2),
        "min_clv"            : round(float(df["CLV"].min()), 2),
        "high_value_pct"     : round(len(high) / len(df) * 100, 1),
        "segment_distribution": seg_dist,
        "avg_by_segment"     : {
            "Low Value"    : safe_mean(low),
            "Medium Value" : safe_mean(medium),
            "High Value"   : safe_mean(high),
        },
        "age_avg"            : round(float(df["Age"].mean()), 1),
        "avg_order_value_avg": round(float(df["AvgOrderValue"].mean()), 2),
        "avg_tenure_months"  : round(float(df["Tenure"].mean()), 1),
    }

# ── GET / (health) ─────────────────────────────────────────
@app.get("/", summary="Health check")
async def root():
    return {
        "status"  : "running",
        "app"     : "CLV Prediction API",
        "version" : "1.0.0",
        "docs"    : "/docs",
    }
