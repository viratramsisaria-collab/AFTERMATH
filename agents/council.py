
"""AFTERMATH mayoral advisory council."""

from agents.base import AgentProfile, AgentRole, BaseAgent


COUNCIL_MEMBERS = [
    {
        "id": "council-economist",
        "name": "Dr. Elias Morgan",
        "role": AgentRole.ECONOMIST,
        "description": "Evaluates financial sustainability, economic growth and public spending.",
        "priorities": [
            "budget",
            "employment",
            "economic_growth",
            "financial_sustainability",
        ],
    },
    {
        "id": "council-planner",
        "name": "Mira Chen",
        "role": AgentRole.URBAN_PLANNER,
        "description": "Evaluates urban development, housing and spatial planning.",
        "priorities": [
            "housing",
            "infrastructure",
            "land_use",
            "accessibility",
        ],
    },
    {
        "id": "council-environment",
        "name": "Dr. Amara Okafor",
        "role": AgentRole.ENVIRONMENTALIST,
        "description": "Evaluates environmental impact, energy and sustainability.",
        "priorities": [
            "environment",
            "energy",
            "water",
            "green_space",
        ],
    },
    {
        "id": "council-health",
        "name": "Dr. Sofia Reyes",
        "role": AgentRole.PUBLIC_HEALTH,
        "description": "Evaluates healthcare access, public wellbeing and health risks.",
        "priorities": [
            "healthcare",
            "wellbeing",
            "public_health",
            "accessibility",
        ],
    },
    {
        "id": "council-transport",
        "name": "Noah Williams",
        "role": AgentRole.TRANSPORT,
        "description": "Evaluates public transport, congestion and mobility.",
        "priorities": [
            "mobility",
            "traffic",
            "public_transport",
            "road_safety",
        ],
    },
    {
        "id": "council-equity",
        "name": "Leila Haddad",
        "role": AgentRole.SOCIAL_ADVOCATE,
        "description": "Evaluates fairness, affordability and unequal consequences.",
        "priorities": [
            "social_equity",
            "affordability",
            "inclusion",
            "opportunity",
        ],
    },
    {
        "id": "council-safety",
        "name": "Marcus Bennett",
        "role": AgentRole.SAFETY,
        "description": "Evaluates public safety, emergency readiness and resilience.",
        "priorities": [
            "safety",
            "emergency_response",
            "resilience",
            "infrastructure_risk",
        ],
    },
    {
        "id": "council-technology",
        "name": "Aiko Tanaka",
        "role": AgentRole.TECHNOLOGY,
        "description": "Evaluates technology adoption, digital infrastructure and automation.",
        "priorities": [
            "technology",
            "automation",
            "digital_access",
            "innovation",
        ],
    },
]


class CouncilAgent(BaseAgent):
    """A specialised mayoral advisor profile."""

    def __init__(self, member: dict):
        profile = AgentProfile(
            id=member["id"],
            name=member["name"],
            role=member["role"],
            description=member["description"],
            priorities=member["priorities"],
            influence=1.0,
        )

        super().__init__(profile)


class MayoralCouncil:
    """Maintains the city's advisory council."""

    def __init__(self):
        self.members = [
            CouncilAgent(member)
            for member in COUNCIL_MEMBERS
        ]

    def get_members(self) -> list[CouncilAgent]:
        return self.members

    def get_member(self, agent_id: str) -> CouncilAgent | None:
        return next(
            (
                member
                for member in self.members
                if member.agent_id == agent_id
            ),
            None,
        )

    def get_by_role(
        self,
        role: AgentRole,
    ) -> list[CouncilAgent]:
        return [
            member
            for member in self.members
            if member.role == role
        ]

    def get_roster(self) -> list[dict]:
        return [
            {
                "id": member.agent_id,
                "name": member.name,
                "role": member.role.value,
                "description": member.profile.description,
                "priorities": member.profile.priorities,
            }
            for member in self.members
        ]
