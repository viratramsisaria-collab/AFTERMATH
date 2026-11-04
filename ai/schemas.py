
"""Structured AI outputs used by the AFTERMATH council."""

from typing import Literal

from pydantic import BaseModel, Field


class CouncilPerspective(BaseModel):
    role: str = Field(description="Council member's specialist role.")
    stance: Literal["support", "conditional", "oppose"]
    reasoning: str
    expected_benefits: list[str] = Field(default_factory=list)
    identified_risks: list[str] = Field(default_factory=list)
    recommendation: str


class CouncilDeliberation(BaseModel):
    problem: str
    executive_summary: str
    perspectives: list[CouncilPerspective]
    major_tradeoffs: list[str] = Field(default_factory=list)
    unanswered_questions: list[str] = Field(default_factory=list)
    human_decision_required: bool = True
