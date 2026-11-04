
"""AFTERMATH human-centred policy judgement engine."""

from judgement.assessment import (
    PolicyAssessment,
    PolicyProposal,
)
from judgement.metrics import (
    DEFAULT_WEIGHTS,
    HumanValues,
    calculate_weighted_score,
    identify_tradeoffs,
)


class JudgementEngine:
    """Evaluates policy proposals and exposes their trade-offs."""

    def __init__(
        self,
        weights: dict[str, float] | None = None,
    ):
        self.weights = weights or DEFAULT_WEIGHTS.copy()

    def assess(
        self,
        proposal: PolicyProposal,
        values: HumanValues,
    ) -> PolicyAssessment:
        """Assess a policy using an explicit human-value profile."""

        value_scores = values.model_dump()

        score = calculate_weighted_score(
            value_scores,
            self.weights,
        )

        tradeoffs = identify_tradeoffs(value_scores)

        strengths = [
            dimension
            for dimension, value in value_scores.items()
            if value >= 75
        ]

        concerns = [
            dimension
            for dimension, value in value_scores.items()
            if value < 45
        ]

        if score >= 75 and not concerns:
            recommendation = "favourable"
            explanation = (
                "The supplied assessment indicates broadly positive "
                "human-value outcomes. Review the remaining trade-offs "
                "before making a decision."
            )
        elif score >= 55:
            recommendation = "mixed"
            explanation = (
                "The proposal has meaningful benefits and concerns. "
                "Consider revisions or additional safeguards."
            )
        else:
            recommendation = "high_concern"
            explanation = (
                "The supplied assessment identifies substantial "
                "human-value concerns. Reconsider the proposal or "
                "introduce stronger protections."
            )

        return PolicyAssessment(
            proposal_id=proposal.id,
            proposal_title=proposal.title,
            overall_score=score,
            values=values,
            strengths=strengths,
            concerns=concerns,
            tradeoffs=tradeoffs,
            estimated_cost=proposal.estimated_cost,
            recommendation=recommendation,
            explanation=explanation,
            human_decision_required=True,
        )
