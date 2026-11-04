
"""AFTERMATH scenario and campaign subsystem."""

from scenarios.campaigns import (
    CAMPAIGNS,
    Campaign,
    CampaignObjective,
    ObjectiveType,
)
from scenarios.manager import (
    CampaignProgress,
    ObjectiveProgress,
    ScenarioManager,
)

__all__ = [
    "CAMPAIGNS",
    "Campaign",
    "CampaignObjective",
    "ObjectiveType",
    "CampaignProgress",
    "ObjectiveProgress",
    "ScenarioManager",
]
