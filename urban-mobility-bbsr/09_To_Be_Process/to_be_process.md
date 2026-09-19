# To-Be Process: Data-Driven Route & Frequency Optimization

## Purpose
This document describes the proposed future-state process, incorporating the analytical framework demonstrated in this project, to address the gaps identified in the As-Is Process and Root Cause Analysis.

## To-Be Process Flow

1. **Periodic Demand Data Refresh**
   Ridership/boarding data (ideally real, from ITS/ticketing systems; synthetic/proxy-based where real data is unavailable) is aggregated at the stop level on a regular cycle (e.g., quarterly).

2. **Demand Modeling & Hotspot Identification**
   Stop-level demand is quantified and ranked (as demonstrated via the POI-weighted demand model in this project), identifying high-demand zones independent of current service levels.

3. **Service-vs-Demand Gap Flagging**
   Current route frequency is compared against modeled demand to flag mismatches — routes that are under-served relative to demand ("Increase Frequency"), adequately served, or over-served relative to demand.

4. **Congestion Cross-Reference**
   Flagged routes are cross-referenced against road network congestion data (e.g., centrality analysis on the road graph, or real traffic data if available) to identify routes where service gaps and congestion risk overlap — these become top priority.

5. **Cost-Benefit & Environmental Impact Scoring**
   For each flagged route, estimate the operational cost of a frequency increase, the likely revenue/ridership gain, and the environmental impact (CO2 reduction from mode shift) — enabling ranked prioritization by ROI and/or public benefit, not just demand alone.

6. **Prioritized Recommendation & Business Case**
   Output a ranked list of routes (e.g., Top 10 by net benefit or by demand+congestion overlap) packaged as a business case for CRUT decision-makers, including financial trade-offs (subsidy required vs. CO2 benefit).

7. **Stakeholder Review & Decision**
   CRUT planning team reviews the prioritized recommendations, validates against real operational knowledge (driver feedback, fleet constraints, budget), and approves a subset for implementation.

8. **Implementation & Feedback Loop**
   Approved frequency changes are implemented; results (actual ridership change, cost incurred) are monitored and fed back into the next cycle's demand model — closing the loop that was missing in the As-Is process.

## To-Be Process Diagram (Text Representation)

```
[Periodic Demand Data Refresh]
            ↓
[Demand Modeling & Hotspot Identification]
            ↓
[Service-vs-Demand Gap Flagging]
            ↓
[Congestion Cross-Reference]
            ↓
[Cost-Benefit & Environmental Impact Scoring]
            ↓
[Prioritized Recommendation / Business Case]
            ↓
[Stakeholder Review & Decision]
            ↓
[Implementation] → feeds back into → [Periodic Demand Data Refresh]
(Closed feedback loop, unlike As-Is)
```

## What This Project Demonstrates vs. What a Real Deployment Would Need

| This Project (Proof of Concept) | Real CRUT Deployment Would Need |
|---|---|
| Synthetic demand model (POI-based proxy) | Real ridership data from ticketing/ITS systems |
| One-time analysis snapshot | Recurring quarterly (or similar) refresh cycle |
| Static dashboard | Dashboard connected to live/updated data sources |
| Assumed cost/fare figures | CRUT's actual operating cost and fare structure |
| No stakeholder validation | Review cycle with CRUT planning team and drivers |

## Benefit of Moving From As-Is to To-Be
- Replaces reactive, complaint-driven adjustment with proactive, quantified prioritization.
- Connects previously siloed data (transit demand and road congestion) into one decision framework.
- Gives CRUT a defensible, repeatable business case for budget requests tied to frequency increases, rather than ad-hoc justification.