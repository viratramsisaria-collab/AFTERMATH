"""AFTERMATH city defeat conditions and evaluation."""

from dataclasses import dataclass

from simulation.state import CityState


@dataclass(frozen=True)
class LossCondition:
    metric: str
    label: str
    threshold: float
    operator: str
    description: str

    def is_failed(self, value: float) -> bool:
        if self.operator == "below":
            return value < self.threshold

        if self.operator == "above":
            return value > self.threshold

        raise ValueError(f"Unsupported loss operator: {self.operator}")


LOSS_CONDITIONS = (
    LossCondition(
        "economic_health", "Economic Growth", 20, "below",
        "The city's economy has fallen below a sustainable level.",
    ),
    LossCondition(
        "mobility", "Urban Mobility", 4, "below",
        "The city's transport network can no longer maintain mobility.",
    ),
    LossCondition(
        "environmental_health", "Environmental Health", 20, "below",
        "Environmental conditions have deteriorated beyond recovery.",
    ),
    LossCondition(
        "social_equity", "Social Equity", 30, "below",
        "Inequality has exceeded the city's acceptable limit.",
    ),
    LossCondition(
        "safety", "Public Safety", 25, "below",
        "Public safety has fallen below the minimum acceptable level.",
    ),
    LossCondition(
        "healthcare_access", "Healthcare Access", 30, "below",
        "The city can no longer provide sufficient healthcare access.",
    ),
    LossCondition(
        "happiness", "Citizen Happiness", 20, "below",
        "Citizen happiness has fallen to a critical level.",
    ),
    LossCondition(
        "energy_reserve", "Energy Reserves", 39, "below",
        "The city no longer has sufficient energy reserves.",
    ),
    LossCondition(
        "water_reserve", "Water Reserves", 12, "below",
        "The city no longer has sufficient water reserves.",
    ),
    LossCondition(
        "traffic_congestion", "Traffic Congestion", 80, "above",
        "Traffic congestion has exceeded the city's critical limit.",
    ),
)


def evaluate_loss(city: CityState) -> dict | None:
    """Return the first failed condition, or None if the city survives."""

    for condition in LOSS_CONDITIONS:
        value = float(getattr(city.metrics, condition.metric))

        if condition.is_failed(value):
            return {
                "metric": condition.metric,
                "label": condition.label,
                "value": round(value, 2),
                "threshold": condition.threshold,
                "operator": condition.operator,
                "description": condition.description,
                "day": city.day,
            }

    return None