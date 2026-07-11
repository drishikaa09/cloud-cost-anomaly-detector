# Cloud Cost Anomaly Detector

End-to-end FinOps pipeline that detects AWS cloud cost anomalies using machine learning, deployed via a fully automated CI/CD pipeline.

## Architecture

S3 (raw CSV) → AWS Glue Crawler → Glue ETL Job (PySpark) → S3 (Parquet) → Athena
↓
Isolation Forest Model
↓
Jenkins Pipeline (EC2)
↓
Docker → ECR → FastAPI (EC2)

## Tech Stack

| | |
|---|---|
| ETL | AWS Glue, PySpark, S3, Athena |
| ML | scikit-learn (Isolation Forest) |
| API | FastAPI, Docker, AWS ECR |
| CI/CD | Jenkins (declarative pipeline) |
| Infrastructure | AWS EC2, IAM |
| Dashboard | Streamlit |

## API

```bash
curl -X POST http://<EC2_IP>:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-01-16", "service": "EC2", "daily_cost": 19.22, "rolling_mean_7d": 5.04}'
```

```json
{"service": "EC2", "date": "2025-01-16", "daily_cost": 19.22, "is_anomaly": true, "anomaly_score": -0.3004}
```

## Pipeline Stages

Checkout → Model Training → Verify Output → Docker Build → ECR Push → Deploy

## Results

- 6 AWS services monitored (EC2, RDS, S3, Lambda, CloudWatch, DataTransfer)
- 7/7 ground truth anomalies detected (100% recall)
- Live inference endpoint serving predictions via REST API
