
from __future__ import annotations

from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class DisasterType(StrEnum):
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    CYCLONE = "cyclone"
    HEATWAVE = "heatwave"
    WILDFIRE = "wildfire"
    DROUGHT = "drought"
    INDUSTRIAL_ACCIDENT = "industrial_accident"


class DisasterStatus(StrEnum):
    DETECTED = "detected"
    ACTIVE = "active"
    CONTAINED = "contained"
    RECOVERING = "recovering"
    RESOLVED = "resolved"
    FAILED = "failed"


class DisasterSeverity(StrEnum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"


class ScaleAssessment(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    scale_name: str
    measured_value: float
    unit: str
    category: str
    severity_score: float = Field(ge=0, le=100)
    description: str
    secondary_values: dict[str, float | str] = Field(default_factory=dict)


class DisasterObjective(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:10])
    title: str
    description: str
    target_district_id: str | None = None
    required_progress: float = Field(default=100, ge=1, le=100)
    current_progress: float = Field(default=0, ge=0, le=100)
    is_completed: bool = False


class DisasterInstance(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: str = Field(default_factory=lambda: uuid4().hex)
    disaster_type: DisasterType
    title: str
    description: str

    status: DisasterStatus = DisasterStatus.DETECTED
    severity: DisasterSeverity = DisasterSeverity.MODERATE
    severity_score: float = Field(default=30, ge=0, le=100)

    scheduled_day: int = Field(ge=1)
    detected_day: int = Field(ge=1)
    deadline_day: int = Field(ge=1)

    affected_district_ids: list[str] = Field(default_factory=list)
    measurements: list[ScaleAssessment] = Field(default_factory=list)
    objectives: list[DisasterObjective] = Field(default_factory=list)

    containment_progress: float = Field(default=0, ge=0, le=100)
    is_contained: bool = False

    initial_damage_applied: bool = False
    recovery_started: bool = False
    recovery_progress: float = Field(default=0, ge=0, le=100)

    created_at_day: int = Field(ge=1)
    resolved_at_day: int | None = None

    def all_objectives_completed(self) -> bool:
        return bool(self.objectives) and all(
            objective.is_completed
            for objective in self.objectives
        )

    def days_remaining(self, current_day: int) -> int:
        return max(0, self.deadline_day - current_day)

    def mark_contained(self, current_day: int) -> None:
        self.is_contained = True
        self.status = DisasterStatus.CONTAINED
        self.resolved_at_day = current_day
        self.containment_progress = 100


class DisasterRecord(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    disaster_id: str
    disaster_type: DisasterType
    severity_score: float
    affected_district_ids: list[str] = Field(default_factory=list)
    detected_day: int
    contained: bool
    resolved_day: int | None = None
    economic_damage: float = 0
    people_affected: int = 0
