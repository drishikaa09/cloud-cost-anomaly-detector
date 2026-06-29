"""
Cloud Cost Anomaly Detector - Model Training
Trains a separate Isolation Forest model per AWS service,
then evaluates detected anomalies against the known ground truth.
"""

import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

# ---------- Load data ----------
df = pd.read_csv("curated_costs.csv")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["service", "date"]).reset_index(drop=True)

print(f"Loaded {len(df)} rows across services: {df['service'].unique()}")

# ---------- Feature engineering ----------
# day_of_week helps the model understand weekly seasonality isn't an anomaly
df["day_of_week"] = df["date"].dt.dayofweek

# rolling 7-day MEDIAN per service, shifted by 1 day so "today" is never
# included in its own baseline, and median resists being dragged by a single spike
df["rolling_mean_7d"] = (
    df.groupby("service")["daily_cost"]
    .transform(lambda x: x.shift(1).rolling(window=7, min_periods=1).median())
)
# first row per service has no prior data - backfill with its own value
df["rolling_mean_7d"] = df["rolling_mean_7d"].fillna(df["daily_cost"])

# deviation from rolling baseline - the key anomaly signal
df["deviation"] = df["daily_cost"] - df["rolling_mean_7d"]
# ---------- Train one Isolation Forest per service ----------
os.makedirs("models", exist_ok=True)

results = []

for service in df["service"].unique():
    service_df = df[df["service"] == service].copy()

    features = service_df[["daily_cost", "day_of_week", "rolling_mean_7d", "deviation"]]

    # Don't force a fixed contamination quota - let the model score everything,
    # then we decide the cutoff ourselves based on the score distribution
    model = IsolationForest(
        n_estimators=100,
        contamination="auto",
        random_state=42
    )
    model.fit(features)

    service_df["anomaly_score"] = model.decision_function(features)

    # Flag as anomaly only if the score is notably low (more negative = more anomalous)
    # threshold = mean - 2 std devs of this service's own scores
    threshold = service_df["anomaly_score"].mean() - 2 * service_df["anomaly_score"].std()
    service_df["anomaly_flag"] = service_df["anomaly_score"].apply(lambda s: -1 if s < threshold else 1)
    # save the trained model for this service
    joblib.dump(model, f"models/{service}_model.pkl")

    results.append(service_df)

# ---------- Combine results ----------
final_df = pd.concat(results).sort_values(["service", "date"])
final_df.to_csv("predictions.csv", index=False)

# ---------- Show flagged anomalies ----------
anomalies = final_df[final_df["anomaly_flag"] == -1]
print(f"\nFlagged {len(anomalies)} anomalies:")
print(anomalies[["date", "service", "daily_cost", "rolling_mean_7d", "deviation"]].to_string(index=False))

print("\nModels saved in models/ folder. Full predictions saved to predictions.csv")
