
"""Base models for AFTERMATH agents."""

from enum import Enum

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    CITIZEN = "citizen"
    ECONOMIST = "economist"
    URBAN_PLANNER = "urban_planner"
    ENVIRONMENTALIST = "environmentalist"
    PUBLIC_HEALTH = "public_health"
    TRANSPORT = "transport"
    SOCIAL_ADVOCATE = "social_advocate"
    SAFETY = "safety"
    TECHNOLOGY = "technology"
    MAYOR_ADVISOR = "mayor_advisor"


class AgentProfile(BaseModel):
    id: str
    name: str
    role: AgentRole
    description: str

    district_id: str | None = None

    priorities: list[str] = Field(default_factory=list)
    influence: float = Field(default=1.0, ge=0.0, le=1.0)


class AgentOpinion(BaseModel):
    agent_id: str
    subject: str
    position: str
    reasoning: str

    sentiment: float = Field(default=0.0, ge=-1.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)

    affected_values: list[str] = Field(default_factory=list)


class BaseAgent:
    """Common interface for AFTERMATH agent implementations."""

    def __init__(self, profile: AgentProfile):
        self.profile = profile

    @property
    def agent_id(self) -> str:
        return self.profile.id

    @property
    def name(self) -> str:
        return self.profile.name

    @property
    def role(self) -> AgentRole:
        return self.profile.role

    def get_profile(self) -> AgentProfile:
        return self.profile
