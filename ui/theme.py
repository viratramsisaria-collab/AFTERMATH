"""AFTERMATH visual theme."""

import streamlit as st

from core.constants import CITY_PALETTE


def inject_theme() -> None:
    p = CITY_PALETTE

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {{
            --bg: {p["background"]};
            --surface: {p["surface"]};
            --surface-light: {p["surface_light"]};
            --primary: {p["primary"]};
            --accent: {p["accent"]};
            --warning: {p["warning"]};
            --danger: {p["danger"]};
            --success: {p["success"]};
            --text: {p["text"]};
            --muted: {p["muted"]};
        }}

        html, body, [class*="css"] {{
            font-family: 'Manrope', sans-serif;
        }}

        .stApp {{
            background:
                radial-gradient(ellipse at 85% 0%, rgba(39,201,215,.09), transparent 35%),
                var(--bg);
            color: var(--text);
        }}

        [data-testid="stHeader"] {{
            background: rgba(8,15,29,.88);
        }}

        [data-testid="stSidebar"] {{
            background: #0b1726;
            border-right: 1px solid rgba(130,149,168,.16);
        }}

        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1.5rem;
        }}

        h1, h2, h3 {{
            letter-spacing: -0.035em;
            color: var(--text);
        }}

        h1 {{ font-weight: 800; }}
        h2, h3 {{ font-weight: 700; }}

        p, label, li {{
            color: #c2cfdb;
        }}

        .eyebrow {{
            font-family: 'DM Mono', monospace;
            font-size: .68rem;
            letter-spacing: .18em;
            color: var(--primary);
            text-transform: uppercase;
            margin-bottom: .35rem;
        }}

        .hero-title {{
            font-size: clamp(2rem, 4vw, 3.1rem);
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -.055em;
            margin: 0;
        }}

        .hero-subtitle {{
            color: var(--muted);
            font-size: .95rem;
            margin-top: .65rem;
        }}

        .panel {{
            background: linear-gradient(145deg, rgba(16,29,45,.96), rgba(12,24,39,.96));
            border: 1px solid rgba(130,149,168,.16);
            border-radius: 15px;
            padding: 1rem 1.15rem;
            margin-bottom: .8rem;
        }}

        .panel-label {{
            font-family: 'DM Mono', monospace;
            color: var(--muted);
            font-size: .68rem;
            letter-spacing: .12em;
            text-transform: uppercase;
        }}

        .panel-value {{
            color: var(--text);
            font-size: 1.65rem;
            font-weight: 800;
            margin-top: .3rem;
        }}

        .panel-note {{
            color: var(--muted);
            font-size: .75rem;
            margin-top: .2rem;
        }}

        .status-dot {{
            display: inline-block;
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--success);
            margin-right: 7px;
            box-shadow: 0 0 10px rgba(69,185,154,.7);
        }}

        .mono {{
            font-family: 'DM Mono', monospace;
        }}

        .muted {{
            color: var(--muted);
        }}

        .stButton > button {{
            border-radius: 9px;
            border: 1px solid rgba(39,201,215,.3);
            background: rgba(39,201,215,.09);
            color: var(--text);
            font-weight: 700;
            transition: all .18s ease;
        }}

        .stButton > button:hover {{
            border-color: var(--primary);
            background: rgba(39,201,215,.18);
            color: white;
        }}

        .stButton > button[kind="primary"] {{
            background: var(--primary);
            border-color: var(--primary);
            color: #06131d;
        }}

        div[data-testid="stMetric"] {{
            background: rgba(16,29,45,.78);
            border: 1px solid rgba(130,149,168,.15);
            border-radius: 12px;
            padding: 13px 15px;
        }}

        div[data-testid="stMetricLabel"] {{
            color: var(--muted);
        }}

        div[data-testid="stMetricValue"] {{
            color: var(--text);
        }}

        .stProgress > div > div > div > div {{
            background-color: var(--primary);
        }}

        div[data-testid="stExpander"] {{
            border: 1px solid rgba(130,149,168,.17);
            border-radius: 10px;
            background: rgba(16,29,45,.45);
        }}

        hr {{
            border-color: rgba(130,149,168,.15);
        }}

        footer {{
            visibility: hidden;
        }}

        #MainMenu {{
            visibility: hidden;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )