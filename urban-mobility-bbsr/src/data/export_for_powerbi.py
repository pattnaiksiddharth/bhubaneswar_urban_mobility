"""
export_for_powerbi.py

Consolidates all processed analytics outputs into clean, dashboard-ready CSV tables
in data/dashboard/ for Power BI import.

Outputs:
    - data/dashboard/dim_stops.csv
    - data/dashboard/dim_routes.csv
    - data/dashboard/fact_hourly_demand.csv
    - data/dashboard/fact_daily_forecast.csv
    - data/dashboard/top_congestion_points.csv
"""

from pathlib import Path
import geopandas as gpd
import pandas as pd
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
PROC_DIR = PROJECT_ROOT / "data" / "processed"
DASHBOARD_DIR = PROJECT_ROOT / "data" / "dashboard"
DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)


def build_dim_stops():
    flags_df = pd.read_csv(PROC_DIR / "route_optimization_flags.csv")
    summary_df = pd.read_csv(PROC_DIR / "stop_demand_summary.csv")

    dim_stops = flags_df.merge(summary_df[["stop_id", "lat", "lon"]], on="stop_id", how="left")
    dim_stops = dim_stops.drop_duplicates(subset=["stop_id"]).copy()

    cols = [
        "stop_id",
        "lat",
        "lon",
        "dominant_type",
        "total_daily_demand",
        "demand_quartile",
        "current_frequency",
        "primary_flag",
        "near_congestion_point",
    ]
    dim_stops = dim_stops[cols]
    out_path = DASHBOARD_DIR / "dim_stops.csv"
    dim_stops.to_csv(out_path, index=False)
    return dim_stops, out_path


def build_dim_routes():
    flags_df = pd.read_csv(PROC_DIR / "route_optimization_flags.csv")
    routes_gdf = gpd.read_file(PROC_DIR / "synthetic_routes.geojson")

    # Project to EPSG:32644 for accurate distance calculation in meters -> km
    routes_proj = routes_gdf.to_crs(epsg=32644)
    routes_proj["route_length_km"] = (routes_proj.geometry.length / 1000.0).round(2)

    dim_routes = flags_df.merge(
        routes_proj[["route_id", "route_length_km"]], on="route_id", how="left"
    )

    cols = [
        "route_id",
        "stop_id",
        "dominant_type",
        "primary_flag",
        "near_congestion_point",
        "route_length_km",
    ]
    dim_routes = dim_routes[cols].copy()
    out_path = DASHBOARD_DIR / "dim_routes.csv"
    dim_routes.to_csv(out_path, index=False)
    return dim_routes, out_path


def build_fact_hourly_demand():
    hourly_df = pd.read_csv(PROC_DIR / "stop_demand_weights.csv")
    out_path = DASHBOARD_DIR / "fact_hourly_demand.csv"
    hourly_df.to_csv(out_path, index=False)
    return hourly_df, out_path


def build_fact_daily_forecast():
    citywide_df = pd.read_csv(PROC_DIR / "citywide_daily_demand.csv")
    citywide_df["date"] = pd.to_datetime(citywide_df["date"])

    train_df = citywide_df.iloc[:45].copy()
    test_df = citywide_df.iloc[45:].copy()

    # Prophet model forecast for test period
    prophet_train = train_df.rename(columns={"date": "ds", "total_demand": "y"})
    m_prophet = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False)
    m_prophet.fit(prophet_train)
    future = m_prophet.make_future_dataframe(periods=15, freq="D")
    forecast_prophet = m_prophet.predict(future)
    prophet_test_preds = forecast_prophet.iloc[45:]["yhat"].round(2).values

    # SARIMA model forecast for test period
    sarima_model = SARIMAX(
        train_df["total_demand"],
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 7),
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    sarima_fit = sarima_model.fit(disp=False)
    sarima_test_preds = sarima_fit.forecast(steps=15).round(2).values

    # Combine into full 60-day dataframe
    fact_forecast = citywide_df.rename(columns={"total_demand": "actual_demand"}).copy()
    fact_forecast["date"] = fact_forecast["date"].dt.strftime("%Y-%m-%d")
    fact_forecast["prophet_forecast"] = None
    fact_forecast["sarima_forecast"] = None
    fact_forecast["is_test_period"] = False

    # Populate test period rows (last 15 rows)
    fact_forecast.loc[45:, "prophet_forecast"] = prophet_test_preds
    fact_forecast.loc[45:, "sarima_forecast"] = sarima_test_preds
    fact_forecast.loc[45:, "is_test_period"] = True

    out_path = DASHBOARD_DIR / "fact_daily_forecast.csv"
    fact_forecast.to_csv(out_path, index=False)
    return fact_forecast, out_path


def build_top_congestion_points():
    nodes_gdf = gpd.read_file(PROC_DIR / "high_centrality_nodes.geojson")
    nodes_df = pd.DataFrame({
        "node_id": nodes_gdf["osmid"],
        "lat": nodes_gdf.geometry.y,
        "lon": nodes_gdf.geometry.x,
        "centrality_score": nodes_gdf["centrality_score"].round(6),
    })

    out_path = DASHBOARD_DIR / "top_congestion_points.csv"
    nodes_df.to_csv(out_path, index=False)
    return nodes_df, out_path


def main():
    print("=== Exporting Dashboard-Ready Datasets for Power BI ===", flush=True)

    stops_df, stops_path = build_dim_stops()
    routes_df, routes_path = build_dim_routes()
    hourly_df, hourly_path = build_fact_hourly_demand()
    forecast_df, forecast_path = build_fact_daily_forecast()
    congestion_df, congestion_path = build_top_congestion_points()

    print("\n--- Summary of Exported Dashboard Tables ---", flush=True)
    
    tables = [
        ("dim_stops.csv", stops_df, stops_path),
        ("dim_routes.csv", routes_df, routes_path),
        ("fact_hourly_demand.csv", hourly_df, hourly_path),
        ("fact_daily_forecast.csv", forecast_df, forecast_path),
        ("top_congestion_points.csv", congestion_df, congestion_path),
    ]

    for name, df, path in tables:
        print(f"\nFile: {name}")
        print(f"  Path: {path}")
        print(f"  Row Count: {len(df)}")
        print(f"  Columns ({len(df.columns)}): {list(df.columns)}")
        print(f"  File Size: {path.stat().st_size:,} bytes")

    print("\nAll 5 dashboard-ready CSV files generated successfully in data/dashboard/", flush=True)


if __name__ == "__main__":
    main()
