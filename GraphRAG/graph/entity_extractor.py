"""Conservative entity extraction; candidate entities only."""
from __future__ import annotations
import re
from typing import Any, Dict, List

IDENTIFIER_PATTERNS = (
    re.compile(r"\b[A-Z]{2,6}(?:-[A-Z0-9]{1,8})?\b"),
    re.compile(r"\b\d{1,2}-\d{1,3}-\d{1,3}\b"),
)
KNOWN_TERMS = {
    "aircraft", "fuselage", "wingspan", "wing", "wings", "landing gear",
    "nose landing gear", "main landing gear", "engine", "engines", "apu",
    "auxiliary power unit", "maximum take-off weight", "maximum takeoff weight",
    "maximum landing weight", "maximum zero fuel weight", "mtow", "mlw", "mzfw",
    "overall length", "overall height", "aircraft dimensions", "horizontal stabilizer",
    "vertical stabilizer", "wing span", "ground clearance", "tail", "cockpit",
    "cabin", "door", "doors", "cargo compartment", "fuel tank", "fuel tanks",
    "hydraulic system", "electrical system", "flight control system", "brake", "brakes",
}

def _canonical(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip(" ,.;:()[]{}")).casefold()

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """Extract unique known terms and technical identifiers explicitly in text."""
    if not isinstance(text, str) or not text.strip():
        return []
    found: Dict[str, Dict[str, Any]] = {}
    for term in sorted(KNOWN_TERMS, key=len, reverse=True):
        pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.I)
        if pattern.search(text):
            key = _canonical(term)
            found.setdefault(key, {"name": term, "canonical_name": key, "entity_type": "technical_term"})
    for pattern in IDENTIFIER_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(0).strip()
            if len(value) < 3:
                continue
            key = _canonical(value)
            found.setdefault(key, {"name": value, "canonical_name": key, "entity_type": "technical_identifier"})
    return list(found.values())
