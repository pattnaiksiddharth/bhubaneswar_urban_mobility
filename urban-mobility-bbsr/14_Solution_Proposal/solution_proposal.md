# Solution Proposal

## Executive Summary
This project presents a data-driven evaluation of Bhubaneswar's public transport corridor network to assist Capital Region Urban Transport (CRUT) in optimizing service frequencies and expanding transit coverage. By integrating geospatial network centrality, synthetic demand modeling, financial cost-benefit estimation, and environmental impact analysis, this framework identifies priority corridors where frequency enhancements would yield the greatest combined social, financial, and ecological return.

Across a network of **73 analyzed routes**, **22 routes** were flagged for service frequency increases. Implementing an additional 4 round trips per day on these flagged corridors is estimated to produce a citywide net daily financial impact of **−₹38,153.97** (accounting for operational costs versus incremental revenue captured across high- and lower-demand routes) while removing approximately **179.58 kg of CO2 daily**, scaling to **65,545.90 kg of annual CO2 savings**.

## Proposed Solution
A repeatable analytical framework (this project) that:
1. Models stop-level transit demand using real road network and points-of-interest data, in the absence of public ridership data.
2. Flags routes where service frequency likely does not match modeled demand.
3. Cross-references those flags against road network congestion risk (betweenness centrality on real OSM data).
4. Forecasts near-term citywide demand using Prophet (selected over SARIMA based on lower RMSE/MAE on a 15-day test period: 54.89/44.31 vs 63.85/50.77).
5. Quantifies the financial and environmental cost/benefit of addressing each flagged route.
6. Delivers all findings via an interactive Power BI dashboard and a SQL-queryable dataset, so both non-technical and technical stakeholders can engage with the findings.

## Top Priority Routes
The following routes are both flagged "Increase Frequency" *and* located near one of the city's top 20 highest-centrality (most congestion-prone) road junctions — making them the highest-priority candidates for service investment:

| Route ID | Total Daily Demand | Net Daily Benefit | ROI Ratio | Near Congestion |
|---|---|---|---|---|
| R_SYN002 | 1,509 | −₹73 | 0.98 | True |
| R_SYN043 | 813 | −₹1,562 | — | True |
| R_SYN017 | 696 | −₹1,454 | 0.52 | True |
| R_SYN018 | 406 | −₹459 | 0.67 | True |
| R_SYN054 | 232 | −₹2,182 | — | True |
| R_SYN055 | 232 | −₹2,447 | — | True |

**Headline recommendation**: **R_SYN002** stands out as the strongest candidate for immediate action — it has the highest demand among all flagged routes (1,509 riders/day) and is nearly break-even on a standalone financial basis (−₹73/day, ROI ratio 0.98). It represents the lowest-risk, highest-impact starting point for a phased rollout, rather than committing to all 22 flagged routes simultaneously.

## Phased Rollout Recommendation
Given that the full 22-route rollout is net financially negative under current assumptions, a phased approach is recommended:
- **Phase 1**: Implement frequency increases on the routes with the best (least negative or positive) ROI ratio first — starting with R_SYN002 — to validate real-world ridership capture against the model's 15% assumption before scaling further.
- **Phase 2**: Reassess remaining flagged routes using actual Phase 1 results to refine the demand-capture and cost assumptions.
- **Phase 3**: Extend to lower-ROI routes only if justified by updated environmental/social value assessments (e.g., if CO2 reduction is formally valued by BSCL's sustainability budget).

## Methodology & Assumptions (Full List)
- **Demand modeling**: 73 synthetic stops generated from real OpenStreetMap road network + POI data (hospitals, colleges, malls, marketplaces, transit hubs), clustered via DBSCAN and weighted by estimated trip-generation potential.
- **Demand curves**: Hour-of-day and day-of-week patterns applied per POI type (documented limitation: "always-on" POI types like hospitals accumulate higher total daily demand than "peaked" types like colleges, even when peak-hour demand is lower — see `05_Python_EDA` notes).
- **Congestion**: Road network betweenness centrality computed on real OSM road graph; top 20 nodes used as congestion-risk proxy.
- **Cost assumption**: ₹65/km operating cost (based on published Indian STU diesel bus figures, e.g. BMTC ~₹68.53/km).
- **Service increase assumption**: +4 additional round trips/day per flagged route.
- **Fare assumption**: ₹15/rider (typical flat-fare range for Indian city bus systems).
- **Demand capture assumption**: 15% of unmet demand proxy captured as new riders — a conservative estimate, not empirically derived.
- **Mode-shift assumption**: 20% of new riders shift from private vehicles (car/two-wheeler) rather than being net-new trips.
- **Emissions factors**: Private vehicle ≈100 gCO2/km/passenger (blended car/two-wheeler); bus ≈25 gCO2/km/passenger (diesel, ~40 occupancy); average trip distance assumed at 6 km.

## Limitations
- This analysis uses **synthetic demand data**, since real Mo Bus/CRUT ridership data is not publicly available. All findings should be validated against real CRUT operational data (ticketing, ITS records) before any operational or budget decision is made.
- No direct stakeholder interviews were conducted; stakeholder needs and the As-Is process are inferred (see `02_Stakeholder_Analysis` and `08_As_Is_Process`).
- Cost, fare, and mode-shift figures are reasonable published-reference or conservative assumptions, not CRUT's actual figures.

## Next Steps
1. Share this framework and Phase 1 recommendation (R_SYN002) with CRUT planning stakeholders for validation.
2. If real ridership/cost data becomes available, re-run the pipeline (all scripts are reproducible and documented) to replace synthetic assumptions with real figures.
3. Expand the congestion data source beyond road network centrality to real traffic data, if accessible, for a more precise congestion-risk signal.