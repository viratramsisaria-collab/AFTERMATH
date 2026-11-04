
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DistrictExposure(BaseModel):
    district_id: str
    population: int = 0
    building_count: int = 0
    operational_buildings: int = 0
    building_resilience: float = Field(default=50, ge=0, le=100)
    population_density_factor: float = Field(default=1, ge=0, le=2)
    infrastructure_vulnerability: float = Field(default=50, ge=0, le=100)
    exposure_score: float = Field(default=50, ge=0, le=100)
    risk_category: str = "Moderate"


class ExposureReport(BaseModel):
    disaster_id: str
    district_exposures: list[DistrictExposure] = Field(default_factory=list)
    total_population_exposed: int = 0
    total_buildings_exposed: int = 0
    average_exposure_score: float = 0
    highest_risk_district_id: str | None = None


def _get_id(item: Any) -> str:
    value = getattr(item, "id", None)
    if value is None:
        value = getattr(item, "district_id", None)
    if value is None:
        raise ValueError("District or building is missing its id.")
    return str(value)


def _district_population(district: Any) -> int:
    for name in ("population", "residents", "citizen_count"):
        value = getattr(district, name, None)
        if value is not None:
            return max(0, int(value))
    return 0


def _risk_category(score: float) -> str:
    if score < 20:
        return "Low"
    if score < 40:
        return "Moderate"
    if score < 60:
        return "High"
    if score < 80:
        return "Very High"
    return "Critical"


class ExposureEngine:
    def calculate(
        self,
        city: Any,
        disaster: Any,
    ) -> ExposureReport:
        districts = list(getattr(city, "districts", []))
        buildings = list(getattr(city, "buildings", []))

        affected_ids = set(disaster.affected_district_ids)
        selected_districts = [
            district for district in districts
            if _get_id(district) in affected_ids
        ]

        if not selected_districts:
            raise ValueError("No affected districts were found in the city.")

        district_results = []

        for district in selected_districts:
            district_id = _get_id(district)
            district_buildings = [
                building
                for building in buildings
                if str(getattr(building, "district_id", "")) == district_id
            ]

            operational = sum(
                1 for building in district_buildings
                if bool(getattr(building, "operational", True))
            )

            building_count = len(district_buildings)
            population = _district_population(district)

            building_resilience = self._building_resilience(
                district_buildings
            )

            density_factor = self._density_factor(
                population,
                building_count,
            )

            infrastructure_vulnerability = self._infrastructure_vulnerability(
                district,
                district_buildings,
            )

            raw_score = (
                (100 - building_resilience) * 0.35
                + density_factor * 50 * 0.25
                + infrastructure_vulnerability * 0.40
            )

            exposure_score = max(0, min(100, raw_score))

            district_results.append(
                DistrictExposure(
                    district_id=district_id,
                    population=population,
                    building_count=building_count,
                    operational_buildings=operational,
                    building_resilience=round(building_resilience, 2),
                    population_density_factor=round(density_factor, 2),
                    infrastructure_vulnerability=round(
                        infrastructure_vulnerability, 2
                    ),
                    exposure_score=round(exposure_score, 2),
                    risk_category=_risk_category(exposure_score),
                )
            )

        total_population = sum(
            item.population for item in district_results
        )
        total_buildings = sum(
            item.building_count for item in district_results
        )
        average = (
            sum(item.exposure_score for item in district_results)
            / len(district_results)
        )

        highest_risk = max(
            district_results,
            key=lambda item: item.exposure_score,
        )

        return ExposureReport(
            disaster_id=disaster.id,
            district_exposures=district_results,
            total_population_exposed=total_population,
            total_buildings_exposed=total_buildings,
            average_exposure_score=round(average, 2),
            highest_risk_district_id=highest_risk.district_id,
        )

    @staticmethod
    def _building_resilience(buildings: list[Any]) -> float:
        if not buildings:
            return 35.0

        values = []

        for building in buildings:
            operational = bool(getattr(building, "operational", True))
            floors = max(1, int(getattr(building, "floors", 1)))

            # A gameplay proxy, not a structural engineering assessment.
            score = 45 + min(floors, 20) * 1.5

            if not operational:
                score -= 25

            values.append(max(0, min(100, score)))

        return sum(values) / len(values)

    @staticmethod
    def _density_factor(
        population: int,
        building_count: int,
    ) -> float:
        if building_count <= 0:
            return min(2.0, population / 50000)

        estimated_density = population / building_count
        return max(0.1, min(2.0, estimated_density / 1000))

    @staticmethod
    def _infrastructure_vulnerability(
        district: Any,
        buildings: list[Any],
    ) -> float:
        existing_stress = float(getattr(district, "stress", 0) or 0)
        existing_damage = sum(
            1
            for building in buildings
            if not bool(getattr(building, "operational", True))
        )

        damage_ratio = (
            existing_damage / len(buildings)
            if buildings else 0
        )

        return max(
            0,
            min(100, 40 + existing_stress * 0.25 + damage_ratio * 40),
        )


def calculate_exposure(
    city: Any,
    disaster: Any,
) -> ExposureReport:
    return ExposureEngine().calculate(city, disaster)
