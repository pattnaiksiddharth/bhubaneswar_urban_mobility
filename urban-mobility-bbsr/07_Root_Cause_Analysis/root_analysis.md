# Root Cause Analysis

## Problem Restated
Bus service frequency across Bhubaneswar's Mo Bus network appears (based on this project's demand modeling) to be misaligned with actual demand in several corridors — some high-demand stops are likely under-served, while service capacity may be better matched elsewhere.

## Method
A simplified 5-Whys approach is used below, informed by general knowledge of Indian city transit operations and the patterns observed in this project's synthetic demand/route flagging (22 of 73 routes flagged "Increase Frequency"; 6 of those also sit near high-congestion road junctions).

## 5-Whys Analysis

**Why is service frequency misaligned with demand in some corridors?**
→ Because frequency allocation decisions are not driven by a systematic, quantified demand model.

**Why isn't frequency allocation driven by a quantified demand model?**
→ Because granular ridership data (boardings per stop, per hour) is not captured or is not analyzed at that level of detail — CRUT's ITS system tracks broad travel patterns but this project found no public evidence of stop-level, model-driven frequency optimization.

**Why isn't granular ridership data used for stop-level planning?**
→ Likely a combination of: (a) data collection infrastructure captures ridership but analytical tooling/capacity to convert it into route-level recommendations may be limited, and (b) route planning in fast-growing STUs (State Transport Undertakings) often evolves incrementally (adding routes/buses as the city expands) rather than through periodic full-network re-optimization.

**Why does route planning evolve incrementally rather than through re-optimization?**
→ Network re-optimization requires dedicated analytical resourcing, and in a rapidly expanding transit system (35 routes and growing), maintaining and extending existing service often takes priority over revisiting existing route frequencies.

**Why does extending service take priority over re-optimization?**
→ Because visible service gaps (unserved areas) are more immediately apparent and politically/operationally urgent than frequency mismatches on already-served routes, which are harder to detect without dedicated analysis — which is precisely the gap this project's flagging framework is designed to fill.

## Root Cause Summary
The core root cause is **the absence of a lightweight, repeatable, data-driven method to detect demand-frequency mismatches on existing routes**, not a lack of underlying data collection capability. CRUT's ITS system reportedly does track travel patterns; the gap is in analytical translation of that data into prioritized, quantified route recommendations — which is the exact function this project's pipeline (demand modeling → flagging → cost-benefit → congestion overlay) is intended to demonstrate as a reusable framework.

## Contributing Factors (Secondary)
- No public GTFS or open ridership dataset exists for Bhubaneswar, which limits both internal and external (academic, civic-tech) analysis of the network.
- Road congestion and transit demand are typically analyzed by different teams/authorities (traffic police vs. transit operator), so overlap between the two (found in this project — 6 urgent routes near congestion points) may not be systematically cross-referenced in current planning.

## Note on Evidence Level
This root cause analysis is based on reasonable inference from public information about CRUT and general STU operational patterns, not internal CRUT process documentation or stakeholder interviews. It should be treated as a hypothesis to validate, not a confirmed diagnosis.