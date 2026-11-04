
"""Population and community wellbeing simulation system."""

import random

from simulation.state import CityState


def update_population(
    state: CityState,
    rng: random.Random,
) -> dict:
    total_population_change = 0
    district_results = []

    for district in state.districts:
        previous_population = district.population

        wellbeing = (
            district.happiness * 0.35
            + district.safety * 0.20
            + district.healthcare_access * 0.20
            + district.wealth_index * 0.15
            + (100.0 - district.stress) * 0.10
        )

        # Small, bounded synthetic daily growth.
        growth_rate = (wellbeing - 60.0) / 100_000

        variation = rng.uniform(-0.00015, 0.00015)

        growth = growth_rate + variation

        population_change = round(
            district.population * growth
        )

        district.population = max(
            0,
            district.population + population_change,
        )

        total_population_change += (
            district.population - previous_population
        )

        # Stress responds to environmental and mobility pressure.
        congestion_pressure = (
            state.metrics.traffic_congestion - 40
        ) * 0.025

        district.stress = max(
            0.0,
            min(
                100.0,
                district.stress
                + congestion_pressure
                + rng.uniform(-0.3, 0.3),
            ),
        )

        district.happiness = max(
            0.0,
            min(
                100.0,
                district.happiness
                + (wellbeing - district.happiness) * 0.025
                - congestion_pressure * 0.2,
            ),
        )

        district_results.append({
            "district_id": district.id,
            "population_change": district.population - previous_population,
            "happiness": round(district.happiness, 2),
            "stress": round(district.stress, 2),
        })

    if state.districts:
        average_happiness = sum(
            district.happiness for district in state.districts
        ) / len(state.districts)

        average_stress = sum(
            district.stress for district in state.districts
        ) / len(state.districts)

        state.metrics.happiness = round(
            average_happiness,
            2,
        )

        state.metrics.public_wellbeing = round(
            max(
                0.0,
                min(100.0, average_happiness - average_stress * 0.12),
            ),
            2,
        )

        state.metrics.safety = round(
            sum(d.safety for d in state.districts)
            / len(state.districts),
            2,
        )

        state.metrics.healthcare_access = round(
            sum(d.healthcare_access for d in state.districts)
            / len(state.districts),
            2,
        )

        state.metrics.social_equity = round(
            100.0 - (
                max(d.wealth_index for d in state.districts)
                - min(d.wealth_index for d in state.districts)
            ),
            2,
        )

    return {
        "population_change": total_population_change,
        "population": state.population,
        "districts_updated": len(district_results),
        "district_results": district_results,
    }
