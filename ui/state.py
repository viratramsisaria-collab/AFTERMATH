# type: ignore
"""Streamlit session state and simulation lifecycle."""

import streamlit as st

from agents import MayoralCouncil, SocietySimulation
from core.constants import CITY_DEFAULT_SEED, CITY_INITIAL_BUDGET, CITY_NAME
from database import init_db, save_city
from events import EventGenerator
from scenarios.manager import ScenarioManager
from simulation.engine import SimulationEngine
from simulation.rules import evaluate_loss
from simulation.state import CityState
from world import generate_city


def initialize_state() -> None:
    if st.session_state.get("_aftermath_initialized"):
        return

    init_db()

    city = generate_city(
        seed=CITY_DEFAULT_SEED,
        city_name=CITY_NAME,
        initial_budget=CITY_INITIAL_BUDGET,
    )

    st.session_state.provider = "otari"

    replace_city(city)

    st.session_state._aftermath_initialized = True
    persist_city()


def replace_city(city: CityState) -> None:
    """Replace the active city and rebuild dependent game objects."""

    st.session_state.city = city
    st.session_state.engine = SimulationEngine(city)
    st.session_state.council = MayoralCouncil()
    st.session_state.society = SocietySimulation(city)
    st.session_state.scenario_manager = ScenarioManager()
    st.session_state.event_generator = EventGenerator(
        seed=city.seed
    )

    st.session_state.active_events = []
    st.session_state.council_result = None
    st.session_state.last_assessment = None
    st.session_state.last_proposal = None
    st.session_state.last_decision_id = None
    st.session_state.active_campaign_id = None

    st.session_state.game_over_message_attempted = False
    st.session_state.game_over_message_error = None


def _fallback_game_over_tagline(city: CityState) -> str:
    label = city.game_over_label or "A critical city system"
    value = city.game_over_value
    threshold = city.game_over_threshold
    operator = city.game_over_operator

    if value is None or threshold is None:
        return (
            f"{city.city_name} has reached the end of its administration. "
            "The city can no longer continue under its current conditions."
        )

    comparison = (
        "fell below"
        if operator == "below"
        else "exceeded"
    )

    return (
        f"{city.city_name} reached a breaking point on Day "
        f"{city.game_over_day or city.day}. {label} {comparison} "
        f"its required threshold: {value:.2f} against {threshold:.2f}. "
        "The city can no longer continue under this administration."
    )


def check_game_over(city: CityState | None = None) -> bool:
    """Record defeat, generate its closing message, and persist it."""

    city = city or st.session_state.city

    if not city.is_game_over:
        failure = evaluate_loss(city)

        if failure is None:
            return False

        city.is_game_over = True
        city.is_running = False
        city.game_over_metric = failure["metric"]
        city.game_over_label = failure["label"]
        city.game_over_value = failure["value"]
        city.game_over_threshold = failure["threshold"]
        city.game_over_operator = failure["operator"]
        city.game_over_reason = failure["description"]
        city.game_over_day = failure["day"]

        city.add_event(
            f"CITY DEFEAT: {failure['label']} reached "
            f"{failure['value']:.2f}; required condition: "
            f"{failure['operator']} {failure['threshold']:.2f}."
        )

    if not city.game_over_tagline:
        city.game_over_tagline = _fallback_game_over_tagline(city)

    if not st.session_state.get("game_over_message_attempted", False):
        st.session_state.game_over_message_attempted = True

        try:
            from ai.service import generate_game_over_tagline

            tagline = generate_game_over_tagline(
                metric_name=city.game_over_metric or "unknown",
                metric_label=city.game_over_label or "Unknown metric",
                value=city.game_over_value or 0.0,
                threshold=city.game_over_threshold or 0.0,
                operator=city.game_over_operator or "below",
                day=city.game_over_day or city.day,
                city_name=city.city_name,
                provider=st.session_state.get("provider", "otari"),
            )

            if tagline:
                city.game_over_tagline = tagline

        except Exception as exc:
            st.session_state.game_over_message_error = str(exc)

    city.is_running = False

    if city is st.session_state.get("city"):
        persist_city()

    return True


def persist_city() -> None:
    city = st.session_state.get("city")

    if city is None:
        return

    campaign_id = st.session_state.get("active_campaign_id")

    save_city(
        city,
        save_id="autosave",
        campaign_id=campaign_id,
    )
