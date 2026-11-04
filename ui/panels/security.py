
"""Security Command Centre — public safety operations and emergency response."""

from __future__ import annotations

import streamlit as st

from security.engine import SecurityEngine
from security.models import (
    DeploymentStatus,
    IncidentStatus,
    IncidentType,
    UnitStatus,
)
from ui.state import persist_city


def _value(value) -> str:
    return str(getattr(value, "value", value)).replace("_", " ").title()


def _money(value: float) -> str:
    return f"${value:,.0f}"


def _unit_label(unit) -> str:
    return (
        f"{unit.name} · {_value(unit.unit_type)} · "
        f"{unit.available_personnel:,} available"
    )


def _render_records(records: list[dict]) -> None:
    """Render records without using st.dataframe or Pandas."""
    if not records:
        st.info("No records available.")
        return

    for record in records:
        with st.container(border=True):
            for label, value in record.items():
                st.write(f"**{label}:** {value}")


def render_security_center(city) -> None:
    """Render the Security Command Centre."""

    engine = SecurityEngine()
    state = engine.initialize(city)
    dashboard = engine.get_dashboard(city)

    st.title("🛡️ Security Command Centre")
    st.caption(
        "Coordinate public safety departments, deploy emergency units, "
        "and monitor city-wide security operations."
    )

    # ------------------------------------------------------------------
    # Overview metrics
    # ------------------------------------------------------------------

    metric_cols = st.columns(4)
    metric_cols[0].metric("Total Personnel", f"{state.total_personnel:,}")
    metric_cols[1].metric(
        "Available Personnel",
        f"{state.available_personnel:,}",
    )
    metric_cols[2].metric("Active Incidents", f"{state.active_incidents:,}")
    metric_cols[3].metric(
        "Active Deployments",
        f"{state.active_deployments:,}",
    )

    tabs = st.tabs(
        [
            "Overview",
            "Incidents",
            "Units & Departments",
            "Resources",
            "Operations Log",
        ]
    )

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------

    with tabs[0]:
        st.subheader("Department Readiness")

        departments = list(state.departments)

        if departments:
            for department in departments:
                with st.container(border=True):
                    cols = st.columns([3, 2, 2])

                    cols[0].markdown(f"**{department.name}**")
                    cols[1].write(_value(department.unit_type))
                    cols[2].write(
                        "Active" if department.active else "Inactive"
                    )

                    st.caption(
                        department.description or "No description available."
                    )
                    st.write(
                        f"Registered units: {len(department.unit_ids)}"
                    )
        else:
            st.info("No security departments are currently registered.")

        st.subheader("Operational Performance")

        performance_cols = st.columns(3)

        performance_items = [
            ("Successful Operations", state.successful_operations),
            ("Failed Operations", state.failed_operations),
            ("Total Deployments", state.total_deployments),
        ]

        for column, (label, value) in zip(
            performance_cols,
            performance_items,
        ):
            column.metric(label, f"{value:,}")

        st.metric(
            "Total Operational Cost",
            _money(state.total_operational_cost),
        )

        st.subheader("Active Deployments")

        active = [
            deployment
            for deployment in state.deployments
            if deployment.status
            not in {
                DeploymentStatus.COMPLETED,
                DeploymentStatus.FAILED,
                DeploymentStatus.RECALLED,
            }
        ]

        if active:
            rows = []

            for deployment in active:
                rows.append(
                    {
                        "Deployment": deployment.id,
                        "Incident": deployment.incident_id or "Disaster response",
                        "Personnel": deployment.personnel,
                        "Status": _value(deployment.status),
                        "Progress": f"{deployment.progress:.1f}%",
                        "Daily Cost": _money(deployment.daily_cost),
                    }
                )

            _render_records(rows)
        else:
            st.info("There are no active deployments.")

    # ------------------------------------------------------------------
    # Incidents
    # ------------------------------------------------------------------

    with tabs[1]:
        st.subheader("Incident Management")

        district_options = {
            district.id: district.name
            for district in city.districts
        }

        with st.expander("＋ Register New Incident", expanded=False):
            if not district_options:
                st.warning("No districts are available.")
            else:
                with st.form("security_create_incident"):
                    incident_type = st.selectbox(
                        "Incident Type",
                        options=list(IncidentType),
                        format_func=_value,
                    )

                    district_id = st.selectbox(
                        "District",
                        options=list(district_options),
                        format_func=lambda value: district_options[value],
                    )

                    severity = st.slider(
                        "Severity",
                        min_value=1,
                        max_value=10,
                        value=5,
                    )

                    title = st.text_input("Incident Title")
                    description = st.text_area("Description")

                    population_at_risk = st.number_input(
                        "Population at Risk",
                        min_value=0,
                        value=0,
                        step=100,
                    )

                    deadline_days = st.number_input(
                        "Response Deadline (days)",
                        min_value=1,
                        max_value=30,
                        value=3,
                    )

                    submitted = st.form_submit_button(
                        "Register Incident",
                        width="stretch",
                    )

                    if submitted:
                        try:
                            engine.create_incident(
                                city=city,
                                incident_type=incident_type,
                                district_id=district_id, # type: ignore
                                severity=severity,
                                title=title.strip() or None,
                                description=description.strip() or None,
                                deadline_days=int(deadline_days),
                                population_at_risk=int(population_at_risk),
                            )
                            persist_city()
                            st.success("Incident registered.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Could not register incident: {exc}")

        all_incidents = list(state.incidents)

        status_filter = st.selectbox(
            "Filter incidents",
            [
                "All",
                "Detected",
                "Active",
                "Contained",
                "Resolved",
                "Failed",
            ],
        )

        filtered_incidents = all_incidents

        if status_filter != "All":
            filtered_incidents = [
                incident
                for incident in all_incidents
                if _value(incident.status) == status_filter
            ]

        if not filtered_incidents:
            st.info("No incidents match this filter.")
        else:
            for incident in sorted(
                filtered_incidents,
                key=lambda item: item.detected_day,
                reverse=True,
            ):
                with st.container(border=True):
                    heading_cols = st.columns([4, 1])

                    heading_cols[0].markdown(
                        f"**{incident.title or incident.id}**"
                    )
                    heading_cols[0].caption(
                        f"{incident.id} · {_value(incident.incident_type)}"
                    )
                    heading_cols[1].write(_value(incident.status))

                    district_name = district_options.get(
                        incident.district_id,
                        incident.district_id,
                    )

                    st.write(
                        f"**District:** {district_name}  ·  "
                        f"**Severity:** {incident.severity}/10  ·  "
                        f"**Population at risk:** "
                        f"{incident.population_at_risk:,}"
                    )

                    if incident.description:
                        st.write(incident.description)

                    required_types = set(incident.required_response)

                    st.caption(
                        "Required response: "
                        + (
                            ", ".join(
                                _value(item) for item in required_types
                            )
                            or "Not specified"
                        )
                    )

                    if incident.status in {
                        IncidentStatus.DETECTED,
                        IncidentStatus.ACTIVE,
                    }:
                        eligible_units = [
                            unit
                            for unit in state.units
                            if unit.status == UnitStatus.AVAILABLE
                            and unit.available_personnel > 0
                            and unit.unit_type in required_types
                        ]

                        if eligible_units:
                            units_by_id = {
                                unit.id: unit
                                for unit in eligible_units
                            }

                            with st.form(f"dispatch_{incident.id}"):
                                selected_unit_ids = st.multiselect(
                                    "Select response units",
                                    options=list(units_by_id),
                                    format_func=lambda unit_id: _unit_label(
                                        units_by_id[unit_id]
                                    ),
                                    key=f"units_{incident.id}",
                                )

                                dispatch_submitted = st.form_submit_button(
                                    "Dispatch Selected Units",
                                    width="stretch",
                                )

                                if dispatch_submitted:
                                    if not selected_unit_ids:
                                        st.warning(
                                            "Select at least one response unit."
                                        )
                                    else:
                                        try:
                                            engine.dispatch(
                                                city=city,
                                                incident_id=incident.id,
                                                unit_ids=selected_unit_ids,
                                            )
                                            persist_city()
                                            st.success(
                                                f"Units dispatched to {incident.id}."
                                            )
                                            st.rerun()
                                        except Exception as exc:
                                            st.error(f"Dispatch failed: {exc}")
                        else:
                            st.warning(
                                "No available units currently match this "
                                "incident's required response."
                            )

        st.divider()
        st.subheader("Deployment Controls")

        active_deployments = [
            deployment
            for deployment in state.deployments
            if deployment.status
            not in {
                DeploymentStatus.COMPLETED,
                DeploymentStatus.FAILED,
                DeploymentStatus.RECALLED,
            }
        ]

        if active_deployments:
            for deployment in active_deployments:
                cols = st.columns([3, 2, 1])

                cols[0].write(
                    f"**{deployment.id}** · "
                    f"{deployment.incident_id or 'Disaster response'}"
                )
                cols[1].write(
                    f"{_value(deployment.status)} · "
                    f"{deployment.progress:.1f}%"
                )

                if cols[2].button(
                    "Recall",
                    key=f"recall_security_{deployment.id}",
                ):
                    try:
                        engine.recall(city, deployment.id)
                        persist_city()
                        st.success("Deployment recalled.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not recall deployment: {exc}")
        else:
            st.info("No deployments require manual control.")

    # ------------------------------------------------------------------
    # Units and departments
    # ------------------------------------------------------------------

    with tabs[2]:
        st.subheader("Security Units")

        units = list(state.units)

        if units:
            unit_rows = []

            for unit in units:
                unit_rows.append(
                    {
                        "Unit": unit.name,
                        "Type": _value(unit.unit_type),
                        "Status": _value(unit.status),
                        "Personnel": unit.personnel,
                        "Available": unit.available_personnel,
                        "Readiness": f"{unit.readiness:.1f}%",
                        "Equipment": f"{unit.equipment_rating:.1f}%",
                    }
                )

            _render_records(unit_rows)
        else:
            st.info("No security units are registered.")

        st.subheader("Department Directory")

        for department in state.departments:
            with st.expander(department.name):
                st.write(f"Type: {_value(department.unit_type)}")
                st.write(
                    f"Budget allocation: "
                    f"{_money(department.budget_allocation)}"
                )
                st.write(
                    f"Headquarters district: "
                    f"{department.headquarters_district_id or 'Not assigned'}"
                )

                department_units = [
                    unit
                    for unit in units
                    if unit.department_id == department.id
                ]

                st.write(f"Registered units: {len(department_units)}")

                for unit in department_units:
                    st.caption(_unit_label(unit))

        st.divider()
        st.subheader("Unit Maintenance")

        maintenance_units = [
            unit
            for unit in units
            if unit.status == UnitStatus.AVAILABLE
        ]

        if maintenance_units:
            units_by_id = {
                unit.id: unit
                for unit in maintenance_units
            }

            with st.form("security_maintenance"):
                selected_unit_id = st.selectbox(
                    "Unit",
                    options=list(units_by_id),
                    format_func=lambda unit_id: _unit_label(
                        units_by_id[unit_id]
                    ),
                )

                maintenance_days = st.number_input(
                    "Maintenance Duration (days)",
                    min_value=1,
                    max_value=30,
                    value=2,
                )

                maintenance_submitted = st.form_submit_button(
                    "Schedule Maintenance",
                    width="stretch",
                )

                if maintenance_submitted:
                    try:
                        engine.set_maintenance(
                            city,
                            selected_unit_id,
                            int(maintenance_days),
                        )
                        persist_city()
                        st.success("Maintenance scheduled.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not schedule maintenance: {exc}")
        else:
            st.info("No available units can be scheduled for maintenance.")

    # ------------------------------------------------------------------
    # Resources
    # ------------------------------------------------------------------

    with tabs[3]:
        st.subheader("Emergency Resource Inventory")

        resources = list(state.resources)

        if resources:
            resource_rows = []

            for resource in resources:
                resource_rows.append(
                    {
                        "Resource": resource.name,
                        "Category": _value(resource.category),
                        "Total Quantity": resource.quantity,
                        "Available": resource.available_quantity,
                        "Daily Unit Cost": _money(resource.unit_cost_per_day),
                        "District": resource.district_id or "Central",
                    }
                )

            _render_records(resource_rows)
        else:
            st.info("No emergency resources are registered.")

    # ------------------------------------------------------------------
    # Operations log
    # ------------------------------------------------------------------

    with tabs[4]:
        st.subheader("Security Operations Log")

        logs = list(state.operations_log)

        if logs:
            for entry in reversed(logs[-100:]):
                if isinstance(entry, dict):
                    st.write(
                        f"**Day {entry.get('day', '?')}** · "
                        f"{entry.get('action', 'Operation')} — "
                        f"{entry.get('description', '')}"
                    )
                else:
                    st.write(
                        f"**Day {getattr(entry, 'day', '?')}** · "
                        f"{getattr(entry, 'category', 'Operation')} — "
                        f"{getattr(entry, 'message', str(entry))}"
                    )
        else:
            st.info("No security operations have been recorded.")
