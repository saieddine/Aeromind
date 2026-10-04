"""AeroMind interaction history.

Tracks how the assistant has interacted with the user around a technical
topic. This is separate from the full conversation history stored by the
QA state.

It records interaction-level signals that can later help the assistant
avoid unnecessary repetition and adjust explanation depth.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class InteractionHistory:
    """Track explanation and interaction patterns for a technical topic."""

    examples_given: int = 0
    re_explanations: int = 0
    simplifications: int = 0
    detail_level: int = 0

    used_examples: List[str] = field(default_factory=list)
    used_strategies: List[str] = field(default_factory=list)

    def record_example(self, example: str = ""):
        """Record that the assistant gave an example."""
        self.examples_given += 1

        if example:
            self.used_examples.append(example)

    def record_re_explanation(self, strategy: str = ""):
        """Record that the assistant explained the topic again."""
        self.re_explanations += 1

        if strategy:
            self.used_strategies.append(strategy)

    def record_simplification(self):
        """Record that the explanation was simplified."""
        self.simplifications += 1

    def increase_detail(self):
        """Increase the tracked explanation depth."""
        self.detail_level += 1

    def has_examples(self) -> bool:
        return self.examples_given > 0

    def has_been_simplified(self) -> bool:
        return self.simplifications > 0

    def has_multiple_examples(self) -> bool:
        return self.examples_given > 1

    def reset(self):
        """Clear interaction history for a new technical topic."""
        self.examples_given = 0
        self.re_explanations = 0
        self.simplifications = 0
        self.detail_level = 0
        self.used_examples.clear()
        self.used_strategies.clear()

    def to_dict(self):
        return {
            "examples_given": self.examples_given,
            "re_explanations": self.re_explanations,
            "simplifications": self.simplifications,
            "detail_level": self.detail_level,
            "used_examples": self.used_examples,
            "used_strategies": self.used_strategies,
        }

    def __str__(self):
        return f"""
============================================================
Interaction History
============================================================

Examples Given:
{self.examples_given}

Re-explanations:
{self.re_explanations}

Simplifications:
{self.simplifications}

Detail Level:
{self.detail_level}

Used Examples:
{self.used_examples}

Interaction Strategies:
{self.used_strategies}

============================================================
"""
