
"""AFTERMATH campaign progression manager."""

from pydantic import BaseModel, Field

from scenarios.campaigns import (
    CAMPAIGNS,
    Campaign,
    CampaignObjective,
    ObjectiveType,
)
from simulation.state import CityState


class ObjectiveProgress(BaseModel):
    objective_id: str
    title: str

    completed: bool = False
    current_value: float | None = None
    target_value: float | None = None

    message: str = ""


class CampaignProgress(BaseModel):
    campaign_id: str
    started_day: int

    objectives: list[ObjectiveProgress] = Field(
        default_factory=list
    )

    is_completed: bool = False
    is_failed: bool = False


class ScenarioManager:
    """Manages campaign selection and objective progression."""

    def __init__(self):
        self.campaigns = {
            campaign.id: campaign
            for campaign in CAMPAIGNS
        }

        self.active_campaign: Campaign | None = None
        self.progress: CampaignProgress | None = None

    def get_campaigns(self) -> list[Campaign]:
        return list(self.campaigns.values())

    def get_campaign(self, campaign_id: str) -> Campaign | None:
        return self.campaigns.get(campaign_id)

    def start_campaign(
        self,
        campaign_id: str,
        city: CityState,
    ) -> Campaign:
        campaign = self.get_campaign(campaign_id)

        if campaign is None:
            raise ValueError(
                f"Unknown campaign: {campaign_id}"
            )

        city.day = campaign.starting_day
        city.budget = campaign.starting_budget
        city.history.clear()

        self.active_campaign = campaign

        self.progress = CampaignProgress(
            campaign_id=campaign.id,
            started_day=city.day,
            objectives=[
                ObjectiveProgress(
                    objective_id=objective.id,
                    title=objective.title,
                    target_value=objective.target,
                )
                for objective in campaign.objectives
            ],
        )

        city.add_event(
            f"Campaign started: {campaign.title}."
        )

        return campaign

    def _evaluate_objective(
        self,
        objective: CampaignObjective,
        city: CityState,
        started_day: int,
    ) -> ObjectiveProgress:
        current = None
        completed = False
        message = ""

        elapsed_days = city.day - started_day + 1

        if objective.objective_type == ObjectiveType.SURVIVE_DAYS:
            current = float(elapsed_days)
            completed = (
                elapsed_days >= objective.required_days
                and city.budget > 0
            )

            message = (
                "Required survival period reached."
                if completed
                else "Keep the city operating until the target day."
            )

        elif objective.objective_type == ObjectiveType.SPEND_BELOW:
            current = city.budget

            completed = (
                objective.target is not None
                and city.budget >= objective.target
            )

            message = (
                "Budget threshold achieved."
                if completed
                else "The city budget is below its required threshold."
            )

        elif objective.metric:
            if not hasattr(city.metrics, objective.metric):
                raise ValueError(
                    f"Unknown city metric: {objective.metric}"
                )

            current = float(
                getattr(city.metrics, objective.metric)
            )

            target = objective.target

            if target is None:
                raise ValueError(
                    f"Objective {objective.id} has no target."
                )

            if objective.objective_type == ObjectiveType.REACH:
                completed = current >= target

            elif objective.objective_type == ObjectiveType.MAINTAIN:
                completed = current >= target

            message = (
                "Objective achieved."
                if completed
                else f"Current: {current:.2f} / Target: {target:.2f}"
            )

        if (
            objective.deadline_day is not None
            and city.day > objective.deadline_day
            and not completed
        ):
            message = "Deadline missed."

        return ObjectiveProgress(
            objective_id=objective.id,
            title=objective.title,
            completed=completed,
            current_value=current,
            target_value=objective.target,
            message=message,
        )

    def update(self, city: CityState) -> CampaignProgress:
        if self.active_campaign is None or self.progress is None:
            raise RuntimeError("No active campaign.")

        if self.progress.is_completed or self.progress.is_failed:
            return self.progress

        evaluated = [
            self._evaluate_objective(
                objective,
                city,
                self.progress.started_day,
            )
            for objective in self.active_campaign.objectives
        ]

        self.progress.objectives = evaluated

        missed_deadline = any(
            objective.deadline_day is not None
            and city.day > objective.deadline_day
            and not result.completed
            for objective, result in zip(
                self.active_campaign.objectives,
                evaluated,
            )
        )

        self.progress.is_failed = missed_deadline

        self.progress.is_completed = (
            all(item.completed for item in evaluated)
            and not self.progress.is_failed
        )

        return self.progress

    def get_summary(self) -> dict:
        if self.active_campaign is None or self.progress is None:
            return {
                "active": False,
                "campaigns_available": len(self.campaigns),
            }

        total = len(self.progress.objectives)
        completed = sum(
            item.completed
            for item in self.progress.objectives
        )

        return {
            "active": True,
            "campaign_id": self.active_campaign.id,
            "title": self.active_campaign.title,
            "completed_objectives": completed,
            "total_objectives": total,
            "completion_percentage": round(
                completed / total * 100,
                2,
            ) if total else 0.0,
            "is_completed": self.progress.is_completed,
            "is_failed": self.progress.is_failed,
        }
