"""Routing destinations used by the AeroMind assistant."""

from enum import Enum


class Route(Enum):
    CONVERSATION = "CONVERSATION"
    RAG = "RAG"
    GRAPHRAG = "GRAPHRAG"
    LIGHTRAG = "LIGHTRAG"
    SIMULATION = "SIMULATION"
