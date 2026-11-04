
"""Synthetic society and community sentiment aggregation."""

from collections import defaultdict

from agents.citizen import (
    CITIZEN_ARCHETYPES,
    CitizenAgent,
)
from simulation.state import CityState, District


class SocietySimulation:
    """Manages citizen perspectives and community sentiment."""

    def __init__(self, city: CityState):
        self.city = city
        self.citizens: list[CitizenAgent] = []

        self._create_citizens()

    def _create_citizens(self) -> None:
        """Create one representative per archetype per district."""

        self.citizens.clear()

        for district in self.city.districts:
            for index, archetype in enumerate(
                CITIZEN_ARCHETYPES.values(),
                start=1,
            ):
                self.citizens.append(
                    CitizenAgent(
                        district=district,
                        archetype=archetype,
                        index=index,
                    )
                )

    def evaluate_district(self, district: District) -> dict:
        """Aggregate the citizen perspectives in one district."""

        opinions = [
            citizen.evaluate_district(district)
            for citizen in self.citizens
            if citizen.profile.district_id == district.id
        ]

        if not opinions:
            return {
                "district_id": district.id,
                "community_score": 0.0,
                "sentiment": "unrepresented",
                "groups": [],
            }

        scores = [opinion["score"] for opinion in opinions]
        average = sum(scores) / len(scores)

        if average >= 75:
            sentiment = "positive"
        elif average >= 55:
            sentiment = "mixed"
        else:
            sentiment = "negative"

        return {
            "district_id": district.id,
            "community_score": round(average, 2),
            "sentiment": sentiment,
            "groups": opinions,
        }

    def evaluate_city(self) -> dict:
        """Generate a city-wide synthetic community report."""

        district_reports = [
            self.evaluate_district(district)
            for district in self.city.districts
        ]

        if not district_reports:
            return {
                "city": self.city.city_name,
                "community_score": 0.0,
                "sentiment": "unrepresented",
                "districts": [],
                "group_summary": {},
            }

        population_total = sum(
            district.population for district in self.city.districts
        )

        weighted_score = 0.0

        for district, report in zip(
            self.city.districts,
            district_reports,
        ):
            weighted_score += (
                report["community_score"] * district.population
            )

        city_score = (
            weighted_score / population_total
            if population_total
            else 0.0
        )

        group_scores = defaultdict(list)

        for report in district_reports:
            for group in report["groups"]:
                group_scores[group["group"]].append(group["score"])

        group_summary = {
            name: round(sum(scores) / len(scores), 2)
            for name, scores in group_scores.items()
            if scores
        }

        if city_score >= 75:
            sentiment = "positive"
        elif city_score >= 55:
            sentiment = "mixed"
        else:
            sentiment = "negative"

        return {
            "city": self.city.city_name,
            "community_score": round(city_score, 2),
            "sentiment": sentiment,
            "represented_groups": len(group_summary),
            "districts": district_reports,
            "group_summary": group_summary,
            "is_synthetic": True,
        }
