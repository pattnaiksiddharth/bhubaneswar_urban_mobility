# Business Problem

## Context
Bhubaneswar's public bus network, operated by the Capital Region Urban Transport (CRUT) under the Mo Bus / Ama Bus brand, serves over 1.7 lakh riders daily across 35 routes and roughly 265 buses. The network has expanded rapidly to cover Bhubaneswar, Cuttack, Khordha, Puri, Konark, and surrounding areas. However, route and frequency planning decisions have historically relied on operational experience and ad-hoc adjustments rather than systematic, data-driven demand analysis.

## Problem Statement
CRUT does not currently have a public, data-driven method for identifying where bus service frequency is mismatched with actual or likely rider demand, and where that mismatch overlaps with the city's most congestion-prone road corridors. As a result:

- Some high-demand areas (near hospitals, colleges, and commercial hubs) may be under-served relative to their trip-generation potential.
- Frequency increases, where needed, are not prioritized using a consistent, quantifiable framework that weighs demand, cost, and congestion risk together.
- There is no readily available estimate of the financial (cost vs. fare revenue) or environmental (CO2 reduction) impact of service changes, which limits CRUT's ability to build a business case for specific route investments.

## Why This Matters
- **Rider experience**: Under-served high-demand stops likely mean overcrowding, long wait times, and reduced transit reliability — pushing riders toward private vehicles.
- **Congestion**: Bhubaneswar's key arterial junctions (e.g., Janpath/Vani Vihar, Jaydev Vihar/NH-16, Acharya Vihar/NH-16, Kalpana Square) already experience high traffic stress; under-optimized bus routing near these points compounds congestion rather than relieving it.
- **Sustainability**: Odisha's Smart City and urban mobility goals benefit from measurable mode-shift from private vehicles to public transit, which requires targeted, defensible service investment.
- **Financial planning**: CRUT, like most Indian city transit operators, balances public subsidy against fare revenue. Prioritizing frequency increases without cost-benefit context risks inefficient spending.

## Objective of This Analysis
To build a reproducible, data-driven framework that:
1. Identifies public transport demand patterns across Bhubaneswar using available open data and defensible modeling assumptions (given the absence of public real-time ridership data).
2. Flags routes where current service frequency likely does not match demand.
3. Cross-references those routes against road network congestion risk.
4. Forecasts near-term demand trends to support planning.
5. Quantifies the estimated cost, revenue, and environmental impact of addressing the top-priority gaps.
6. Delivers findings as an interactive dashboard and a structured business case usable by CRUT or similar stakeholders.

## Key Constraint
Real Mo Bus ridership and schedule (GTFS) data is not publicly available at the granularity required for this analysis. This project therefore uses a **documented synthetic demand model** built on real road network data (OpenStreetMap) and real points-of-interest data (hospitals, colleges, malls, transit hubs) as a proxy for ridership demand. All financial and environmental estimates are based on stated assumptions (see `10_BRD` and `15_Business_Impact` for full assumption list) and should be validated against real CRUT operational data before any operational decision is made.