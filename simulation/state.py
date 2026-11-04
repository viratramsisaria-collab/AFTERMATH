
"""AFTERMATH simulation state models."""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from disasters.impact import DisasterImpactReport
from disasters.models import DisasterInstance
from disasters.recovery import RecoveryState
from disasters.scheduler import DisasterScheduleState
from security.models import SecurityState


class CityMetrics(BaseModel):
    economic_health: float = 72.0
    mobility: float = 68.0
    public_wellbeing: float = 74.0
    environmental_health: float = 61.0
    social_equity: float = 63.0
    safety: float = 80.0
    healthcare_access: float = 70.0
    happiness: float = 71.0
    energy_reserve: float = 83.0
    water_reserve: float = 78.0
    traffic_congestion: float = 32.0

    @field_validator(
        "economic_health",
        "mobility",
        "public_wellbeing",
        "environmental_health",
        "social_equity",
        "safety",
        "healthcare_access",
        "happiness",
        "energy_reserve",
        "water_reserve",
        "traffic_congestion",
    )
    @classmethod
    def validate_percentage(cls, value: float) -> float:
        return max(0.0, min(100.0, value))


class Building(BaseModel):
    id: str
    name: str
    district_id: str
    building_type: str
    latitude: float
    longitude: float
    height_m: float
    floors: int
    footprint_m2: float
    color: list[int] = Field(default_factory=list)
    operational: bool = True


class District(BaseModel):
    id: str
    name: str
    district_type: str
    center_lat: float
    center_lon: float
    population: int
    happiness: float = 70.0
    safety: float = 75.0
    healthcare_access: float = 65.0
    green_space: float = 30.0
    wealth_index: float = 55.0
    stress: float = 35.0


class RoadSegment(BaseModel):
    id: str
    name: str
    road_type: str
    coordinates: list[tuple[float, float]]
    lanes: int = 2
    congestion: float = 30.0
    operational: bool = True


class SimulationSnapshot(BaseModel):
    day: int
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    budget: float
    population: int
    metrics: CityMetrics


class CityState(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    city_name: str = "NOVA YORK"
    seed: int = 42

    day: int = 1
    budget: float = 2_500_000_000

    districts: list[District] = Field(default_factory=list)
    buildings: list[Building] = Field(default_factory=list)
    roads: list[RoadSegment] = Field(default_factory=list)

    metrics: CityMetrics = Field(default_factory=CityMetrics)
    security: SecurityState = Field(default_factory=SecurityState)

    # Persistent disaster-management state.
    disasters: list[DisasterInstance] = Field(default_factory=list)
    disaster_schedule: DisasterScheduleState = Field(
        default_factory=DisasterScheduleState
    )
    disaster_impacts: dict[str, DisasterImpactReport] = Field(
        default_factory=dict
    )
    disaster_recoveries: dict[str, RecoveryState] = Field(
        default_factory=dict
    )

    event_log: list[str] = Field(default_factory=list)
    history: list[SimulationSnapshot] = Field(default_factory=list)

    is_running: bool = False

    # Persistent defeat information.
    is_game_over: bool = False
    game_over_metric: str | None = None
    game_over_label: str | None = None
    game_over_value: float | None = None
    game_over_threshold: float | None = None
    game_over_operator: str | None = None
    game_over_reason: str | None = None
    game_over_day: int | None = None
    game_over_tagline: str | None = None

    @property
    def population(self) -> int:
        return sum(d.population for d in self.districts)

    @property
    def district_count(self) -> int:
        return len(self.districts)

    @property
    def building_count(self) -> int:
        return len(self.buildings)

    @property
    def active_disasters(self) -> list[DisasterInstance]:
        from disasters.models import DisasterStatus

        active_statuses = {
            DisasterStatus.DETECTED,
            DisasterStatus.ACTIVE,
            DisasterStatus.RECOVERING,
        }

        return [
            disaster
            for disaster in self.disasters
            if disaster.status in active_statuses
        ]

    def get_disaster(self, disaster_id: str) -> DisasterInstance | None:
        return next(
            (
                disaster
                for disaster in self.disasters
                if disaster.id == disaster_id
            ),
            None,
        )

    def add_event(self, message: str) -> None:
        self.event_log.append(f"DAY {self.day}: {message}")
        self.event_log = self.event_log[-100:]

    def capture_snapshot(self) -> SimulationSnapshot:
        snapshot = SimulationSnapshot(
            day=self.day,
            budget=self.budget,
            population=self.population,
            metrics=self.metrics.model_copy(deep=True),
        )

        self.history.append(snapshot)
        self.history = self.history[-366:]

        return snapshot
