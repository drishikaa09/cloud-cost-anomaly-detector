"""
Cloud Cost Anomaly Detector - FastAPI Inference Endpoint
Accepts daily cost data and returns anomaly predictions.
"""

from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import os

app = FastAPI(title="Cloud Cost Anomaly Detector")

# Load all trained models at startup
MODELS_DIR = os.path.join(os.path.dirname(__file__), "model/models")
models = {}
for fname in os.listdir(MODELS_DIR):
    if fname.endswith("_model.pkl"):
        service = fname.replace("_model.pkl", "")
        models[service] = joblib.load(os.path.join(MODELS_DIR, fname))

print(f"Loaded models for services: {list(models.keys())}")


class CostRecord(BaseModel):
    date: str
    service: str
    daily_cost: float
    rolling_mean_7d: float


class PredictionResponse(BaseModel):
    service: str
    date: str
    daily_cost: float
    is_anomaly: bool
    anomaly_score: float


@app.get("/")
def root():
    return {"status": "ok", "services_loaded": list(models.keys())}


@app.post("/predict", response_model=PredictionResponse)
def predict(record: CostRecord):
    if record.service not in models:
        return {"error": f"No model found for service: {record.service}"}

    model = models[record.service]

    date = pd.to_datetime(record.date)
    features = pd.DataFrame([{
        "daily_cost": record.daily_cost,
        "day_of_week": date.dayofweek,
        "rolling_mean_7d": record.rolling_mean_7d,
        "deviation": record.daily_cost - record.rolling_mean_7d
    }])

    score = float(model.decision_function(features)[0])
    threshold = -0.1  # scores below this = anomaly
    is_anomaly = score < threshold

    return PredictionResponse(
        service=record.service,
        date=record.date,
        daily_cost=record.daily_cost,
        is_anomaly=is_anomaly,
        anomaly_score=round(score, 4)
    )
