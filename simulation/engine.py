
"""AFTERMATH deterministic city simulation engine."""

import random
from typing import Any

from core.constants import METRIC_MAX, METRIC_MIN
from core.exceptions import InvalidSimulationState, SimulationError

from disasters.impact import DisasterImpactEngine
from disasters.models import DisasterStatus
from disasters.recovery import DisasterRecoveryEngine
from disasters.response import DisasterResponseEngine
from disasters.scheduler import DisasterScheduler

from security.engine import SecurityEngine

from simulation.rules import evaluate_loss
from simulation.state import CityState
from simulation.systems import (
    update_economy,
    update_environment,
    update_population,
    update_traffic,
)


class SimulationEngine:
    """Coordinates city, security and disaster simulation systems."""

    def __init__(self, state: CityState):
        self.state = state

        self.security_engine = SecurityEngine()
        self.disaster_scheduler = DisasterScheduler.from_state(
            state.disaster_schedule.model_dump(mode="json")
        )
        self.disaster_impact_engine = DisasterImpactEngine()
        self.disaster_recovery_engine = DisasterRecoveryEngine()
        self.disaster_response_engine = DisasterResponseEngine()

        self._validate_initial_state()
        self.security_engine.initialize(self.state)

        self._check_game_over()

    def _validate_initial_state(self) -> None:
        state = self.state

        if state.day < 1:
            raise InvalidSimulationState(
                "Simulation day must be at least 1."
            )

        if state.budget < 0:
            raise InvalidSimulationState(
                "City budget cannot be negative."
            )

        district_ids = {
            district.id for district in state.districts
        }

        if len(district_ids) != len(state.districts):
            raise InvalidSimulationState(
                "Duplicate district identifiers detected."
            )

        building_ids = {
            building.id for building in state.buildings
        }

        if len(building_ids) != len(state.buildings):
            raise InvalidSimulationState(
                "Duplicate building identifiers detected."
            )

        for building in state.buildings:
            if building.district_id not in district_ids:
                raise InvalidSimulationState(
                    f"Building {building.id} references an "
                    "unknown district."
                )

    def _validate_state(self) -> None:
        state = self.state

        if state.budget < 0:
            raise InvalidSimulationState(
                "Simulation produced a negative budget."
            )

        if state.population < 0:
            raise InvalidSimulationState(
                "Simulation produced a negative population."
            )

        for name, value in state.metrics.model_dump().items():
            if not METRIC_MIN <= value <= METRIC_MAX:
                raise InvalidSimulationState(
                    f"Metric '{name}' is outside its valid range."
                )

        for road in state.roads:
            if not 0 <= road.congestion <= 100:
                raise InvalidSimulationState(
                    f"Invalid congestion value on {road.id}."
                )

    def _check_game_over(self) -> dict | None:
        """Evaluate and persist the first failed city condition."""

        if self.state.is_game_over:
            return {
                "metric": self.state.game_over_metric,
                "label": self.state.game_over_label,
                "value": self.state.game_over_value,
                "threshold": self.state.game_over_threshold,
                "operator": self.state.game_over_operator,
                "description": self.state.game_over_reason,
                "day": self.state.game_over_day,
            }

        failure = evaluate_loss(self.state)

        if failure is None:
            return None

        self.state.is_game_over = True
        self.state.is_running = False
        self.state.game_over_metric = failure["metric"]
        self.state.game_over_label = failure["label"]
        self.state.game_over_value = failure["value"]
        self.state.game_over_threshold = failure["threshold"]
        self.state.game_over_operator = failure["operator"]
        self.state.game_over_reason = failure["description"]
        self.state.game_over_day = failure["day"]

        self.state.add_event(
            f"CITY DEFEAT: {failure['label']} reached "
            f"{failure['value']:.2f}; required condition: "
            f"{failure['operator']} {failure['threshold']:.2f}."
        )

        return failure

    def _process_disaster_schedule(self) -> list:
        """Generate and register disasters scheduled for this day."""

        generated = self.disaster_scheduler.process_day(
            city=self.state,
            existing_disasters=self.state.disasters,
        )

        for disaster in generated:
            self.state.disasters.append(disaster)

            report = self.disaster_impact_engine.apply(
                self.state,
                disaster,
            )

            self.state.disaster_impacts[disaster.id] = report

            self.state.add_event(
                f"DISASTER DETECTED: {disaster.title} "
                f"({disaster.severity.value}) affecting "
                f"{len(disaster.affected_district_ids)} districts."
            )

        return generated

    
    def _process_disaster_deadlines(self) -> list[str]:
        """Mark disasters that have exceeded their response deadline."""

        failed = []

        for disaster in self.state.disasters:
            previous_status = disaster.status

            self.disaster_response_engine.check_deadline(
                disaster,
                self.state.day,
            )

            if (
                previous_status != DisasterStatus.FAILED
                and disaster.status == DisasterStatus.FAILED
            ):
                failed.append(disaster.id)

                self.disaster_scheduler.unregister_disaster(
                    disaster.id
                )

                self.state.add_event(
                    f"DISASTER RESPONSE FAILED: {disaster.title} "
                    "exceeded its response deadline."
                )

        return failed

    
    def _start_contained_recoveries(self) -> list[str]:
        """Start recovery for newly contained disasters."""

        started = []

        for disaster in self.state.disasters:
            if disaster.status != DisasterStatus.CONTAINED:
                continue

            if disaster.recovery_started:
                continue

            impact_report = self.state.disaster_impacts.get(
                disaster.id
            )

            if impact_report is None:
                self.state.add_event(
                    f"RECOVERY BLOCKED: impact report missing for "
                    f"{disaster.title}."
                )
                continue

            recovery_state = self.disaster_recovery_engine.start(
                city=self.state,
                disaster=disaster,
                impact_report=impact_report,
                current_day=self.state.day,
            )

            self.state.disaster_recoveries[
                disaster.id
            ] = recovery_state

            self.state.add_event(
                f"RECOVERY INITIATED: {disaster.title}."
            )

            started.append(disaster.id)

        return started

    def _advance_disaster_recoveries(self) -> list[dict]:
        """Advance recovery operations already in progress."""

        reports = []

        for disaster in self.state.disasters:
            recovery_state = self.state.disaster_recoveries.get(
                disaster.id
            )

            if recovery_state is None or recovery_state.is_complete:
                continue

            if disaster.status != DisasterStatus.RECOVERING:
                continue

            report = self.disaster_recovery_engine.advance_day(
                city=self.state,
                disaster=disaster,
                state=recovery_state,
                current_day=self.state.day,
            )

            reports.append(report.model_dump(mode="json"))

            if report.is_complete:
                self.disaster_scheduler.unregister_disaster(
                    disaster.id
                )

                self.state.add_event(
                    f"DISASTER RESOLVED: {disaster.title}. "
                    "Recovery operations are complete."
                )

        return reports

    def _sync_disaster_scheduler(self) -> None:
        """Keep scheduler progress inside the persistent city state."""

        for disaster in self.state.disasters:
            self.disaster_scheduler.register_disaster(disaster)

        self.disaster_scheduler._refresh_active(
            self.state.disasters
        )

        self.state.disaster_schedule = (
            self.disaster_scheduler.state.model_copy(deep=True)
        )

    def _advance_disaster_system(self) -> dict[str, Any]:
        """Run the complete disaster lifecycle for the current day."""

        generated = self._process_disaster_schedule()

        # Security deployments apply objective progress to these instances.
        security = self.security_engine.advance_day(
            self.state,
            self.state.disasters,
        )

        failed = self._process_disaster_deadlines()
        started = self._start_contained_recoveries()
        recoveries = self._advance_disaster_recoveries()

        self._sync_disaster_scheduler()

        return {
            "generated": [
                item.id for item in generated
            ],
            "active": [
                item.id for item in self.state.active_disasters
            ],
            "failed": failed,
            "recovery_started": started,
            "recoveries": recoveries,
            "security": security,
        }

    def step(self) -> dict[str, Any]:
        """Advance the entire city by one simulation day."""

        if self.state.is_game_over:
            raise InvalidSimulationState(
                "The city has been defeated. Start a new city "
                "to continue playing."
            )

        previous_day = self.state.day

        try:
            self.state.day += 1

            rng = random.Random(
                self.state.seed + self.state.day
            )

            traffic = update_traffic(self.state, rng)
            environment = update_environment(self.state, rng)
            economy = update_economy(self.state)
            population = update_population(self.state, rng)

            disaster_report = self._advance_disaster_system()

            self._validate_state()

            failure = self._check_game_over()

            report = {
                "day": self.state.day,
                "population": self.state.population,
                "budget": round(self.state.budget, 2),
                "traffic": traffic,
                "environment": environment,
                "economy": economy,
                "population_changes": population,
                "security": disaster_report["security"],
                "disasters": disaster_report,
                "metrics": self.state.metrics.model_dump(),
                "game_over": failure is not None,
                "game_over_details": failure,
            }

            self.state.add_event(
                f"Simulation day {self.state.day} completed."
            )

            self.state.capture_snapshot()

            return report

        except InvalidSimulationState:
            self.state.day = previous_day
            raise

        except Exception as exc:
            self.state.day = previous_day

            raise SimulationError(
                f"Simulation tick failed: {exc}"
            ) from exc

    def run(self, days: int = 1) -> list[dict[str, Any]]:
        """Run consecutive days, stopping immediately on defeat."""

        if days < 1:
            raise ValueError("Days must be at least 1.")

        if self.state.is_game_over:
            raise InvalidSimulationState(
                "The city has been defeated. Start a new city "
                "to continue playing."
            )

        if self.state.day + days > 365:
            raise ValueError(
                "Simulation cannot exceed day 365."
            )

        self.state.is_running = True
        reports = []

        try:
            for _ in range(days):
                report = self.step()
                reports.append(report)

                if report["game_over"]:
                    break

        finally:
            self.state.is_running = False

        return reports

    def pause(self) -> None:
        self.state.is_running = False

    def get_summary(self) -> dict[str, Any]:
        """Return a compact view of the current city."""

        security = self.state.security

        return {
            "city": self.state.city_name,
            "day": self.state.day,
            "population": self.state.population,
            "districts": self.state.district_count,
            "buildings": self.state.building_count,
            "roads": len(self.state.roads),
            "budget": round(self.state.budget, 2),
            "metrics": self.state.metrics.model_dump(),
            "security": {
                "units": len(security.units),
                "personnel": security.total_personnel,
                "available_personnel": security.available_personnel,
                "active_incidents": security.active_incidents,
                "active_deployments": security.active_deployments,
                "successful_operations": security.successful_operations,
                "failed_operations": security.failed_operations,
            },
            "disasters": {
                "total": len(self.state.disasters),
                "active": len(self.state.active_disasters),
                "next_scheduled_day": (
                    self.state.disaster_schedule.next_disaster_day
                ),
                "recovering": sum(
                    1
                    for item in self.state.disasters
                    if item.status == DisasterStatus.RECOVERING
                ),
                "resolved": sum(
                    1
                    for item in self.state.disasters
                    if item.status == DisasterStatus.RESOLVED
                ),
                "failed": sum(
                    1
                    for item in self.state.disasters
                    if item.status == DisasterStatus.FAILED
                ),
            },
            "is_game_over": self.state.is_game_over,
            "game_over_metric": self.state.game_over_metric,
        }
