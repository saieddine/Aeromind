"""Conservative sentence-local relation extraction for technical prose.

This emits candidates only. The graph builder independently validates source evidence.
"""
from __future__ import annotations
import re
from typing import Any, Dict, List, Pattern, Tuple

RELATION_PATTERNS: List[Tuple[str, Pattern[str]]] = [
 ("consists_of", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+consists\s+of\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("includes", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+includes\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("comprises", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+comprises\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("located_in", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+(?:is|are)\s+(?:located|positioned|installed|mounted)\s+in\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("located_under", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+(?:is|are)\s+located\s+under\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("equipped_with", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+(?:is|are)\s+(?:equipped|fitted)\s+with\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("connected_to", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+(?:is|are)\s+connected\s+to\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("supplied_by", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+(?:is|are)\s+supplied\s+by\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("installed_on", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+(?:is|are)\s+(?:mounted|installed)\s+on\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("operated_by", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+(?:is|are)\s+operated\s+by\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("controlled_by", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+(?:is|are)\s+controlled\s+by\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("retracts_into", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+retracts\s+(?:forward\s+)?into\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("retracts_toward", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+retract(?:s)?\s+(?:sideways\s+)?towards?\s+(?P<object>[^,;.!?]{2,100})", re.I)),
 ("supported_by", re.compile(r"\b(?P<subject>[^,;.!?]{2,90}?)\s+(?:is|are)\s+supported\s+by\s+(?P<object>[^,;.!?]{2,100})", re.I)),
]
BAD_CONTEXT = re.compile(r"\b(?:FIGURE[- ]|SUBJECT\s+\d|CHAPTER\s+\d|LAST REVISION|CROSS WIND EFFECT|DANGER AREA|PAGE\s*:\s*\d)\b", re.I)
LEADING = re.compile(r"^(?:(?:the|a|an|this|these|those)\s+)+", re.I)
STOP_TAIL = re.compile(r"\s+(?:to allow|to initiate|to enable|for towing|which|that|while|when|where|carrying|with adequate)\b.*$", re.I)
SUBJECT_BOUNDARY = re.compile(r"\b(?:and|but|additionally|moreover|the following)\b", re.I)

def _clean(v: str, *, subject: bool=False) -> str:
    v = re.sub(r"\s+", " ", v).strip(" \t\r\n,.;:()[]{}-")
    v = LEADING.sub("", v)
    if subject:
        # Keep the closest plausible subject phrase before the relation verb.
        v = SUBJECT_BOUNDARY.split(v)[-1].strip()
        words = v.split()
        if len(words) > 6:
            v = " ".join(words[-6:])
    else:
        v = STOP_TAIL.sub("", v)
    return v.strip(" \t\r\n,.;:()[]{}-")

def extract_relations(text: str, *, chunk_id: str, document_id=None, aircraft_id=None, page=None, section=None) -> List[Dict[str, Any]]:
    if not isinstance(text, str) or not text.strip():
        return []
    out, seen = [], set()
    for raw in re.split(r"(?<=[.!?])\s+|\n+", text):
        sent = re.sub(r"\s+", " ", raw).strip()
        if not sent or BAD_CONTEXT.search(sent):
            continue
        if len(sent.split()) > 55 or len(re.findall(r"\d", sent)) > max(10, len(sent)//7):
            continue
        # Reject likely heading fragments rather than treating them as prose.
        if re.match(r"^(?:chapter|figure|subject|page|last revision|contents)\b", sent, re.I):
            continue
        for pred, pat in RELATION_PATTERNS:
            for m in pat.finditer(sent):
                s = _clean(m.group("subject"), subject=True)
                o = _clean(m.group("object"))
                if not s or not o or s.casefold() == o.casefold():
                    continue
                if len(s.split()) > 6 or len(o.split()) > 12 or len(s) > 70 or len(o) > 100:
                    continue
                if re.search(r"\b(?:figure|chapter|subject|page|revision|includes cross wind effect|danger area)\b", s+" "+o, re.I):
                    continue
                # Require endpoints to be noun-like, not entire clause fragments.
                if re.search(r"\b(?:are|is|was|were|retracts|includes|consists|comprises)\b", s, re.I):
                    continue
                key = (s.casefold(), pred, o.casefold())
                if key in seen:
                    continue
                seen.add(key)
                out.append({
                    "subject": s, "predicate": pred, "object": o, "evidence": sent,
                    "document_id": document_id, "aircraft_id": aircraft_id, "chunk_id": chunk_id,
                    "page": page, "section": section, "extraction_method": "explicit_rule_v4"
                })
    return out
