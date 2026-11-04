
"""Personnel allocation, release, readiness and maintenance."""

from security.models import UnitStatus
from security.registry import get_unit


# ─────────────────────────────────────────────
# PERSONNEL ALLOCATION
# ─────────────────────────────────────────────

def allocate_personnel(
    unit,
    amount: int,
    deployment_id: str,
):

    if (
        not isinstance(amount, int)
        or isinstance(amount, bool)
        or amount < 1
    ):
        raise ValueError(
            "Personnel allocation must be a positive integer."
        )

    if unit.status in {
        UnitStatus.MAINTENANCE,
        UnitStatus.RESTING,
    }:
        raise ValueError(
            f"{unit.name} is unavailable."
        )

    if unit.available_personnel < amount:
        raise ValueError(
            f"{unit.name} has only "
            f"{unit.available_personnel} personnel available."
        )

    unit.available_personnel -= amount

    if deployment_id not in unit.active_deployments:
        unit.active_deployments.append(deployment_id)

    unit.status = UnitStatus.DEPLOYED


# ─────────────────────────────────────────────
# PERSONNEL RELEASE
# ─────────────────────────────────────────────

def release_personnel(
    state,
    deployment,
):

    for (
        unit_id,
        amount,
    ) in deployment.personnel_allocations.items():

        unit = get_unit(
            state,
            unit_id,
        )

        if deployment.id in unit.active_deployments:

            unit.active_deployments.remove(
                deployment.id
            )

            unit.available_personnel = min(
                unit.personnel,
                unit.available_personnel + amount,
            )

        if (
            not unit.active_deployments
            and unit.status == UnitStatus.DEPLOYED
        ):
            unit.status = UnitStatus.AVAILABLE


# ─────────────────────────────────────────────
# VALIDATE PERSONNEL ALLOCATIONS
# ─────────────────────────────────────────────

def validate_allocations(
    units,
    requested: dict[str, int] | None = None,
):

    if requested is not None:

        selected_ids = {
            unit.id
            for unit in units
        }

        if set(requested) != selected_ids:
            raise ValueError(
                "Provide an allocation for every selected unit "
                "and no other units."
            )

    allocations = {}

    for unit in units:

        amount = (
            requested[unit.id]
            if requested is not None
            else unit.available_personnel
        )

        if (
            not isinstance(amount, int)
            or isinstance(amount, bool)
            or amount < 1
        ):
            raise ValueError(
                "Each personnel allocation must be a positive integer."
            )

        if unit.status in {
            UnitStatus.MAINTENANCE,
            UnitStatus.RESTING,
        }:
            raise ValueError(
                f"{unit.name} is unavailable."
            )

        if amount > unit.available_personnel:
            raise ValueError(
                f"{unit.name} only has "
                f"{unit.available_personnel} personnel available."
            )

        allocations[unit.id] = amount

    return allocations


# ─────────────────────────────────────────────
# MAINTENANCE
# ─────────────────────────────────────────────

def put_on_maintenance(
    city,
    unit,
    duration_days: int,
):

    if (
        not isinstance(duration_days, int)
        or isinstance(duration_days, bool)
        or duration_days < 1
    ):
        raise ValueError(
            "Maintenance must last at least one day."
        )

    if unit.active_deployments:
        raise ValueError(
            "Recall active deployments before maintenance."
        )

    unit.status = UnitStatus.MAINTENANCE

    unit.maintenance_until_day = (
        city.day + duration_days
    )


# ─────────────────────────────────────────────
# PERSONNEL RECOVERY
# ─────────────────────────────────────────────

def advance_personnel_recovery(city):

    for unit in city.security.units:

        if unit.status == UnitStatus.MAINTENANCE:

            if (
                unit.maintenance_until_day is not None
                and city.day >= unit.maintenance_until_day
            ):

                unit.status = UnitStatus.AVAILABLE

                unit.maintenance_until_day = None

                unit.readiness = min(
                    100,
                    unit.readiness + 10,
                )

        elif not unit.active_deployments:

            unit.readiness = min(
                100,
                unit.readiness + 1,
            )

            if (
                unit.available_personnel == unit.personnel
                and unit.status == UnitStatus.DEPLOYED
            ):
                unit.status = UnitStatus.AVAILABLE


# ─────────────────────────────────────────────
# PERSONNEL SUMMARY
# ─────────────────────────────────────────────

def personnel_summary(state):

    return {

        "total": state.total_personnel,

        "available": state.available_personnel,

        "deployed": (
            state.total_personnel
            - state.available_personnel
        ),

        "units": [

            {
                "id": unit.id,

                "name": unit.name,

                "type": unit.unit_type.value,

                "personnel": unit.personnel,

                "available": unit.available_personnel,

                "readiness": unit.readiness,

                "status": unit.status.value,

            }

            for unit in state.units

        ],

    }
