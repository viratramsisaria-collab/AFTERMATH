
"""Persistent data models for AFTERMATH's Security Command Centre."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class UnitType(StrEnum):
    POLICE = "police"
    FIRE = "fire"
    MEDICAL = "medical"
    RESCUE = "rescue"
    ENGINEERING = "engineering"
    EVACUATION = "evacuation"


class IncidentType(StrEnum):
    CRIME = "crime"
    FIRE = "fire"
    MEDICAL = "medical"
    INFRASTRUCTURE = "infrastructure"
    PUBLIC_DISORDER = "public_disorder"
    DISASTER = "disaster"


class IncidentStatus(StrEnum):
    DETECTED = "detected"
    ACTIVE = "active"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    FAILED = "failed"


class UnitStatus(StrEnum):
    AVAILABLE = "available"
    DEPLOYED = "deployed"
    RESTING = "resting"
    MAINTENANCE = "maintenance"


class DeploymentStatus(StrEnum):
    DISPATCHED = "dispatched"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    COMPLETED = "completed"
    FAILED = "failed"
    RECALLED = "recalled"


# ─────────────────────────────────────────────
# DEPARTMENT
# ─────────────────────────────────────────────

class SecurityDepartment(BaseModel):
    id: str
    name: str
    unit_type: UnitType

    description: str = ""

    unit_ids: list[str] = Field(default_factory=list)

    headquarters_district_id: str | None = None

    budget_allocation: float = Field(
        default=0,
        ge=0,
    )

    active: bool = True


# ─────────────────────────────────────────────
# SECURITY UNIT
# ─────────────────────────────────────────────

class SecurityUnit(BaseModel):
    id: str
    name: str

    unit_type: UnitType

    personnel: int = Field(ge=1)
    available_personnel: int = Field(ge=0)

    home_district_id: str
    department_id: str | None = None

    status: UnitStatus = UnitStatus.AVAILABLE

    readiness: float = Field(
        default=100,
        ge=0,
        le=100,
    )

    equipment_rating: float = Field(
        default=75,
        ge=0,
        le=100,
    )

    active_deployments: list[str] = Field(
        default_factory=list,
    )

    maintenance_until_day: int | None = None

    @model_validator(mode="after")
    def validate_personnel(self):
        if self.available_personnel > self.personnel:
            raise ValueError(
                "Available personnel cannot exceed total personnel."
            )

        return self


# ─────────────────────────────────────────────
# SECURITY INCIDENT
# ─────────────────────────────────────────────

class SecurityIncident(BaseModel):
    id: str

    title: str
    description: str

    incident_type: IncidentType

    status: IncidentStatus = IncidentStatus.DETECTED

    district_id: str

    severity: float = Field(
        ge=0,
        le=100,
    )

    population_at_risk: int = Field(
        default=0,
        ge=0,
    )

    detected_day: int
    deadline_day: int

    required_response: list[UnitType] = Field(
        default_factory=list,
    )

    response_progress: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    resolved_day: int | None = None

    created_by_disaster: bool = False
    disaster_id: str | None = None

    assigned_deployment_ids: list[str] = Field(
        default_factory=list,
    )


# ─────────────────────────────────────────────
# SECURITY DEPLOYMENT
# ─────────────────────────────────────────────

class SecurityDeployment(BaseModel):
    id: str

    unit_ids: list[str]

    personnel_allocations: dict[str, int] = Field(
        default_factory=dict,
    )

    incident_id: str | None = None

    disaster_id: str | None = None
    objective_id: str | None = None

    district_id: str

    personnel: int = Field(ge=1)

    status: DeploymentStatus = DeploymentStatus.DISPATCHED

    dispatched_day: int
    arrival_day: int

    remaining_days: int = Field(
        default=0,
        ge=0,
    )

    progress: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    daily_cost: float = Field(
        default=0,
        ge=0,
    )

    total_cost: float = Field(
        default=0,
        ge=0,
    )

    failure_reason: str | None = None


# ─────────────────────────────────────────────
# SECURITY RESOURCES
# ─────────────────────────────────────────────

class SecurityResource(BaseModel):
    id: str
    name: str
    category: str

    quantity: int = Field(ge=0)

    available_quantity: int = Field(ge=0)

    unit_cost_per_day: float = Field(
        default=0,
        ge=0,
    )

    district_id: str | None = None

    @model_validator(mode="after")
    def validate_quantity(self):
        if self.available_quantity > self.quantity:
            raise ValueError(
                "Available quantity cannot exceed total quantity."
            )

        return self


# ─────────────────────────────────────────────
# SECURITY OPERATIONS LOG
# ─────────────────────────────────────────────

class SecurityLogEntry(BaseModel):
    id: str

    day: int

    category: str
    message: str

    severity: str = "info"

    metadata: dict[
        str,
        str | int | float | bool | None
    ] = Field(default_factory=dict)


# ─────────────────────────────────────────────
# CENTRAL SECURITY STATE
# ─────────────────────────────────────────────

class SecurityState(BaseModel):

    model_config = ConfigDict(
        validate_assignment=True,
    )

    departments: list[SecurityDepartment] = Field(
        default_factory=list,
    )

    units: list[SecurityUnit] = Field(
        default_factory=list,
    )

    incidents: list[SecurityIncident] = Field(
        default_factory=list,
    )

    deployments: list[SecurityDeployment] = Field(
        default_factory=list,
    )

    resources: list[SecurityResource] = Field(
        default_factory=list,
    )

    operations_log: list[SecurityLogEntry] = Field(
        default_factory=list,
    )

    initialized: bool = False

    next_incident_day: int = 7

    incident_sequence: int = 0
    deployment_sequence: int = 0
    log_sequence: int = 0

    total_deployments: int = 0

    successful_operations: int = 0
    failed_operations: int = 0

    total_operational_cost: float = 0

    total_mobilizations: int = 0

    # ─────────────────────────────────────
    # COMPUTED PROPERTIES
    # ─────────────────────────────────────

    @property
    def total_personnel(self) -> int:
        return sum(
            unit.personnel
            for unit in self.units
        )

    @property
    def available_personnel(self) -> int:
        return sum(
            unit.available_personnel
            for unit in self.units
        )

    @property
    def active_deployments(self) -> int:
        active_statuses = {
            DeploymentStatus.DISPATCHED,
            DeploymentStatus.EN_ROUTE,
            DeploymentStatus.ON_SCENE,
        }

        return sum(
            deployment.status in active_statuses
            for deployment in self.deployments
        )

    @property
    def active_incidents(self) -> int:
        active_statuses = {
            IncidentStatus.DETECTED,
            IncidentStatus.ACTIVE,
        }

        return sum(
            incident.status in active_statuses
            for incident in self.incidents
        )
