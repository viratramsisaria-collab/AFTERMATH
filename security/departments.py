
"""Security department definitions and management."""

from security.models import (
    SecurityDepartment,
    UnitType,
)


# ─────────────────────────────────────────────
# DEPARTMENT BLUEPRINTS
# ─────────────────────────────────────────────

DEPARTMENT_BLUEPRINTS = (

    (
        "DEP-POL",
        "Metropolitan Police",
        UnitType.POLICE,
        "Public safety, crime prevention and crowd control.",
    ),

    (
        "DEP-FIR",
        "Fire and Rescue",
        UnitType.FIRE,
        "Fire suppression and hazardous-scene response.",
    ),

    (
        "DEP-MED",
        "Emergency Medical Services",
        UnitType.MEDICAL,
        "Emergency treatment, triage and medical transport.",
    ),

    (
        "DEP-RES",
        "Urban Search and Rescue",
        UnitType.RESCUE,
        "Search operations, extraction and technical rescue.",
    ),

    (
        "DEP-ENG",
        "Infrastructure Response",
        UnitType.ENGINEERING,
        "Critical infrastructure inspection and repair support.",
    ),

    (
        "DEP-EVC",
        "Civil Protection and Evacuation",
        UnitType.EVACUATION,
        "Public warning, evacuation and shelter coordination.",
    ),
)


# ─────────────────────────────────────────────
# DEPARTMENT CONSTRUCTION
# ─────────────────────────────────────────────

def build_departments(
    district_ids: set[str],
) -> list[SecurityDepartment]:

    headquarters = (
        sorted(district_ids)[0]
        if district_ids
        else None
    )

    departments = []

    for (
        department_id,
        name,
        unit_type,
        description,
    ) in DEPARTMENT_BLUEPRINTS:

        department = SecurityDepartment(
            id=department_id,
            name=name,
            unit_type=unit_type,
            description=description,
            headquarters_district_id=headquarters,
        )

        departments.append(department)

    return departments


# ─────────────────────────────────────────────
# DEPARTMENT LOOKUP
# ─────────────────────────────────────────────

def get_department(
    state,
    department_id: str,
) -> SecurityDepartment:

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
            f"Unknown security department: {department_id}"
        )

    return department


# ─────────────────────────────────────────────
# DEPARTMENT SUMMARY
# ─────────────────────────────────────────────

def department_summary(state) -> list[dict]:

    results = []

    for department in state.departments:

        units = [
            unit
            for unit in state.units
            if unit.department_id == department.id
        ]

        results.append({

            "id": department.id,

            "name": department.name,

            "unit_type": department.unit_type.value,

            "units": len(units),

            "personnel": sum(
                unit.personnel
                for unit in units
            ),

            "available_personnel": sum(
                unit.available_personnel
                for unit in units
            ),

            "active": department.active,

        })

    return results
