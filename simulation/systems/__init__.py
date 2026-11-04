
"""AFTERMATH simulation systems."""

from simulation.systems.economy import update_economy
from simulation.systems.environment import update_environment
from simulation.systems.population import update_population
from simulation.systems.traffic import update_traffic

__all__ = [
    "update_economy",
    "update_environment",
    "update_population",
    "update_traffic",
]
