
"""Emergency mobilization and department activation."""

from security.models import (
    UnitStatus,
    IncidentStatus,
)


# ─────────────────────────────────────────────
# DEPARTMENT MOBILIZATION
# ─────────────────────────────────────────────

def mobilize_department(
    city,
    department_id: str,
):

    state = city.security

    department = next(
        (
            item
            for item in state.departments
            if item.id == department_id
        ),
        None,
    )

    if department is None:
        raise ValueError(
            f"Unknown department: {department_id}"
        )

    if not department.active:
        raise ValueError(
            "Cannot mobilize an inactive department."
        )

    units = [

        unit

        for unit in state.units

        if unit.department_id == department_id

    ]

    mobilized_units = []

    for unit in units:

        if unit.status == UnitStatus.RESTING:
            unit.status = UnitStatus.AVAILABLE

        if (
            unit.status == UnitStatus.AVAILABLE
            and unit.available_personnel > 0
        ):
            mobilized_units.append(unit.id)

    state.total_mobilizations += 1

    return {

        "department_id": department_id,

        "mobilized_units": mobilized_units,

        "count": len(mobilized_units),

    }


# ─────────────────────────────────────────────
# INCIDENT MOBILIZATION
# ─────────────────────────────────────────────

def mobilize_for_incident(
    city,
    incident_id: str,
):

    state = city.security

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

    if incident.status not in {
        IncidentStatus.DETECTED,
        IncidentStatus.ACTIVE,
    }:
        raise ValueError(
            "Incident is not active."
        )

    departments = [

        department

        for department in state.departments

        if (
            department.unit_type
            in incident.required_response
            and department.active
        )

    ]

    results = [

        mobilize_department(
            city,
            department.id,
        )

        for department in departments

    ]

    return {

        "incident_id": incident_id,

        "departments": results,

    }


# ─────────────────────────────────────────────
# DEPARTMENT ACTIVATION / DEACTIVATION
# ─────────────────────────────────────────────

def set_department_status(
    state,
    department_id: str,
    active: bool,
):

    department = next(
        (
            item
            for item in state.departments
            if item.id == department_id
        ),
        None,
    )

    if department is None:
        raise ValueError(
            f"Unknown department: {department_id}"
        )

    if not active:

        has_active_deployments = any(

            unit.active_deployments

            for unit in state.units

            if unit.department_id == department_id

        )

        if has_active_deployments:
            raise ValueError(
                "Cannot deactivate a department "
                "with active deployments."
            )

    department.active = active

    return department
