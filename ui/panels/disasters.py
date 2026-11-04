
"""Disaster Management — response coordination and city recovery."""

from __future__ import annotations

import streamlit as st

from disasters.models import DisasterStatus
from security.engine import SecurityEngine
from security.models import DeploymentStatus, UnitStatus
from ui.state import persist_city


ACTIVE_STATUSES = {
    DisasterStatus.DETECTED,
    DisasterStatus.ACTIVE,
}


def _label(value) -> str:
    return str(getattr(value, "value", value)).replace("_", " ").title()


def _district_name(city, district_id: str) -> str:
    for district in city.districts:
        if district.id == district_id:
            return district.name
    return district_id


def _persist_and_rerun() -> None:
    persist_city()
    st.rerun()


def render_disaster_management(city) -> None:
    """Render disaster response, recovery, and historical reporting."""

    security_engine = SecurityEngine()
    security_state = security_engine.initialize(city)

    disasters = list(city.disasters)

    # Security collections are lists, so create an ID lookup for UI selection.
    units_by_id = {
        unit.id: unit
        for unit in security_state.units
    }

    active_disasters = [
        disaster
        for disaster in disasters
        if disaster.status in ACTIVE_STATUSES
    ]

    recovering_disasters = [
        disaster
        for disaster in disasters
        if disaster.status == DisasterStatus.RECOVERING
    ]

    resolved_disasters = [
        disaster
        for disaster in disasters
        if disaster.status
        in {
            DisasterStatus.RESOLVED,
            DisasterStatus.FAILED,
            DisasterStatus.CONTAINED,
        }
    ]

    st.title("🌪️ Disaster Management")
    st.caption(
        "Monitor city-wide disasters, coordinate emergency deployments, "
        "and manage post-disaster recovery."
    )

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------

    metric_cols = st.columns(4)
    metric_cols[0].metric("Total Disasters", len(disasters))
    metric_cols[1].metric("Active Disasters", len(active_disasters))
    metric_cols[2].metric("Recovering", len(recovering_disasters))
    metric_cols[3].metric(
        "Available Personnel",
        security_state.available_personnel,
    )

    tabs = st.tabs(
        [
            "Active Response",
            "Recovery Operations",
            "Disaster History",
        ]
    )

    # ------------------------------------------------------------------
    # Active response
    # ------------------------------------------------------------------

    with tabs[0]:
        st.subheader("Active Disaster Response")

        if not active_disasters:
            st.success("There are no active disasters requiring response.")
        else:
            for disaster in active_disasters:
                with st.container(border=True):
                    st.markdown(f"### {disaster.title}")
                    st.caption(
                        f"{disaster.id} · {_label(disaster.disaster_type)} · "
                        f"{_label(disaster.severity)}"
                    )

                    st.write(disaster.description)

                    district_names = [
                        _district_name(city, district_id)
                        for district_id in disaster.affected_district_ids
                    ]

                    st.write(
                        "**Affected districts:** "
                        + (", ".join(district_names) or "Not specified")
                    )

                    status_cols = st.columns(3)
                    status_cols[0].metric(
                        "Severity Score",
                        f"{disaster.severity_score:.1f}",
                    )
                    status_cols[1].metric(
                        "Containment",
                        f"{disaster.containment_progress:.1f}%",
                    )
                    status_cols[2].metric(
                        "Days Remaining",
                        max(0, disaster.days_remaining(city.day)),
                    )

                    st.progress(
                        min(
                            1.0,
                            max(0.0, disaster.containment_progress / 100),
                        )
                    )

                    st.markdown("#### Response Objectives")

                    objectives = list(disaster.objectives)

                    if not objectives:
                        st.info("No response objectives are registered.")
                    else:
                        for objective in objectives:
                            objective_cols = st.columns([4, 1])

                            objective_cols[0].write(
                                f"**{objective.title}**"
                            )
                            objective_cols[0].caption(
                                objective.description
                            )

                            objective_cols[1].write(
                                "Complete"
                                if objective.is_completed
                                else "In progress"
                            )

                            progress_ratio = (
                                objective.current_progress
                                / max(objective.required_progress, 1)
                            )

                            st.progress(
                                min(1.0, max(0.0, progress_ratio))
                            )

                    # --------------------------------------------------
                    # Dispatch security units to an objective
                    # --------------------------------------------------

                    incomplete_objectives = [
                        objective
                        for objective in objectives
                        if not objective.is_completed
                    ]

                    available_units = [
                        unit
                        for unit in security_state.units
                        if unit.status == UnitStatus.AVAILABLE
                        and unit.available_personnel > 0
                    ]

                    if incomplete_objectives and available_units:
                        st.markdown("#### Dispatch Disaster Response")

                        with st.form(
                            f"disaster_dispatch_{disaster.id}"
                        ):
                            selected_objective_id = st.selectbox(
                                "Response Objective",
                                options=[
                                    objective.id
                                    for objective in incomplete_objectives
                                ],
                                format_func=lambda objective_id: next(
                                    objective.title
                                    for objective in incomplete_objectives
                                    if objective.id == objective_id
                                ),
                                key=f"objective_{disaster.id}",
                            )

                            selected_unit_ids = st.multiselect(
                                "Available Security Units",
                                options=[
                                    unit.id for unit in available_units
                                ],
                                format_func=lambda unit_id: (
                                    f"{units_by_id[unit_id].name} · "
                                    f"{_label(units_by_id[unit_id].unit_type)} · "
                                    f"{units_by_id[unit_id].available_personnel} "
                                    "available"
                                ),
                                key=f"disaster_units_{disaster.id}",
                            )

                            dispatch_submitted = st.form_submit_button(
                                "Dispatch Response Units",
                                use_container_width=True,
                            )

                            if dispatch_submitted:
                                if not selected_unit_ids:
                                    st.warning(
                                        "Select at least one response unit."
                                    )
                                else:
                                    try:
                                        security_engine.dispatch_disaster_response(
                                            city=city,
                                            disaster=disaster,
                                            objective_id=selected_objective_id, # type: ignore
                                            unit_ids=selected_unit_ids,
                                        )
                                        persist_city()
                                        st.success(
                                            "Disaster response units dispatched."
                                        )
                                        st.rerun()
                                    except Exception as exc:
                                        st.error(
                                            f"Dispatch failed: {exc}"
                                        )

                    elif incomplete_objectives:
                        st.warning(
                            "No available security units can currently "
                            "be assigned to this disaster."
                        )

                    # --------------------------------------------------
                    # Current deployments
                    # --------------------------------------------------

                    disaster_deployments = [
                        deployment
                        for deployment in security_state.deployments
                        if deployment.disaster_id == disaster.id
                        and deployment.status
                        not in {
                            DeploymentStatus.COMPLETED,
                            DeploymentStatus.FAILED,
                            DeploymentStatus.RECALLED,
                        }
                    ]

                    if disaster_deployments:
                        st.markdown("#### Active Disaster Deployments")

                        for deployment in disaster_deployments:
                            deployment_cols = st.columns([3, 2, 1])

                            deployment_cols[0].write(
                                f"**{deployment.id}**"
                            )
                            deployment_cols[1].write(
                                f"{_label(deployment.status)} · "
                                f"{deployment.progress:.1f}%"
                            )

                            if deployment_cols[2].button(
                                "Recall",
                                key=f"recall_disaster_{deployment.id}",
                            ):
                                try:
                                    security_engine.recall(
                                        city,
                                        deployment.id,
                                    )
                                    persist_city()
                                    st.success("Deployment recalled.")
                                    st.rerun()
                                except Exception as exc:
                                    st.error(
                                        f"Could not recall deployment: {exc}"
                                    )

                    # --------------------------------------------------
                    # Impact report
                    # --------------------------------------------------

                    impact_report = city.disaster_impacts.get(disaster.id)

                    if impact_report is not None:
                        with st.expander("Initial Impact Assessment"):
                            report_data = (
                                impact_report.model_dump()
                                if hasattr(impact_report, "model_dump")
                                else vars(impact_report)
                            )

                            for key, value in report_data.items():
                                if key == "district_impacts":
                                    continue

                                st.write(
                                    f"**{_label(key)}:** {value}"
                                )

                            district_impacts = report_data.get(
                                "district_impacts",
                                [],
                            )

                            if district_impacts:
                                st.write("District impact details")
                                st.json(district_impacts)

    # ------------------------------------------------------------------
    # Recovery operations
    # ------------------------------------------------------------------

    with tabs[1]:
        st.subheader("Recovery Operations")

        if not recovering_disasters:
            st.info("No disasters are currently in the recovery phase.")
        else:
            for disaster in recovering_disasters:
                recovery = city.disaster_recoveries.get(disaster.id)

                with st.container(border=True):
                    st.markdown(f"### {disaster.title}")
                    st.caption(
                        f"{disaster.id} · Recovery started on "
                        f"Day {recovery.started_day if recovery else '—'}"
                    )

                    if recovery is None:
                        st.warning(
                            "No recovery state is currently associated "
                            "with this disaster."
                        )
                        continue

                    st.metric(
                        "Recovery Progress",
                        f"{recovery.progress:.1f}%",
                    )

                    st.progress(
                        min(
                            1.0,
                            max(0.0, recovery.progress / 100),
                        )
                    )

                    recovery_cols = st.columns(3)
                    recovery_cols[0].metric(
                        "Duration",
                        f"{recovery.duration_days} days",
                    )
                    recovery_cols[1].metric(
                        "Damaged Buildings",
                        len(recovery.damaged_building_ids),
                    )
                    recovery_cols[2].metric(
                        "Repaired Buildings",
                        len(recovery.repaired_building_ids),
                    )

                    st.write(
                        f"**Started:** Day {recovery.started_day}"
                    )
                    st.write(
                        f"**Recovery status:** "
                        f"{'Complete' if recovery.is_complete else 'In progress'}"
                    )

                    if recovery.repaired_building_ids:
                        with st.expander("Repaired Buildings"):
                            st.write(
                                ", ".join(recovery.repaired_building_ids)
                            )

                    if recovery.damaged_building_ids:
                        with st.expander("Damaged Buildings"):
                            st.write(
                                ", ".join(recovery.damaged_building_ids)
                            )

                    if recovery.metrics:
                        with st.expander("Recovery Metrics"):
                            for metric in recovery.metrics:
                                st.write(str(metric))

    # ------------------------------------------------------------------
    # Disaster history
    # ------------------------------------------------------------------

    with tabs[2]:
        st.subheader("Disaster History")

        if not disasters:
            st.info("No disasters have been recorded.")
        else:
            history_rows = []

            for disaster in sorted(
                disasters,
                key=lambda item: item.created_at_day,
                reverse=True,
            ):
                history_rows.append(
                    {
                        "Disaster": disaster.title,
                        "ID": disaster.id,
                        "Type": _label(disaster.disaster_type),
                        "Severity": _label(disaster.severity),
                        "Status": _label(disaster.status),
                        "Detected Day": disaster.detected_day,
                        "Resolved Day": (
                            disaster.resolved_at_day
                            if disaster.resolved_at_day is not None
                            else "—"
                        ),
                        "Affected Districts": len(
                            disaster.affected_district_ids
                        ),
                    }
                )

            st.dataframe(
                history_rows,
                use_container_width=True,
                hide_index=True,
            )

            st.divider()

            for disaster in sorted(
                disasters,
                key=lambda item: item.created_at_day,
                reverse=True,
            ):
                with st.expander(
                    f"{disaster.title} · {_label(disaster.status)}"
                ):
                    st.write(disaster.description)
                    st.write(
                        f"**Type:** {_label(disaster.disaster_type)}"
                    )
                    st.write(
                        f"**Severity:** {_label(disaster.severity)}"
                    )
                    st.write(
                        f"**Detected:** Day {disaster.detected_day}"
                    )
                    st.write(
                        f"**Resolved:** "
                        f"{disaster.resolved_at_day if disaster.resolved_at_day is not None else 'Not resolved'}"
                    )
