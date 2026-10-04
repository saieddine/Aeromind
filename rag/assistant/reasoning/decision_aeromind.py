"""AeroMind reasoning decision object.

Represents a decision produced by the reasoning layer. The object keeps
the action, confidence, reason, and optional metadata in a stable format
for communication between AeroMind modules.
"""

from dataclasses import dataclass, field


@dataclass
class Decision:
    """
    Represents a decision made by the Reasoning Engine.

    Every intelligent module communicates using this object
    instead of raw dictionaries.
    """

    action: str

    confidence: float = 1.0

    reason: str = ""

    metadata: dict = field(default_factory=dict)