
"""Structured policy assessment models."""

from pydantic import BaseModel, Field, model_validator

from judgement.metrics import HumanValues


class PolicyImpact(BaseModel):
    metric: str
    before: float
    after: float
    explanation: str

    @property
    def change(self) -> float:
        return round(self.after - self.before, 2)


class PolicyProposal(BaseModel):
    id: str
    title: str
    description: str

    estimated_cost: float = Field(default=0.0, ge=0)
    duration_days: int = Field(default=1, ge=1)

    district_ids: list[str] = Field(default_factory=list)
    expected_impacts: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_impacts(self):
        allowed = {
            "economic_health",
            "mobility",
            "public_wellbeing",
            "environmental_health",
            "social_equity",
            "safety",
            "healthcare_access",
            "happiness",
            "energy_reserve",
            "water_reserve",
            "traffic_congestion",
        }

        invalid = set(self.expected_impacts) - allowed

        if invalid:
            raise ValueError(
                f"Unsupported impact metrics: {sorted(invalid)}"
            )

        return self


class PolicyAssessment(BaseModel):
    proposal_id: str
    proposal_title: str

    overall_score: float = Field(ge=0, le=100)
    values: HumanValues

    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)

    estimated_cost: float = 0.0

    recommendation: str
    explanation: str

    human_decision_required: bool = True
