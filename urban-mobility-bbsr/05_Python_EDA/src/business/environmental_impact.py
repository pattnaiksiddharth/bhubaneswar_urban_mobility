"""
Environmental Impact Analysis for Bhubaneswar Urban Mobility Analytics.

Estimates CO2 emissions savings resulting from public transport mode-shift
on routes recommended for frequency increases.

Assumptions (documented as model assumptions):
- Mode shift rate: 20% of estimated_new_riders are shifting from private vehicles (car/two-wheeler) rather than induced new trips
- Average intra-city trip distance: 6 km
- Emission factor - Private vehicles: 100 g CO2/km per passenger (blended car/two-wheeler average)
- Emission factor - Diesel bus: 25 g CO2/km per passenger (~40 occupancy average)
- Net emission reduction per shifted passenger-km: 75 g CO2/km (100 - 25 g CO2/km)
"""

import os
import pandas as pd

def run_environmental_impact():
    # Define file paths relative to script location or project root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    cba_path = os.path.join(base_dir, "03_Data", "dashboard", "cost_benefit_analysis.csv")
    output_path = os.path.join(base_dir, "03_Data", "dashboard", "environmental_impact.csv")

    # Load cost benefit analysis data
    cba_df = pd.read_csv(cba_path)

    # Documented Assumptions:
    MODE_SHIFT_PCT = 0.20
    AVG_TRIP_KM = 6.0
    PRIVATE_VEHICLE_EMISSION_G = 100.0  # g CO2/km per passenger
    BUS_EMISSION_G = 25.0               # g CO2/km per passenger
    NET_SAVING_G_PER_KM = PRIVATE_VEHICLE_EMISSION_G - BUS_EMISSION_G  # 75 g CO2/km

    # 1. shifted_riders = estimated_new_riders * 0.20
    cba_df["shifted_riders"] = cba_df["estimated_new_riders"] * MODE_SHIFT_PCT

    # 2. daily_co2_saved_kg = (shifted_riders * 6 * (100-25)) / 1000
    cba_df["daily_co2_saved_kg"] = (cba_df["shifted_riders"] * AVG_TRIP_KM * NET_SAVING_G_PER_KM) / 1000.0

    # 3. annual_co2_saved_kg = daily_co2_saved_kg * 365
    cba_df["annual_co2_saved_kg"] = cba_df["daily_co2_saved_kg"] * 365.0

    # Select required columns
    output_cols = [
        "route_id",
        "shifted_riders",
        "daily_co2_saved_kg",
        "annual_co2_saved_kg"
    ]
    result_df = cba_df[output_cols]

    # Save to data/dashboard/environmental_impact.csv
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result_df.to_csv(output_path, index=False)
    print(f"Environmental impact saved to {output_path} ({len(result_df)} routes processed)")

    # Print total citywide daily_co2_saved_kg and annual_co2_saved_kg
    total_daily = result_df["daily_co2_saved_kg"].sum()
    total_annual = result_df["annual_co2_saved_kg"].sum()

    print(f"Total citywide daily CO2 saved: {total_daily:.2f} kg")
    print(f"Total citywide annual CO2 saved: {total_annual:.2f} kg")

if __name__ == "__main__":
    run_environmental_impact()
