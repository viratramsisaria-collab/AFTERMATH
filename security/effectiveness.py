
"""Security response effectiveness and performance metrics."""

from security.models import (
    IncidentStatus,
    DeploymentStatus,
    UnitStatus,
)


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    return max(
        minimum,
        min(maximum, value),
    )


def calculate_unit_effectiveness(unit) -> float:
    """Calculate a unit's operational readiness score."""

    readiness = clamp(unit.readiness)

    personnel_ratio = (
        unit.available_personnel / unit.personnel
        if unit.personnel > 0
        else 0.0
    )

    equipment = clamp(unit.equipment_rating)

    if unit.status == UnitStatus.MAINTENANCE:
        status_factor = 0.0
    elif unit.status == UnitStatus.RESTING:
        status_factor = 0.5
    else:
        status_factor = 1.0

    score = (
        readiness * 0.35
        + personnel_ratio * 100 * 0.30
        + equipment * 0.35
    )

    return round(
        clamp(score * status_factor),
        2,
    )


def calculate_deployment_effectiveness(
    deployment,
    units,
) -> float:
    """Calculate deployment effectiveness from its assigned units."""

    if not units:
        return 0.0

    unit_scores = [
        calculate_unit_effectiveness(unit)
        for unit in units
    ]

    average_score = sum(unit_scores) / len(unit_scores)

    progress_factor = clamp(deployment.progress) / 100

    if deployment.status == DeploymentStatus.COMPLETED:
        progress_factor = 1.0

    if deployment.status in {
        DeploymentStatus.FAILED,
        DeploymentStatus.RECALLED,
    }:
        return 0.0

    return round(
        average_score * (0.5 + 0.5 * progress_factor),
        2,
    )


def calculate_response_effectiveness(
    incident,
    deployments,
) -> float:
    """Evaluate the response coverage and progress for an incident."""

    if incident.status == IncidentStatus.FAILED:
        return 0.0

    if incident.status == IncidentStatus.RESOLVED:
        return 100.0

    active_deployments = [
        deployment
        for deployment in deployments
        if deployment.status in {
            DeploymentStatus.DISPATCHED,
            DeploymentStatus.EN_ROUTE,
            DeploymentStatus.ON_SCENE,
            DeploymentStatus.COMPLETED,
        }
    ]

    if not active_deployments:
        return round(
            clamp(incident.response_progress) * 0.5,
            2,
        )

    total_personnel = sum(
        deployment.personnel
        for deployment in active_deployments
    )

    progress = clamp(
        incident.response_progress
    )

    coverage = min(
        100.0,
        total_personnel / max(
            1,
            incident.population_at_risk,
        ) * 100,
    )

    score = (
        progress * 0.7
        + coverage * 0.3
    )

    return round(
        clamp(score),
        2,
    )


def calculate_security_readiness(state) -> float:
    """Calculate the overall security force readiness."""

    if not state.units:
        return 0.0

    scores = [
        calculate_unit_effectiveness(unit)
        for unit in state.units
    ]

    return round(
        sum(scores) / len(scores),
        2,
    )


def calculate_success_rate(state) -> float:
    """Calculate the percentage of successful closed operations."""

    total = (
        state.successful_operations
        + state.failed_operations
    )

    if total == 0:
        return 100.0

    return round(
        state.successful_operations / total * 100,
        2,
    )


def calculate_deployment_utilization(state) -> float:
    """Calculate the percentage of personnel currently deployed."""

    total = state.total_personnel

    if total == 0:
        return 0.0

    deployed = total - state.available_personnel

    return round(
        clamp(deployed / total * 100),
        2,
    )


def calculate_operational_efficiency(state) -> float:
    """Combine readiness, success rate and deployment utilization."""

    readiness = calculate_security_readiness(state)

    success_rate = calculate_success_rate(state)

    utilization = calculate_deployment_utilization(state)

    # High utilization is not automatically good:
    # excessive deployment reduces reserve capacity.
    utilization_score = 100.0 - abs(
        utilization - 55.0
    )

    return round(
        clamp(
            readiness * 0.40
            + success_rate * 0.40
            + utilization_score * 0.20
        ),
        2,
    )


def security_performance_report(state) -> dict:
    """Return a consolidated security performance report."""

    return {
        "readiness": calculate_security_readiness(state),

        "success_rate": calculate_success_rate(state),

        "deployment_utilization": (
            calculate_deployment_utilization(state)
        ),

        "operational_efficiency": (
            calculate_operational_efficiency(state)
        ),

        "total_personnel": state.total_personnel,

        "available_personnel": state.available_personnel,

        "active_deployments": state.active_deployments,

        "active_incidents": state.active_incidents,

        "successful_operations": state.successful_operations,

        "failed_operations": state.failed_operations,

        "total_operational_cost": (
            round(state.total_operational_cost, 2)
        ),
    }
