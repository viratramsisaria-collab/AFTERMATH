
"""Environmental and resource simulation system."""

import random

from simulation.state import CityState


def update_environment(
    state: CityState,
    rng: random.Random,
) -> dict:
    population = state.population

    energy_consumption = min(
        2.5,
        population / 100_000 * 0.65,
    )

    water_consumption = min(
        2.0,
        population / 100_000 * 0.55,
    )

    green_space_bonus = (
        sum(d.green_space for d in state.districts)
        / max(1, len(state.districts))
    ) * 0.015

    environmental_variation = rng.uniform(-0.4, 0.4)

    state.metrics.energy_reserve = max(
        0.0,
        state.metrics.energy_reserve - energy_consumption
        + rng.uniform(0.05, 0.2),
    )

    state.metrics.water_reserve = max(
        0.0,
        state.metrics.water_reserve - water_consumption
        + rng.uniform(0.05, 0.15),
    )

    resource_health = (
        state.metrics.energy_reserve * 0.35
        + state.metrics.water_reserve * 0.35
        + state.metrics.environmental_health * 0.30
    )

    state.metrics.environmental_health = round(
        max(
            0.0,
            min(
                100.0,
                state.metrics.environmental_health
                + green_space_bonus
                + environmental_variation,
            ),
        ),
        2,
    )

    if state.metrics.energy_reserve < 20:
        state.add_event("Energy reserves critically low.")

    if state.metrics.water_reserve < 20:
        state.add_event("Water reserves critically low.")

    return {
        "energy_consumption": round(energy_consumption, 2),
        "water_consumption": round(water_consumption, 2),
        "resource_health": round(resource_health, 2),
        "environmental_health": state.metrics.environmental_health,
    }
