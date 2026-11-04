
"""Command center and city simulation screens."""

import streamlit as st

from ui.components.agent_feed import (
    render_activity_feed,
    render_society_summary,
)
from ui.components.city_map import render_city_map
from ui.components.metrics import (
    render_metric_grid,
    render_metric_trend,
)
from ui.layout import render_page_header
from ui.state import check_game_over, persist_city


def render_command_center(city) -> None:
    render_page_header(
        "01 / OVERVIEW",
        "Command Center",
        "The city is a system. Every decision changes its trajectory.",
        city,
    )

    if city.is_game_over:
        st.error(
            "ADMINISTRATION TERMINATED — simulation controls are disabled. "
            "Visit the Game Over screen for the final report."
        )

    left, right = st.columns([1.6, 1])

    with left:
        st.markdown("### City performance")
        render_metric_grid(city.metrics, columns=3)

    with right:
        st.markdown("### Simulation controls")

        if st.button(
            "ADVANCE ONE DAY",
            type="primary",
            use_container_width=True,
            disabled=city.is_game_over,
        ):
            report = st.session_state.engine.step()

            defeated = check_game_over(city)

            if not defeated:
                manager = st.session_state.scenario_manager

                if st.session_state.active_campaign_id:
                    manager.update(city)

                persist_city()
                st.success(f"Simulation advanced to day {city.day}.")

            st.rerun()

        if st.button(
            "ADVANCE FIVE DAYS",
            use_container_width=True,
            disabled=city.is_game_over,
        ):
            st.session_state.engine.run(5)

            defeated = check_game_over(city)

            if not defeated:
                manager = st.session_state.scenario_manager

                if st.session_state.active_campaign_id:
                    manager.update(city)

                persist_city()
                st.success(f"Simulation advanced to day {city.day}.")

            st.rerun()

        st.markdown("---")
        st.markdown("**Current administration**")
        st.write(f"Budget: **${city.budget:,.0f}**")
        st.write(f"Buildings: **{city.building_count:,}**")
        st.write(f"Road segments: **{len(city.roads):,}**")

    st.markdown("---")
    left, right = st.columns([1.4, 1])

    with left:
        render_metric_trend(city, "public_wellbeing", "Public wellbeing")

    with right:
        render_activity_feed(city)

    report = st.session_state.society.evaluate_city()

    st.markdown("---")
    render_society_summary(report)


def render_city_simulator(city) -> None:
    render_page_header(
        "02 / SIMULATION",
        "City Simulator",
        "Inspect the urban system, explore districts and review city conditions.",
        city,
    )

    if city.is_game_over:
        st.warning(
            "This city has been defeated. The map and district data remain "
            "available for inspection, but the simulation is frozen."
        )

    st.markdown("### NOVA YORK // 3D CITY MODEL")
    render_city_map(city, height=690)

    st.markdown("---")
    st.markdown("### District intelligence")

    districts = city.districts

    if not districts:
        st.warning("No districts are available.")
        return

    district_names = {
        district.name: district
        for district in districts
    }

    selected_name = st.selectbox(
        "Select a district",
        list(district_names),
    )

    district = district_names[selected_name]

    left, right = st.columns([1, 1])

    with left:
        st.markdown(f"#### {district.name}")
        st.caption(f"{district.district_type.upper()} DISTRICT")
        st.metric("Population", f"{district.population:,}")
        st.metric("Happiness", f"{district.happiness:.1f}/100")
        st.metric("Safety", f"{district.safety:.1f}/100")

    with right:
        st.metric("Healthcare access", f"{district.healthcare_access:.1f}/100")
        st.metric("Green space", f"{district.green_space:.1f}/100")
        st.metric("Wealth index", f"{district.wealth_index:.1f}/100")
        st.metric("Stress index", f"{district.stress:.1f}/100")

    society = st.session_state.society
    district_report = society.evaluate_district(district)

    st.markdown("#### Synthetic community perspective")
    st.caption(
        "This is a simulated model, not a survey of actual residents."
    )

    st.write(
        f"Community score: **{district_report['community_score']:.1f}/100** "
        f"· Sentiment: **{district_report['sentiment']}**"
    )

    with st.expander("Buildings in this district"):
        buildings = [
            building
            for building in city.buildings
            if building.district_id == district.id
        ]

        if buildings:
            st.dataframe(
                [
                    {
                        "Building": building.name,
                        "Type": building.building_type,
                        "Height": f"{building.height_m:.0f} m",
                        "Floors": building.floors,
                        "Operational": building.operational,
                    }
                    for building in buildings
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No buildings are registered in this district.")
