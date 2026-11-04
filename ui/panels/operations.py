"""Crisis management and campaign screens."""

import streamlit as st

from database import record_event
from events import apply_event, apply_response
from ui.state import persist_city


def render_crisis_center(city) -> None:
    st.markdown(
        '<div class="eyebrow">04 / EMERGENCY OPERATIONS</div>',
        unsafe_allow_html=True,
    )
    st.title("Crisis Center")
    st.caption("Every event has consequences. Every response has a cost.")

    if st.button("GENERATE CITY EVENT", type="primary"):
        generated = st.session_state.event_generator.generate(city, count=1)
        st.session_state.active_events.extend(generated)

        persist_city()
        for event in generated:
            record_event(event, save_id="autosave")

        st.rerun()

    events = st.session_state.active_events

    if not events:
        st.info("No active event is awaiting a response.")
        return

    st.markdown("---")
    for event in events:
        if event.is_resolved:
            continue

        severity = event.severity.value.upper()
        st.markdown(f"### {event.title}")
        st.caption(
            f"{severity} · {event.category.value.replace('_', ' ').upper()}"
        )
        st.write(event.description)

        if event.district_id:
            district = next(
                (
                    item for item in city.districts
                    if item.id == event.district_id
                ),
                None,
            )
            if district:
                st.caption(f"Affected district: {district.name}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Budget impact", f"${event.budget_impact:,.0f}")
        col2.metric("Happiness impact", f"{event.happiness_impact:+.1f}")
        col3.metric("Safety impact", f"{event.safety_impact:+.1f}")

        responses = event.response_options or []

        if responses:
            st.markdown("**Available response plans**")

            for index, response in enumerate(responses):
                response_title = (
                    response.get("title")
                    or response.get("name")
                    or f"Response option {index + 1}"
                )
                response_description = response.get("description", "")
                response_cost = response.get("cost", 0)

                with st.container(border=True):
                    st.markdown(f"**{response_title}**")
                    if response_description:
                        st.write(response_description)
                    if response_cost:
                        st.caption(f"Estimated response cost: ${response_cost:,.0f}")

                    if st.button(
                        f"EXECUTE RESPONSE {index + 1}",
                        key=f"response_{event.id}_{index}",
                    ):
                        try:
                            apply_response(city, event, response)
                            persist_city()
                            st.success(f"Response applied: {response_title}")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Could not apply response: {exc}")

        else:
            if st.button(
                "APPLY EVENT IMPACT",
                key=f"apply_event_{event.id}",
            ):
                try:
                    apply_event(city, event)
                    persist_city()
                    st.success("Event impact applied to the city.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not apply event: {exc}")

        st.markdown("---")

    resolved = [event for event in events if event.is_resolved]
    if resolved:
        with st.expander(f"Resolved events · {len(resolved)}"):
            for event in resolved:
                st.write(f"✓ {event.title}")


def render_campaigns(city) -> None:
    st.markdown(
        '<div class="eyebrow">05 / LONG-TERM STRATEGY</div>',
        unsafe_allow_html=True,
    )
    st.title("Campaigns")
    st.caption("Choose the future your administration is trying to build.")

    manager = st.session_state.scenario_manager
    campaigns = manager.get_campaigns()

    if not campaigns:
        st.warning("No campaigns are currently available.")
        return

    campaign_by_title = {campaign.title: campaign for campaign in campaigns}

    selected_title = st.selectbox(
        "Select a campaign",
        list(campaign_by_title),
    )
    campaign = campaign_by_title[selected_title]

    st.markdown(
        f"""
        <div class="panel">
            <div class="eyebrow">{campaign.difficulty.upper()} DIFFICULTY</div>
            <div style="font-size:1.5rem;font-weight:800">{campaign.title}</div>
            <div style="color:#27C9D7;margin:.4rem 0">{campaign.subtitle}</div>
            <div style="color:#8295A8;font-size:.88rem">{campaign.description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Campaign objectives")
    for objective in campaign.objectives:
        st.markdown(
            f"""
            <div class="panel">
                <div style="font-weight:700">{objective.title}</div>
                <div class="panel-note">{objective.description}</div>
                <div class="panel-note">
                    TYPE: {objective.objective_type.value.upper()}
                    {" · DEADLINE: DAY " + str(objective.deadline_day) if objective.deadline_day else ""}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    active_id = st.session_state.get("active_campaign_id")

    if active_id == campaign.id:
        st.success("This campaign is currently active.")
    elif st.button("START THIS CAMPAIGN", type="primary"):
        try:
            manager.start_campaign(campaign.id, city)
            st.session_state.active_campaign_id = campaign.id

            persist_city()
            st.success(f"Campaign started: {campaign.title}")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not start campaign: {exc}")

    if active_id:
        active_campaign = next(
            (item for item in campaigns if item.id == active_id),
            None,
        )

        if active_campaign:
            st.markdown("---")
            st.markdown(f"### Active campaign · {active_campaign.title}")

            for objective in active_campaign.objectives:
                metric = objective.metric
                if metric and hasattr(city.metrics, metric):
                    current = float(getattr(city.metrics, metric))
                    target = float(objective.target or 0)
                    progress = min(1.0, current / target) if target > 0 else 0.0

                    st.write(
                        f"**{objective.title}** · {current:.1f} / {target:.1f}"
                    )
                    st.progress(progress)

                elif objective.objective_type.value == "survive_days":
                    required = objective.required_days
                    elapsed = max(0, city.day - active_campaign.starting_day)
                    progress = min(1.0, elapsed / required)

                    st.write(
                        f"**{objective.title}** · {elapsed} / {required} days"
                    )
                    st.progress(progress)