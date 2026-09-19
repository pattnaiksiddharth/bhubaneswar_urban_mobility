"""
build_database.py
-----------------
Loads all CSV files from data/dashboard/ into a SQLite database at
04_SQL_Analysis/bhubaneswar_mobility.db. Each CSV becomes a table
with the same name. Run from the project root directory.
"""

import os
import sqlite3
import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR     = os.path.join(PROJECT_ROOT, "03_Data", "dashboard")
DB_DIR       = os.path.join(PROJECT_ROOT, "04_SQL_Analysis")
DB_PATH      = os.path.join(DB_DIR, "bhubaneswar_mobility.db")

# ── Table list ────────────────────────────────────────────────────────────────
TABLES = [
    "dim_stops",
    "dim_routes",
    "fact_hourly_demand",
    "fact_daily_forecast",
    "cost_benefit_analysis",
    "environmental_impact",
    "top_congestion_points",
]

def build_database() -> None:
    # Ensure output directory exists
    os.makedirs(DB_DIR, exist_ok=True)

    # Remove stale database so we always get a fresh build
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"[INFO] Removed existing database: {DB_PATH}\n")

    conn = sqlite3.connect(DB_PATH)

    print("=" * 60)
    print("  Building Bhubaneswar Mobility SQLite Database")
    print("=" * 60)

    for table in TABLES:
        csv_path = os.path.join(DATA_DIR, f"{table}.csv")
        if not os.path.exists(csv_path):
            print(f"[WARN] CSV not found, skipping: {csv_path}")
            continue

        df = pd.read_csv(csv_path)
        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f"  OK  Table '{table}' created  -- {len(df):>5} rows")

    conn.close()

    print("\n" + "=" * 60)
    print(f"  Database saved to: {DB_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    build_database()
