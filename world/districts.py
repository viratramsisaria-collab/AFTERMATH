
"""District definitions and procedural district generation."""

import random

from simulation.state import District


DISTRICT_BLUEPRINTS = [
    {
        "id": "central",
        "name": "Central Heights",
        "type": "civic",
        "population": 21000,
        "offset": (0.000, 0.000),
        "happiness": 76,
        "safety": 85,
        "healthcare": 78,
        "green_space": 35,
        "wealth": 82,
        "stress": 28,
    },
    {
        "id": "financial",
        "name": "Financial Quarter",
        "type": "financial",
        "population": 16500,
        "offset": (0.010, 0.006),
        "happiness": 68,
        "safety": 82,
        "healthcare": 75,
        "green_space": 18,
        "wealth": 94,
        "stress": 45,
    },
    {
        "id": "residential",
        "name": "Westhaven",
        "type": "residential",
        "population": 14500,
        "offset": (-0.010, -0.009),
        "happiness": 78,
        "safety": 76,
        "healthcare": 70,
        "green_space": 42,
        "wealth": 62,
        "stress": 30,
    },
    {
        "id": "commercial",
        "name": "Mercury Square",
        "type": "commercial",
        "population": 14200,
        "offset": (0.004, -0.013),
        "happiness": 69,
        "safety": 72,
        "healthcare": 67,
        "green_space": 20,
        "wealth": 70,
        "stress": 48,
    },
    {
        "id": "green",
        "name": "Evergreen District",
        "type": "green",
        "population": 13800,
        "offset": (-0.014, 0.008),
        "happiness": 86,
        "safety": 80,
        "healthcare": 72,
        "green_space": 85,
        "wealth": 58,
        "stress": 19,
    },
    {
        "id": "waterfront",
        "name": "Azure Waterfront",
        "type": "waterfront",
        "population": 12500,
        "offset": (0.016, -0.003),
        "happiness": 81,
        "safety": 78,
        "healthcare": 70,
        "green_space": 48,
        "wealth": 76,
        "stress": 25,
    },
    {
        "id": "innovation",
        "name": "Innovation Park",
        "type": "innovation",
        "population": 11500,
        "offset": (-0.004, 0.017),
        "happiness": 77,
        "safety": 81,
        "healthcare": 74,
        "green_space": 38,
        "wealth": 88,
        "stress": 35,
    },
    {
        "id": "cultural",
        "name": "Old Quarter",
        "type": "cultural",
        "population": 10800,
        "offset": (0.012, 0.014),
        "happiness": 74,
        "safety": 70,
        "healthcare": 66,
        "green_space": 32,
        "wealth": 52,
        "stress": 37,
    },
    {
        "id": "industrial",
        "name": "Ironworks",
        "type": "industrial",
        "population": 9500,
        "offset": (-0.017, -0.014),
        "happiness": 62,
        "safety": 68,
        "healthcare": 58,
        "green_space": 12,
        "wealth": 46,
        "stress": 57,
    },
    {
        "id": "harbor",
        "name": "Liberty Harbor",
        "type": "waterfront",
        "population": 8500,
        "offset": (0.020, 0.012),
        "happiness": 79,
        "safety": 77,
        "healthcare": 68,
        "green_space": 55,
        "wealth": 64,
        "stress": 29,
    },
]


def generate_districts(
    seed: int = 42,
    center_lat: float = 40.754,
    center_lon: float = -73.985,
) -> list[District]:
    """Generate the city's ten districts."""

    rng = random.Random(seed)
    districts = []

    for blueprint in DISTRICT_BLUEPRINTS:
        lat_offset, lon_offset = blueprint["offset"]

        districts.append(
            District(
                id=blueprint["id"],
                name=blueprint["name"],
                district_type=blueprint["type"],
                center_lat=round(
                    center_lat + lat_offset + rng.uniform(-0.001, 0.001),
                    6,
                ),
                center_lon=round(
                    center_lon + lon_offset + rng.uniform(-0.001, 0.001),
                    6,
                ),
                population=blueprint["population"],
                happiness=blueprint["happiness"],
                safety=blueprint["safety"],
                healthcare_access=blueprint["healthcare"],
                green_space=blueprint["green_space"],
                wealth_index=blueprint["wealth"],
                stress=blueprint["stress"],
            )
        )

    return districts
