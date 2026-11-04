
"""Procedural building generation."""

import random

from simulation.state import Building, District


BUILDING_TYPES_BY_DISTRICT = {
    "civic": [
        "government",
        "public_library",
        "residential",
        "commercial",
        "hospital",
    ],
    "financial": [
        "office_tower",
        "bank",
        "commercial",
        "hotel",
        "residential",
    ],
    "residential": [
        "residential",
        "apartment",
        "school",
        "community_center",
        "commercial",
    ],
    "commercial": [
        "commercial",
        "shopping_center",
        "office_tower",
        "hotel",
        "residential",
    ],
    "green": [
        "residential",
        "community_center",
        "public_library",
        "greenhouse",
        "school",
    ],
    "waterfront": [
        "hotel",
        "residential",
        "commercial",
        "recreation",
        "office_tower",
    ],
    "innovation": [
        "research_center",
        "office_tower",
        "university",
        "residential",
        "laboratory",
    ],
    "cultural": [
        "museum",
        "theater",
        "residential",
        "commercial",
        "public_library",
    ],
    "industrial": [
        "factory",
        "warehouse",
        "energy_plant",
        "residential",
        "commercial",
    ],
}

BUILDING_HEIGHT_RANGES = {
    "government": (30, 65),
    "public_library": (12, 28),
    "residential": (20, 85),
    "commercial": (15, 60),
    "hospital": (25, 55),
    "office_tower": (80, 240),
    "bank": (35, 100),
    "hotel": (35, 130),
    "apartment": (25, 100),
    "school": (12, 35),
    "community_center": (10, 25),
    "shopping_center": (15, 40),
    "greenhouse": (8, 20),
    "recreation": (8, 30),
    "research_center": (30, 100),
    "university": (20, 80),
    "laboratory": (20, 65),
    "museum": (15, 50),
    "theater": (15, 40),
    "factory": (15, 55),
    "warehouse": (8, 25),
    "energy_plant": (20, 60),
}

BUILDING_COLORS = {
    "government": [115, 145, 170],
    "public_library": [95, 165, 175],
    "residential": [110, 145, 165],
    "commercial": [65, 165, 190],
    "hospital": [175, 205, 210],
    "office_tower": [75, 125, 165],
    "bank": [105, 125, 155],
    "hotel": [145, 135, 180],
    "apartment": [90, 150, 175],
    "school": [175, 165, 115],
    "community_center": [125, 175, 155],
    "shopping_center": [165, 135, 155],
    "greenhouse": [85, 165, 115],
    "recreation": [75, 175, 145],
    "research_center": [75, 155, 190],
    "university": [100, 135, 180],
    "laboratory": [90, 175, 190],
    "museum": [175, 155, 125],
    "theater": [165, 115, 155],
    "factory": [125, 130, 140],
    "warehouse": [115, 125, 135],
    "energy_plant": [195, 155, 75],
}


def generate_buildings(
    districts: list[District],
    seed: int = 42,
    buildings_per_district: int = 9,
) -> list[Building]:
    """Generate buildings within each district."""

    if buildings_per_district < 1:
        raise ValueError("Each district must have at least one building.")

    rng = random.Random(seed)
    buildings = []

    for district in districts:
        available_types = BUILDING_TYPES_BY_DISTRICT.get(
            district.district_type,
            ["residential", "commercial"],
        )

        for index in range(buildings_per_district):
            building_type = rng.choice(available_types)
            min_height, max_height = BUILDING_HEIGHT_RANGES.get(
                building_type,
                (15, 50),
            )

            height = rng.randint(min_height, max_height)
            floors = max(2, round(height / 3.5))

            building_id = f"{district.id}-BLD-{index + 1:02d}"

            buildings.append(
                Building(
                    id=building_id,
                    name=(
                        f"{district.name} "
                        f"{building_type.replace('_', ' ').title()} "
                        f"{index + 1:02d}"
                    ),
                    district_id=district.id,
                    building_type=building_type,
                    latitude=round(
                        district.center_lat + rng.uniform(-0.003, 0.003),
                        6,
                    ),
                    longitude=round(
                        district.center_lon + rng.uniform(-0.003, 0.003),
                        6,
                    ),
                    height_m=float(height),
                    floors=floors,
                    footprint_m2=float(
                        rng.randint(450, 4200)
                    ),
                    color=BUILDING_COLORS.get(
                        building_type,
                        [110, 145, 165],
                    ),
                    operational=True,
                )
            )

    return buildings
