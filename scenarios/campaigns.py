
"""AFTERMATH campaign and objective definitions."""

from enum import Enum

from pydantic import BaseModel, Field


class ObjectiveType(str, Enum):
    REACH = "reach"
    MAINTAIN = "maintain"
    SPEND_BELOW = "spend_below"
    SURVIVE_DAYS = "survive_days"


class CampaignObjective(BaseModel):
    id: str
    title: str
    description: str

    objective_type: ObjectiveType

    metric: str | None = None
    target: float | None = None

    deadline_day: int | None = None
    required_days: int = 1


class Campaign(BaseModel):
    id: str
    title: str
    subtitle: str
    description: str
    difficulty: str

    starting_budget: float
    starting_day: int = 1

    objectives: list[CampaignObjective] = Field(
        default_factory=list
    )


CAMPAIGNS = [
    Campaign(
        id="first-100-days",
        title="The First 100 Days",
        subtitle="A city is built one decision at a time.",
        description=(
            "Establish a stable administration, improve public "
            "wellbeing and maintain financial sustainability."
        ),
        difficulty="normal",
        starting_budget=2_500_000_000,
        objectives=[
            CampaignObjective(
                id="stable-economy",
                title="Financial Stability",
                description="Reach an economic health score of 70.",
                objective_type=ObjectiveType.REACH,
                metric="economic_health",
                target=70,
                deadline_day=30,
            ),
            CampaignObjective(
                id="community-wellbeing",
                title="Community Wellbeing",
                description="Reach public wellbeing of 75.",
                objective_type=ObjectiveType.REACH,
                metric="public_wellbeing",
                target=75,
                deadline_day=60,
            ),
            CampaignObjective(
                id="long-term-stability",
                title="Build for the Future",
                description="Maintain a positive city budget through day 100.",
                objective_type=ObjectiveType.SURVIVE_DAYS,
                required_days=100,
            ),
        ],
    ),
    Campaign(
        id="breaking-point",
        title="The Breaking Point",
        subtitle="Every crisis has a human cost.",
        description=(
            "Navigate infrastructure failures, environmental "
            "pressure and competing community needs."
        ),
        difficulty="hard",
        starting_budget=1_200_000_000,
        objectives=[
            CampaignObjective(
                id="protect-safety",
                title="Protect Residents",
                description="Keep city safety at or above 65.",
                objective_type=ObjectiveType.MAINTAIN,
                metric="safety",
                target=65,
                deadline_day=30,
            ),
            CampaignObjective(
                id="restore-resources",
                title="Resource Recovery",
                description="Restore energy reserves to 60.",
                objective_type=ObjectiveType.REACH,
                metric="energy_reserve",
                target=60,
                deadline_day=45,
            ),
            CampaignObjective(
                id="preserve-wellbeing",
                title="People Before Numbers",
                description="Maintain public wellbeing above 55.",
                objective_type=ObjectiveType.MAINTAIN,
                metric="public_wellbeing",
                target=55,
                required_days=20,
            ),
        ],
    ),
    Campaign(
        id="tomorrows-city",
        title="Tomorrow's City",
        subtitle="Efficiency is not the same as progress.",
        description=(
            "Develop a technologically advanced city without "
            "sacrificing equity, accessibility or sustainability."
        ),
        difficulty="expert",
        starting_budget=3_000_000_000,
        objectives=[
            CampaignObjective(
                id="green-future",
                title="A Sustainable Future",
                description="Reach environmental health of 80.",
                objective_type=ObjectiveType.REACH,
                metric="environmental_health",
                target=80,
                deadline_day=75,
            ),
            CampaignObjective(
                id="equal-opportunity",
                title="Opportunity for Everyone",
                description="Reach social equity of 70.",
                objective_type=ObjectiveType.REACH,
                metric="social_equity",
                target=70,
                deadline_day=90,
            ),
            CampaignObjective(
                id="mobility-future",
                title="Connected City",
                description="Reach mobility of 75.",
                objective_type=ObjectiveType.REACH,
                metric="mobility",
                target=75,
                deadline_day=100,
            ),
        ],
    ),
]
