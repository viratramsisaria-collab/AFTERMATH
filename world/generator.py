
"""AFTERMATH procedural city generator."""

import random

from simulation.state import CityState, RoadSegment
from world.buildings import generate_buildings
from world.districts import generate_districts


CITY_CENTER_LAT = 40.754
CITY_CENTER_LON = -73.985

CITY_NAME = "NOVA YORK"
INITIAL_BUDGET = 2_500_000_000
BUILDINGS_PER_DISTRICT = 9


def generate_roads(
    districts,
    seed: int = 42,
) -> list[RoadSegment]:
    """Generate a connected collection of city road segments."""

    rng = random.Random(seed + 1000)
    roads = []

    ordered = sorted(
        districts,
        key=lambda district: district.center_lat,
    )

    # Ten horizontal connectors.
    for index in range(10):
        first = ordered[index]

        second = ordered[(index + 1) % len(ordered)]

        roads.append(
            RoadSegment(
                id=f"ROAD-H-{index + 1:02d}",
                name=f"Metropolitan Avenue {index + 1}",
                road_type="arterial",
                coordinates=[
                    (first.center_lat, first.center_lon),
                    (second.center_lat, second.center_lon),
                ],
                lanes=rng.choice([2, 3, 4, 6]),
                congestion=round(rng.uniform(20, 42), 2),
                operational=True,
            )
        )

    # Eight cross-city connectors.
    ordered_by_longitude = sorted(
        districts,
        key=lambda district: district.center_lon,
    )

    for index in range(8):
        first = ordered_by_longitude[index]
        second = ordered_by_longitude[index + 2]

        roads.append(
            RoadSegment(
                id=f"ROAD-V-{index + 1:02d}",
                name=f"Cross City Boulevard {index + 1}",
                road_type="connector",
                coordinates=[
                    (first.center_lat, first.center_lon),
                    (second.center_lat, second.center_lon),
                ],
                lanes=rng.choice([2, 3, 4]),
                congestion=round(rng.uniform(18, 38), 2),
                operational=True,
            )
        )

    return roads


def generate_city(
    seed: int = 42,
    city_name: str = CITY_NAME,
    initial_budget: float = INITIAL_BUDGET,
) -> CityState:
    """Generate a complete playable starting city."""

    if initial_budget < 0:
        raise ValueError("Initial budget cannot be negative.")

    districts = generate_districts(
        seed=seed,
        center_lat=CITY_CENTER_LAT,
        center_lon=CITY_CENTER_LON,
    )

    buildings = generate_buildings(
        districts=districts,
        seed=seed,
        buildings_per_district=BUILDINGS_PER_DISTRICT,
    )

    roads = generate_roads(
        districts=districts,
        seed=seed,
    )

    city = CityState(
        city_name=city_name,
        seed=seed,
        day=1,
        budget=initial_budget,
        districts=districts,
        buildings=buildings,
        roads=roads,
    )

    city.add_event(
        f"{city_name} simulation initialized."
    )

    city.add_event(
        f"{len(districts)} districts generated."
    )

    city.add_event(
        f"{len(buildings)} buildings generated."
    )

    city.add_event(
        f"{len(roads)} road segments generated."
    )

    return city
