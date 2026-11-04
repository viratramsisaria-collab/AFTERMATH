
from __future__ import annotations

import random
from typing import Any

from disasters.models import (
    DisasterInstance,
    DisasterObjective,
    DisasterSeverity,
    DisasterType,
)
from disasters.registry import DISASTER_REGISTRY
from disasters.scales import (
    earthquake_assessment,
    flood_assessment,
    cyclone_assessment,
    heatwave_assessment,
    wildfire_assessment,
    drought_assessment,
    industrial_accident_assessment,
)


SCALE_GENERATORS = {
    DisasterType.EARTHQUAKE: earthquake_assessment,
    DisasterType.FLOOD: flood_assessment,
    DisasterType.CYCLONE: cyclone_assessment,
    DisasterType.HEATWAVE: heatwave_assessment,
    DisasterType.WILDFIRE: wildfire_assessment,
    DisasterType.DROUGHT: drought_assessment,
    DisasterType.INDUSTRIAL_ACCIDENT: industrial_accident_assessment,
}


def _district_id(district: Any) -> str:
    value = getattr(district, "id", None)
    if value is None:
        value = getattr(district, "district_id", None)
    if value is None:
        raise ValueError("A district is missing its id.")
    return str(value)


def _severity(score: float) -> DisasterSeverity:
    if score < 15:
        return DisasterSeverity.MINOR
    if score < 35:
        return DisasterSeverity.MODERATE
    if score < 55:
        return DisasterSeverity.MAJOR
    if score < 75:
        return DisasterSeverity.SEVERE
    return DisasterSeverity.CATASTROPHIC


class DisasterGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed

    def generate(
        self,
        city: Any,
        day: int | None = None,
        sequence: int = 0,
        disaster_type: DisasterType | None = None,
        district_count: int | None = None,
    ) -> DisasterInstance:
        current_day = day if day is not None else int(city.day)

        if current_day < 1:
            raise ValueError("Disaster generation day must be positive.")

        districts = list(getattr(city, "districts", []))
        if not districts:
            raise ValueError("Cannot generate a disaster without city districts.")

        rng = random.Random(self.seed + sequence * 104729)

        selected_type = disaster_type or rng.choice(list(DisasterType))
        template = DISASTER_REGISTRY[selected_type]

        available_ids = [_district_id(district) for district in districts]
        rng.shuffle(available_ids)

        if district_count is None:
            district_count = rng.randint(1, min(4, len(available_ids)))

        district_count = max(1, min(district_count, len(available_ids)))
        affected_ids = available_ids[:district_count]

        measurements = self._generate_measurements(selected_type, rng)
        primary_score = measurements[0].severity_score

        # Additional variation makes repeated disasters less predictable.
        score = max(0.0, min(100.0, primary_score + rng.uniform(-4, 4)))
        score = round(score, 2)

        severity = _severity(score)
        title = template["title"]

        objectives = self._generate_objectives(
            selected_type,
            affected_ids,
            severity,
        )

        response_window = int(template["response_window_days"])

        return DisasterInstance(
            disaster_type=selected_type,
            title=title,
            description=template["description"],
            status="detected", # type: ignore
            severity=severity,
            severity_score=score,
            scheduled_day=current_day,
            detected_day=current_day,
            deadline_day=current_day + response_window,
            affected_district_ids=affected_ids,
            measurements=measurements,
            objectives=objectives,
            created_at_day=current_day,
        )

    @staticmethod
    def _generate_measurements(
        disaster_type: DisasterType,
        rng: random.Random,
    ) -> list:
        if disaster_type == DisasterType.EARTHQUAKE:
            magnitude = round(rng.uniform(4.0, 8.2), 1)
            depth = round(rng.uniform(5, 70), 1)
            mmi = max(1, min(12, round(2 + (magnitude - 3) * 1.35)))
            return [
                earthquake_assessment(magnitude, depth, mmi)
            ]

        if disaster_type == DisasterType.FLOOD:
            return [
                flood_assessment(
                    round(rng.uniform(0.3, 3.5), 2),
                    round(rng.uniform(0.2, 3.0), 2),
                    round(rng.uniform(6, 72), 1),
                )
            ]

        if disaster_type == DisasterType.CYCLONE:
            return [
                cyclone_assessment(
                    round(rng.uniform(80, 280), 1),
                    round(rng.uniform(0.5, 6), 1),
                )
            ]

        if disaster_type == DisasterType.HEATWAVE:
            return [
                heatwave_assessment(
                    round(rng.uniform(32, 55), 1),
                    round(rng.uniform(24, 120), 1),
                )
            ]

        if disaster_type == DisasterType.WILDFIRE:
            return [
                wildfire_assessment(
                    round(rng.uniform(5, 45), 1),
                    round(rng.uniform(5, 100), 1),
                )
            ]

        if disaster_type == DisasterType.DROUGHT:
            return [
                drought_assessment(
                    round(rng.uniform(-2.8, -0.5), 2)
                )
            ]

        if disaster_type == DisasterType.INDUSTRIAL_ACCIDENT:
            return [
                industrial_accident_assessment(
                    round(rng.uniform(20, 100), 1),
                    rng.randint(500, 25000),
                    round(rng.uniform(1, 48), 1),
                )
            ]

        raise ValueError(f"Unsupported disaster type: {disaster_type}")

    @staticmethod
    def _generate_objectives(
        disaster_type: DisasterType,
        district_ids: list[str],
        severity: DisasterSeverity,
    ) -> list[DisasterObjective]:
        objective_templates = {
            DisasterType.EARTHQUAKE: [
                ("Rescue trapped residents", "Deploy rescue teams to affected areas."),
                ("Secure damaged structures", "Prevent secondary structural incidents."),
                ("Restore emergency access", "Reopen essential routes for responders."),
            ],
            DisasterType.FLOOD: [
                ("Rescue affected residents", "Reach and evacuate flooded areas."),
                ("Protect critical infrastructure", "Secure power and water facilities."),
                ("Control flood spread", "Reduce exposure and contain the affected zone."),
            ],
            DisasterType.CYCLONE: [
                ("Complete evacuations", "Move vulnerable residents to safe shelters."),
                ("Protect critical infrastructure", "Secure essential utilities."),
                ("Restore emergency access", "Clear routes for response teams."),
            ],
            DisasterType.HEATWAVE: [
                ("Establish cooling support", "Provide safe cooling and hydration facilities."),
                ("Protect vulnerable residents", "Prioritize medical support for high-risk groups."),
                ("Stabilize energy supply", "Protect critical power availability."),
            ],
            DisasterType.WILDFIRE: [
                ("Protect evacuation routes", "Keep routes accessible for residents."),
                ("Contain fire spread", "Limit expansion into populated districts."),
                ("Establish medical support", "Treat smoke exposure and injuries."),
            ],
            DisasterType.DROUGHT: [
                ("Secure emergency water", "Protect and distribute essential water supplies."),
                ("Protect vulnerable communities", "Prioritize districts with limited reserves."),
                ("Stabilize water infrastructure", "Prevent further supply losses."),
            ],
            DisasterType.INDUSTRIAL_ACCIDENT: [
                ("Secure the hazard zone", "Restrict access to the affected area."),
                ("Evacuate exposed residents", "Move people away from hazardous exposure."),
                ("Establish medical response", "Support exposed and injured residents."),
            ],
        }

        templates = objective_templates[disaster_type]
        required_progress = {
            DisasterSeverity.MINOR: 55,
            DisasterSeverity.MODERATE: 65,
            DisasterSeverity.MAJOR: 75,
            DisasterSeverity.SEVERE: 85,
            DisasterSeverity.CATASTROPHIC: 95,
        }[severity]

        objectives = []

        for index, (title, description) in enumerate(templates):
            district_id = district_ids[index % len(district_ids)]
            objectives.append(
                DisasterObjective(
                    title=title,
                    description=description,
                    target_district_id=district_id,
                    required_progress=required_progress,
                )
            )

        return objectives
