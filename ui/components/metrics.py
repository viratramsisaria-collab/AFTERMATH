"""Reusable city metric visualisations."""

import streamlit as st


METRIC_LABELS = {
    "economic_health": "Economic health",
    "mobility": "Mobility",
    "public_wellbeing": "Public wellbeing",
    "environmental_health": "Environmental health",
    "social_equity": "Social equity",
    "safety": "Public safety",
    "healthcare_access": "Healthcare access",
    "happiness": "Happiness",
    "energy_reserve": "Energy reserve",
    "water_reserve": "Water reserve",
    "traffic_congestion": "Traffic congestion",
}


def metric_color(value: float, inverse: bool = False) -> str:
    score = 100 - value if inverse else value

    if score >= 70:
        return "#45B99A"
    if score >= 45:
        return "#E6B85C"
    return "#E46D73"


def render_metric_grid(metrics, columns: int = 3) -> None:
    values = metrics.model_dump()
    keys = list(METRIC_LABELS)

    for start in range(0, len(keys), columns):
        cols = st.columns(columns)

        for col, key in zip(cols, keys[start:start + columns]):
            value = float(values[key])
            inverse = key == "traffic_congestion"
            display_value = 100 - value if inverse else value
            color = metric_color(value, inverse)

            with col:
                st.markdown(
                    f"""
                    <div class="panel">
                        <div class="panel-label">{METRIC_LABELS[key]}</div>
                        <div style="font-size:1.55rem;font-weight:800;
                                    color:{color};margin:.3rem 0">
                            {value:.1f}<span style="font-size:.75rem;color:#8295A8"> / 100</span>
                        </div>
                        <div style="height:5px;background:#26384A;border-radius:8px">
                            <div style="height:5px;width:{display_value}%;
                                        background:{color};border-radius:8px"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_metric_trend(city, metric: str, title: str) -> None:
    rows = [
        {"Day": snapshot.day, title: getattr(snapshot.metrics, metric)}
        for snapshot in city.history
    ]

    if rows:
        st.line_chart(
            rows,
            x="Day",
            y=title,
            color="#27C9D7",
            use_container_width=True,
        )
    else:
        st.info("No simulation history yet. Advance the simulation to create a trend.")