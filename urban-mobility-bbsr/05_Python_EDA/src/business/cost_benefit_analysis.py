"""
Cost-Benefit Analysis for Bhubaneswar Urban Mobility Analytics.

Estimates operating costs, revenues, net daily benefit, and ROI ratio
for routes recommended for service frequency increases.

Assumptions (documented as estimates, not CRUT actuals):
- Operating cost: Rs 65 per km (based on published Indian STU diesel bus operating costs, e.g. BMTC ~Rs 68.53/km)
- Service increase: +4 additional round trips per day per flagged route
- Round trip multiplier: 2 (additional_daily_km = route_length_km * 4 * 2)
- Average fare: Rs 15 per rider (flat-fare assumption typical for Indian city bus systems)
- New riders captured: 15% of total daily demand (conservative assumption that increased frequency captures 15% of unmet demand proxy)
"""

import os
import pandas as pd

def run_cost_benefit_analysis():
    # Define file paths relative to script location or project root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    dim_routes_path = os.path.join(base_dir, "03_Data", "dashboard", "dim_routes.csv")
    flags_path = os.path.join(base_dir, "03_Data", "processed", "route_optimization_flags.csv")
    stops_path = os.path.join(base_dir, "03_Data", "processed", "stop_demand_summary.csv")
    output_path = os.path.join(base_dir, "03_Data", "dashboard", "cost_benefit_analysis.csv")

    # Load input data
    dim_routes = pd.read_csv(dim_routes_path)
    flags = pd.read_csv(flags_path)
    stops = pd.read_csv(stops_path)

    # Filter for routes flagged for frequency increase
    flagged_routes = flags[flags["primary_flag"] == "Increase Frequency"].copy()

    # Merge with dim_routes to get route_length_km
    merged = pd.merge(
        flagged_routes,
        dim_routes[["route_id", "route_length_km"]],
        on="route_id",
        how="left"
    )

    # Documented Assumptions:
    # Operating cost per km: Rs 65 (Estimate based on published STU benchmark)
    OPERATING_COST_PER_KM = 65.0
    # Additional round trips per day: 4
    ADDITIONAL_ROUND_TRIPS = 4
    # Flat fare per rider: Rs 15
    AVERAGE_FARE_RS = 15.0
    # New ridership capture rate: 15% of total daily demand (conservative proxy assumption)
    CAPTURE_RATE = 0.15

    # 1. additional_daily_km = route_length_km * 4 * 2 (round trip)
    merged["additional_daily_km"] = merged["route_length_km"] * ADDITIONAL_ROUND_TRIPS * 2

    # 2. additional_daily_cost = additional_daily_km * 65
    merged["additional_daily_cost"] = merged["additional_daily_km"] * OPERATING_COST_PER_KM

    # 3. estimated_new_riders = total_daily_demand * 0.15
    merged["estimated_new_riders"] = merged["total_daily_demand"] * CAPTURE_RATE

    # 4. additional_daily_revenue = estimated_new_riders * 15
    merged["additional_daily_revenue"] = merged["estimated_new_riders"] * AVERAGE_FARE_RS

    # 5. net_daily_benefit = additional_daily_revenue - additional_daily_cost
    merged["net_daily_benefit"] = merged["additional_daily_revenue"] - merged["additional_daily_cost"]

    # 6. roi_ratio = additional_daily_revenue / additional_daily_cost
    merged["roi_ratio"] = merged["additional_daily_revenue"] / merged["additional_daily_cost"]

    # Select required columns
    output_cols = [
        "route_id",
        "stop_id",
        "route_length_km",
        "additional_daily_km",
        "additional_daily_cost",
        "estimated_new_riders",
        "additional_daily_revenue",
        "net_daily_benefit",
        "roi_ratio"
    ]
    result_df = merged[output_cols]

    # Save to data/dashboard/cost_benefit_analysis.csv
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result_df.to_csv(output_path, index=False)
    print(f"Cost-benefit analysis saved to {output_path} ({len(result_df)} routes processed)")

if __name__ == "__main__":
    run_cost_benefit_analysis()
