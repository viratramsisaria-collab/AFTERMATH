
"""AFTERMATH shared application layout."""

import html

import streamlit as st

from core.constants import APP_DESCRIPTION, APP_NAME, APP_TAGLINE


PAGES = [
    ("Command Center", "◈", "Overview"),
    ("City Simulator", "⌖", "Explore and advance the city"),
    ("AI Council", "◎", "Eight specialist perspectives"),
    ("Crisis Center", "⚠", "Events and emergency responses"),
    ("Security Command Centre", "🛡", "Public safety and emergency units"),
    ("Disaster Management", "🌪", "Disaster response and recovery"),
    ("Campaigns", "▤", "Long-term objectives"),
    ("Policy & Decisions", "◇", "Human-centred judgement"),
    ("Save / Load", "▣", "Simulation persistence"),
    ("Rules", "⚖", "Survival conditions"),
    ("Game Over", "✕", "Final city report"),
]

DEFEATED_PAGES = {
    "Command Center",
    "City Simulator",
    "Save / Load",
    "Rules",
    "Game Over",
}


def _safe(value) -> str:
    """Escape dynamic content before inserting it into HTML."""

    return html.escape(str(value))


def _inject_styles() -> None:
    """Inject shared layout styles."""

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(148,163,184,0.12);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.4rem;
        }

        .af-brand {
            padding: 0.3rem 0.2rem 1.1rem;
        }

        .af-eyebrow {
            color: #8292a5;
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.15em;
            margin-bottom: 0.6rem;
        }

        .af-brand-name {
            color: #e8eef6;
            font-size: 1.65rem;
            font-weight: 850;
            letter-spacing: 0.12em;
        }

        .af-tagline {
            color: #64d8c8;
            font-size: 0.65rem;
            font-weight: 650;
            letter-spacing: 0.09em;
            margin-top: 0.45rem;
        }

        .af-description {
            color: #8492a5;
            font-size: 0.71rem;
            line-height: 1.6;
            margin-top: 0.7rem;
        }

        .af-section {
            color: #7f8da0;
            font-size: 0.62rem;
            font-weight: 750;
            letter-spacing: 0.15em;
            margin: 0.3rem 0 0.5rem;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] > div {
            gap: 0.2rem;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            border-radius: 7px;
            padding: 0.35rem 0.5rem;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: rgba(100,216,200,0.07);
        }

        .af-status {
            padding: 0.9rem;
            border: 1px solid rgba(148,163,184,0.14);
            border-radius: 9px;
            background: rgba(148,163,184,0.035);
        }

        .af-status-heading {
            color: #8292a5;
            font-size: 0.61rem;
            font-weight: 750;
            letter-spacing: 0.14em;
            margin-bottom: 0.8rem;
        }

        .af-status-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.5rem;
            margin-top: 0.65rem;
        }

        .af-status-label {
            color: #8998aa;
            font-size: 0.69rem;
        }

        .af-status-value {
            color: #e2e8f0;
            font-size: 0.73rem;
            font-weight: 700;
            text-align: right;
        }

        .af-provider {
            color: #8292a5;
            font-size: 0.67rem;
            margin-top: 0.65rem;
        }

        .af-provider strong {
            color: #d4deea;
        }

        .af-footer {
            width: 100%;
            box-sizing: border-box;
            margin-top: 3rem;
            padding: 1.1rem 0 0.7rem;
            border-top: 1px solid rgba(148,163,184,0.15);
        }

        .af-footer-inner {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.8rem 1.5rem;
        }

        .af-footer-brand {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .af-footer-mark {
            color: #64d8c8;
            font-weight: 850;
            font-size: 1rem;
        }

        .af-footer-name {
            color: #e2e8f0;
            font-size: 0.73rem;
            font-weight: 750;
            letter-spacing: 0.12em;
        }

        .af-footer-description {
            color: #8292a5;
            font-size: 0.68rem;
        }

        .af-footer-status {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            color: #91bba9;
            font-size: 0.68rem;
        }

        .af-footer-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #43c99a;
        }

        .af-footer-tagline {
            color: #748398;
            font-size: 0.64rem;
            font-weight: 650;
            letter-spacing: 0.06em;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(
    eyebrow: str,
    title: str,
    description: str,
    city,
) -> None:
    """Render a page heading with current city information."""

    st.markdown(
        f'<div class="eyebrow">{_safe(eyebrow)}</div>',
        unsafe_allow_html=True,
    )

    st.title(title)
    st.caption(description)

    col1, col2, col3 = st.columns(3)

    col1.metric("CURRENT DAY", city.day)
    col2.metric("POPULATION", f"{city.population:,}")
    col3.metric("CITY BUDGET", f"${city.budget:,.0f}")


def render_sidebar(city, provider) -> str:
    """Render the sidebar and return the selected page."""

    _inject_styles()

    brand_html = f"""
    <div class="af-brand">
        <div class="af-eyebrow">CITY MANAGEMENT SIMULATION</div>
        <div class="af-brand-name">{_safe(APP_NAME)}</div>
        <div class="af-tagline">{_safe(APP_TAGLINE)}</div>
        <div class="af-description">{_safe(APP_DESCRIPTION)}</div>
    </div>
    """

    st.sidebar.markdown(brand_html, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    available_pages = [
        page
        for page in PAGES
        if not city.is_game_over or page[0] in DEFEATED_PAGES
    ]

    page_names = [page[0] for page in available_pages]
    page_icons = {page[0]: page[1] for page in available_pages}
    page_descriptions = {page[0]: page[2] for page in available_pages}

    default_page = "Game Over" if city.is_game_over else "Command Center"

    current_page = st.session_state.get(
        "aftermath_navigation",
        default_page,
    )

    if current_page not in page_names:
        current_page = default_page

    st.sidebar.markdown(
        '<div class="af-section">WORKSPACE</div>',
        unsafe_allow_html=True,
    )

    selected_page = st.sidebar.radio(
        "NAVIGATION",
        options=page_names,
        key="aftermath_navigation",
        index=page_names.index(current_page),
        format_func=lambda name: f"{page_icons[name]}  {name}",
        label_visibility="collapsed",
    )

    st.sidebar.caption(page_descriptions[selected_page])
    st.sidebar.markdown("---")

    status_html = (
        '<div class="af-status">'
        '<div class="af-status-heading">SIMULATION STATUS</div>'
        '<div class="af-status-row">'
        '<span class="af-status-label">Current day</span>'
        f'<span class="af-status-value">{_safe(city.day)}</span>'
        '</div>'
        '<div class="af-status-row">'
        '<span class="af-status-label">Population</span>'
        f'<span class="af-status-value">{_safe(f"{city.population:,}")}</span>'
        '</div>'
        '<div class="af-status-row">'
        '<span class="af-status-label">City budget</span>'
        f'<span class="af-status-value">{_safe(f"${city.budget:,.0f}")}</span>'
        '</div>'
        '</div>'
    )

    st.sidebar.markdown(
        status_html,
        unsafe_allow_html=True,
    )
    
    st.sidebar.markdown(status_html, unsafe_allow_html=True)

    if provider is not None:
        provider_name = getattr(
            provider,
            "name",
            type(provider).__name__,
        )

        st.sidebar.markdown(
            f'<div class="af-provider">AI PROVIDER · '
            f'<strong>{_safe(provider_name)}</strong></div>',
            unsafe_allow_html=True,
        )

    return selected_page


def render_footer() -> None:
    """Render the AFTERMATH product footer."""

    footer_html = (
        '<div class="af-footer">'
        '<div class="af-footer-inner">'
        '<div class="af-footer-brand">'
        '<span class="af-footer-mark">A.</span>'
        f'<span class="af-footer-name">{_safe(APP_NAME)}</span>'
        '<span class="af-footer-description">'
        '· AI-powered city simulation'
        '</span>'
        '</div>'
        '<div class="af-footer-status">'
        '<span class="af-footer-dot"></span>'
        '<span>Simulation active</span>'
        '</div>'
        '<div class="af-footer-tagline">'
        f'{_safe(APP_TAGLINE)}'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        footer_html,
        unsafe_allow_html=True,
    )