
"""AFTERMATH Security Command Centre package."""

from security.engine import SecurityEngine

from security.models import (
    DeploymentStatus,
    IncidentStatus,
    IncidentType,
    SecurityDepartment,
    SecurityDeployment,
    SecurityIncident,
    SecurityLogEntry,
    SecurityResource,
    SecurityState,
    SecurityUnit,
    UnitStatus,
    UnitType,
)

from security.effectiveness import (
    calculate_unit_effectiveness,
    calculate_deployment_effectiveness,
    calculate_response_effectiveness,
    calculate_security_readiness,
    calculate_success_rate,
    calculate_deployment_utilization,
    calculate_operational_efficiency,
    security_performance_report,
)

from security.resources import (
    initialize_resources,
    reserve_resource,
    release_resource,
    resource_summary,
)

from security.personnel import (
    allocate_personnel,
    release_personnel,
    validate_allocations,
    put_on_maintenance,
    advance_personnel_recovery,
    personnel_summary,
)

from security.operations import (
    create_incident,
    resolve_incident,
    fail_incident,
    incident_summary,
    recent_operations,
    log_operation,
)

__all__ = [
    # Engine
    "SecurityEngine",

    # Models
    "SecurityState",
    "SecurityUnit",
    "SecurityDepartment",
    "SecurityIncident",
    "SecurityDeployment",
    "SecurityResource",
    "SecurityLogEntry",

    # Enums
    "UnitType",
    "UnitStatus",
    "IncidentType",
    "IncidentStatus",
    "DeploymentStatus",

    # Effectiveness
    "calculate_unit_effectiveness",
    "calculate_deployment_effectiveness",
    "calculate_response_effectiveness",
    "calculate_security_readiness",
    "calculate_success_rate",
    "calculate_deployment_utilization",
    "calculate_operational_efficiency",
    "security_performance_report",

    # Resources
    "initialize_resources",
    "reserve_resource",
    "release_resource",
    "resource_summary",

    # Personnel
    "allocate_personnel",
    "release_personnel",
    "validate_allocations",
    "put_on_maintenance",
    "advance_personnel_recovery",
    "personnel_summary",

    # Operations
    "create_incident",
    "resolve_incident",
    "fail_incident",
    "incident_summary",
    "recent_operations",
    "log_operation",
]
