
"""Security incident creation, lifecycle and operational logging."""

from uuid import uuid4

from security.models import (
    SecurityIncident,
    SecurityLogEntry,
    UnitType,
    IncidentType,
    IncidentStatus,
    DeploymentStatus,
)

from security.deployment import (
    complete_deployment,
    recall_deployment,
)


INCIDENT_DEFAULTS = {
    IncidentType.CRIME: {
        "response": [UnitType.POLICE],
        "deadline": 3,
    },
    IncidentType.FIRE: {
        "response": [UnitType.FIRE],
        "deadline": 2,
    },
    IncidentType.MEDICAL: {
        "response": [UnitType.MEDICAL],
        "deadline": 2,
    },
    IncidentType.INFRASTRUCTURE: {
        "response": [UnitType.ENGINEERING],
        "deadline": 4,
    },
    IncidentType.PUBLIC_DISORDER: {
        "response": [UnitType.POLICE, UnitType.MEDICAL],
        "deadline": 3,
    },
    IncidentType.DISASTER: {
        "response": [
            UnitType.POLICE,
            UnitType.FIRE,
            UnitType.MEDICAL,
            UnitType.RESCUE,
            UnitType.ENGINEERING,
            UnitType.EVACUATION,
        ],
        "deadline": 5,
    },
}

def _log(
    state,
    day: int,
    category: str,
    message: str,
    severity: str = "INFO",
    metadata: dict | None = None,
):
    """Append an operational log entry."""

    state.log_sequence += 1

    entry = SecurityLogEntry(
        id=f"SEC-LOG-{state.log_sequence:06d}",
        day=day,
        category=category,
        message=message,
        severity=severity,
        metadata=metadata or {},
    )

    state.operations_log.append(entry)

    return entry


def log_operation(
    state,
    day: int,
    category: str,
    message: str,
    severity: str = "INFO",
    metadata: dict | None = None,
):
    return _log(
        state,
        day,
        category,
        message,
        severity,
        metadata,
    )


def create_incident(
    city,
    title: str,
    description: str,
    incident_type: IncidentType,
    district_id: str,
    severity: int = 50,
    population_at_risk: int = 0,
    deadline_days: int | None = None,
    created_by_disaster: bool = False,
    disaster_id: str | None = None,
):
    """Create and register a security incident."""

    state = city.security

    if not title.strip():
        raise ValueError("Incident title cannot be empty.")

    if not 1 <= severity <= 100:
        raise ValueError("Severity must be between 1 and 100.")

    if population_at_risk < 0:
        raise ValueError("Population at risk cannot be negative.")

    if district_id not in {
        district.id
        for district in city.districts
    }:
        raise ValueError(
            f"Unknown district: {district_id}"
        )

    defaults = INCIDENT_DEFAULTS[incident_type]

    if deadline_days is None:
        deadline_days = defaults["deadline"]

    if deadline_days < 1: # type: ignore
        raise ValueError(
            "Incident deadline must be at least one day."
        )

    state.incident_sequence += 1

    incident_id = (
        f"INC-{state.incident_sequence:05d}"
    )

    incident = SecurityIncident(
        id=incident_id,
        title=title.strip(),
        description=description.strip(),
        incident_type=incident_type,
        status=IncidentStatus.DETECTED,
        district_id=district_id,
        severity=severity,
        population_at_risk=population_at_risk,
        detected_day=city.day,
        deadline_day=city.day + deadline_days,
        required_response=defaults["response"],
        response_progress=0.0,
        created_by_disaster=created_by_disaster,
        disaster_id=disaster_id,
    )

    state.incidents.append(incident)

    _log(
        state,
        city.day,
        "INCIDENT",
        f"Incident detected: {incident.title}",
        "WARNING" if severity >= 70 else "INFO",
        {
            "incident_id": incident.id,
            "district_id": district_id,
            "severity": severity,
        },
    )

    return incident


def get_incident(state, incident_id: str):
    """Retrieve an incident by ID."""

    incident = next(
        (
            item
            for item in state.incidents
            if item.id == incident_id
        ),
        None,
    )

    if incident is None:
        raise ValueError(
            f"Unknown incident: {incident_id}"
        )

    return incident


def update_incident_progress(
    state,
    incident,
    progress: float,
):
    """Increase response progress for an incident."""

    if incident.status not in {
        IncidentStatus.DETECTED,
        IncidentStatus.ACTIVE,
    }:
        raise ValueError(
            "Incident cannot receive additional progress."
        )

    if not 0 <= progress <= 100:
        raise ValueError(
            "Progress must be between 0 and 100."
        )

    incident.response_progress = min(
        100.0,
        incident.response_progress + progress,
    )

    incident.status = IncidentStatus.ACTIVE

    return incident


def resolve_incident(
    city,
    incident,
):
    """Resolve an incident and complete its active deployments."""

    state = city.security

    if incident.status in {
        IncidentStatus.RESOLVED,
        IncidentStatus.FAILED,
    }:
        raise ValueError(
            "Incident is already closed."
        )

    for deployment_id in incident.assigned_deployment_ids:

        deployment = next(
            (
                item
                for item in state.deployments
                if item.id == deployment_id
            ),
            None,
        )

        if deployment is None:
            continue

        if deployment.status in {
            DeploymentStatus.DISPATCHED,
            DeploymentStatus.EN_ROUTE,
            DeploymentStatus.ON_SCENE,
        }:
            complete_deployment(
                state,
                deployment,
            )

    incident.status = IncidentStatus.RESOLVED
    incident.resolved_day = city.day
    incident.response_progress = 100.0

    state.successful_operations += 1

    _log(
        state,
        city.day,
        "RESOLUTION",
        f"Incident resolved: {incident.title}",
        "SUCCESS",
        {"incident_id": incident.id},
    )

    return incident


def fail_incident(
    city,
    incident,
    reason: str = "Response deadline exceeded.",
):
    """Mark an incident as failed and recall active deployments."""

    state = city.security

    if incident.status in {
        IncidentStatus.RESOLVED,
        IncidentStatus.FAILED,
    }:
        raise ValueError(
            "Incident is already closed."
        )

    for deployment_id in incident.assigned_deployment_ids:

        deployment = next(
            (
                item
                for item in state.deployments
                if item.id == deployment_id
            ),
            None,
        )

        if deployment is None:
            continue

        if deployment.status in {
            DeploymentStatus.DISPATCHED,
            DeploymentStatus.EN_ROUTE,
            DeploymentStatus.ON_SCENE,
        }:
            recall_deployment(
                state,
                deployment,
            )

    incident.status = IncidentStatus.FAILED

    state.failed_operations += 1

    _log(
        state,
        city.day,
        "FAILURE",
        f"Incident failed: {incident.title}. {reason}",
        "CRITICAL",
        {"incident_id": incident.id},
    )

    return incident


def advance_incidents(city):
    """Check unresolved incidents against their deadlines."""

    state = city.security

    failed = []

    for incident in state.incidents:

        if incident.status not in {
            IncidentStatus.DETECTED,
            IncidentStatus.ACTIVE,
        }:
            continue

        if city.day > incident.deadline_day:

            fail_incident(
                city,
                incident,
            )

            failed.append(incident)

    return failed


def incident_summary(state):
    """Return incident counts grouped by status."""

    return {
        status.value: sum(
            incident.status == status
            for incident in state.incidents
        )
        for status in IncidentStatus
    }


def recent_operations(
    state,
    limit: int = 20,
):
    """Return the latest operational log entries."""

    if limit < 1:
        raise ValueError("Limit must be positive.")

    return list(
        reversed(state.operations_log[-limit:])
    )
