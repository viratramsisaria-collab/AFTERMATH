
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from disasters.models import DisasterInstance, DisasterStatus


class ResponseResult(BaseModel):
    disaster_id: str
    objective_id: str
    progress_added: float
    current_progress: float
    objective_completed: bool
    disaster_contained: bool
    days_remaining: int


class DeadlineResult(BaseModel):
    disaster_id: str
    deadline_day: int
    current_day: int
    failed: bool
    days_remaining: int


class DisasterResponseEngine:
    def apply_progress(
        self,
        disaster: DisasterInstance,
        objective_id: str,
        progress: float,
        current_day: int,
    ) -> ResponseResult:
        if disaster.status in {
            DisasterStatus.CONTAINED,
            DisasterStatus.RESOLVED,
            DisasterStatus.FAILED,
        }:
            raise ValueError("This disaster is no longer accepting operations.")

        if current_day > disaster.deadline_day:
            self.check_deadline(disaster, current_day)
            raise ValueError("The disaster response deadline has expired.")

        if progress <= 0:
            raise ValueError("Response progress must be greater than zero.")

        objective = next(
            (
                item for item in disaster.objectives
                if item.id == objective_id
            ),
            None,
        )

        if objective is None:
            raise ValueError(f"Unknown disaster objective: {objective_id}")

        if objective.is_completed:
            raise ValueError("This objective is already complete.")

        objective.current_progress = min(
            objective.required_progress,
            objective.current_progress + progress,
        )

        objective.is_completed = (
            objective.current_progress >= objective.required_progress
        )

        disaster.status = DisasterStatus.ACTIVE

        total_progress = sum(
            min(
                100,
                objective_item.current_progress
                / objective_item.required_progress * 100,
            )
            for objective_item in disaster.objectives
        )

        disaster.containment_progress = round(
            total_progress / max(1, len(disaster.objectives)),
            2,
        )

        contained = disaster.all_objectives_completed()

        if contained:
            disaster.mark_contained(current_day)

        return ResponseResult(
            disaster_id=disaster.id,
            objective_id=objective.id,
            progress_added=round(progress, 2),
            current_progress=round(objective.current_progress, 2),
            objective_completed=objective.is_completed,
            disaster_contained=contained,
            days_remaining=disaster.days_remaining(current_day),
        )

    def check_deadline(
        self,
        disaster: DisasterInstance,
        current_day: int,
    ) -> DeadlineResult:
        if disaster.status not in {
            DisasterStatus.CONTAINED,
            DisasterStatus.RESOLVED,
            DisasterStatus.FAILED,
        } and current_day > disaster.deadline_day:
            disaster.status = DisasterStatus.FAILED

        return DeadlineResult(
            disaster_id=disaster.id,
            deadline_day=disaster.deadline_day,
            current_day=current_day,
            failed=disaster.status == DisasterStatus.FAILED,
            days_remaining=disaster.days_remaining(current_day),
        )

    @staticmethod
    def activate(disaster: DisasterInstance) -> None:
        if disaster.status != DisasterStatus.DETECTED:
            raise ValueError("Only detected disasters can be activated.")

        disaster.status = DisasterStatus.ACTIVE

    @staticmethod
    def get_remaining_objectives(
        disaster: DisasterInstance,
    ) -> list:
        return [
            objective
            for objective in disaster.objectives
            if not objective.is_completed
        ]

    @staticmethod
    def get_response_summary(
        disaster: DisasterInstance,
        current_day: int,
    ) -> dict[str, Any]:
        return {
            "disaster_id": disaster.id,
            "status": disaster.status.value,
            "severity": disaster.severity.value,
            "severity_score": disaster.severity_score,
            "containment_progress": disaster.containment_progress,
            "completed_objectives": sum(
                objective.is_completed
                for objective in disaster.objectives
            ),
            "total_objectives": len(disaster.objectives),
            "days_remaining": disaster.days_remaining(current_day),
            "deadline_day": disaster.deadline_day,
            "is_contained": disaster.is_contained,
        }


def apply_response_progress(
    disaster: DisasterInstance,
    objective_id: str,
    progress: float,
    current_day: int,
) -> ResponseResult:
    return DisasterResponseEngine().apply_progress(
        disaster,
        objective_id,
        progress,
        current_day,
    )


def check_disaster_deadline(
    disaster: DisasterInstance,
    current_day: int,
) -> DeadlineResult:
    return DisasterResponseEngine().check_deadline(
        disaster,
        current_day,
    )
