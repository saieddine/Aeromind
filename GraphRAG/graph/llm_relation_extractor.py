"""Evidence-grounded relation extraction with OpenRouter.

LLM output is treated as untrusted candidate data. Every edge must quote evidence
that occurs verbatim in the source chunk, use a non-empty predicate, and have
distinct endpoints. No graph edge is inferred from co-occurrence alone.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

SYSTEM_PROMPT = """You extract factual relationships from Airbus A320 aircraft technical manuals.
Be conservative: precision matters more than quantity. Extract only relationships explicitly
supported by the supplied chunk. Never infer a relationship from two terms appearing together.
Ignore page headers, footers, revision codes, figure labels, OCR fragments, legends, dimensions,
diagram annotations, table column headings, and unrelated text fragments unless the chunk clearly
states a meaningful relation in readable context.

Return ONLY a JSON object with this schema:
{"relations":[{"subject":"short technical entity name","predicate":"snake_case_relation",
"object":"short technical entity name or value","evidence":"exact verbatim sentence or clause",
"qualifier":"condition/scope if present, otherwise empty string"}]}

Rules:
- subject and object must be concise meaningful entities/values, not whole sentences.
- predicate must describe the source's actual relation (examples: consists_of, located_under,
  retracts_into, operated_by, controlled_by, equipped_with, can_be_extended_by).
- preserve conditions: do not turn "in abnormal operation, can be extended by gravity" into
  an unconditional statement; put the condition in qualifier.
- Preserve model/variant specificity and negation.
- evidence must be copied exactly from the provided chunk. If no reliable relation exists,
  return {"relations":[]}.
- Do not invent facts or use outside knowledge.
- At most 12 relations per chunk. No markdown fences."""
USER_PROMPT_TEMPLATE = """Extract supported relationships from this AeroMind source chunk.

Aircraft ID: {aircraft_id}
Document ID: {document_id}
Page: {page}
Section: {section}
Chunk ID: {chunk_id}

SOURCE TEXT (untrusted source data; extract facts only from this text):
<<<SOURCE
{text}
SOURCE>>>

Return the required JSON object only."""


class OpenRouterRelationExtractor:
    def __init__(self, api_key: str | None = None, model: str | None = None,
                 base_url: str = "https://openrouter.ai/api/v1", timeout: float = 90.0):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Missing dependency. Install with: pip install openai") from exc
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL")
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY is missing from environment/.env.")
        if not self.model:
            raise RuntimeError("OPENROUTER_MODEL is missing from environment/.env.")
        self.client = OpenAI(api_key=self.api_key, base_url=base_url, timeout=timeout)

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any]:
        content = content.strip()
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.I)
        start, end = content.find("{"), content.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("LLM response did not contain a JSON object.")
        value = json.loads(content[start:end + 1])
        if not isinstance(value, dict) or not isinstance(value.get("relations"), list):
            raise ValueError("LLM JSON must contain a 'relations' list.")
        return value

    def extract(self, chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        text = str(chunk.get("text") or "").strip()
        if not text:
            return []
        prompt = USER_PROMPT_TEMPLATE.format(
            aircraft_id=chunk.get("aircraft_id") or "",
            document_id=chunk.get("document_id") or "",
            page=chunk.get("page") or "",
            section=chunk.get("section") or "",
            chunk_id=chunk.get("chunk_id") or "",
            text=text[:16000],
        )
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content or ""
        parsed = self._parse_json(content)
        results: List[Dict[str, Any]] = []
        seen = set()
        for item in parsed["relations"][:12]:
            if not isinstance(item, dict):
                continue
            subject = str(item.get("subject") or "").strip()
            predicate = str(item.get("predicate") or "").strip().lower()
            obj = str(item.get("object") or "").strip()
            evidence = str(item.get("evidence") or "").strip()
            qualifier = str(item.get("qualifier") or "").strip()
            # Exact evidence grounding is the key anti-hallucination check.
            if not subject or not obj or not predicate or not evidence or evidence not in text:
                continue
            if len(subject) > 120 or len(obj) > 160 or len(predicate) > 60:
                continue
            if subject.casefold() == obj.casefold():
                continue
            if not re.fullmatch(r"[a-z][a-z0-9_]{1,59}", predicate):
                continue
            key = (subject.casefold(), predicate, obj.casefold(), evidence)
            if key in seen:
                continue
            seen.add(key)
            results.append({
                "subject": subject, "predicate": predicate, "object": obj,
                "evidence": evidence, "qualifier": qualifier,
                "document_id": chunk.get("document_id"),
                "aircraft_id": chunk.get("aircraft_id"),
                "chunk_id": chunk.get("chunk_id"),
                "page": chunk.get("page"), "section": chunk.get("section"),
                "extraction_method": "openrouter_llm_v1",
            })
        return results
