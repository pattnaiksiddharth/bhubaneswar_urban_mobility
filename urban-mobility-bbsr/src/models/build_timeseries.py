"""
build_timeseries.py

Generates synthetic 60-day time series demand data (Jan 1, 2026 - Mar 1, 2026) for Bhubaneswar.

Inputs:
    - data/processed/stop_demand_weights.csv
    - data/processed/stop_demand_summary.csv

Outputs:
    - data/processed/citywide_daily_demand.csv
    - data/processed/top5_stops_daily_demand.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
PROC_DIR = PROJECT_ROOT / "data" / "processed"

# Config
START_DATE = "2026-01-01"
DAYS = 60
TOTAL_TREND_GROWTH = 0.02  # 2% growth over 60 days
NOISE_STD = 0.05  # +/- 5-10% Gaussian noise


def get_weekend_multiplier(dominant_type):
    dtype = str(dominant_type).lower()
    if dtype in ["hospital", "mall"]:
        return 0.70
    elif dtype in ["college", "university"]:
        return 0.30
    else:
        return 0.90


def main():
    print("=== Generating 60-Day Time Series Demand Dataset ===", flush=True)
    
    # Load input data
    weights_df = pd.read_csv(PROC_DIR / "stop_demand_weights.csv")
    summary_df = pd.read_csv(PROC_DIR / "stop_demand_summary.csv")

    stop_type_map = summary_df.set_index("stop_id")["dominant_type"].to_dict()
    top5_stops = summary_df.sort_values("total_daily_demand", ascending=False).head(5)["stop_id"].tolist()

    date_range = pd.date_range(start=START_DATE, periods=DAYS, freq="D")

    all_hourly_records = []

    np.random.seed(42)

    for day_idx, date in enumerate(date_range):
        is_weekend = date.weekday() >= 5
        trend_mult = 1.0 + (day_idx / (DAYS - 1)) * TOTAL_TREND_GROWTH

        for _, row in weights_df.iterrows():
            stop_id = row["stop_id"]
            hour = int(row["hour"])
            base_proxy = row["demand_proxy"]
            dom_type = stop_type_map.get(stop_id, "hospital")

            if is_weekend:
                day_mult = get_weekend_multiplier(dom_type)
            else:
                day_mult = 1.0

            # Apply +/-10% Gaussian noise
            noise = np.random.normal(1.0, NOISE_STD)
            noise = np.clip(noise, 0.85, 1.15)

            hourly_demand = base_proxy * day_mult * trend_mult * noise

            all_hourly_records.append({
                "date": date.strftime("%Y-%m-%d"),
                "stop_id": stop_id,
                "hour": hour,
                "demand": hourly_demand,
            })

    full_df = pd.DataFrame(all_hourly_records)

    # Aggregate daily demand per stop
    daily_stop_df = full_df.groupby(["date", "stop_id"])["demand"].sum().reset_index()

    # 1. Citywide Daily Total Demand Series
    citywide_daily = (
        daily_stop_df.groupby("date")["demand"]
        .sum()
        .reset_index()
        .rename(columns={"demand": "total_demand"})
    )
    citywide_daily["total_demand"] = citywide_daily["total_demand"].round(2)
    
    citywide_path = PROC_DIR / "citywide_daily_demand.csv"
    citywide_daily.to_csv(citywide_path, index=False)
    print(f"Saved citywide daily demand dataset ({len(citywide_daily)} days: {citywide_daily['date'].min()} to {citywide_daily['date'].max()}) to {citywide_path}", flush=True)

    # 2. Top 5 Stops Daily Demand Series
    top5_daily = daily_stop_df[daily_stop_df["stop_id"].isin(top5_stops)].copy()
    top5_daily["demand"] = top5_daily["demand"].round(2)
    top5_daily = top5_daily.rename(columns={"demand": "daily_demand"})

    top5_path = PROC_DIR / "top5_stops_daily_demand.csv"
    top5_daily.to_csv(top5_path, index=False)
    print(f"Saved top 5 stops daily demand dataset ({len(top5_daily)} rows) to {top5_path}", flush=True)


if __name__ == "__main__":
    main()
