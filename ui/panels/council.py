# type: ignore
"""AI Council deliberation interface."""

import streamlit as st

from ai import get_provider_status, run_council_deliberation


PROVIDERS = ["otari", "gemini", "groq"]


def _provider_is_configured(status: dict, provider: str) -> bool:
    details = status.get(provider, {})
    if isinstance(details, dict):
        return bool(
            details.get("configured")
            and details.get("model_configured", True)
        )
    return bool(details)


def render_council(city) -> None:
    st.markdown(
        '<div class="eyebrow">03 / ADVISORY SYSTEM</div>',
        unsafe_allow_html=True,
    )
    st.title("AI Council")
    st.caption(
        "Eight specialist perspectives. One decision remains with the mayor."
    )

    status = get_provider_status()
    configured = [
        provider for provider in PROVIDERS
        if _provider_is_configured(status, provider)
    ]

    if not configured:
        st.error("No AI provider is currently configured.")
        return

    current_provider = st.session_state.provider
    if current_provider not in configured:
        current_provider = configured[0]

    provider = st.selectbox(
        "Deliberation provider",
        configured,
        index=configured.index(current_provider),
        format_func=lambda value: value.upper(),
    )
    st.session_state.provider = provider

    problem = st.text_area(
        "What should the council evaluate?",
        placeholder=(
            "Example: Should the city prioritise a major public transport "
            "expansion, even if it delays other infrastructure projects?"
        ),
        height=110,
        key="council_problem",
    )

    if st.button("CONVENE THE COUNCIL", type="primary"):
        if not problem.strip():
            st.warning("Enter a policy question or city problem first.")
        else:
            context = {
                "city": city.city_name,
                "day": city.day,
                "population": city.population,
                "budget": city.budget,
                "district_count": city.district_count,
                "building_count": city.building_count,
                "metrics": city.metrics.model_dump(),
                "recent_events": city.event_log[-8:],
            }

            with st.spinner(f"Convening the council through {provider.upper()}..."):
                try:
                    result = run_council_deliberation(
                        problem=problem.strip(),
                        city_context=context,
                        provider=provider,
                    )
                    st.session_state.council_result = result
                except Exception as exc:
                    st.error(f"Council deliberation failed: {exc}")

    result = st.session_state.get("council_result")
    if result is None:
        st.info("The council is waiting for an issue to deliberate.")
        return

    st.markdown("---")
    st.markdown("### Executive summary")
    st.write(result.executive_summary)

    st.info(
        "The council is advisory. The final decision must be made by the human mayor."
    )

    perspectives = result.perspectives
    st.markdown(f"### Council perspectives · {len(perspectives)}")

    for index, perspective in enumerate(perspectives, start=1):
        stance = perspective.stance.upper()
        with st.expander(
            f"{index:02d} · {perspective.role} — {stance}",
            expanded=index == 1,
        ):
            st.write(perspective.reasoning)

            left, right = st.columns(2)
            with left:
                st.markdown("**Expected benefits**")
                for item in perspective.expected_benefits:
                    st.markdown(f"- {item}")

            with right:
                st.markdown("**Identified risks**")
                for item in perspective.identified_risks:
                    st.markdown(f"- {item}")

            st.markdown("**Recommendation**")
            st.write(perspective.recommendation)

    st.markdown("---")
    left, right = st.columns(2)

    with left:
        st.markdown("### Major trade-offs")
        for item in result.major_tradeoffs:
            st.markdown(f"- {item}")

    with right:
        st.markdown("### Unanswered questions")
        for item in result.unanswered_questions:
            st.markdown(f"- {item}")