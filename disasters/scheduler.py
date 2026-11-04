
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from disasters.generator import DisasterGenerator
from disasters.models import DisasterInstance, DisasterStatus


class DisasterScheduleState(BaseModel):
    seed: int = 42
    interval_days: int = 15
    response_window_days: int = 10

    next_disaster_day: int = 15
    generation_count: int = 0

    active_disaster_ids: list[str] = Field(default_factory=list)
    generated_disaster_ids: list[str] = Field(default_factory=list)
    last_processed_day: int = 0


class DisasterScheduler:
    def __init__(
        self,
        state: DisasterScheduleState | None = None,
        seed: int = 42,
        interval_days: int = 15,
    ):
        self.state = state or DisasterScheduleState(
            seed=seed,
            interval_days=interval_days,
            next_disaster_day=interval_days,
        )

        if self.state.interval_days < 1:
            raise ValueError("Disaster interval must be at least one day.")

        self.generator = DisasterGenerator(self.state.seed)

    def process_day(
        self,
        city: Any,
        existing_disasters: list[DisasterInstance] | None = None,
    ) -> list[DisasterInstance]:
        current_day = int(city.day)

        if current_day < 1:
            raise ValueError("Current city day must be positive.")

        if current_day <= self.state.last_processed_day:
            return []

        existing = existing_disasters or []
        existing_ids = {item.id for item in existing}

        self._refresh_active(existing)

        generated: list[DisasterInstance] = []

        while current_day >= self.state.next_disaster_day:
            scheduled_day = self.state.next_disaster_day

            disaster = self.generator.generate(
                city=city,
                day=scheduled_day,
                sequence=self.state.generation_count,
            )

            # Avoid creating a disaster whose detection day is in the past
            # with an already-expired deadline after a large simulation jump.
            if scheduled_day < current_day:
                disaster.detected_day = current_day
                disaster.deadline_day = current_day + self.state.response_window_days
                disaster.created_at_day = current_day

            if disaster.id not in existing_ids:
                generated.append(disaster)
                existing_ids.add(disaster.id)

            self.state.generation_count += 1
            self.state.next_disaster_day += self.state.interval_days

        self.state.last_processed_day = current_day

        for disaster in generated:
            self.state.generated_disaster_ids.append(disaster.id)
            self.state.active_disaster_ids.append(disaster.id)

        return generated

    def _refresh_active(
        self,
        disasters: list[DisasterInstance],
    ) -> None:
        active_statuses = {
            DisasterStatus.DETECTED,
            DisasterStatus.ACTIVE,
            DisasterStatus.RECOVERING,
        }

        self.state.active_disaster_ids = [
            disaster.id
            for disaster in disasters
            if disaster.status in active_statuses
        ]

    def register_disaster(self, disaster: DisasterInstance) -> None:
        if disaster.id not in self.state.generated_disaster_ids:
            self.state.generated_disaster_ids.append(disaster.id)

        if (
            disaster.status not in {
                DisasterStatus.CONTAINED,
                DisasterStatus.RESOLVED,
                DisasterStatus.FAILED,
            }
            and disaster.id not in self.state.active_disaster_ids
        ):
            self.state.active_disaster_ids.append(disaster.id)

    def unregister_disaster(self, disaster_id: str) -> None:
        self.state.active_disaster_ids = [
            item for item in self.state.active_disaster_ids
            if item != disaster_id
        ]

    def get_active_count(self) -> int:
        return len(self.state.active_disaster_ids)

    def get_next_disaster_day(self) -> int:
        return self.state.next_disaster_day

    def export_state(self) -> dict:
        return self.state.model_dump(mode="json")

    @classmethod
    def from_state(cls, data: dict) -> "DisasterScheduler":
        return cls(state=DisasterScheduleState.model_validate(data))
