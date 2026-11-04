
"""Synthetic citizen agents and community perspectives."""

from pydantic import BaseModel, Field

from agents.base import AgentProfile, AgentRole, BaseAgent
from simulation.state import District


class CitizenArchetype(BaseModel):
    """Defines how a particular community group evaluates the city."""

    key: str
    label: str
    priorities: list[str]
    description: str

    happiness_weight: float = Field(ge=0.0, le=1.0)
    safety_weight: float = Field(ge=0.0, le=1.0)
    healthcare_weight: float = Field(ge=0.0, le=1.0)
    wealth_weight: float = Field(ge=0.0, le=1.0)
    green_space_weight: float = Field(ge=0.0, le=1.0)
    stress_weight: float = Field(ge=0.0, le=1.0)

    def validate_weights(self) -> None:
        """Ensure the scoring profile represents exactly 100%."""

        total = sum(
            (
                self.happiness_weight,
                self.safety_weight,
                self.healthcare_weight,
                self.wealth_weight,
                self.green_space_weight,
                self.stress_weight,
            )
        )

        if abs(total - 1.0) > 0.0001:
            raise ValueError(
                f"Invalid scoring weights for {self.label}: "
                f"expected 1.0, received {total:.4f}."
            )


CITIZEN_ARCHETYPES = {
    "working_family": CitizenArchetype(
        key="working_family",
        label="Working Families",
        priorities=[
            "affordable_housing",
            "education",
            "healthcare",
            "transport",
        ],
        description=(
            "Residents balancing household costs, work and family needs."
        ),
        happiness_weight=0.20,
        safety_weight=0.18,
        healthcare_weight=0.22,
        wealth_weight=0.18,
        green_space_weight=0.08,
        stress_weight=0.14,
    ),

    "young_professional": CitizenArchetype(
        key="young_professional",
        label="Young Professionals",
        priorities=[
            "employment",
            "mobility",
            "technology",
            "housing",
        ],
        description=(
            "Residents focused on careers, connectivity and opportunity."
        ),
        happiness_weight=0.18,
        safety_weight=0.12,
        healthcare_weight=0.10,
        wealth_weight=0.28,
        green_space_weight=0.12,
        stress_weight=0.20,
    ),

    "senior_resident": CitizenArchetype(
        key="senior_resident",
        label="Senior Residents",
        priorities=[
            "healthcare",
            "safety",
            "accessibility",
            "community",
        ],
        description=(
            "Older residents who value access, safety and reliable services."
        ),
        happiness_weight=0.18,
        safety_weight=0.25,
        healthcare_weight=0.27,
        wealth_weight=0.08,
        green_space_weight=0.08,
        stress_weight=0.14,
    ),

    "small_business": CitizenArchetype(
        key="small_business",
        label="Small Business Owners",
        priorities=[
            "economic_health",
            "transport",
            "public_safety",
            "commercial_activity",
        ],
        description=(
            "Local business owners concerned with economic conditions."
        ),
        happiness_weight=0.12,
        safety_weight=0.18,
        healthcare_weight=0.08,
        wealth_weight=0.35,
        green_space_weight=0.07,
        stress_weight=0.20,
    ),

    "student": CitizenArchetype(
        key="student",
        label="Students",
        priorities=[
            "education",
            "affordability",
            "mobility",
            "technology",
        ],
        description=(
            "Students focused on education, access and future opportunities."
        ),
        happiness_weight=0.18,
        safety_weight=0.10,
        healthcare_weight=0.10,
        wealth_weight=0.25,
        green_space_weight=0.12,
        stress_weight=0.25,
    ),

    "environmental_advocate": CitizenArchetype(
        key="environmental_advocate",
        label="Environmental Advocates",
        priorities=[
            "environment",
            "green_space",
            "clean_energy",
            "sustainability",
        ],
        description=(
            "Residents who prioritise environmental protection."
        ),
        happiness_weight=0.12,
        safety_weight=0.10,
        healthcare_weight=0.08,
        wealth_weight=0.10,
        green_space_weight=0.40,
        stress_weight=0.20,
    ),
}


# Validate every archetype when the module is imported.
for archetype in CITIZEN_ARCHETYPES.values():
    archetype.validate_weights()


class CitizenAgent(BaseAgent):
    """A synthetic citizen perspective in a city district."""

    def __init__(
        self,
        district: District,
        archetype: CitizenArchetype,
        index: int,
    ):
        profile = AgentProfile(
            id=f"{district.id}-CIT-{index:02d}",
            name=f"{archetype.label} · {district.name}",
            role=AgentRole.CITIZEN,
            description=archetype.description,
            district_id=district.id,
            priorities=archetype.priorities,
        )

        super().__init__(profile)

        self.archetype = archetype

    def evaluate_district(self, district: District) -> dict:
        """Evaluate a district using this group's individual priorities."""

        if district.id != self.profile.district_id:
            raise ValueError(
                "Citizen cannot evaluate a different district."
            )

        archetype = self.archetype

        # Each group evaluates the same district conditions differently.
        happiness_contribution = (
            district.happiness * archetype.happiness_weight
        )

        safety_contribution = (
            district.safety * archetype.safety_weight
        )

        healthcare_contribution = (
            district.healthcare_access * archetype.healthcare_weight
        )

        wealth_contribution = (
            district.wealth_index * archetype.wealth_weight
        )

        green_space_contribution = (
            district.green_space * archetype.green_space_weight
        )

        stress_contribution = (
            (100.0 - district.stress) * archetype.stress_weight
        )

        score = (
            happiness_contribution
            + safety_contribution
            + healthcare_contribution
            + wealth_contribution
            + green_space_contribution
            + stress_contribution
        )

        score = max(0.0, min(100.0, score))

        if score >= 75:
            sentiment = "positive"
        elif score >= 55:
            sentiment = "mixed"
        else:
            sentiment = "negative"

        return {
            "agent_id": self.agent_id,
            "group": archetype.label,
            "district_id": district.id,
            "score": round(score, 2),
            "sentiment": sentiment,
            "priorities": archetype.priorities,
        }
