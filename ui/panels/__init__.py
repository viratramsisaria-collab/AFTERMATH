
"""AFTERMATH page panels."""

from ui.panels.city import (
    render_city_simulator,
    render_command_center,
)
from ui.panels.council import render_council
from ui.panels.judgement import render_judgement
from ui.panels.operations import (
    render_campaigns,
    render_crisis_center,
)
from ui.panels.security import render_security_center
from ui.panels.disasters import render_disaster_management

__all__ = [
    "render_command_center",
    "render_city_simulator",
    "render_council",
    "render_crisis_center",
    "render_campaigns",
    "render_judgement",
    "render_security_center",
    "render_disaster_management",
]
