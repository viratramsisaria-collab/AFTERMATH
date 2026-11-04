
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from disasters.exposure import ExposureEngine, ExposureReport


class DistrictImpact(BaseModel):
    district_id: str
    exposure_score: float
    metric_changes: dict[str, float] = Field(default_factory=dict)
    buildings_damaged: int = 0
    population_affected: int = 0
    estimated_economic_loss: float = 0


class DisasterImpactReport(BaseModel):
    disaster_id: str
    disaster_type: str
    severity_score: float
    district_impacts: list[DistrictImpact] = Field(default_factory=list)
    city_metric_changes: dict[str, float] = Field(default_factory=dict)
    total_buildings_damaged: int = 0
    total_population_affected: int = 0
    total_economic_loss: float = 0
    applied: bool = False


# Values represent maximum game-model impacts at severity 100.
# Positive values are increases; negative values are decreases.
IMPACT_PROFILES = {
    "earthquake": {
        "economic_health": -20,
        "public_wellbeing": -18,
        "happiness": -25,
        "safety": -25,
        "healthcare_access": -18,
        "mobility": -25,
        "environmental_health": -8,
        "social_equity": -12,
        "energy_reserve": -18,
        "water_reserve": -12,
        "traffic_congestion": 25,
    },
    "flood": {
        "economic_health": -18,
        "public_wellbeing": -16,
        "happiness": -20,
        "safety": -18,
        "healthcare_access": -14,
        "mobility": -25,
        "environmental_health": -22,
        "social_equity": -12,
        "energy_reserve": -15,
        "water_reserve": -20,
        "traffic_congestion": 28,
    },
    "cyclone": {
        "economic_health": -22,
        "public_wellbeing": -18,
        "happiness": -22,
        "safety": -20,
        "healthcare_access": -14,
        "mobility": -22,
        "environmental_health": -18,
        "social_equity": -12,
        "energy_reserve": -24,
        "water_reserve": -12,
        "traffic_congestion": 22,
    },
    "heatwave": {
        "economic_health": -12,
        "public_wellbeing": -22,
        "happiness": -25,
        "safety": -10,
        "healthcare_access": -25,
        "mobility": -8,
        "environmental_health": -12,
        "social_equity": -15,
        "energy_reserve": -28,
        "water_reserve": -25,
        "traffic_congestion": 10,
    },
    "wildfire": {
        "economic_health": -18,
        "public_wellbeing": -22,
        "happiness": -22,
        "safety": -24,
        "healthcare_access": -20,
        "mobility": -15,
        "environmental_health": -30,
        "social_equity": -12,
        "energy_reserve": -12,
        "water_reserve": -18,
        "traffic_congestion": 18,
    },
    "drought": {
        "economic_health": -18,
        "public_wellbeing": -20,
        "happiness": -20,
        "safety": -5,
        "healthcare_access": -18,
        "mobility": -4,
        "environmental_health": -25,
        "social_equity": -22,
        "energy_reserve": -12,
        "water_reserve": -35,
        "traffic_congestion": 5,
    },
    "industrial_accident": {
        "economic_health": -20,
        "public_wellbeing": -18,
        "happiness": -22,
        "safety": -25,
        "healthcare_access": -25,
        "mobility": -12,
        "environmental_health": -28,
        "social_equity": -12,
        "energy_reserve": -12,
        "water_reserve": -15,
        "traffic_congestion": 15,
    },
}


def _clamp_metric(name: str, value: float) -> float:
    if name == "traffic_congestion":
        return max(0, min(100, value))
    return max(0, min(100, value))


def _district_id(district: Any) -> str:
    value = getattr(district, "id", None)
    if value is None:
        value = getattr(district, "district_id", None)
    if value is None:
        raise ValueError("District is missing its id.")
    return str(value)


