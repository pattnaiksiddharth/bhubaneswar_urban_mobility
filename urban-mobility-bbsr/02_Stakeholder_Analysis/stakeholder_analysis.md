# Stakeholder Analysis

## Purpose
This document identifies the individuals, groups, and organizations who have an interest in, influence over, or are affected by decisions related to Bhubaneswar's public transport service optimization. Understanding these stakeholders informs the requirements, priorities, and communication approach for this project.

## Stakeholder Map

| Stakeholder | Role / Interest | Influence | Impact of Project | Engagement Approach |
|---|---|---|---|---|
| **CRUT (Capital Region Urban Transport)** | Owns and operates Mo Bus / Ama Bus network; responsible for route planning, scheduling, budgets | High | Direct — primary decision-maker on any route/frequency changes | Primary audience for Solution Proposal, BRD, dashboard |
| **Bhubaneswar Smart City Ltd (BSCL)** | Drives Smart City initiatives, sustainability and mobility goals for the city | High | Indirect — policy and funding alignment (e.g., emissions targets) | Secondary audience; environmental impact findings most relevant |
| **Bus Commuters / Riders** | End users of the service; affected by frequency, wait times, overcrowding | Low (individually), Medium (collectively via feedback/complaints) | Direct — service quality outcome | Represented via demand modeling assumptions; not directly consulted in this project's scope |
| **Bus Drivers & Operations Staff** | Operate the service day-to-day; affected by schedule/route changes | Low | Indirect — workload/scheduling impact if frequency changes are implemented | Not directly consulted; flagged as a limitation |
| **Odisha State Transport Department** | Regulatory and funding oversight for state transit operators | Medium | Indirect — approval/funding for any operational changes | Not directly engaged; relevant for scaling recommendations |
| **City Traffic Police / Congestion Management Authorities** | Manage traffic flow at key junctions identified in this analysis | Medium | Indirect — congestion-point overlap is relevant to their planning too | Potential secondary stakeholder for congestion findings |
| **General Public / Private Vehicle Users** | Potential beneficiaries of mode-shift (less congestion, cleaner air) | Low | Indirect — long-term, if recommendations are implemented | Not directly consulted |
| **Project Analyst (You)** | Conducts the analysis, builds the dashboard, proposes recommendations | N/A | N/A | Delivers findings to CRUT/BSCL-equivalent audience |

## Stakeholder Prioritization (Power/Interest Grid)

- **High Power, High Interest (Manage Closely)**: CRUT — this analysis is built directly for their planning use case.
- **High Power, Lower Interest (Keep Satisfied)**: Bhubaneswar Smart City Ltd, Odisha State Transport Department — care about outcomes (sustainability, funding) more than day-to-day mechanics.
- **Low Power, High Interest (Keep Informed)**: Bus commuters — most affected by outcomes, but limited direct influence over CRUT's planning process in this project's scope.
- **Low Power, Lower Interest (Monitor)**: General public, private vehicle users — benefit indirectly if recommendations are adopted.

## Key Stakeholder Needs This Project Addresses
1. **CRUT** needs a prioritized, quantified list of which routes to invest additional frequency in, and why — addressed by the `primary_flag` classification, cost-benefit analysis, and Top Priority Routes table.
2. **CRUT / BSCL** need to understand the financial trade-off (subsidy required) versus environmental benefit (CO2 reduction) of service changes — addressed by `14_Solution_Proposal` and `15_Business_Impact`.
3. **Traffic management stakeholders** need visibility into where transit demand overlaps with already-congested corridors — addressed by the congestion analysis and interactive map.

## Limitation
This project was conducted as an independent analytical exercise without direct stakeholder interviews or CRUT operational data access. Stakeholder needs above are inferred from public information about CRUT's mandate and general urban transit planning priorities, not confirmed through direct consultation. A real-world engagement would begin with stakeholder interviews to validate these assumed priorities before analysis.