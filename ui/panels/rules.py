
"""AFTERMATH — THE SURVIVAL CODEX
Official in-game handbook and administration field manual.
"""

from __future__ import annotations

import html

import streamlit as st

from simulation.rules import LOSS_CONDITIONS
from ui.layout import render_page_header


# ============================================================
# DESIGN SYSTEM
# ============================================================

def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .codex {
            --cyan: #36D5DF;
            --green: #58C9A5;
            --red: #EA737D;
            --amber: #E9B36A;
            --text: #E5EDF4;
            --muted: #91A2B3;
            --line: rgba(145,170,190,.17);
        }

        .codex-hero {
            position: relative;
            overflow: hidden;
            padding: 36px;
            border-radius: 15px;
            border: 1px solid rgba(54,213,223,.24);
            background:
                radial-gradient(ellipse at 90% 0%,
                    rgba(54,213,223,.15), transparent 43%),
                linear-gradient(135deg,#142B3A,#091722);
            margin: 12px 0 25px;
        }

        .codex-hero:after {
            content: "AFTERMATH";
            position: absolute;
            right: -12px;
            bottom: -35px;
            font-size: 92px;
            font-weight: 950;
            letter-spacing: -.09em;
            color: rgba(255,255,255,.025);
            pointer-events: none;
        }

        .codex-eyebrow {
            font-family: monospace;
            font-size: 10px;
            letter-spacing: .2em;
            color: var(--cyan);
            margin-bottom: 17px;
            font-weight: 800;
        }

        .codex-title {
            font-size: clamp(32px,5vw,49px);
            font-weight: 950;
            line-height: 1.02;
            letter-spacing: -.065em;
            color: #F0F8FC;
        }

        .codex-subtitle {
            font-size: 13px;
            line-height: 1.9;
            max-width: 650px;
            color: #9BB0C0;
            margin-top: 17px;
        }

        .codex-tags {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 24px;
        }

        .codex-tag {
            font-family: monospace;
            font-size: 9px;
            letter-spacing: .09em;
            color: #A7E7E9;
            border: 1px solid rgba(54,213,223,.22);
            background: rgba(54,213,223,.07);
            padding: 7px 10px;
            border-radius: 4px;
        }

        .codex-section {
            margin: 30px 0 15px;
            padding-bottom: 13px;
            border-bottom: 1px solid var(--line);
        }

        .codex-index {
            font-family: monospace;
            font-size: 10px;
            color: var(--cyan);
            letter-spacing: .18em;
            margin-bottom: 7px;
        }

        .codex-heading {
            font-size: 23px;
            color: var(--text);
            font-weight: 900;
            letter-spacing: -.045em;
        }

        .codex-description {
            color: var(--muted);
            font-size: 12px;
            line-height: 1.8;
            margin-top: 6px;
        }

        .codex-card {
            height: 100%;
            min-height: 115px;
            padding: 17px;
            margin-bottom: 10px;
            border: 1px solid var(--line);
            border-radius: 9px;
            background: linear-gradient(145deg,
                rgba(22,42,57,.86),
                rgba(12,26,38,.86));
        }

        .codex-card-label {
            color: #849BAC;
            font-family: monospace;
            font-size: 9px;
            letter-spacing: .13em;
        }

        .codex-card-value {
            color: #EAF5FA;
            font-size: 23px;
            font-weight: 900;
            margin-top: 9px;
        }

        .codex-card-description {
            color: #91A5B5;
            font-size: 11px;
            line-height: 1.7;
            margin-top: 7px;
        }

        .codex-panel {
            background: rgba(17,34,48,.72);
            border: 1px solid var(--line);
            border-radius: 9px;
            padding: 16px;
            margin: 9px 0;
        }

        .codex-panel-title {
            font-size: 13px;
            font-weight: 850;
            color: #E6F0F5;
        }

        .codex-panel-category {
            font-family: monospace;
            font-size: 9px;
            color: var(--cyan);
            letter-spacing: .12em;
            margin-top: 5px;
        }

        .codex-panel-text {
            font-size: 11px;
            line-height: 1.85;
            color: #94A9B9;
            margin-top: 10px;
        }

        .codex-condition {
            background: rgba(18,34,47,.8);
            border: 1px solid var(--line);
            border-radius: 9px;
            padding: 14px;
            margin-bottom: 9px;
        }

        .codex-condition-name {
            font-size: 12px;
            color: #E6F0F5;
            font-weight: 850;
        }

        .codex-condition-value {
            font-family: monospace;
            font-size: 13px;
            color: #F0A0A4;
            font-weight: 800;
            margin-top: 10px;
        }

        .codex-condition-description {
            color: #91A5B5;
            font-size: 11px;
            line-height: 1.7;
            margin-top: 6px;
        }

        .codex-status {
            font-family: monospace;
            font-size: 9px;
            font-weight: 900;
            letter-spacing: .1em;
        }

        .codex-good { color: #58C9A5; }
        .codex-bad { color: #EA737D; }

        .codex-callout {
            padding: 17px;
            border-radius: 8px;
            margin: 13px 0;
            font-size: 12px;
            line-height: 1.9;
        }

        .codex-warning {
            color: #E8B4B7;
            border: 1px solid rgba(234,115,125,.25);
            background: rgba(234,115,125,.07);
        }

        .codex-info {
            color: #A7CDD5;
            border: 1px solid rgba(54,213,223,.23);
            background: rgba(54,213,223,.055);
        }

        .codex-success {
            color: #A8DCCB;
            border: 1px solid rgba(88,201,165,.23);
            background: rgba(88,201,165,.055);
        }

        .codex-timeline {
            border-left: 2px solid rgba(54,213,223,.32);
            margin: 18px 0 18px 9px;
            padding-left: 22px;
        }

        .codex-step {
            position: relative;
            padding-bottom: 20px;
        }

        .codex-step:before {
            content: "";
            position: absolute;
            left: -28px;
            top: 4px;
            width: 10px;
            height: 10px;
            background: var(--cyan);
            border-radius: 50%;
            box-shadow: 0 0 12px rgba(54,213,223,.35);
        }

        .codex-step-title {
            font-size: 12px;
            color: #E5F0F5;
            font-weight: 850;
        }

        .codex-step-text {
            color: #91A5B5;
            font-size: 11px;
            line-height: 1.8;
            margin-top: 5px;
        }

        .codex-rule-id {
            font-family: monospace;
            color: var(--cyan);
            font-size: 10px;
        }

        .codex-footer {
            text-align: center;
            padding: 27px 10px;
            margin-top: 35px;
            border-top: 1px solid var(--line);
            font-family: monospace;
            color: #8095A7;
            font-size: 9px;
            letter-spacing: .15em;
            line-height: 2.2;
        }

        .codex .stTabs [data-baseweb="tab"] {
            font-family: monospace;
            font-size: 10px;
        }

        .codex .stTabs [aria-selected="true"] {
            color: var(--cyan);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# REUSABLE COMPONENTS
# ============================================================

def section(index: str, title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="codex-section">
            <div class="codex-index">{index} // CODEX ENTRY</div>
            <div class="codex-heading">{title}</div>
            <div class="codex-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(label: str, value: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="codex-card">
            <div class="codex-card-label">{label}</div>
            <div class="codex-card-value">{value}</div>
            <div class="codex-card-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel(
    title: str,
    category: str,
    description: str,
) -> None:
    st.markdown(
        f"""
        <div class="codex-panel">
            <div class="codex-panel-title">{title}</div>
            <div class="codex-panel-category">{category}</div>
            <div class="codex-panel-text">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def callout(message: str, kind: str = "info") -> None:
    css_class = {
        "info": "codex-info",
        "warning": "codex-warning",
        "success": "codex-success",
    }.get(kind, "codex-info")

    st.markdown(
        f'<div class="codex-callout {css_class}">{message}</div>',
        unsafe_allow_html=True,
    )


def timeline(steps: list[tuple[str, str]]) -> None:
    content = "".join(
        f"""
        <div class="codex-step">
            <div class="codex-step-title">{html.escape(title)}</div>
            <div class="codex-step-text">{html.escape(description)}</div>
        </div>
        """
        for title, description in steps
    )

    st.markdown(
        f'<div class="codex-timeline">{content}</div>',
        unsafe_allow_html=True,
    )


def metric(city, name: str, default=None):
    return getattr(city.metrics, name, default)


def metric_display(value) -> str:
    if value is None:
        return "N/A"

    if isinstance(value, (int, float)):
        return f"{value:,.2f}".rstrip("0").rstrip(".")

    return html.escape(str(value))


# ============================================================
# 00 — MISSION CONTROL
# ============================================================

def render_overview(city) -> None:
    city_name = html.escape(str(getattr(city, "city_name", "Unknown City")))
    day = int(getattr(city, "day", 0))
    game_over = bool(getattr(city, "is_game_over", False))

    section(
        "00",
        "THE ADMINISTRATOR'S DIRECTIVE",
        "Your appointment begins here. Your responsibility ends only "
        "when the city survives or the administration falls.",
    )

    cols = st.columns(4)

    with cols[0]:
        card("CURRENT DAY", f"{day:03d}", "The current simulation day.")

    with cols[1]:
        card(
            "DISTRICTS",
            str(getattr(city, "district_count", "—")),
            "Districts represented in the city simulation.",
        )

    with cols[2]:
        card(
            "CITY BUDGET",
            f"{getattr(city, 'budget', 0):,.0f}",
            "Current available administration funds.",
        )

    with cols[3]:
        card(
            "ADMINISTRATION",
            "DEFEATED" if game_over else "ACTIVE",
            "Current simulation status.",
        )

    panel(
        f"THE CITY OF {city_name.upper()}",
        "YOUR JURISDICTION",
        "You are responsible for managing an interconnected urban "
        "system. Infrastructure, residents, the economy, public "
        "services, disasters and security operations all contribute "
        "to the city's condition.",
    )

    section(
        "00.1",
        "THE OBJECTIVE",
        "There is no single metric that defines a successful city.",
    )

    panel(
        "PRESERVE THE CITY",
        "PRIMARY OBJECTIVE",
        "Keep every defeat-sensitive city system within its survival "
        "limits while managing the consequences of your decisions.",
    )

    panel(
        "MANAGE THE CONSEQUENCES",
        "ADMINISTRATIVE OBJECTIVE",
        "Policies, simulation changes, crisis decisions and resource "
        "allocations can influence several connected systems.",
    )

    panel(
        "RESPOND TO THE UNEXPECTED",
        "EMERGENCY OBJECTIVE",
        "Use the crisis, disaster and security systems to coordinate "
        "responses to threats affecting the city.",
    )

    panel(
        "MAKE INFORMED DECISIONS",
        "GOVERNANCE OBJECTIVE",
        "Use the AI Council, city information and simulation feedback "
        "as decision-support resources. The final authority remains "
        "with the player.",
    )

    callout(
        "<b>THE GOLDEN RULE</b><br>"
        "A city can look healthy in one area and still be approaching "
        "collapse in another. Never manage a single metric in isolation.",
        "warning",
    )


# ============================================================
# 01 — SIMULATION ENGINE
# ============================================================

def render_simulation(city) -> None:
    section(
        "01",
        "THE SIMULATION ENGINE",
        "The machinery behind every passing day.",
    )

    panel(
        "DAILY SIMULATION",
        "CORE MECHANIC",
        "The simulation engine advances the city through daily updates. "
        "The economy, environment, population and transportation "
        "systems interact and influence the city's condition.",
    )

    st.markdown(
        """
        <div class="codex-timeline">
            <div class="codex-step">
                <div class="codex-step-title">01 — ADMINISTRATIVE ACTION</div>
                <div class="codex-step-text">The player makes decisions through the available city-management systems.</div>
            </div>
            <div class="codex-step">
                <div class="codex-step-title">02 — WORLD UPDATE</div>
                <div class="codex-step-text">The simulation processes changes to the city's interconnected systems and conditions.</div>
            </div>
            <div class="codex-step">
                <div class="codex-step-title">03 — EMERGENCY PROCESSING</div>
                <div class="codex-step-text">The disaster and security systems process their scheduled operations, deployments, deadlines and recovery progress.</div>
            </div>
            <div class="codex-step">
                <div class="codex-step-title">04 — SURVIVAL VALIDATION</div>
                <div class="codex-step-text">The game evaluates the loss conditions. A failed condition terminates the administration.</div>
            </div>
            <div class="codex-step">
                <div class="codex-step-title">05 — HISTORY</div>
                <div class="codex-step-text">Successful simulation progression is recorded in the city's simulation history.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="codex-callout codex-warning">
            <b>TIME IS A RESOURCE</b><br>
            Advancing the simulation is not a harmless interface action.
            It allows the city's systems and ongoing operations to progress.
        </div>
        """,
        unsafe_allow_html=True,
    )

    section(
        "01.1",
        "THE WORLD",
        "The city is represented by interconnected urban components.",
    )

    panel(
        "DISTRICTS",
        "URBAN GEOGRAPHY",
        "Districts divide the city into manageable areas. They provide "
        "geographical context for city conditions, disaster exposure "
        "and response operations.",
    )

    panel(
        "BUILDINGS",
        "BUILT ENVIRONMENT",
        "Buildings represent the city's physical assets. Disaster "
        "impacts and recovery operations can affect building conditions, "
        "including damage and repairs.",
    )

    panel(
        "ROADS",
        "TRANSPORT NETWORK",
        "Road infrastructure supports movement and transportation. "
        "Road conditions and congestion form part of the city's "
        "transportation picture.",
    )

    panel(
        "POPULATION",
        "CITIZEN SYSTEM",
        "Residents are part of the city's simulation. Their wellbeing "
        "and the city's public conditions are important considerations "
        "in administration.",
    )

    section(
        "01.2",
        "THE FEEDBACK LOOP",
        "Understand why decisions can have consequences beyond their target.",
    )

    st.markdown(
        """
        <div class="codex-callout codex-info">
            <b>INTERCONNECTED SYSTEMS</b><br>
            An intervention in one urban system may create pressure elsewhere.
            For example, infrastructure, economic conditions, public services
            and environmental conditions should be considered together.
            The game is a simulation, not a calibrated real-world forecast.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 02 — CITY SYSTEMS
# ============================================================

def render_city_systems(city) -> None:
    section(
        "02",
        "THE CITY'S VITAL SYSTEMS",
        "Read the city's condition before making your next move.",
    )

    systems = [
        (
            "Economic Health",
            "economic_health",
            "ECONOMY",
            "The condition of the city's economic system.",
            "◈",
        ),
        (
            "Mobility",
            "mobility",
            "TRANSPORT",
            "The city's transportation and movement condition.",
            "⇄",
        ),
        (
            "Environmental Health",
            "environmental_health",
            "ENVIRONMENT",
            "The condition of the urban environment.",
            "♧",
        ),
        (
            "Social Equity",
            "social_equity",
            "SOCIETY",
            "The city's social balance and equity condition.",
            "◎",
        ),
        (
            "Public Safety",
            "safety",
            "SECURITY",
            "The safety condition of the city.",
            "⬡",
        ),
        (
            "Healthcare Access",
            "healthcare_access",
            "HEALTHCARE",
            "Access to healthcare services.",
            "+",
        ),
        (
            "Happiness",
            "happiness",
            "CITIZEN WELLBEING",
            "The happiness condition of the population.",
            "◇",
        ),
        (
            "Energy Reserve",
            "energy_reserve",
            "UTILITIES",
            "The available energy reserve.",
            "ϟ",
        ),
        (
            "Water Reserve",
            "water_reserve",
            "UTILITIES",
            "The available water reserve.",
            "◉",
        ),
        (
            "Traffic Congestion",
            "traffic_congestion",
            "TRANSPORT",
            "Traffic pressure across the city.",
            "⌁",
        ),
    ]

    for start in range(0, len(systems), 2):
        cols = st.columns(2)

        for col, item in zip(cols, systems[start:start + 2]):
            title, key, category, description, symbol = item

            with col:
                value = metric(city, key)
                displayed = metric_display(value)

                st.markdown(
                    f"""
                    <div class="codex-panel">
                        <div class="codex-panel-category">
                            {category}
                        </div>
                        <div class="codex-panel-title">
                            {symbol} &nbsp; {title}
                        </div>
                        <div class="codex-panel-text">
                            {description}
                        </div>
                        <div style="font-family:monospace;
                                    color:#36D5DF;font-size:15px;
                                    font-weight:800;margin-top:12px">
                            {displayed}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    callout(
        "<b>READ THE INDICATORS</b><br>"
        "The live values above are drawn from the current city's metrics. "
        "Not every metric has an independent defeat condition. "
        "The following chapter identifies the actual loss conditions.",
        "info",
    )


# ============================================================
# 03 — LOSS CONDITIONS
# ============================================================

def render_failure_protocol(city) -> None:
    section(
        "03",
        "THE FAILURE PROTOCOL",
        "Ten survival checks stand between the city and administrative collapse.",
    )

    failed_count = 0
    rows = []

    for condition in LOSS_CONDITIONS:
        value = float(getattr(city.metrics, condition.metric))
        failed = condition.is_failed(value)

        if failed:
            failed_count += 1

        direction = (
            "BELOW"
            if condition.operator == "below"
            else "ABOVE"
        )

        rows.append((condition, value, failed, direction))

    cols = st.columns(3)

    with cols[0]:
        card(
            "TOTAL CONDITIONS",
            str(len(LOSS_CONDITIONS)),
            "Independent defeat checks.",
        )

    with cols[1]:
        card(
            "BREACHED CONDITIONS",
            str(failed_count),
            "Currently failed survival checks.",
        )

    with cols[2]:
        card(
            "GAME STATE",
            "DEFEATED" if city.is_game_over else "SURVIVING",
            "Current administration status.",
        )

    callout(
        "<b>STRICT THRESHOLD LAW</b><br>"
        "A condition fails only when the metric crosses its threshold. "
        "Equality survives. A condition using BELOW fails only when "
        "the value is strictly lower. A condition using ABOVE fails "
        "only when the value is strictly higher.",
        "warning",
    )

    st.markdown("#### THE TEN CONDITIONS")

    left, right = st.columns(2)

    for index, (condition, value, failed, direction) in enumerate(rows):
        with (left if index % 2 == 0 else right):
            status = "FAILED" if failed else "STABLE"
            css = "codex-bad" if failed else "codex-good"

            st.markdown(
                f"""
                <div class="codex-condition">
                    <div style="display:flex;justify-content:space-between;
                                align-items:center;gap:8px">
                        <div class="codex-condition-name">
                            {index + 1:02d} // {html.escape(condition.label)}
                        </div>
                        <div class="codex-status {css}">
                            {status}
                        </div>
                    </div>
                    <div class="codex-condition-value">
                        {value:.2f} &nbsp; | &nbsp;
                        {direction} {condition.threshold:g}
                    </div>
                    <div class="codex-condition-description">
                        {html.escape(condition.description)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("#### HOW DEFEAT IS DETERMINED")

    panel(
        "FIRST FAILED CONDITION WINS",
        "EVALUATION ORDER",
        "The simulation evaluates the configured LOSS_CONDITIONS. "
        "When a failed condition is found, evaluate_loss() returns "
        "the first failed condition. The administration does not "
        "need to violate all ten conditions to lose.",
    )

    timeline([
        ("METRIC INSPECTION", "Read the current value of a protected city metric."),
        ("THRESHOLD COMPARISON", "Apply the configured below or above operator."),
        ("CONDITION EVALUATION", "Use the condition's own is_failed() implementation."),
        ("GAME OVER", "The first failed condition determines the reported failure."),
    ])

    if city.is_game_over:
        callout(
            "<b>ADMINISTRATION TERMINATED</b><br>"
            f"Day {getattr(city, 'game_over_day', None) or city.day}. "
            f"Failure: {html.escape(str(getattr(city, 'game_over_label', None) or 'Critical city condition'))}.",
            "warning",
        )


# ============================================================
# 04 — COMMAND CENTER
# ============================================================

def render_command_center() -> None:
    section(
        "04",
        "COMMAND CENTER",
        "Your central administrative intelligence dashboard.",
    )

    panel(
        "CITY OVERVIEW",
        "COMMAND CENTER",
        "The Command Center provides the primary overview of the city. "
        "It is the place to inspect the current state of the administration "
        "and understand what requires attention.",
    )

    panel(
        "SYSTEM MONITORING",
        "LIVE CITY STATUS",
        "Use the available city indicators to identify deteriorating "
        "conditions and monitor the effect of administrative decisions.",
    )

    panel(
        "OPERATIONAL NAVIGATION",
        "CONTROL ACCESS",
        "The Command Center provides access to the major management "
        "systems, including simulation, governance, AI Council, "
        "crisis response, security and disaster management.",
    )

    callout(
        "<b>FIELD ADVICE</b><br>"
        "Use the Command Center as your starting point. Investigate "
        "critical indicators before advancing the simulation.",
        "info",
    )


# ============================================================
# 05 — AI COUNCIL
# ============================================================

def render_ai_council() -> None:
    section(
        "05",
        "THE AI COUNCIL",
        "Intelligence may advise the administration. It does not govern it.",
    )

    panel(
        "DECISION SUPPORT",
        "AI COUNCIL",
        "The AI Council provides an intelligence layer for evaluating "
        "city conditions and considering administrative decisions. "
        "Its output is intended to assist the player.",
    )

    panel(
        "CITY CONTEXT",
        "INFORMED RECOMMENDATIONS",
        "AI-assisted analysis can be considered alongside the city's "
        "current metrics, problems and operational circumstances.",
    )

    panel(
        "HUMAN AUTHORITY",
        "FINAL DECISION",
        "AI recommendations are not binding decisions. The player "
        "retains authority over the administration and its choices.",
    )

    callout(
        "<b>THE COUNCIL IS AN ADVISOR, NOT A MAYOR.</b><br>"
        "Do not treat an AI-generated recommendation as a guaranteed "
        "outcome. Consider the current city state and potential "
        "consequences before taking action.",
        "warning",
    )


# ============================================================
# 06 — CRISIS CENTER
# ============================================================

def render_crisis_center() -> None:
    section(
        "06",
        "THE CRISIS CENTER",
        "Understand the threats facing the population.",
    )

    panel(
        "CRISIS MONITORING",
        "CRISIS CENTER",
        "The Crisis Center provides a dedicated place to examine "
        "developing city crises and their implications for "
        "administrative stability.",
    )

    panel(
        "PUBLIC CONDITIONS",
        "CITIZEN PERSPECTIVES",
        "The application can present synthetic citizen perspectives "
        "to help contextualize public conditions and administrative "
        "challenges.",
    )

    panel(
        "PRIORITY AND RESPONSE",
        "CRISIS MANAGEMENT",
        "Use crisis information together with the city indicators "
        "and available response systems to determine what needs "
        "attention first.",
    )

    callout(
        "<b>IMPORTANT — SYNTHETIC PERSPECTIVES</b><br>"
        "Citizen perspectives generated by the simulation are not "
        "actual resident surveys. They are contextual game outputs, "
        "not verified public-opinion research.",
        "info",
    )


# ============================================================
# 07 — DISASTER MANAGEMENT
# ============================================================

def render_disaster_management() -> None:
    section(
        "07",
        "DISASTER MANAGEMENT",
        "An emergency is not resolved simply because it has been detected.",
    )

    panel(
        "DISASTER GENERATION",
        "GENERATOR AND SCHEDULER",
        "The disaster system generates and schedules emergency "
        "events. Its scheduling and generation logic are part "
        "of the simulation.",
    )

    panel(
        "DISTRICT EXPOSURE",
        "VULNERABILITY",
        "Disaster exposure considers affected districts and their "
        "vulnerability. A disaster is therefore not just a global "
        "city notification.",
    )

    panel(
        "DISASTER IMPACT",
        "IMPACT ENGINE",
        "Disasters can affect city metrics and physical assets, "
        "including buildings. The impact system records the "
        "consequences of an event.",
    )

    panel(
        "RESPONSE OBJECTIVES",
        "CONTAINMENT",
        "Disasters have response objectives and progress tracking. "
        "Deployments and operational progress contribute to the "
        "response process.",
    )

    panel(
        "RECOVERY",
        "POST-DISASTER OPERATIONS",
        "Recovery is represented separately from immediate containment. "
        "The application tracks recovery operations and building "
        "damage and repair information.",
    )

    section(
        "07.1",
        "THE DISASTER LIFECYCLE",
        "From initial detection to long-term recovery.",
    )

    timeline([
        (
            "01 — GENERATION",
            "The disaster generator creates a disaster instance.",
        ),
        (
            "02 — SCHEDULING",
            "The scheduler determines when events enter the simulation.",
        ),
        (
            "03 — EXPOSURE",
            "Affected districts and vulnerability are considered.",
        ),
        (
            "04 — IMPACT",
            "The impact engine applies the disaster's consequences.",
        ),
        (
            "05 — RESPONSE",
            "Objectives and deployments track the response operation.",
        ),
        (
            "06 — CONTAINMENT",
            "Response progress determines the containment outcome.",
        ),
        (
            "07 — RECOVERY",
            "Recovery operations track post-event restoration.",
        ),
    ])

    callout(
        "<b>CONTAINMENT IS NOT RECOVERY</b><br>"
        "Containing an emergency and restoring damaged city assets "
        "are separate parts of disaster management. Do not assume "
        "that a contained disaster automatically means every "
        "consequence has been repaired.",
        "warning",
    )


# ============================================================
# 08 — SECURITY COMMAND CENTRE
# ============================================================

def render_security() -> None:
    section(
        "08",
        "SECURITY COMMAND CENTRE",
        "Personnel, incidents, deployments and operational resources.",
    )

    panel(
        "DEPARTMENTS AND UNITS",
        "SECURITY ORGANIZATION",
        "Security operations are organized through departments "
        "and operational units. The security system maintains "
        "the personnel and resources associated with its operations.",
    )

    panel(
        "PERSONNEL MANAGEMENT",
        "WORKFORCE",
        "The security system tracks personnel and their operational "
        "availability. Personnel are part of the response capacity "
        "of the city.",
    )

    panel(
        "INCIDENT MANAGEMENT",
        "EMERGENCY OPERATIONS",
        "Incidents can be created and tracked through the security "
        "system. Operations can be dispatched and recalled.",
    )

    panel(
        "DEPLOYMENT MANAGEMENT",
        "FIELD OPERATIONS",
        "Deployments connect security resources with operational "
        "requirements. Deployment progress is also relevant to "
        "disaster response.",
    )

    panel(
        "RESOURCE MANAGEMENT",
        "OPERATIONAL CAPACITY",
        "Security resources and operational costs form part of "
        "the security management system.",
    )

    panel(
        "OPERATIONAL LOGS",
        "PERFORMANCE AND HISTORY",
        "The security system records operational activity, costs "
        "and performance information for administration review.",
    )

    callout(
        "<b>PERSONNEL ARE NOT INFINITE</b><br>"
        "Consider the operational requirements and resource "
        "implications of dispatching and managing security units.",
        "warning",
    )


# ============================================================
# 09 — CAMPAIGNS
# ============================================================

def render_campaigns() -> None:
    section(
        "09",
        "CAMPAIGNS",
        "A structured way to experience the city's challenges.",
    )

    panel(
        "CAMPAIGN MANAGEMENT",
        "CAMPAIGNS",
        "The application includes a dedicated campaign system "
        "for organizing the game experience around campaign "
        "scenarios and their associated objectives.",
    )

    panel(
        "OBJECTIVE-DRIVEN PLAY",
        "PROGRESSION",
        "Campaigns provide an additional layer of direction "
        "beyond simply monitoring city metrics.",
    )

    panel(
        "ADMINISTRATIVE CHALLENGE",
        "DECISION MAKING",
        "Campaign gameplay should be approached by considering "
        "the city state, available management systems and "
        "the objectives presented by the active campaign.",
    )

    callout(
        "<b>CAMPAIGN-SPECIFIC RULES</b><br>"
        "The active campaign's own displayed objectives and "
        "conditions are authoritative. This handbook does not "
        "assign unverified rewards, story events, difficulty "
        "modifiers or victory conditions.",
        "info",
    )


# ============================================================
# 10 — POLICY AND DECISIONS
# ============================================================

def render_policies() -> None:
    section(
        "10",
        "POLICY & DECISIONS",
        "Administration is the art of choosing what happens next.",
    )

    panel(
        "POLICY MANAGEMENT",
        "GOVERNANCE",
        "The application provides a dedicated policy and decisions "
        "system for making administrative choices that influence "
        "the city.",
    )

    panel(
        "SYSTEM CONSEQUENCES",
        "CITY MANAGEMENT",
        "Policy decisions should be considered in relation to "
        "the city's connected systems. A decision should not "
        "be evaluated solely by its immediate target.",
    )

    panel(
        "DECISION AUTHORITY",
        "PLAYER CONTROL",
        "The player remains responsible for the decisions made "
        "on behalf of the administration. AI assistance does "
        "not replace this authority.",
    )

    callout(
        "<b>NO DECISION IS AUTOMATICALLY A GOOD DECISION.</b><br>"
        "Review the current city conditions and available "
        "decision information before committing to a policy.",
        "warning",
    )


# ============================================================
# 11 — SAVE AND LOAD
# ============================================================

def render_save_load() -> None:
    section(
        "11",
        "SAVE / LOAD PROTOCOL",
        "Preserve your administration and return to its state.",
    )

    panel(
        "SAVE SYSTEM",
        "PERSISTENCE",
        "The Save/Load interface provides the game's persistence "
        "workflow. Use it to preserve a city state through the "
        "available save functionality.",
    )

    panel(
        "LOAD SYSTEM",
        "RESTORATION",
        "The loading workflow restores a previously saved game "
        "state so that the administration can continue from "
        "that stored state.",
    )

    panel(
        "CITY STATE",
        "PERSISTED SIMULATION",
        "The game state includes the city simulation and its "
        "associated systems, including security and disaster "
        "state managed by CityState.",
    )

    callout(
        "<b>ADMINISTRATION PRACTICE</b><br>"
        "Use the actual save and load controls provided by the "
        "application. This handbook does not assume automatic "
        "saving or an unverified checkpoint system.",
        "info",
    )


# ============================================================
# 12 — GAME OVER
# ============================================================

def render_game_over(city) -> None:
    section(
        "12",
        "GAME OVER",
        "The end of an administration is the result of a failed survival check.",
    )

    if city.is_game_over:
        st.markdown(
            """
            <div class="codex-hero"
                 style="border-color:rgba(234,115,125,.4);
                        background:linear-gradient(135deg,#351C28,#17151E)">
                <div class="codex-eyebrow" style="color:#EA737D">
                    ADMINISTRATION TERMINATED
                </div>
                <div class="codex-title">CITY LOST.</div>
                <div class="codex-subtitle">
                    The simulation has recorded a failed survival condition.
                    This administration has reached its end.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cols = st.columns(2)

        with cols[0]:
            card(
                "FAILURE DAY",
                str(getattr(city, "game_over_day", None) or city.day),
                "The recorded day of defeat.",
            )

        with cols[1]:
            card(
                "FAILURE CONDITION",
                str(
                    getattr(city, "game_over_label", None)
                    or "Critical city system"
                ),
                "The reported reason for termination.",
            )

    else:
        st.markdown(
            """
            <div class="codex-hero"
                 style="border-color:rgba(88,201,165,.3)">
                <div class="codex-eyebrow">
                    ADMINISTRATION STATUS
                </div>
                <div class="codex-title">STILL STANDING.</div>
                <div class="codex-subtitle">
                    The city has not entered a game-over state.
                    Continue monitoring its systems and responding
                    to the challenges of administration.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    panel(
        "WHAT ENDS THE GAME?",
        "LOSS EVALUATION",
        "The simulation checks LOSS_CONDITIONS. The first condition "
        "whose is_failed() evaluation returns true causes the "
        "administration to end.",
    )

    panel(
        "WHAT DOES NOT END THE GAME BY ITSELF?",
        "IMPORTANT DISTINCTION",
        "A difficult decision, an active crisis or an ongoing "
        "disaster is not automatically equivalent to game over. "
        "The actual defeat rules are the configured loss conditions.",
    )


# ============================================================
# 13 — ADMINISTRATOR'S FIELD NOTES
# ============================================================

def render_field_notes() -> None:
    section(
        "13",
        "FIELD NOTES",
        "Operational principles for surviving the administration.",
    )

    notes = [
        (
            "01",
            "WATCH THE WHOLE CITY",
            "Do not focus exclusively on one metric. Monitor the "
            "full set of survival conditions.",
        ),
        (
            "02",
            "UNDERSTAND THE CONSEQUENCES",
            "A decision can influence more than one part of the "
            "urban system.",
        ),
        (
            "03",
            "DO NOT IGNORE EMERGENCIES",
            "Disaster response, security deployments and recovery "
            "operations require attention.",
        ),
        (
            "04",
            "USE INTELLIGENCE RESPONSIBLY",
            "AI recommendations and synthetic citizen perspectives "
            "are decision-support material, not verified guarantees.",
        ),
        (
            "05",
            "REVIEW BEFORE ADVANCING",
            "Inspect the city and its outstanding operations before "
            "allowing the simulation to progress.",
        ),
        (
            "06",
            "UNDERSTAND THE FAILURE RULES",
            "Know which indicators can terminate the administration "
            "and the direction in which each threshold applies.",
        ),
        (
            "07",
            "PRESERVE YOUR PROGRESS",
            "Use the available save system to retain important "
            "administrative progress.",
        ),
    ]

    for number, title, description in notes:
        st.markdown(
            f"""
            <div class="codex-panel">
                <div class="codex-rule-id">FIELD NOTE // {number}</div>
                <div class="codex-panel-title" style="margin-top:7px">
                    {title}
                </div>
                <div class="codex-panel-text">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# MAIN HANDBOOK
# ============================================================

def render_rules(city) -> None:
    """Render the complete AFTERMATH Survival Codex."""

    inject_styles()

    render_page_header(
        "08 / GOVERNANCE",
        "The Survival Codex",
        "The official field manual of AFTERMATH. Learn the systems, "
        "understand the consequences, and protect your administration.",
        city,
    )

    st.markdown('<div class="codex">', unsafe_allow_html=True)

    city_name = html.escape(str(getattr(city, "city_name", "YOUR CITY")))
    day = int(getattr(city, "day", 0))

    st.markdown(
        f"""
        <div class="codex-hero">
            <div class="codex-eyebrow">
                AFTERMATH // OFFICIAL ADMINISTRATION HANDBOOK
            </div>
            <div class="codex-title">
                THE SURVIVAL<br>CODEX.
            </div>
            <div class="codex-subtitle">
                Every city has a breaking point. Every administration
                has a responsibility. This document contains the
                systems, rules and operational knowledge required
                to understand the world of AFTERMATH.
                <br><br>
                <b style="color:#DDECF3">{city_name}</b> //
                SIMULATION DAY {day:03d}
            </div>
            <div class="codex-tags">
                <span class="codex-tag">CLASSIFICATION: OFFICIAL</span>
                <span class="codex-tag">DOCUMENT: 08-001</span>
                <span class="codex-tag">STATUS: ACTIVE</span>
                <span class="codex-tag">EDITION: 01</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs([
        "01 / OVERVIEW",
        "02 / SIMULATION",
        "03 / CITY SYSTEMS",
        "04 / SURVIVAL",
        "05 / COMMAND",
        "06 / INTELLIGENCE",
        "07 / CRISIS",
        "08 / DISASTERS",
        "09 / SECURITY",
        "10 / CAMPAIGNS",
        "11 / POLICIES",
        "12 / SAVE / LOAD",
        "13 / GAME OVER",
        "14 / FIELD NOTES",
    ])

    renderers = [
        render_overview,
        render_simulation,
        render_city_systems,
        render_failure_protocol,
        render_command_center,
        render_ai_council,
        render_crisis_center,
        render_disaster_management,
        render_security,
        render_campaigns,
        render_policies,
        render_save_load,
        render_game_over,
        render_field_notes,
    ]

    for tab, renderer in zip(tabs, renderers):
        with tab:
            if renderer in (
                render_overview,
                render_simulation,
                render_city_systems,
                render_failure_protocol,
                render_game_over,
            ):
                renderer(city)
            else:
                renderer()

    st.markdown(
        """
        <div class="codex-footer">
            AFTERMATH // THE SURVIVAL CODEX<br>
            OFFICIAL CITY ADMINISTRATION DOCUMENT<br>
            KNOW THE SYSTEM. UNDERSTAND THE CONSEQUENCES.<br>
            THE CITY'S FUTURE IS IN YOUR HANDS.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
