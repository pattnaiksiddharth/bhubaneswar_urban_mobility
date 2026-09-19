"""
route_optimization.py

Rule-based route and frequency optimization flagging for Bhubaneswar public transport network.

Inputs:
    - data/processed/stop_demand_summary.csv
    - data/processed/synthetic_routes.geojson
    - data/processed/high_centrality_nodes.geojson

Outputs:
    - data/processed/route_optimization_flags.csv
"""

from pathlib import Path
import geopandas as gpd
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]
PROC_DIR = PROJECT_ROOT / "03_Data" / "processed"


def main():
    print("=== Bhubaneswar Route & Frequency Optimization Flagging ===", flush=True)

    # 1. Load data
    demand_summary = pd.read_csv(PROC_DIR / "stop_demand_summary.csv")
    routes_gdf = gpd.read_file(PROC_DIR / "synthetic_routes.geojson")
    nodes_gdf = gpd.read_file(PROC_DIR / "high_centrality_nodes.geojson")

    # 2. Merge routes with stop demand summary
    merged_df = routes_gdf.merge(demand_summary, on="stop_id")

    # 3. Compute Demand Quartile across all 73 stops (Q1=lowest 25%, Q4=highest 25%)
    merged_df["demand_quartile"] = pd.qcut(
        merged_df["total_daily_demand"].rank(method="first"), 4, labels=["Q1", "Q2", "Q3", "Q4"]
    )

    # 4. Assign synthetic "current_frequency" ("High" 30%, "Low" 70% probability)
    # Modeling Assumption: Simulated CRUT schedule alignment mismatch (seed 42)
    np.random.seed(42)
    frequencies = np.random.choice(["High", "Low"], size=len(merged_df), p=[0.3, 0.7])
    merged_df["current_frequency"] = frequencies

    # 5. Flag primary_flag category
    def assign_primary_flag(row):
        q = str(row["demand_quartile"])
        freq = row["current_frequency"]
        if q in ["Q3", "Q4"] and freq == "Low":
            return "Increase Frequency"
        elif q in ["Q3", "Q4"] and freq == "High":
            return "Well-Served"
        else:  # Q1 or Q2
            return "Adequate"

    merged_df["primary_flag"] = merged_df.apply(assign_primary_flag, axis=1)

    # 6. Flag near_congestion_point (within 500m of top 20 high-centrality nodes)
    # Convert stop locations to projected CRS (EPSG:32644 for meters)
    stops_projected = gpd.GeoDataFrame(
        merged_df,
        geometry=gpd.points_from_xy(merged_df["lon"], merged_df["lat"]),
        crs="EPSG:4326",
    ).to_crs(epsg=32644)

    nodes_projected = nodes_gdf.to_crs(epsg=32644)

    # Check if stop is within 500m of any high-centrality node
    nodes_union_buffer = nodes_projected.geometry.buffer(500).union_all()
    near_congestion = stops_projected.geometry.within(nodes_union_buffer)
    merged_df["near_congestion_point"] = near_congestion

    # 7. Save result
    output_cols = [
        "route_id",
        "stop_id",
        "dominant_type",
        "total_daily_demand",
        "demand_quartile",
        "current_frequency",
        "primary_flag",
        "near_congestion_point",
    ]
    out_df = merged_df[output_cols].copy()
    out_path = PROC_DIR / "route_optimization_flags.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Saved route optimization flags table ({len(out_df)} rows) to {out_path}\n", flush=True)

    # 8. Print Summary Statistics
    print("--- Primary Flag Summary Counts ---", flush=True)
    flag_counts = out_df["primary_flag"].value_counts()
    for flag, count in flag_counts.items():
        print(f"  {flag}: {count}", flush=True)

    congestion_count = out_df["near_congestion_point"].sum()
    print(f"\nRoutes Flagged Near Congestion Point (within 500m): {congestion_count} / {len(out_df)}", flush=True)

    print("\nBreakdown of Congestion Risk by Primary Flag:", flush=True)
    ct = pd.crosstab(out_df["primary_flag"], out_df["near_congestion_point"])
    print(ct, flush=True)


if __name__ == "__main__":
    main()
