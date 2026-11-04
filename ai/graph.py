
"""LangGraph workflow for AI Council deliberation."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from ai.schemas import CouncilDeliberation
from ai.service import run_council_deliberation


class CouncilState(TypedDict, total=False):
    problem: str
    city_context: dict
    provider: str
    deliberation: dict
    error: str


def deliberation_node(state: CouncilState) -> CouncilState:
    """Generate the council's structured analysis."""

    try:
        result = run_council_deliberation(
            problem=state["problem"], # type: ignore
            city_context=state["city_context"], # type: ignore
            provider=state.get("provider"),
        )

        return {
            **state,
            "deliberation": result.model_dump(),
            "error": "",
        }

    except Exception as exc:
        return {
            **state,
            "deliberation": {},
            "error": str(exc),
        }


def build_council_graph():
    """Build and compile the council workflow."""

    workflow = StateGraph(CouncilState)

    workflow.add_node("deliberate", deliberation_node)

    workflow.add_edge(START, "deliberate")
    workflow.add_edge("deliberate", END)

    return workflow.compile()


council_graph = build_council_graph()


def deliberate(
    problem: str,
    city_context: dict,
    provider: str | None = None,
) -> CouncilState:
    """Run the complete council workflow."""

    return council_graph.invoke(
        {
            "problem": problem,
            "city_context": city_context,
            "provider": provider or "",
        }
    ) # type: ignore
