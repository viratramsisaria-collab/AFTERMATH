
"""Centralized entity lookup and registry utilities."""

from security.models import (
    DeploymentStatus,
    IncidentStatus,
)


# ─────────────────────────────────────────────
# GENERIC LOOKUP
# ─────────────────────────────────────────────

def find_by_id(
    items: list,
    identifier: str,
    label: str,
):

    item = next(
        (
            entry
            for entry in items
            if entry.id == identifier
        ),
        None,
    )

    if item is None:
        raise ValueError(
            f"Unknown {label}: {identifier}"
        )

    return item


# ─────────────────────────────────────────────
# ENTITY LOOKUPS
# ─────────────────────────────────────────────

def get_unit(
    state,
    unit_id: str,
):
    return find_by_id(
        state.units,
        unit_id,
        "security unit",
    )


def get_incident(
    state,
    incident_id: str,
):
    return find_by_id(
        state.incidents,
        incident_id,
        "security incident",
    )


def get_deployment(
    state,
    deployment_id: str,
):
    return find_by_id(
        state.deployments,
        deployment_id,
        "security deployment",
    )


def get_resource(
    state,
    resource_id: str,
):
    return find_by_id(
        state.resources,
        resource_id,
        "security resource",
    )


# ─────────────────────────────────────────────
# ACTIVE ENTITY FILTERS
# ─────────────────────────────────────────────

def active_deployments(
    state,
    incident_id: str | None = None,
):

    active_statuses = {
        DeploymentStatus.DISPATCHED,
        DeploymentStatus.EN_ROUTE,
        DeploymentStatus.ON_SCENE,
    }

    return [

        deployment

        for deployment in state.deployments

        if deployment.status in active_statuses

        and (
            incident_id is None
            or deployment.incident_id == incident_id
        )

    ]


def active_incidents(state):

    active_statuses = {
        IncidentStatus.DETECTED,
        IncidentStatus.ACTIVE,
    }

    return [

        incident

        for incident in state.incidents

        if incident.status in active_statuses

    ]
