"""
Stakeholder Recommendation Report Generator for Bhubaneswar Urban Mobility Analytics.

Compiles data-analyst flags, cost-benefit analysis, environmental impact, and network centrality
into an executive-level recommendation report for CRUT (Capital Region Urban Transport).
"""

import os
import json
import pandas as pd

def run_stakeholder_report():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    flags_path = os.path.join(base_dir, "03_Data", "processed", "route_optimization_flags.csv")
    cba_path = os.path.join(base_dir, "03_Data", "dashboard", "cost_benefit_analysis.csv")
    env_path = os.path.join(base_dir, "03_Data", "dashboard", "environmental_impact.csv")
    geojson_path = os.path.join(base_dir, "03_Data", "processed", "high_centrality_nodes.geojson")
    report_path = os.path.join(base_dir, "reports", "stakeholder_recommendation_report.md")

    # Load datasets
    flags_df = pd.read_csv(flags_path)
    cba_df = pd.read_csv(cba_path)
    env_df = pd.read_csv(env_path)

    with open(geojson_path, "r", encoding="utf-8") as f:
        centrality_data = json.load(f)

    # Compute aggregate metrics
    total_routes_analyzed = len(flags_df)
    flagged_routes_count = len(cba_df)
    total_net_daily_benefit = cba_df["net_daily_benefit"].sum()
    total_annual_co2_saved = env_df["annual_co2_saved_kg"].sum()
    total_daily_co2_saved = env_df["daily_co2_saved_kg"].sum()

    # Merge data for Top 5 Priority Routes table
    merged = pd.merge(
        cba_df,
        flags_df[["route_id", "dominant_type", "total_daily_demand", "near_congestion_point"]],
        on="route_id",
        how="left"
    )

    # Sort by net_daily_benefit descending
    top5_df = merged.sort_values(by="net_daily_benefit", ascending=False).head(5)

    # Build Top 5 Markdown Table
    top5_table_rows = []
    top5_table_rows.append("| route_id | dominant_type | total_daily_demand | net_daily_benefit | roi_ratio | near_congestion_point |")
    top5_table_rows.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for _, row in top5_df.iterrows():
        route_id = row["route_id"]
        dom_type = row["dominant_type"]
        demand = f"{row['total_daily_demand']:.2f}"
        net_benefit = f"{row['net_daily_benefit']:.2f}"
        roi = f"{row['roi_ratio']:.4f}"
        near_cong = str(row["near_congestion_point"])
        top5_table_rows.append(f"| {route_id} | {dom_type} | {demand} | {net_benefit} | {roi} | {near_cong} |")
    top5_table_md = "\n".join(top5_table_rows)

    # Construct report content
    report_md = f"""# Bhubaneswar Public Transport Optimization: Recommendations for CRUT

## Executive Summary

This report presents a comprehensive data-driven evaluation of Bhubaneswar's public transport corridor network to assist Capital Region Urban Transport (CRUT) in optimizing service frequencies and expanding transit coverage. Integrating geospatial network centrality, synthetic demand modeling, financial cost-benefit estimation, and environmental impact analysis, this decision framework identifies high-priority corridors where frequency enhancements yield the greatest social, financial, and ecological returns.

Across the network of **{total_routes_analyzed} analyzed routes**, **{flagged_routes_count} routes** have been flagged for service frequency increases. Implementing an additional 4 round trips per day on these flagged corridors results in an estimated citywide net daily financial benefit of **Rs {total_net_daily_benefit:,.2f}** (accounting for operational costs versus incremental revenue captured across high-demand vs lower-demand routes) and removes approximately **{total_daily_co2_saved:,.2f} kg of CO2 daily**, scaling to **{total_annual_co2_saved:,.2f} kg of annual CO2 savings**.

## Top 5 Priority Routes

The table below highlights the top 5 corridor interventions prioritized by net daily financial benefit (sorted descending). These corridors represent high-demand origin-destination nodes anchored by major healthcare, commercial, and transport hubs.

{top5_table_md}

## Methodology & Assumptions

To maintain full transparency and methodological rigor across the urban mobility analytics pipeline, the underlying modeling frameworks and parameters are documented below:

1. **Synthetic Stop Generation & Spatial Coverage**:
   - 75 synthetic transit stops were generated across the urban core of Bhubaneswar (spanning key hospital, university, commercial, rail, and bus transit hubs) to construct a realistic origin-destination topology in the absence of open GTFS feeds.

2. **Demand Weighting & Temporal Profiling**:
   - Stop-level demand is weighted based on Point of Interest (POI) dominant types (e.g., healthcare facilities, inter-city bus stations, railway stations, and educational campuses).
   - Demand profiles incorporate hourly peak/off-peak distributions to simulate real-world commuter dynamics.

3. **Operating Cost Benchmark**:
   - Operating cost is estimated at **Rs 65 per km**, derived from published Indian State Transport Undertaking (STU) diesel bus fleet benchmarks (e.g., BMTC operational cost ~Rs 68.53/km). Note: This serves as an industry proxy and does not reflect actual CRUT/Mo Bus internal financial ledgers.

4. **Service Frequency & Revenue Assumptions**:
   - **Service Increase**: Flagged routes receive +4 additional round trips per day (`additional_daily_km = route_length_km * 4 * 2`).
   - **Average Fare**: Assumed flat fare of **Rs 15 per rider**, typical for intra-city municipal bus systems in India.
   - **Ridership Capture**: Service frequency enhancement is conservatively assumed to capture **15% of unmet stop-level demand** as new riders (`estimated_new_riders = total_daily_demand * 0.15`).

5. **Environmental Impact & Mode-Shift Modeling**:
   - **Mode-Shift Rate**: Assumes **20% of new riders** are modal shifters from private motor vehicles (cars and two-wheelers), rather than induced new trips.
   - **Trip Length**: Average intra-city trip distance is set to **6 km**.
   - **Emissions Factors**: Private motorized transport is benchmarked at **100 g CO2/km per passenger** (blended average), compared to **25 g CO2/km per passenger** for diesel buses (assuming ~40 passenger average occupancy), yielding a net saving of **75 g CO2/km** per shifted passenger.

## Limitations

- **Synthetic Data Scope**: This model utilizes synthetically generated demand distributions and POI proxy weights due to the lack of publicly available real-time ridership data for Mo Bus services.
- **Operational Validation Required**: While the pipeline provides robust structural recommendations, all cost-benefit estimates, ROI ratios, and schedule modifications must be validated against internal CRUT operational benchmarks, actual ticketing/E-ticketing revenue data, and real bus fleet deployment constraints prior to operational implementation.
"""

    # Save to reports/stakeholder_recommendation_report.md
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    # Calculate word count and line count
    lines = report_md.strip().split("\n")
    words = report_md.split()

    print(f"Stakeholder recommendation report created at {report_path}")
    print(f"Report metrics: {len(lines)} lines, {len(words)} words")

if __name__ == "__main__":
    run_stakeholder_report()
