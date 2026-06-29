import csv
import random
from datetime import date, timedelta

START_DATE = date(2025, 1, 1)
NUM_DAYS = 90
ACCOUNT_ID = "732778637529"
REGION = "eu-north-1"

SERVICES = {
    "EC2": 5.0,
    "RDS": 3.0,
    "S3": 0.5,
    "Lambda": 0.2,
    "CloudWatch": 0.3,
    "DataTransfer": 1.0,
}

NOISE_FRACTION = 0.08
WEEKEND_MULTIPLIER = 0.7
TOTAL_TREND_GROWTH = 0.15

random.seed(42)

ANOMALIES = [
    (15, "EC2", "spike", 4.0),
    (30, "RDS", "spike", 3.5),
    (42, "S3", "spike", 6.0),
    (50, "DataTransfer", "spike", 5.0),
    (60, "Lambda", "spike", 8.0),
    (70, "EC2", "drop", 0.1),
    (80, "CloudWatch", "spike", 5.0),
]


def get_trend_multiplier(day_index):
    progress = day_index / (NUM_DAYS - 1)
    return 1.0 + (TOTAL_TREND_GROWTH * progress)


def get_weekend_multiplier(current_date):
    if current_date.weekday() in (5, 6):
        return WEEKEND_MULTIPLIER
    return 1.0


def get_anomaly_multiplier(day_index, service):
    for (anom_day, anom_service, anom_type, multiplier) in ANOMALIES:
        if day_index == anom_day and service == anom_service:
            return multiplier
    return 1.0


def generate_data():
    rows = []
    for day_index in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day_index)
        trend_mult = get_trend_multiplier(day_index)
        weekend_mult = get_weekend_multiplier(current_date)

        for service, baseline in SERVICES.items():
            anomaly_mult = get_anomaly_multiplier(day_index, service)
            noise = 1.0 + random.uniform(-NOISE_FRACTION, NOISE_FRACTION)
            cost = baseline * trend_mult * weekend_mult * noise * anomaly_mult
            cost = round(max(cost, 0), 4)

            rows.append({
                "date": current_date.isoformat(),
                "service": service,
                "region": REGION,
                "daily_cost": cost,
                "account_id": ACCOUNT_ID,
            })
    return rows


def write_costs_csv(rows, path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "service", "region", "daily_cost", "account_id"])
        writer.writeheader()
        writer.writerows(rows)


def write_ground_truth_csv(path):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "service", "anomaly_type", "multiplier_applied"])
        for (day_offset, service, anomaly_type, multiplier) in ANOMALIES:
            anomaly_date = START_DATE + timedelta(days=day_offset)
            writer.writerow([anomaly_date.isoformat(), service, anomaly_type, multiplier])


if __name__ == "__main__":
    rows = generate_data()
    write_costs_csv(rows, "output/synthetic_costs.csv")
    write_ground_truth_csv("output/ground_truth_anomalies.csv")
    print(f"Generated {len(rows)} cost records across {NUM_DAYS} days for {len(SERVICES)} services.")
    print("Files written to output/synthetic_costs.csv and output/ground_truth_anomalies.csv")
