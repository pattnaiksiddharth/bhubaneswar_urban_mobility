"""
run_queries.py
--------------
Connects to the Bhubaneswar Mobility SQLite database, executes all
8 analysis queries from analysis_queries.sql, prints each result as
a formatted table, and saves all outputs to
04_SQL_Analysis/query_results.txt.

Run from the project root directory:
    py src/sql/run_queries.py
"""

import os
import sqlite3
import textwrap
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DB_PATH      = os.path.join(PROJECT_ROOT, "04_SQL_Analysis", "bhubaneswar_mobility.db")
SQL_PATH     = os.path.join(PROJECT_ROOT, "04_SQL_Analysis", "analysis_queries.sql")
OUTPUT_PATH  = os.path.join(PROJECT_ROOT, "04_SQL_Analysis", "query_results.txt")

# ── 8 named queries ───────────────────────────────────────────────────────────
QUERIES = {
    "Q1 – Top 10 Stops by Total Daily Demand": """
        SELECT
            stop_id,
            dominant_type,
            total_daily_demand,
            demand_quartile,
            primary_flag
        FROM dim_stops
        ORDER BY total_daily_demand DESC
        LIMIT 10;
    """,

    "Q2 – Route Count per Primary Flag Category": """
        SELECT
            primary_flag,
            COUNT(*) AS route_count
        FROM dim_routes
        GROUP BY primary_flag
        ORDER BY route_count DESC;
    """,

    "Q3 – Urgent Routes: Increase Frequency AND Near Congestion": """
        SELECT
            dr.route_id,
            dr.stop_id,
            dr.primary_flag,
            dr.near_congestion_point,
            ds.total_daily_demand,
            cba.net_daily_benefit
        FROM dim_routes AS dr
        JOIN dim_stops             AS ds  ON dr.stop_id  = ds.stop_id
        JOIN cost_benefit_analysis AS cba ON dr.route_id = cba.route_id
        WHERE dr.primary_flag        = 'Increase Frequency'
          AND dr.near_congestion_point = 1
        ORDER BY ds.total_daily_demand DESC;
    """,

    "Q4 – Average Net Daily Benefit by Primary Flag": """
        SELECT
            dr.primary_flag,
            ROUND(AVG(cba.net_daily_benefit), 2) AS avg_net_daily_benefit,
            COUNT(*) AS route_count
        FROM dim_routes            AS dr
        JOIN cost_benefit_analysis AS cba ON dr.route_id = cba.route_id
        GROUP BY dr.primary_flag
        ORDER BY avg_net_daily_benefit DESC;
    """,

    "Q5 – Network Summary: Total Cost, Revenue & Net Benefit": """
        SELECT
            COUNT(*)                                 AS total_routes,
            ROUND(SUM(additional_daily_cost),    2)  AS total_daily_cost,
            ROUND(SUM(additional_daily_revenue), 2)  AS total_daily_revenue,
            ROUND(SUM(net_daily_benefit),        2)  AS total_net_daily_benefit,
            ROUND(AVG(roi_ratio),                4)  AS avg_roi_ratio
        FROM cost_benefit_analysis;
    """,

    "Q6 – Total Demand by Dominant Land-Use Type (Ranked)": """
        SELECT
            dominant_type,
            ROUND(SUM(total_daily_demand), 2) AS total_demand,
            COUNT(*)                           AS stop_count,
            ROUND(AVG(total_daily_demand), 2) AS avg_demand_per_stop
        FROM dim_stops
        GROUP BY dominant_type
        ORDER BY total_demand DESC;
    """,

    "Q7 – Actual vs Prophet Forecast: Last 15 Days (Absolute Error)": """
        SELECT
            date,
            ROUND(actual_demand,    2) AS actual_demand,
            ROUND(prophet_forecast, 2) AS prophet_forecast,
            ROUND(ABS(actual_demand - prophet_forecast), 2) AS absolute_error
        FROM fact_daily_forecast
        WHERE prophet_forecast IS NOT NULL
        ORDER BY date DESC
        LIMIT 15;
    """,

    "Q8 – Top 5 Routes by ROI Ratio (Positive Net Benefit Only)": """
        SELECT
            cba.route_id,
            dr.stop_id,
            dr.primary_flag,
            ROUND(cba.roi_ratio,          4) AS roi_ratio,
            ROUND(cba.net_daily_benefit,  2) AS net_daily_benefit,
            ROUND(cba.additional_daily_cost, 2) AS daily_cost
        FROM cost_benefit_analysis AS cba
        JOIN dim_routes             AS dr ON cba.route_id = dr.route_id
        WHERE cba.net_daily_benefit > 0
        ORDER BY cba.roi_ratio DESC
        LIMIT 5;
    """,
}


def divider(title: str = "", width: int = 72) -> str:
    if title:
        pad  = (width - len(title) - 4) // 2
        return f"\n{'=' * pad}  {title}  {'=' * (width - pad - len(title) - 4)}\n"
    return "=" * width


def run_queries() -> None:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}.\n"
            "Run  py src/sql/build_database.py  first."
        )

    conn = sqlite3.connect(DB_PATH)

    # Widen pandas display so nothing gets truncated
    pd.set_option("display.max_columns",  20)
    pd.set_option("display.max_rows",    100)
    pd.set_option("display.width",       120)
    pd.set_option("display.float_format", "{:.2f}".format)

    lines = []           # collect all output for the text file

    header = textwrap.dedent(f"""
        {"=" * 72}
        BHUBANESWAR URBAN MOBILITY – SQL QUERY RESULTS
        Database : {DB_PATH}
        {"=" * 72}
    """)
    print(header)
    lines.append(header)

    for name, sql in QUERIES.items():
        section = divider(name)
        print(section)
        lines.append(section)

        df = pd.read_sql_query(textwrap.dedent(sql).strip(), conn)

        result_str = df.to_string(index=False)
        print(result_str)
        lines.append(result_str)

        row_note = f"\n  ({len(df)} row{'s' if len(df) != 1 else ''} returned)\n"
        print(row_note)
        lines.append(row_note)

    conn.close()

    # Save to file
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    footer = f"\n{'=' * 72}\nAll results saved to: {OUTPUT_PATH}\n{'=' * 72}"
    print(footer)


if __name__ == "__main__":
    run_queries()
