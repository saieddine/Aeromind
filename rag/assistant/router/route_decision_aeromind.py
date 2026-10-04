"""Structured result produced by the AeroMind request router."""

from dataclasses import dataclass
from .route import Route


@dataclass
class RouteDecision:
    """Represents the route selected for an assistant request."""

    route: Route
    confidence: float
    reason: str
    response: str | None = None
