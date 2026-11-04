
"""Apply city event effects and player responses."""

from events.generator import CityEvent, EventSeverity
from simulation.state import CityState


SEVERITY_MULTIPLIERS = {
    EventSeverity.LOW: 0.5,
    EventSeverity.MODERATE: 0.75,
    EventSeverity.HIGH: 1.0,
    EventSeverity.CRITICAL: 1.25,
}


def _clamp(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)


def apply_event(
    city: CityState,
    event: CityEvent,
) -> dict:
    """Apply the event's default effects to the city."""

    if event.is_resolved:
        raise ValueError("This event has already been resolved.")

    multiplier = SEVERITY_MULTIPLIERS[event.severity]

    budget_change = event.budget_impact * multiplier

    city.budget = max(0.0, city.budget + budget_change)

    city.metrics.happiness = _clamp(
        city.metrics.happiness
        + event.happiness_impact * multiplier
    )

    city.metrics.safety = _clamp(
        city.metrics.safety
        + event.safety_impact * multiplier
    )

    city.metrics.environmental_health = _clamp(
        city.metrics.environmental_health
        + event.environment_impact * multiplier
    )

    city.metrics.mobility = _clamp(
        city.metrics.mobility
        + event.mobility_impact * multiplier
    )

    if event.district_id:
        district = next(
            (
                item for item in city.districts
                if item.id == event.district_id
            ),
            None,
        )

        if district:
            district.happiness = _clamp(
                district.happiness
                + event.happiness_impact * multiplier
            )

            district.safety = _clamp(
                district.safety
                + event.safety_impact * multiplier
            )

            district.stress = _clamp(
                district.stress
                - event.happiness_impact * multiplier
            )

    event.is_resolved = True

    city.add_event(
        f"Event handled: {event.title}."
    )

    return {
        "event_id": event.id,
        "title": event.title,
        "budget_change": round(budget_change, 2),
        "budget_after": round(city.budget, 2),
        "severity": event.severity.value,
        "resolved": True,
    }


def apply_response(
    city: CityState,
    event: CityEvent,
    response: dict,
) -> dict:
    """Apply a player-selected response to an event."""

    if event.is_resolved:
        raise ValueError("This event has already been resolved.")

    cost = float(response.get("cost", 0.0))

    if cost < 0:
        raise ValueError("Response cost cannot be negative.")

    if city.budget < cost:
        raise ValueError("Insufficient city budget.")

    city.budget -= cost

    effects = response.get("effects", {})

    allowed_metrics = {
        "happiness",
        "safety",
        "environmental_health",
        "mobility",
        "economic_health",
        "social_equity",
        "healthcare_access",
        "energy_reserve",
        "water_reserve",
        "public_wellbeing",
        "traffic_congestion",
    }

    for metric, change in effects.items():
        if metric not in allowed_metrics:
            raise ValueError(
                f"Unsupported city metric: {metric}"
            )

        current = getattr(city.metrics, metric)
        setattr(
            city.metrics,
            metric,
            _clamp(current + float(change)),
        )

    event.is_resolved = True

    city.add_event(
        f"Player response selected for {event.title}."
    )

    return {
        "event_id": event.id,
        "response": response.get("label", "Custom response"),
        "cost": cost,
        "remaining_budget": round(city.budget, 2),
        "effects": effects,
        "resolved": True,
    }
