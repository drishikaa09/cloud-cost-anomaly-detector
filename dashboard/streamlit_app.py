"""
Cloud Cost Anomaly Detector - Streamlit Dashboard
"""

import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

st.set_page_config(page_title="Cloud Cost Anomaly Detector", layout="wide")

st.title("☁️ Cloud Cost Anomaly Detector")
st.markdown("AI-powered AWS cost anomaly detection using Isolation Forest")

API_URL = "http://13.63.166.181:8000"

# ---------- Load predictions data ----------
@st.cache_data
def load_data():
    # Hardcoded predictions based on our model output
    # In production this would call the API for each row
    data = {
        "date": pd.date_range("2025-01-01", periods=90),
    }
    return data

# ---------- Sidebar ----------
st.sidebar.header("Settings")
selected_service = st.sidebar.selectbox(
    "Select AWS Service",
    ["EC2", "RDS", "S3", "Lambda", "CloudWatch", "DataTransfer"]
)

# ---------- Live Prediction Form ----------
st.header("🔍 Live Anomaly Prediction")
st.markdown("Test the model with your own cost data:")

col1, col2, col3, col4 = st.columns(4)
with col1:
    input_date = st.date_input("Date", value=pd.to_datetime("2025-01-16"))
with col2:
    input_service = st.selectbox("Service", ["EC2", "RDS", "S3", "Lambda", "CloudWatch", "DataTransfer"])
with col3:
    input_cost = st.number_input("Daily Cost ($)", min_value=0.0, value=19.22, step=0.1)
with col4:
    input_rolling = st.number_input("7-day Rolling Mean ($)", min_value=0.0, value=5.04, step=0.1)

if st.button("🚀 Run Prediction", type="primary"):
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json={
                "date": str(input_date),
                "service": input_service,
                "daily_cost": input_cost,
                "rolling_mean_7d": input_rolling
            },
            timeout=10
        )
        result = response.json()

        if result.get("is_anomaly"):
            st.error(f"🚨 ANOMALY DETECTED! Anomaly score: {result['anomaly_score']}")
        else:
            st.success(f"✅ Normal cost. Anomaly score: {result['anomaly_score']}")

    except Exception as e:
        st.warning(f"Could not reach API: {e}. Make sure the EC2 instance is running.")

st.divider()

# ---------- Cost Chart ----------
st.header("📈 Cost Trends & Detected Anomalies")

# Known anomalies from our model
anomaly_data = {
    "date": ["2025-03-22", "2025-02-20", "2025-02-26", "2025-01-06",
             "2025-01-16", "2025-03-12", "2025-03-02", "2025-01-31",
             "2025-01-05", "2025-02-12"],
    "service": ["CloudWatch", "DataTransfer", "DataTransfer", "EC2",
                "EC2", "EC2", "Lambda", "RDS", "S3", "S3"],
    "daily_cost": [1.26, 5.10, 1.05, 5.29, 19.22, 0.55, 1.24, 11.34, 0.33, 3.47],
    "anomaly_type": ["spike", "spike", "false positive", "false positive",
                     "spike", "drop", "spike", "spike", "false positive", "spike"]
}
anomaly_df = pd.DataFrame(anomaly_data)
anomaly_df["date"] = pd.to_datetime(anomaly_df["date"])

st.subheader(f"Detected Anomalies")
st.dataframe(
    anomaly_df[["date", "service", "daily_cost", "anomaly_type"]].style.apply(
        lambda x: ["background-color: #ffcccc" if v == "spike"
                   else "background-color: #fff3cc" if v == "drop"
                   else "" for v in x], subset=["anomaly_type"]
    ),
    use_container_width=True
)

st.divider()

# ---------- Model Info ----------
st.header("🤖 Model Details")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Algorithm", "Isolation Forest")
col2.metric("Services Monitored", "6")
col3.metric("Days of Data", "90")
col4.metric("Anomalies Detected", "10")

st.markdown("""
**How it works:**
1. AWS cost data is ingested via **AWS Glue ETL** and stored as Parquet in S3
2. An **Isolation Forest** model is trained per service using rolling median baselines
3. The trained model is containerized with **Docker** and deployed via **Jenkins CI/CD**
4. A **FastAPI** endpoint serves live predictions at `/predict`
""")
