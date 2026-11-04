"""AI Council deliberation service."""

import json
import os
import re

from langchain_core.messages import HumanMessage, SystemMessage

from ai.prompts import COUNCIL_SYSTEM_PROMPT, build_council_prompt
from ai.providers import get_chat_model
from ai.schemas import CouncilDeliberation


def _extract_json(content) -> dict:
    """Extract a JSON object from a model response."""

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))

        content = "\n".join(parts)

    if not isinstance(content, str) or not content.strip():
        raise ValueError(
            "The AI provider returned an empty response. "
            "Check the model output limit and provider response."
        )

    cleaned = content.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end <= start:
            raise ValueError(
                "The AI response did not contain a valid JSON object."
            )

        try:
            data = json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The AI returned malformed JSON."
            ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "The AI response must be a JSON object."
        )

    return data


def run_council_deliberation(
    problem: str,
    city_context: dict,
    provider: str | None = None,
) -> CouncilDeliberation:
    """Ask the AI Council to analyse a city problem."""

    if not isinstance(problem, str) or not problem.strip():
        raise ValueError("A city problem must be provided.")

    if not isinstance(city_context, dict):
        raise ValueError("City context must be a dictionary.")

    selected_provider = (
        provider or os.getenv("AI_PROVIDER", "gemini")
    ).lower()

    model = get_chat_model(
        provider=selected_provider,
        temperature=0.2,
    )

    # Otari supports OpenAI-compatible JSON response formatting.

    response = model.invoke(
        [
            SystemMessage(content=COUNCIL_SYSTEM_PROMPT),
            HumanMessage(
                content=build_council_prompt(
                    problem=problem,
                    city_context=city_context,
                )
            ),
        ]
    )

    data = _extract_json(response.content)

    # The mayor must always retain final authority.
    data["human_decision_required"] = True

    return CouncilDeliberation.model_validate(data)


def generate_game_over_tagline(
    metric_name: str,
    metric_label: str,
    value: float,
    threshold: float,
    operator: str,
    day: int,
    city_name: str,
    provider: str | None = None,
) -> str:
    """Generate a concise narrative for the city's defeat."""

    selected_provider = (
        provider or os.getenv("AI_PROVIDER", "gemini")
    ).lower()

    model = get_chat_model(
        provider=selected_provider,
        temperature=0.7,
    )

    direction = (
        "fell below"
        if operator == "below"
        else "exceeded"
    )

    response = model.invoke([
        SystemMessage(
            content=(
                "You write dramatic, intelligent closing messages "
                "for a futuristic city-management simulation. "
                "Write 1-2 concise sentences. Be serious, cinematic, "
                "and specific. Explain the failed metric and its "
                "consequence. Do not invent events, statistics, "
                "or causes. Do not blame the human player. "
                "Return only the closing message."
            )
        ),
        HumanMessage(
            content=(
                f"City: {city_name}\n"
                f"Final day: {day}\n"
                f"Failed condition: {metric_label} ({metric_name})\n"
                f"Final value: {value:.2f}\n"
                f"Required condition: {direction} {threshold:.2f}\n\n"
                "Write the city's final message."
            )
        ),
    ])

    content = response.content

    if isinstance(content, list):
        content = " ".join(
            str(item.get("text", ""))
            if isinstance(item, dict)
            else str(item)
            for item in content
        )

    tagline = str(content).strip().strip('"').strip("'")

    if not tagline:
        raise ValueError("The AI returned an empty defeat message.")

    return tagline[:500]