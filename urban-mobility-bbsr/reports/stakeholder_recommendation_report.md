# Bhubaneswar Public Transport Optimization: Recommendations for CRUT

## Executive Summary

This report presents a comprehensive data-driven evaluation of Bhubaneswar's public transport corridor network to assist Capital Region Urban Transport (CRUT) in optimizing service frequencies and expanding transit coverage. Integrating geospatial network centrality, synthetic demand modeling, financial cost-benefit estimation, and environmental impact analysis, this decision framework identifies high-priority corridors where frequency enhancements yield the greatest social, financial, and ecological returns.

Across the network of **73 analyzed routes**, **22 routes** have been flagged for service frequency increases. Implementing an additional 4 round trips per day on these flagged corridors results in an estimated citywide net daily financial benefit of **Rs -38,153.97** (accounting for operational costs versus incremental revenue captured across high-demand vs lower-demand routes) and removes approximately **179.58 kg of CO2 daily**, scaling to **65,545.90 kg of annual CO2 savings**.

## Top 5 Priority Routes

The table below highlights the top 5 corridor interventions prioritized by net daily financial benefit (sorted descending). These corridors represent high-demand origin-destination nodes anchored by major healthcare, commercial, and transport hubs.

| route_id | dominant_type | total_daily_demand | net_daily_benefit | roi_ratio | near_congestion_point |
| :--- | :--- | :--- | :--- | :--- | :--- |
| R_SYN016 | hospital | 2785.88 | 2831.03 | 1.8236 | False |
| R_SYN009 | hospital | 841.54 | 208.66 | 1.1239 | False |
| R_SYN002 | hospital | 1509.02 | -73.11 | 0.9789 | True |
| R_SYN018 | hospital | 406.30 | -458.62 | 0.6659 | True |
| R_SYN062 | bus_station | 264.81 | -672.98 | 0.4696 | False |

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
