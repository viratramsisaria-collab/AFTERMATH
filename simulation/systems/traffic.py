
"""Traffic and mobility simulation system."""

import random

from simulation.state import CityState


def update_traffic(
    state: CityState,
    rng: random.Random,
) -> dict:
    if not state.roads:
        return {
            "average_congestion": 0.0,
            "mobility": state.metrics.mobility,
        }

    population_pressure = min(
        1.0,
        state.population / 200_000,
    )

    total_congestion = 0.0

    for road in state.roads:
        if not road.operational:
            road.congestion = 100.0
            total_congestion += road.congestion
            continue

        capacity_factor = max(0.35, road.lanes / 4)

        pressure = population_pressure * 2.5 / capacity_factor

        variation = rng.uniform(-2.0, 2.0)

        road.congestion = max(
            0.0,
            min(
                100.0,
                road.congestion + pressure - 0.8 + variation,
            ),
        )

        total_congestion += road.congestion

    average = total_congestion / len(state.roads)

    state.metrics.traffic_congestion = round(average, 2)

    state.metrics.mobility = round(
        max(0.0, min(100.0, 100.0 - average)),
        2,
    )

    return {
        "average_congestion": round(average, 2),
        "mobility": state.metrics.mobility,
        "roads_updated": len(state.roads),
    }