class DisasterImpactEngine:
    def __init__(self):
        self.exposure_engine = ExposureEngine()

    def calculate(
        self,
        city: Any,
        disaster: Any,
        exposure: ExposureReport | None = None,
    ) -> DisasterImpactReport:
        if exposure is None:
            exposure = self.exposure_engine.calculate(city, disaster)

        profile = IMPACT_PROFILES[disaster.disaster_type.value]
        severity_factor = disaster.severity_score / 100

        district_impacts = []

        for item in exposure.district_exposures:
            exposure_factor = 0.35 + (item.exposure_score / 100) * 0.65
            factor = severity_factor * exposure_factor

            changes = {
                metric: round(amount * factor, 2)
                for metric, amount in profile.items()
            }

            buildings_damaged = 0

            if item.building_count > 0 and factor > 0:
                damage_ratio = min(0.85, factor * 0.65)
                buildings_damaged = min(
        item.building_count,
        max(1, round(item.building_count * damage_ratio)),
    )

            population_affected = round(
                item.population * min(0.9, factor * 0.35)
            )

            economic_loss = (
                max(0, float(getattr(city, "budget", 0)))
                * abs(changes["economic_health"])
                / 100
                * 0.025
            )

            district_impacts.append(
                DistrictImpact(
                    district_id=item.district_id,
                    exposure_score=item.exposure_score,
                    metric_changes=changes,
                    buildings_damaged=buildings_damaged,
                    population_affected=population_affected,
                    estimated_economic_loss=round(economic_loss, 2),
                )
            )

        metric_names = list(profile)
        total_weight = sum(
            max(1, item.population)
            for item in exposure.district_exposures
        )

        city_changes = {}

        for metric in metric_names:
            weighted_change = sum(
                impact.metric_changes[metric]
                * max(1, next(
                    (
                        district.population
                        for district in exposure.district_exposures
                        if district.district_id == impact.district_id
                    ),
                    1,
                ))
                for impact in district_impacts
            ) / total_weight

            city_changes[metric] = round(weighted_change, 2)

        return DisasterImpactReport(
            disaster_id=disaster.id,
            disaster_type=disaster.disaster_type.value,
            severity_score=disaster.severity_score,
            district_impacts=district_impacts,
            city_metric_changes=city_changes,
            total_buildings_damaged=sum(
                item.buildings_damaged for item in district_impacts
            ),
            total_population_affected=sum(
                item.population_affected for item in district_impacts
            ),
            total_economic_loss=round(
                sum(item.estimated_economic_loss for item in district_impacts),
                2,
            ),
        )

    def apply(
        self,
        city: Any,
        disaster: Any,
        report: DisasterImpactReport | None = None,
    ) -> DisasterImpactReport:
        if disaster.initial_damage_applied:
            raise ValueError(
                f"Initial impact for disaster {disaster.id} was already applied."
            )

        report = report or self.calculate(city, disaster)

        districts = {
            _district_id(district): district
            for district in city.districts
        }

        for metric, change in report.city_metric_changes.items():
            current = float(getattr(city.metrics, metric))
            setattr(
                city.metrics,
                metric,
                _clamp_metric(metric, current + change),
            )

        for impact in report.district_impacts:
            district = districts.get(impact.district_id)

            if district is None:
                continue

            # Apply district-specific values only when those fields exist.
            for metric, change in impact.metric_changes.items():
                if hasattr(district, metric):
                    current = float(getattr(district, metric))
                    setattr(
                        district,
                        metric,
                        _clamp_metric(metric, current + change),
                    )

            # Mark affected buildings as non-operational.
            affected_buildings = [
                building
                for building in city.buildings
                if str(getattr(building, "district_id", ""))
                == impact.district_id
            ]

            remaining_damage = impact.buildings_damaged

            for building in affected_buildings:
                if remaining_damage <= 0:
                    break

                if bool(getattr(building, "operational", True)):
                    building.operational = False
                    remaining_damage -= 1

        city.budget = max(
            0,
            float(city.budget) - report.total_economic_loss,
        )

        disaster.initial_damage_applied = True
        report.applied = True

        if hasattr(city, "add_event"):
            city.add_event(
                f"{disaster.title} caused damage across "
                f"{len(report.district_impacts)} districts."
            )

        return report


def calculate_disaster_impact(
    city: Any,
    disaster: Any,
) -> DisasterImpactReport:
    return DisasterImpactEngine().calculate(city, disaster)


def apply_disaster_impact(
    city: Any,
    disaster: Any,
) -> DisasterImpactReport:
    return DisasterImpactEngine().apply(city, disaster)
