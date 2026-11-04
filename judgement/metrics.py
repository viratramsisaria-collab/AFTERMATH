
"""Human-centred evaluation dimensions and scoring helpers."""

from pydantic import BaseModel, Field


class HumanValues(BaseModel):
    dignity: float = Field(default=50, ge=0, le=100)
    fairness: float = Field(default=50, ge=0, le=100)
    accessibility: float = Field(default=50, ge=0, le=100)
    safety: float = Field(default=50, ge=0, le=100)
    wellbeing: float = Field(default=50, ge=0, le=100)
    opportunity: float = Field(default=50, ge=0, le=100)
    sustainability: float = Field(default=50, ge=0, le=100)


DEFAULT_WEIGHTS = {
    "dignity": 0.16,
    "fairness": 0.18,
    "accessibility": 0.14,
    "safety": 0.16,
    "wellbeing": 0.15,
    "opportunity": 0.10,
    "sustainability": 0.11,
}


def calculate_weighted_score(
    values: dict[str, float],
    weights: dict[str, float] | None = None,
) -> float:
    """Calculate a weighted score from supplied value assessments."""

    selected_weights = weights or DEFAULT_WEIGHTS

    if set(values) != set(selected_weights):
        raise ValueError(
            "Values and weights must contain the same dimensions."
        )

    if any(
        not 0 <= float(value) <= 100
        for value in values.values()
    ):
        raise ValueError("Scores must be between 0 and 100.")

    if any(weight < 0 for weight in selected_weights.values()):
        raise ValueError("Weights cannot be negative.")

    total_weight = sum(selected_weights.values())

    if total_weight <= 0:
        raise ValueError("At least one positive weight is required.")

    score = sum(
        values[key] * selected_weights[key]
        for key in selected_weights
    ) / total_weight

    return round(score, 2)


def identify_tradeoffs(
    values: dict[str, float],
    threshold: float = 45.0,
) -> list[str]:
    """Identify dimensions that need additional consideration."""

    return [
        dimension
        for dimension, score in values.items()
        if score < threshold
    ]
