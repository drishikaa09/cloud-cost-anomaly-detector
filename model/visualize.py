"""
Cloud Cost Anomaly Detector - Visualization
Plots daily cost per service over time, highlighting flagged anomalies in red.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

df = pd.read_csv("predictions.csv")
df["date"] = pd.to_datetime(df["date"])

os.makedirs("plots", exist_ok=True)

services = df["service"].unique()

fig, axes = plt.subplots(len(services), 1, figsize=(12, 3 * len(services)), sharex=True)

for ax, service in zip(axes, services):
    service_df = df[df["service"] == service].sort_values("date")
    normal = service_df[service_df["anomaly_flag"] == 1]
    anomalies = service_df[service_df["anomaly_flag"] == -1]

    ax.plot(normal["date"], normal["daily_cost"], color="steelblue", linewidth=1, label="Normal")
    ax.scatter(anomalies["date"], anomalies["daily_cost"], color="red", s=50, zorder=5, label="Anomaly")

    ax.set_title(service)
    ax.set_ylabel("Daily Cost ($)")
    ax.legend(loc="upper right", fontsize=8)

plt.xlabel("Date")
plt.tight_layout()
plt.savefig("plots/all_services_anomalies.png", dpi=150)
print("Saved plot to plots/all_services_anomalies.png")

# Also save one combined "total daily cost" view across all services
pivot = df.pivot_table(index="date", columns="service", values="daily_cost", aggfunc="sum")
total_cost = pivot.sum(axis=1)

plt.figure(figsize=(12, 4))
plt.plot(total_cost.index, total_cost.values, color="darkgreen")
plt.title("Total Daily AWS Cost (All Services Combined)")
plt.xlabel("Date")
plt.ylabel("Total Daily Cost ($)")
plt.tight_layout()
plt.savefig("plots/total_daily_cost.png", dpi=150)
print("Saved plot to plots/total_daily_cost.png")
