# Functional Requirements

Each functional requirement (FR) traces back to a Business Requirement (BR) from `10_BRD.md`.

| ID | Functional Requirement | Traces To | Implemented By |
|---|---|---|---|
| FR-01 | The system shall compute a demand score per stop, derived from weighted nearby points-of-interest (hospitals, colleges, malls, marketplaces, transit hubs). | BR-01 | `src/features/build_synthetic_network.py` |
| FR-02 | The system shall rank stops into demand quartiles (Q1–Q4). | BR-01 | `src/models/route_optimization.py` |
| FR-03 | The system shall compute betweenness centrality on the real road network to identify the top 20 congestion-risk junctions. | BR-02 | `src/viz/spatial_eda.py` |
| FR-04 | The system shall flag a route "near congestion" if its stop is within 500m of a top-20 centrality node. | BR-02 | `src/models/route_optimization.py` |
| FR-05 | The system shall classify each route into one of: Increase Frequency, Well-Served, Adequate, based on demand quartile and assigned current frequency. | BR-01, BR-03 | `src/models/route_optimization.py` |
| FR-06 | The system shall calculate additional daily operating cost for a flagged route using route length, an assumed per-km cost, and an assumed additional trip count. | BR-04 | `src/business/cost_benefit_analysis.py` |
| FR-07 | The system shall calculate additional daily revenue using an assumed ridership capture rate and fare. | BR-05 | `src/business/cost_benefit_analysis.py` |
| FR-08 | The system shall calculate net daily benefit and ROI ratio per flagged route. | BR-06 | `src/business/cost_benefit_analysis.py` |
| FR-09 | The system shall estimate daily and annual CO2 savings using an assumed mode-shift rate and emissions factors. | BR-07 | `src/business/environmental_impact.py` |
| FR-10 | The system shall generate a 60-day synthetic daily demand series with weekly seasonality and trend. | BR-08 | `src/models/build_timeseries.py` |
| FR-11 | The system shall forecast the final 15 days of the demand series using both Prophet and SARIMA, and report RMSE/MAE for each. | BR-08 | `src/models/forecast_demand.py` |
| FR-12 | The system shall present stop-level demand, route flags, and congestion points on an interactive geographic map. | BR-09 | Power BI Dashboard, Page 1–2 |
| FR-13 | The system shall present forecast results (actual vs. predicted) as an interactive time-series chart. | BR-09 | Power BI Dashboard, Page 3 |
| FR-14 | The system shall present cost-benefit and environmental impact results in a business-case-formatted page, including a ranked priority table. | BR-09 | Power BI Dashboard, Page 4 |
| FR-15 | The system shall allow users to filter all dashboard pages by route classification (Increase Frequency / Adequate / Well-Served) via a synced slicer. | BR-09 | Power BI Dashboard (cross-page slicer) |
| FR-16 | The system shall expose the final dataset as SQL-queryable tables for ad-hoc analysis beyond the dashboard. | BR-09 (extension) | `src/sql/build_database.py` |
| FR-17 | The system shall document every modeling assumption (demand weighting, cost, fare, emissions, capture rates) in an accessible reference document. | BR-10 | `14_Solution_Proposal`, `10_BRD` §5 |

## Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-01 | The dashboard must load and render within a Power BI Desktop session without requiring external live data connections (fully self-contained from exported CSVs). |
| NFR-02 | All Python scripts must be reproducible: re-running them with the same inputs should produce the same outputs (fixed random seeds used, e.g. seed=42 for frequency assignment). |
| NFR-03 | All synthetic/assumed data must be clearly distinguishable from real data (OSM road network, real POIs) in project documentation. |
| NFR-04 | The project's folder structure and documentation must be understandable by a reader unfamiliar with the original analysis (i.e., self-documenting via README and this BA folder structure). |