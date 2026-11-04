"""Synthetic citizen and city activity panels."""

import streamlit as st


def render_society_summary(report: dict) -> None:
    st.markdown("### Community pulse")
    st.caption(
        "SYNTHETIC CITIZEN MODEL · NOT REAL-WORLD PUBLIC OPINION"
    )

    score = report.get("community_score", 0)
    sentiment = report.get("sentiment", "unknown").upper()
    groups = report.get("represented_groups", 0)

    cols = st.columns(3)
    cols[0].metric("Community score", f"{score:.1f}/100")
    cols[1].metric("Overall sentiment", sentiment)
    cols[2].metric("Represented groups", groups)

    group_summary = report.get("group_summary", {})
    if group_summary:
        st.markdown("**Perspective groups**")
        for name, value in group_summary.items():
            st.write(f"{name.replace('_', ' ').title()} · {value:.1f}/100")
            st.progress(max(0.0, min(1.0, value / 100)))

    with st.expander("District-level community readings"):
        for district_report in report.get("districts", []):
            st.write(
                f"**{district_report['district_id']}** — "
                f"{district_report['community_score']:.1f} · "
                f"{district_report['sentiment']}"
            )


def render_activity_feed(city, limit: int = 10) -> None:
    st.markdown("### City activity")
    events = list(reversed(city.event_log[-limit:]))

    if not events:
        st.caption("No recorded activity yet.")
        return

    for event in events:
        st.markdown(
            f"""
            <div style="padding:.65rem .8rem;margin:.4rem 0;
                        border-left:2px solid #27C9D7;
                        background:rgba(16,29,45,.65);
                        border-radius:0 8px 8px 0;
                        font-size:.82rem">
                {event}
            </div>
            """,
            unsafe_allow_html=True,
        )