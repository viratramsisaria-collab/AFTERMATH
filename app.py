
"""AFTERMATH application entry point."""

import streamlit as st

from core.constants import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_TAGLINE,
)
from database import (
    delete_city_save,
    list_city_saves,
    load_city,
    save_city,
)
from ui.layout import render_footer, render_sidebar
from ui.panels import (
    render_campaigns,
    render_city_simulator,
    render_command_center,
    render_council,
    render_crisis_center,
    render_disaster_management,
    render_judgement,
    render_security_center,
)
from ui.panels.game_over import render_game_over
from ui.panels.rules import render_rules
from ui.state import initialize_state, persist_city, replace_city
from ui.theme import inject_theme


st.set_page_config(
    page_title=f"{APP_NAME} | NOVA YORK",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()
initialize_state()

# Apply pending navigation before the sidebar widget is created.
pending_navigation = st.session_state.pop(
    "_pending_navigation",
    None,
)

if pending_navigation:
    st.session_state["aftermath_navigation"] = pending_navigation

city = st.session_state.city
provider = st.session_state.provider

page = render_sidebar(city, provider)

if page == "Command Center":
    render_command_center(city)

elif page == "City Simulator":
    render_city_simulator(city)

elif page == "AI Council":
    render_council(city)

elif page == "Crisis Center":
    render_crisis_center(city)

elif page == "Security Command Centre":
    render_security_center(city)

elif page == "Disaster Management":
    render_disaster_management(city)

elif page == "Campaigns":
    render_campaigns(city)

elif page == "Policy & Decisions":
    render_judgement(city)

elif page == "Rules":
    render_rules(city)

elif page == "Game Over":
    render_game_over(city)

elif page == "Save / Load":
    st.markdown(
        '<div class="eyebrow">07 / SIMULATION ARCHIVE</div>',
        unsafe_allow_html=True,
    )
    st.title("Save / Load")
    st.caption(
        "Preserve a city timeline, create named saves, and restore a previous state."
    )

    if city.is_game_over:
        st.warning(
            "The current city has been defeated. You can preserve its final "
            "state or load another saved simulation."
        )

    st.markdown("### Current simulation")

    col1, col2, col3 = st.columns(3)
    col1.metric("Current day", city.day)
    col2.metric("Population", f"{city.population:,}")
    col3.metric("Budget", f"${city.budget:,.0f}")

    st.markdown("---")
    st.markdown("### Save current city")

    save_name = st.text_input(
        "Save identifier",
        value="autosave",
        help="Use a short identifier, such as novayork-run-01.",
    )

    if st.button("SAVE SIMULATION", type="primary"):
        if not save_name.strip():
            st.error("Enter a save identifier.")
        else:
            try:
                save_city(
                    city,
                    save_id=save_name.strip(),
                    campaign_id=st.session_state.get("active_campaign_id"),
                )
                st.success(f"Simulation saved as '{save_name.strip()}'.")
            except Exception as exc:
                st.error(f"Could not save simulation: {exc}")

    st.markdown("---")
    st.markdown("### Available saves")

    try:
        saves = list_city_saves()
    except Exception as exc:
        saves = []
        st.error(f"Could not retrieve saved simulations: {exc}")

    if not saves:
        st.info("No saved simulations were found.")
    else:
        save_options = []

        for item in saves:
            if isinstance(item, str):
                save_options.append(item)

            elif isinstance(item, dict):
                save_id = (
                    item.get("save_id")
                    or item.get("id")
                    or item.get("name")
                )

                if save_id:
                    save_options.append(str(save_id))

            else:
                save_id = (
                    getattr(item, "save_id", None)
                    or getattr(item, "id", None)
                )

                if save_id:
                    save_options.append(str(save_id))

        if save_options:
            selected_save = st.selectbox(
                "Select a saved simulation",
                sorted(set(save_options)),
            )

            left, right = st.columns(2)

            with left:
                if st.button("LOAD SELECTED SAVE", type="primary"):
                    if selected_save is None:
                        st.error("Select a saved simulation to load.")
                    else:
                        try:
                            restored_city = load_city(selected_save)

                            if restored_city is None:
                                st.error("That save could not be loaded.")
                            else:
                                replace_city(restored_city)
                                persist_city()
                                st.success(f"Loaded '{selected_save}'.")
                                st.rerun()

                        except Exception as exc:
                            st.error(f"Could not load save: {exc}")

            with right:
                if selected_save is not None and selected_save != "autosave":
                    if st.button("DELETE SELECTED SAVE"):
                        try:
                            delete_city_save(selected_save)
                            st.success(f"Deleted '{selected_save}'.")
                            st.rerun()

                        except Exception as exc:
                            st.error(f"Could not delete save: {exc}")

    st.markdown("---")
    st.markdown("### Automatic save")
    st.caption(
        "The active simulation is also saved to the autosave slot when "
        "simulation days and major operations are completed."
    )

render_footer()