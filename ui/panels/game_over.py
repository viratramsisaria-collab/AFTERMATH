
"""Game over screen and new-city flow."""

from uuid import uuid4

import streamlit as st

from core.constants import CITY_INITIAL_BUDGET, CITY_NAME
from database import save_city
from ui.layout import render_page_header
from ui.state import persist_city, replace_city
from world import generate_city


def render_game_over(city) -> None:
    render_page_header(
        "09 / ADMINISTRATION TERMINATED",
        "The City Has Fallen",
        "The simulation has reached a critical failure state. This administration cannot continue.",
        city,
    )

    st.error(
        city.game_over_tagline
        or "The city has reached a critical failure condition."
    )

    st.markdown("### Cause of failure")

    left, middle, right = st.columns(3)

    left.metric(
        "Failed system",
        city.game_over_label or "Unknown",
    )

    value = city.game_over_value
    threshold = city.game_over_threshold

    middle.metric(
        "Final value",
        "—" if value is None else f"{value:.2f}",
    )

    right.metric(
        "Required threshold",
        "—" if threshold is None else f"{threshold:.2f}",
    )

    st.caption(
        f"Failure occurred on Day {city.game_over_day or city.day}. "
        f"{city.game_over_reason or 'A critical city condition was violated.'}"
    )

    st.markdown("---")
    st.markdown("### Final city report")

    metrics = city.metrics
    columns = st.columns(4)

    final_values = [
        ("Population", f"{city.population:,}"),
        ("City budget", f"${city.budget:,.0f}"),
        ("Economic health", f"{metrics.economic_health:.1f}"),
        ("Public wellbeing", f"{metrics.public_wellbeing:.1f}"),
        ("Mobility", f"{metrics.mobility:.1f}"),
        ("Environmental health", f"{metrics.environmental_health:.1f}"),
        ("Social equity", f"{metrics.social_equity:.1f}"),
        ("Citizen happiness", f"{metrics.happiness:.1f}"),
    ]

    for index, (label, value_text) in enumerate(final_values):
        with columns[index % 4]:
            st.metric(label, value_text)

    st.markdown("---")
    st.markdown("### What happens next?")

    st.write(
        "You can preserve this failed timeline in the simulation archive, "
        "inspect the city, or begin a new administration with a newly "
        "generated city."
    )

    save_col, new_col = st.columns(2)

    with save_col:
        if st.button(
            "SAVE FAILED CITY",
            use_container_width=True,
        ):
            save_id = (
                f"defeat-day-{city.game_over_day or city.day}-"
                f"{uuid4().hex[:8]}"
            )

            try:
                save_city(
                    city,
                    save_id=save_id,
                    campaign_id=st.session_state.get("active_campaign_id"),
                )
                st.success(f"Failed city saved as '{save_id}'.")
            except Exception as exc:
                st.error(f"Could not save failed city: {exc}")

    with new_col:
        if st.button(
            "START A NEW CITY",
            type="primary",
            use_container_width=True,
        ):
            try:
                new_seed = city.seed + 1

                new_city = generate_city(
                    seed=new_seed,
                    city_name=CITY_NAME,
                    initial_budget=CITY_INITIAL_BUDGET,
                )

                replace_city(new_city)
                persist_city()

                st.session_state["_pending_navigation"] = (
    "◈  Command Center"
)

                st.success("A new city has been generated.")
                st.rerun()

            except Exception as exc:
                st.error(f"Could not start a new city: {exc}")
