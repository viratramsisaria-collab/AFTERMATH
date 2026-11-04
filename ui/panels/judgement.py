# type: ignore
"""Human-centred policy assessment and decision interface."""

import uuid

import streamlit as st

from database import record_decision, update_decision
from judgement.assessment import PolicyProposal
from judgement.engine import JudgementEngine
from judgement.metrics import HumanValues
from ui.state import persist_city


VALUE_LABELS = {
    "dignity": "Human dignity",
    "fairness": "Fairness",
    "accessibility": "Accessibility",
    "safety": "Safety",
    "wellbeing": "Wellbeing",
    "opportunity": "Opportunity",
    "sustainability": "Sustainability",
}

IMPACT_METRICS = [
    "economic_health",
    "mobility",
    "public_wellbeing",
    "environmental_health",
    "social_equity",
    "safety",
    "healthcare_access",
    "happiness",
    "energy_reserve",
    "water_reserve",
    "traffic_congestion",
]


def render_judgement(city) -> None:
    st.markdown(
        '<div class="eyebrow">06 / HUMAN AUTHORITY</div>',
        unsafe_allow_html=True,
    )
    st.title("Policy & Decisions")
    st.caption(
        "Measure policy against human values. Review the trade-offs. "
        "Then make the decision."
    )

    with st.form("policy_assessment_form"):
        st.markdown("### Policy proposal")

        title = st.text_input(
            "Policy title",
            placeholder="e.g. Expand the public transport network",
        )
        description = st.text_area(
            "Policy description",
            placeholder="Describe what the policy changes and who it affects.",
            height=100,
        )

        col1, col2 = st.columns(2)
        with col1:
            cost = st.number_input(
                "Estimated cost ($)",
                min_value=0.0,
                value=10_000_000.0,
                step=1_000_000.0,
            )
        with col2:
            duration = st.number_input(
                "Duration (days)",
                min_value=1,
                max_value=365,
                value=30,
                step=1,
            )

        st.markdown("### Expected city impact")
        st.caption(
            "Enter estimated metric changes. Positive values improve a metric; "
            "negative values reduce it. For traffic congestion, a negative "
            "change means less congestion."
        )

        impact_columns = st.columns(2)
        expected_impacts = {}

        for index, metric in enumerate(IMPACT_METRICS):
            with impact_columns[index % 2]:
                expected_impacts[metric] = st.number_input(
                    metric.replace("_", " ").title(),
                    min_value=-100.0,
                    max_value=100.0,
                    value=0.0,
                    step=1.0,
                    key=f"impact_{metric}",
                )

        st.markdown("### Human value priorities")
        st.caption(
            "These sliders express the values the mayor wants the assessment "
            "to prioritise."
        )

        value_columns = st.columns(2)
        value_scores = {}

        defaults = HumanValues().model_dump()
        for index, (key, label) in enumerate(VALUE_LABELS.items()):
            with value_columns[index % 2]:
                value_scores[key] = st.slider(
                    label,
                    min_value=0,
                    max_value=100,
                    value=int(defaults[key]),
                    key=f"value_{key}",
                )

        submitted = st.form_submit_button(
            "ASSESS POLICY",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not title.strip() or not description.strip():
            st.error("A policy title and description are required.")
        else:
            try:
                proposal = PolicyProposal(
                    id=f"policy-{uuid.uuid4().hex[:10]}",
                    title=title.strip(),
                    description=description.strip(),
                    estimated_cost=cost,
                    duration_days=int(duration),
                    district_ids=[],
                    expected_impacts={
                        key: value
                        for key, value in expected_impacts.items()
                        if value != 0
                    },
                )
                values = HumanValues(**value_scores)
                assessment = JudgementEngine().assess(proposal, values)

                st.session_state.last_proposal = proposal
                st.session_state.last_assessment = assessment

                persist_city()
                decision_id = record_decision(
                    proposal,
                    assessment,
                    status="pending",
                    save_id="autosave",
                )
                st.session_state.last_decision_id = decision_id

            except Exception as exc:
                st.error(f"Policy assessment failed: {exc}")

    proposal = st.session_state.get("last_proposal")
    assessment = st.session_state.get("last_assessment")

    if proposal is None or assessment is None:
        st.info("Submit a policy proposal to begin its human-centred assessment.")
        return

    st.markdown("---")
    st.markdown(f"### Assessment · {assessment.proposal_title}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Human values score", f"{assessment.overall_score:.1f}/100")
    col2.metric("Estimated cost", f"${assessment.estimated_cost:,.0f}")
    col3.metric("Human decision", "REQUIRED")

    st.markdown("### Assessment explanation")
    st.write(assessment.explanation)
    st.markdown(f"**Recommendation:** {assessment.recommendation}")

    left, right = st.columns(2)
    with left:
        st.markdown("**Strengths**")
        for item in assessment.strengths:
            st.markdown(f"- {item}")
        st.markdown("**Concerns**")
        for item in assessment.concerns:
            st.markdown(f"- {item}")

    with right:
        st.markdown("**Trade-offs**")
        for item in assessment.tradeoffs:
            st.markdown(f"- {item}")

    st.warning(
        "This assessment does not approve or execute the policy. "
        "The mayor must explicitly choose what happens next."
    )

    decision_id = st.session_state.get("last_decision_id")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("APPROVE POLICY", type="primary", use_container_width=True):
            if decision_id:
                update_decision(
                    decision_id,
                    status="approved",
                    decision="Approved by the human mayor.",
                )
            st.success("Policy approved by the human mayor.")
            st.session_state.last_assessment = None
            st.session_state.last_proposal = None
            st.session_state.last_decision_id = None
            st.rerun()

    with col2:
        if st.button("REJECT POLICY", use_container_width=True):
            if decision_id:
                update_decision(
                    decision_id,
                    status="rejected",
                    decision="Rejected by the human mayor.",
                )
            st.info("Policy rejected by the human mayor.")
            st.session_state.last_assessment = None
            st.session_state.last_proposal = None
            st.session_state.last_decision_id = None
            st.rerun()

    with col3:
        if st.button("DEFER DECISION", use_container_width=True):
            if decision_id:
                update_decision(
                    decision_id,
                    status="deferred",
                    decision="Deferred by the human mayor.",
                )
            st.warning("Decision deferred.")
            st.session_state.last_assessment = None
            st.session_state.last_proposal = None
            st.session_state.last_decision_id = None
            st.rerun()