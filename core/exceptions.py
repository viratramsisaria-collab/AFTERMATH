
"""AFTERMATH application exceptions."""


class AftermathError(Exception):
    """Base exception for application errors."""


class ConfigurationError(AftermathError):
    """Invalid or missing application configuration."""


class ProviderError(AftermathError):
    """AI provider integration failure."""


class ProviderAuthenticationError(ProviderError):
    """Invalid or rejected provider credentials."""


class ProviderRateLimitError(ProviderError):
    """Provider rate limit exceeded."""


class ProviderResponseError(ProviderError):
    """Invalid or unexpected provider response."""


class SimulationError(AftermathError):
    """Simulation execution failure."""


class InvalidSimulationState(SimulationError):
    """The city state is invalid or inconsistent."""


class WorldGenerationError(AftermathError):
    """Failure while generating the simulated world."""


class InvalidDecisionError(AftermathError):
    """A proposed city decision is invalid."""


class JudgementError(AftermathError):
    """Human judgement assessment failure."""


class DatabaseError(AftermathError):
    """Database operation failure."""
