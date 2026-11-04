
"""AFTERMATH event definitions and procedural event generation."""

import random
from enum import Enum

from pydantic import BaseModel, Field

from simulation.state import CityState


class EventCategory(str, Enum):
    ECONOMIC = "economic"
    ENVIRONMENTAL = "environmental"
    INFRASTRUCTURE = "infrastructure"
    SOCIAL = "social"
    PUBLIC_HEALTH = "public_health"
    OPPORTUNITY = "opportunity"


class EventSeverity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class CityEvent(BaseModel):
    id: str
    title: str
    description: str
    category: EventCategory
    severity: EventSeverity

    district_id: str | None = None

    budget_impact: float = 0.0
    happiness_impact: float = 0.0
    safety_impact: float = 0.0
    environment_impact: float = 0.0
    mobility_impact: float = 0.0

    response_options: list[dict] = Field(default_factory=list)
    is_resolved: bool = False


EVENT_CATALOG = [
    {
        "id": "heatwave",
        "title": "Extreme Heatwave",
        "description": "A prolonged heatwave is putting pressure on energy and public health services.",
        "category": EventCategory.ENVIRONMENTAL,
        "severity": EventSeverity.HIGH,
        "budget_impact": -2_500_000,
        "happiness_impact": -4,
        "safety_impact": -2,
        "environment_impact": -5,
        "mobility_impact": -1,
    },
    {
        "id": "transit_disruption",
        "title": "Transit Network Disruption",
        "description": "A major transit connection has been disrupted, increasing travel times.",
        "category": EventCategory.INFRASTRUCTURE,
        "severity": EventSeverity.MODERATE,
        "budget_impact": -750_000,
        "happiness_impact": -2,
        "safety_impact": 0,
        "environment_impact": -1,
        "mobility_impact": -8,
    },
    {
        "id": "business_boom",
        "title": "Unexpected Business Investment",
        "description": "A group of businesses has announced a major investment in the city.",
        "category": EventCategory.OPPORTUNITY,
        "severity": EventSeverity.MODERATE,
        "budget_impact": 3_500_000,
        "happiness_impact": 2,
        "safety_impact": 0,
        "environment_impact": 0,
        "mobility_impact": 1,
    },
    {
        "id": "water_shortage",
        "title": "Water Supply Shortage",
        "description": "Reduced supply is placing pressure on residential and commercial water access.",
        "category": EventCategory.ENVIRONMENTAL,
        "severity": EventSeverity.CRITICAL,
        "budget_impact": -3_000_000,
        "happiness_impact": -6,
        "safety_impact": -1,
        "environment_impact": -7,
        "mobility_impact": 0,
    },
    {
        "id": "community_festival",
        "title": "Citywide Community Festival",
        "description": "A community-led festival is bringing residents and local businesses together.",
        "category": EventCategory.SOCIAL,
        "severity": EventSeverity.LOW,
        "budget_impact": -350_000,
        "happiness_impact": 4,
        "safety_impact": 1,
        "environment_impact": 0,
        "mobility_impact": -1,
    },
    {
        "id": "health_alert",
        "title": "Public Health Alert",
        "description": "Health services are reporting increased demand across several neighbourhoods.",
        "category": EventCategory.PUBLIC_HEALTH,
        "severity": EventSeverity.HIGH,
        "budget_impact": -1_800_000,
        "happiness_impact": -3,
        "safety_impact": -2,
        "environment_impact": 0,
        "mobility_impact": 0,
    },
    {
        "id": "factory_emissions",
        "title": "Industrial Emissions Spike",
        "description": "An industrial facility has reported an emissions control failure.",
        "category": EventCategory.ENVIRONMENTAL,
        "severity": EventSeverity.HIGH,
        "budget_impact": -1_000_000,
        "happiness_impact": -2,
        "safety_impact": -1,
        "environment_impact": -8,
        "mobility_impact": 0,
    },
    {
        "id": "housing_pressure",
        "title": "Housing Affordability Pressure",
        "description": "Rising housing costs are creating additional pressure for lower-income residents.",
        "category": EventCategory.SOCIAL,
        "severity": EventSeverity.HIGH,
        "budget_impact": 0,
        "happiness_impact": -5,
        "safety_impact": 0,
        "environment_impact": 0,
        "mobility_impact": 0,
    },
    {
        "id": "power_outage",
        "title": "Regional Power Outage",
        "description": "An electrical grid fault has interrupted power to part of the city.",
        "category": EventCategory.INFRASTRUCTURE,
        "severity": EventSeverity.CRITICAL,
        "budget_impact": -2_200_000,
        "happiness_impact": -5,
        "safety_impact": -3,
        "environment_impact": -2,
        "mobility_impact": -2,
    },
    {
        "id": "research_grant",
        "title": "Urban Innovation Grant",
        "description": "The city has been offered funding for a sustainable technology pilot.",
        "category": EventCategory.OPPORTUNITY,
        "severity": EventSeverity.LOW,
        "budget_impact": 2_000_000,
        "happiness_impact": 1,
        "safety_impact": 0,
        "environment_impact": 2,
        "mobility_impact": 0,
    },
]


class EventGenerator:
    """Generates reproducible events for the simulation."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self._sequence = 0
        self._used_ids: set[str] = set()

    def generate(
        self,
        city: CityState,
        count: int = 1,
    ) -> list[CityEvent]:
        if count < 1:
            raise ValueError("Event count must be at least 1.")

        available = [
            event for event in EVENT_CATALOG
            if event["id"] not in self._used_ids
        ]

        if not available:
            self._used_ids.clear()
            available = EVENT_CATALOG.copy()

        selected = self.rng.sample(
            available,
            k=min(count, len(available)),
        )

        generated = []

        for template in selected:
            self._sequence += 1

            district = (
                self.rng.choice(city.districts)
                if city.districts
                else None
            )

            payload = dict(template)
            payload["id"] = f"{template['id']}-{self._sequence:03d}"
            payload["district_id"] = (
                district.id if district else None
            )

            event = CityEvent(**payload)

            self._used_ids.add(template["id"])
            generated.append(event)

        return generated
