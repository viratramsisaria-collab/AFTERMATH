
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from disasters.impact import DisasterImpactReport
from disasters.models import DisasterInstance, DisasterStatus


class MetricRecovery(BaseModel):
    metric_name: str
    total_damage: float
    remaining_damage: float
    daily_restoration: float


class RecoveryState(BaseModel):
    disaster_id: str
    started_day: int
    duration_days: int = Field(default=15, ge=1)
    progress: float = Field(default=0, ge=0, le=100)
    metrics: list[MetricRecovery] = Field(default_factory=list)
    damaged_building_ids: list[str] = Field(default_factory=list)
    repaired_building_ids: list[str] = Field(default_factory=list)
    is_complete: bool = False


class RecoveryReport(BaseModel):
    disaster_id: str
    progress: float
    metrics_restored: dict[str, float] = Field(default_factory=dict)
    buildings_repaired: int = 0
    is_complete: bool = False


class DisasterRecoveryEngine:
    def start(
        self,
        city: Any,
        disaster: DisasterInstance,
        impact_report: DisasterImpactReport,
        current_day: int,
        duration_days: int | None = None,
    ) -> RecoveryState:
        if not disaster.is_contained:
            raise ValueError("A disaster must be contained before recovery begins.")

        if disaster.recovery_started:
            raise ValueError("Recovery has already started for this disaster.")

        duration = duration_days or self._recovery_duration(disaster)
        duration = max(1, duration)

        metrics = []

        for metric_name, change in impact_report.city_metric_changes.items():
            damage = abs(min(0, change))

            if damage <= 0:
                continue

            metrics.append(
                MetricRecovery(
                    metric_name=metric_name,
                    total_damage=damage,
                    remaining_damage=damage,
                    daily_restoration=damage / duration,
                )
            )

        affected_ids = set(disaster.affected_district_ids)

        damaged_buildings = [
            building
            for building in city.buildings
            if str(getattr(building, "district_id", "")) in affected_ids
            and not bool(getattr(building, "operational", True))
        ]

        state = RecoveryState(
            disaster_id=disaster.id,
            started_day=current_day,
            duration_days=duration,
            metrics=metrics,
            damaged_building_ids=[
                str(getattr(building, "id"))
                for building in damaged_buildings
                if getattr(building, "id", None) is not None
            ],
        )

        disaster.recovery_started = True
        disaster.status = DisasterStatus.RECOVERING

        return state

    def advance_day(
        self,
        city: Any,
        disaster: DisasterInstance,
        state: RecoveryState,
        current_day: int,
        restoration_multiplier: float = 1.0,
    ) -> RecoveryReport:
        if state.is_complete:
            return RecoveryReport(
                disaster_id=disaster.id,
                progress=100,
                is_complete=True,
            )

        if state.disaster_id != disaster.id:
            raise ValueError("Recovery state belongs to a different disaster.")

        if restoration_multiplier <= 0:
            raise ValueError("Restoration multiplier must be positive.")

        if current_day <= state.started_day:
            raise ValueError("Recovery can only advance on a later day.")

        metrics_restored = {}

        for item in state.metrics:
            if item.remaining_damage <= 0:
                continue

            restoration = min(
                item.remaining_damage,
                item.daily_restoration * restoration_multiplier,
            )

            current = float(getattr(city.metrics, item.metric_name))
            maximum = 100

            if item.metric_name == "traffic_congestion":
                # Congestion is harmful when high, so recovery reduces it.
                new_value = max(0, current - restoration)
            else:
                new_value = min(maximum, current + restoration)

            actual_restoration = abs(new_value - current)

            setattr(city.metrics, item.metric_name, new_value)

            item.remaining_damage = max(
                0,
                item.remaining_damage - actual_restoration,
            )

            metrics_restored[item.metric_name] = round(
                actual_restoration, 2
            )

        buildings_repaired = self._repair_buildings(
            city,
            state,
            restoration_multiplier,
        )

        elapsed = current_day - state.started_day

        state.progress = min(
            100,
            (elapsed / state.duration_days) * 100,
        )

        metrics_finished = all(
            item.remaining_damage <= 0.01
            for item in state.metrics
        )

        buildings_finished = (
            len(state.repaired_building_ids)
            >= len(state.damaged_building_ids)
        )

        if elapsed >= state.duration_days and metrics_finished and buildings_finished:
            state.is_complete = True
            state.progress = 100
            disaster.recovery_progress = 100
            disaster.status = DisasterStatus.RESOLVED
        else:
            disaster.recovery_progress = round(state.progress, 2)

        return RecoveryReport(
            disaster_id=disaster.id,
            progress=round(state.progress, 2),
            metrics_restored=metrics_restored,
            buildings_repaired=buildings_repaired,
            is_complete=state.is_complete,
        )

    @staticmethod
    def _recovery_duration(disaster: DisasterInstance) -> int:
        return max(
            5,
            min(45, 5 + round(disaster.severity_score * 0.4)),
        )

    @staticmethod
    def _repair_buildings(
        city: Any,
        state: RecoveryState,
        multiplier: float,
    ) -> int:
        building_lookup = {
            str(getattr(building, "id", "")): building
            for building in city.buildings
        }

        unrepaired = [
            building_id
            for building_id in state.damaged_building_ids
            if building_id not in state.repaired_building_ids
        ]

        repair_count = min(
            len(unrepaired),
            max(1, round(multiplier * 2)),
        )

        repaired = 0

        for building_id in unrepaired[:repair_count]:
            building = building_lookup.get(building_id)

            if building is None:
                state.repaired_building_ids.append(building_id)
                continue

            building.operational = True
            state.repaired_building_ids.append(building_id)
            repaired += 1

        return repaired


def start_disaster_recovery(
    city: Any,
    disaster: DisasterInstance,
    impact_report: DisasterImpactReport,
    current_day: int,
    duration_days: int | None = None,
) -> RecoveryState:
    return DisasterRecoveryEngine().start(
        city,
        disaster,
        impact_report,
        current_day,
        duration_days,
    )


def advance_disaster_recovery(
    city: Any,
    disaster: DisasterInstance,
    state: RecoveryState,
    current_day: int,
    restoration_multiplier: float = 1.0,
) -> RecoveryReport:
    return DisasterRecoveryEngine().advance_day(
        city,
        disaster,
        state,
        current_day,
        restoration_multiplier,
    )
