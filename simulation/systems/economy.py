
"""Economic simulation system."""

from simulation.state import CityState


def update_economy(state: CityState) -> dict:
    population = state.population

    # Simplified synthetic city economy.
    tax_revenue = population * 19.5
    business_revenue = population * 7.5

    infrastructure_cost = (
        len(state.buildings) * 1_250
        + len(state.roads) * 8_500
    )

    public_service_cost = population * 13.0

    total_revenue = tax_revenue + business_revenue
    total_expenses = infrastructure_cost + public_service_cost

    net_change = total_revenue - total_expenses

    previous_budget = state.budget
    state.budget = max(0.0, state.budget + net_change)

    budget_health = min(
        100.0,
        (state.budget / 2_500_000_000) * 72.0,
    )

    revenue_health = 65.0

    if total_revenue > 0:
        revenue_health = min(
            100.0,
            max(0.0, 70.0 + (net_change / total_revenue) * 100),
        )

    state.metrics.economic_health = round(
        budget_health * 0.55 + revenue_health * 0.45,
        2,
    )

    return {
        "revenue": round(total_revenue, 2),
        "expenses": round(total_expenses, 2),
        "net_change": round(net_change, 2),
        "previous_budget": round(previous_budget, 2),
        "current_budget": round(state.budget, 2),
    }
