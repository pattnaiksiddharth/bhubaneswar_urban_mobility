"""
forecast_demand.py

Fits Prophet and SARIMA forecasting models on 45-day train set and evaluates on 15-day test set.

Inputs:
    - data/processed/citywide_daily_demand.csv

Outputs:
    - data/processed/model_comparison.csv
    - reports/figures/05_forecast_comparison.png
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]
PROC_DIR = PROJECT_ROOT / "03_Data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports" / "figures"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=== Bhubaneswar Citywide Demand Forecasting Pipeline ===", flush=True)

    # 1. Load data
    df = pd.read_csv(PROC_DIR / "citywide_daily_demand.csv")
    df["date"] = pd.to_datetime(df["date"])

    # 2. Train-Test Split (45 days train, 15 days test)
    train_df = df.iloc[:45].copy()
    test_df = df.iloc[45:].copy()
    print(f"Train period: {train_df['date'].min().strftime('%Y-%m-%d')} to {train_df['date'].max().strftime('%Y-%m-%d')} ({len(train_df)} days)", flush=True)
    print(f"Test period:  {test_df['date'].min().strftime('%Y-%m-%d')} to {test_df['date'].max().strftime('%Y-%m-%d')} ({len(test_df)} days)", flush=True)

    # ---------------------------------------------------------------------------
    # Model 1: Facebook Prophet
    # ---------------------------------------------------------------------------
    print("\nFitting Prophet model...", flush=True)
    prophet_train = train_df.rename(columns={"date": "ds", "total_demand": "y"})
    
    m_prophet = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False)
    m_prophet.fit(prophet_train)

    future = m_prophet.make_future_dataframe(periods=15, freq="D")
    forecast_prophet = m_prophet.predict(future)

    prophet_test_preds = forecast_prophet.iloc[45:]["yhat"].values
    y_test = test_df["total_demand"].values

    prophet_rmse = root_mean_squared_error(y_test, prophet_test_preds)
    prophet_mae = mean_absolute_error(y_test, prophet_test_preds)
    print(f"Prophet -> RMSE: {prophet_rmse:.2f}, MAE: {prophet_mae:.2f}", flush=True)

    # ---------------------------------------------------------------------------
    # Model 2: SARIMA Baseline
    # ---------------------------------------------------------------------------
    print("\nFitting SARIMA model...", flush=True)
    sarima_model = SARIMAX(
        train_df["total_demand"],
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 7),
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    sarima_fit = sarima_model.fit(disp=False)
    sarima_test_preds = sarima_fit.forecast(steps=15).values

    sarima_rmse = root_mean_squared_error(y_test, sarima_test_preds)
    sarima_mae = mean_absolute_error(y_test, sarima_test_preds)
    print(f"SARIMA  -> RMSE: {sarima_rmse:.2f}, MAE: {sarima_mae:.2f}", flush=True)

    # ---------------------------------------------------------------------------
    # Save Model Comparison Table
    # ---------------------------------------------------------------------------
    comparison_df = pd.DataFrame([
        {"model": "Prophet", "RMSE": round(prophet_rmse, 2), "MAE": round(prophet_mae, 2)},
        {"model": "SARIMA", "RMSE": round(sarima_rmse, 2), "MAE": round(sarima_mae, 2)},
    ])

    comp_path = PROC_DIR / "model_comparison.csv"
    comparison_df.to_csv(comp_path, index=False)
    print(f"\nSaved model comparison metrics to {comp_path}", flush=True)

    # ---------------------------------------------------------------------------
    # Save Forecast Comparison Plot
    # ---------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot train context & actual test values
    ax.plot(train_df["date"], train_df["total_demand"], color="#444444", label="Train Demand (Actual)", linewidth=1.5)
    ax.plot(test_df["date"], test_df["total_demand"], color="black", label="Test Demand (Actual)", linewidth=2.5, marker="o")

    # Plot predictions
    ax.plot(test_df["date"], prophet_test_preds, color="#d95f02", label=f"Prophet Forecast (RMSE: {prophet_rmse:.1f})", linewidth=2, linestyle="--")
    ax.plot(test_df["date"], sarima_test_preds, color="#7570b3", label=f"SARIMA Forecast (RMSE: {sarima_rmse:.1f})", linewidth=2, linestyle=":")

    ax.set_title("Fig 5: Bhubaneswar Citywide Transit Demand Forecast Comparison (Prophet vs SARIMA)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Daily Demand Proxy")
    ax.legend(loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=20)
    plt.tight_layout()

    fig_path = REPORTS_DIR / "05_forecast_comparison.png"
    fig.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved forecast comparison plot to {fig_path}", flush=True)

    print("\nForecasting pipeline execution complete!", flush=True)


if __name__ == "__main__":
    main()
