
"""Security unit dispatch, deployment tracking and recall."""

from uuid import uuid4

from security.models import (
    SecurityDeployment,
    DeploymentStatus,
    IncidentStatus,
    UnitStatus,
)

from security.personnel import (
    allocate_personnel,
    release_personnel,
    validate_allocations,
)


def _generate_deployment_id(state) -> str:
    """Generate a unique deployment identifier."""

    state.deployment_sequence += 1

    return f"DEP-{state.deployment_sequence:05d}"


def dispatch_units(
    city,
    incident,
    units,
    allocations: dict[str, int] | None = None,
    arrival_days: int = 1,
    daily_cost_per_person: float = 12.0,
):
    """Dispatch selected units to a security incident."""

    state = city.security

    if incident not in state.incidents:
        raise ValueError("Incident does not belong to this city.")

    if incident.status not in {
        IncidentStatus.DETECTED,
        IncidentStatus.ACTIVE,
    }:
        raise ValueError("Incident is not accepting deployments.")

    if not units:
        raise ValueError("At least one unit must be selected.")

    if arrival_days < 0:
        raise ValueError("Arrival days cannot be negative.")

    if daily_cost_per_person < 0:
        raise ValueError("Daily cost cannot be negative.")

    selected_ids = [unit.id for unit in units]

    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError("Duplicate units cannot be deployed.")

    allocations_by_unit = validate_allocations(
        units,
        allocations,
    )

    deployment_id = _generate_deployment_id(state)

    personnel = sum(allocations_by_unit.values())

    daily_cost = personnel * daily_cost_per_person

    deployment = SecurityDeployment(
        id=deployment_id,
        unit_ids=selected_ids,
        personnel_allocations=allocations_by_unit,
        incident_id=incident.id,
        district_id=incident.district_id,
        personnel=personnel,
        status=(
            DeploymentStatus.ON_SCENE
            if arrival_days == 0
            else DeploymentStatus.DISPATCHED
        ),
        dispatched_day=city.day,
        arrival_day=city.day + arrival_days,
        remaining_days=arrival_days,
        progress=0.0,
        daily_cost=daily_cost,
        total_cost=0.0,
    )

    allocated_units = []

    try:
        for unit in units:
            allocate_personnel(
                unit,
                allocations_by_unit[unit.id],
                deployment_id,
            )
            allocated_units.append(unit)

        state.deployments.append(deployment)

        incident.assigned_deployment_ids.append(
            deployment_id
        )

        incident.status = IncidentStatus.ACTIVE

        state.total_deployments += 1

    except Exception:
        for unit in allocated_units:
            amount = allocations_by_unit[unit.id]

            unit.available_personnel = min(
                unit.personnel,
                unit.available_personnel + amount,
            )

            if deployment_id in unit.active_deployments:
                unit.active_deployments.remove(deployment_id)

            if not unit.active_deployments:
                unit.status = UnitStatus.AVAILABLE

        raise

    return deployment


def mark_arrived(deployment):
    """Mark a dispatched deployment as on scene."""

    if deployment.status not in {
        DeploymentStatus.DISPATCHED,
        DeploymentStatus.EN_ROUTE,
    }:
        raise ValueError(
            "Only dispatched or en-route deployments can arrive."
        )

    deployment.status = DeploymentStatus.ON_SCENE
    deployment.remaining_days = 0

    return deployment


def update_deployment_progress(
    deployment,
    progress: float,
):
    """Update deployment progress using a percentage."""

    if deployment.status != DeploymentStatus.ON_SCENE:
        raise ValueError(
            "Deployment must be on scene to make progress."
        )

    if not 0 <= progress <= 100:
        raise ValueError(
            "Progress must be between 0 and 100."
        )

    deployment.progress = min(
        100.0,
        deployment.progress + progress,
    )

    return deployment


def complete_deployment(
    state,
    deployment,
):
    """Complete a deployment and release its personnel."""

    if deployment.status in {
        DeploymentStatus.COMPLETED,
        DeploymentStatus.RECALLED,
        DeploymentStatus.FAILED,
    }:
        return deployment

    deployment.status = DeploymentStatus.COMPLETED

    deployment.progress = 100.0

    release_personnel(
        state,
        deployment,
    )

    return deployment


def recall_deployment(
    state,
    deployment,
):
    """Recall an active deployment and release its personnel."""

    if deployment.status in {
        DeploymentStatus.COMPLETED,
        DeploymentStatus.RECALLED,
        DeploymentStatus.FAILED,
    }:
        raise ValueError(
            "Deployment is already inactive."
        )

    deployment.status = DeploymentStatus.RECALLED

    release_personnel(
        state,
        deployment,
    )

    return deployment


def fail_deployment(
    state,
    deployment,
    reason: str,
):
    """Mark a deployment as failed and release personnel."""

    if deployment.status in {
        DeploymentStatus.COMPLETED,
        DeploymentStatus.RECALLED,
        DeploymentStatus.FAILED,
    }:
        raise ValueError(
            "Deployment is already inactive."
        )

    deployment.status = DeploymentStatus.FAILED
    deployment.failure_reason = reason

    release_personnel(
        state,
        deployment,
    )

    return deployment


def advance_deployments(city):
    """Advance travel timers and accumulate operational costs."""

    state = city.security

    advanced = []

    for deployment in state.deployments:

        if deployment.status not in {
            DeploymentStatus.DISPATCHED,
            DeploymentStatus.EN_ROUTE,
            DeploymentStatus.ON_SCENE,
        }:
            continue

        deployment.total_cost += deployment.daily_cost

        if deployment.status == DeploymentStatus.DISPATCHED:
            deployment.status = DeploymentStatus.EN_ROUTE

        if deployment.remaining_days > 0:
            deployment.remaining_days -= 1

        if deployment.remaining_days <= 0:
            deployment.status = DeploymentStatus.ON_SCENE

        advanced.append(deployment)

    state.total_operational_cost += sum(
        deployment.daily_cost
        for deployment in advanced
    )

    return advanced
