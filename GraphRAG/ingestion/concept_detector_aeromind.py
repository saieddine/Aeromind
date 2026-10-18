"""AeroMind concept detector v2.

Designed for technical/engineering PDFs (aircraft manuals, maintenance manuals,
engineering reports, specifications) while remaining usable for academic PDFs.

Core design principle:
    Do not treat arbitrary numbered text as a concept boundary.
    Prefer the document's native structural anchors (section/subject codes,
    TOC/LEC entries, page headers) and only use semantic fallback when those
    anchors are genuinely unavailable.

Backward-compatible public functions are kept because the ingestion pipeline
uses this module's concept/page helpers.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, Iterable, List, Optional, Tuple


# -----------------------------------------------------------------------------
# Regexes: intentionally strict. Measurements such as "1.83 m" and diagram
# labels must never be interpreted as document sections.
# -----------------------------------------------------------------------------
TECH_SECTION_RE = re.compile(
    r"^(?P<section>\d{1,2}-\d{1,3}-\d{1,3})\s+(?P<title>.+?)\s*$"
)
TECH_SECTION_CODE_RE = re.compile(r"^\d{1,2}-\d{1,3}-\d{1,3}$")
FIGURE_RE = re.compile(r"\bFIGURE(?:-|\s)", re.IGNORECASE)
FIGURE_ID_RE = re.compile(r"\bFIGURE-\d{1,2}-\d{1,3}-\d{1,3}-", re.IGNORECASE)
DRAWING_ID_RE = re.compile(r"\bN_[A-Z0-9_]+\b")
ON_AC_RE = re.compile(r"\bON\s*/?\s*A/C\b", re.IGNORECASE)
PAGE_FOOTER_RE = re.compile(r"\bPage\s+\d+\b", re.IGNORECASE)
DATE_RE = re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2}/\d{2}\b", re.IGNORECASE)
TOC_RE = re.compile(r"\b(?:TABLE\s+OF\s+CONTENTS|T\.O\.C\.?|LIST\s+OF\s+EFFECTIVE\s+CONTENT)\b", re.IGNORECASE)
HIGHLIGHTS_RE = re.compile(r"\bHIGHLIGHTS\b", re.IGNORECASE)

# Academic/general fallback headings. These are deliberately much stricter
# than the old "score >= 1" rule.
ACADEMIC_NUMBER_RE = re.compile(r"^(\d+(?:\.\d+){1,3})\.?\s+(.{3,120})$")
ROMAN_HEADING_RE = re.compile(r"^([IVXLCDM]+)(?:-\d+)?\s+(.{3,120})$", re.IGNORECASE)


# -----------------------------------------------------------------------------
# Basic text helpers
# -----------------------------------------------------------------------------
def _clean_line(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _nonempty_lines(text: str) -> List[str]:
    return [_clean_line(x) for x in str(text or "").splitlines() if _clean_line(x)]


def _first_lines(text: str, limit: int = 24) -> List[str]:
    return _nonempty_lines(text)[:limit]


def _looks_like_title(text: str) -> bool:
    text = _clean_line(text)
    if not text or len(text) < 3 or len(text) > 140:
        return False
    if TECH_SECTION_CODE_RE.fullmatch(text):
        return False
    if PAGE_FOOTER_RE.search(text) or DATE_RE.search(text):
        return False
    if FIGURE_ID_RE.search(text):
        return False
    # A title should contain letters, not be predominantly numbers/symbols.
    letters = sum(ch.isalpha() for ch in text)
    digits = sum(ch.isdigit() for ch in text)
    if letters < 3:
        return False
    if digits > letters * 2:
        return False
    return True


def _page_has_aircraft_marker(text: str) -> bool:
    return bool(ON_AC_RE.search(text))


def _page_is_structure(text: str) -> bool:
    return bool(TOC_RE.search(text))


# -----------------------------------------------------------------------------
# Page/heading inspection
# -----------------------------------------------------------------------------
def get_lines(pages: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    all_lines: List[Dict[str, Any]] = []
    for page in pages:
        for line in _nonempty_lines(page.get("text", "")):
            all_lines.append({"text": line, "page": page.get("page")})
    return all_lines


def heading_score(line: Dict[str, Any]) -> int:
    """Compatibility helper.

    Unlike v1, this score is meaningful only for real heading-like text. A
    one-character unit, measurement, diagram label, or random uppercase token
    receives zero.
    """
    text = _clean_line(line.get("text", ""))
    if not _looks_like_title(text):
        return 0

    score = 0
    words = text.split()
    if 2 <= len(words) <= 12:
        score += 1
    if text.isupper() and len(text) >= 5:
        score += 1
    if ACADEMIC_NUMBER_RE.match(text):
        score += 2
    if re.search(r"\b(?:introduction|general|information|system|data|requirements|overview|procedure|analysis|method)\b", text, re.I):
        score += 1
    return score


def find_structure_pages(pages: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    for page in pages:
        text = str(page.get("text", ""))
        if _page_is_structure(text) or HIGHLIGHTS_RE.search(text):
            result.append(page)
    return result


def extract_structure_candidates(structure_pages: Iterable[Dict[str, Any]]) -> List[str]:
    candidates: List[str] = []
    for page in structure_pages:
        for line in _nonempty_lines(page.get("text", "")):
            line = line.lstrip("•*- ")
            # Technical-manual TOC entries: 5-1-1 Title
            if TECH_SECTION_RE.match(line):
                if line not in candidates:
                    candidates.append(line)
                continue
            # Academic TOC entries: 2.1 Title
            if ACADEMIC_NUMBER_RE.match(line):
                if line not in candidates:
                    candidates.append(line)
    return candidates


# -----------------------------------------------------------------------------
# Technical-manual structure detection
# -----------------------------------------------------------------------------
def _find_tech_anchor_in_page(page: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find a *real subject start* in the top portion of a technical page.

    The A320 manual has two important properties:
      * subject starts look like "5-1-3 Typical Ramp Layout - Gate" near the top;
      * continuation/figure pages repeat the subject code only in the footer.

    We therefore require the code/title pair to occur near the top and require
    evidence that the page is an actual content page (e.g. ON A/C, body prose,
    or a page-1 subject header), which excludes TOC pages and figure footers.
    """
    text = str(page.get("text", ""))
    lines = _first_lines(text, 24)
    if not lines or _page_is_structure(text):
        return None

    # Look only at the top 10 meaningful lines for a subject header.
    for idx, line in enumerate(lines[:12]):
        m = TECH_SECTION_RE.match(line)
        if not m:
            continue

        section = m.group("section")
        title = _clean_line(m.group("title"))

        # "Jun 01/24" and similar footer fragments are not titles.
        if not _looks_like_title(title):
            continue

        context = " ".join(lines[:18])
        has_aircraft_marker = _page_has_aircraft_marker(context)
        has_body_signal = bool(re.search(
            r"\b(?:This section|This manual|Purpose|General|The |For |1\.)\b",
            context,
            re.IGNORECASE,
        ))
        has_page_one_signal = bool(re.search(r"\bPage\s+1\b", context, re.I))

        # A real section-start page in this family almost always has ON A/C or
        # page 1/prose. TOC pages lack these signals.
        if not (has_aircraft_marker or has_body_signal or has_page_one_signal):
            continue

        return {
            "section": section,
            "title": title,
            "page": page.get("page"),
            "line_index": idx,
            "source": "technical_header",
        }

    return None


def _technical_anchor_map(pages: Iterable[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    anchors: Dict[int, Dict[str, Any]] = {}
    for page in pages:
        anchor = _find_tech_anchor_in_page(page)
        if anchor:
            anchors[int(page["page"])] = anchor
    return anchors


def detect_document_profile(pages: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    pages = list(pages)
    anchors = _technical_anchor_map(pages)
    structure_pages = find_structure_pages(pages)

    figure_pages = sum(
        1 for p in pages
        if FIGURE_RE.search(str(p.get("text", ""))) or FIGURE_ID_RE.search(str(p.get("text", "")))
    )

    technical_score = 0
    if len(anchors) >= 3:
        technical_score += 5
    if len({a["section"] for a in anchors.values()}) >= 3:
        technical_score += 3
    if figure_pages >= 3:
        technical_score += 2
    if any(_page_has_aircraft_marker(str(p.get("text", ""))) for p in pages[:40]):
        technical_score += 2

    academic_score = 0
    decimal_heading_count = 0
    for p in pages:
        for line in _nonempty_lines(p.get("text", ""))[:30]:
            if ACADEMIC_NUMBER_RE.match(line):
                decimal_heading_count += 1
                if decimal_heading_count >= 10:
                    break
        if decimal_heading_count >= 10:
            break
    if decimal_heading_count >= 10:
        academic_score += 5
    if len(structure_pages) >= 1:
        academic_score += 1

    if technical_score >= max(6, academic_score + 2):
        profile = "technical_manual"
    elif academic_score >= 5:
        profile = "academic"
    else:
        profile = "generic"

    return {
        "profile": profile,
        "technical_score": technical_score,
        "academic_score": academic_score,
        "technical_anchor_count": len(anchors),
        "technical_section_count": len({a["section"] for a in anchors.values()}),
        "structure_page_count": len(structure_pages),
        "figure_page_count": figure_pages,
    }


# -----------------------------------------------------------------------------
# Backward-compatible heading functions. These now use the document profile.
# -----------------------------------------------------------------------------
def get_section_number(text: str) -> Optional[str]:
    text = _clean_line(text)
    m = TECH_SECTION_RE.match(text)
    if m:
        return m.group("section")

    m = re.match(r"^(\d+(?:\.\d+){1,3})\.?\s+", text)
    if m:
        return m.group(1)

    m = re.match(r"^([IVXLCDM]+-\d+)\s+", text, re.I)
    if m:
        return m.group(1)

    m = re.match(r"^([IVXLCDM]+)\s*-\s+", text, re.I)
    if m:
        return m.group(1)

    return None


def find_numbered_headings(pages: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    pages = list(pages)
    profile = detect_document_profile(pages)

    if profile["profile"] == "technical_manual":
        return list(_technical_anchor_map(pages).values())

    headings: List[Dict[str, Any]] = []
    for page in pages:
        for line in _nonempty_lines(page.get("text", "")):
            m = ACADEMIC_NUMBER_RE.match(line)
            if not m:
                m = ROMAN_HEADING_RE.match(line)
            if not m:
                continue
            section = get_section_number(line)
            title = _clean_line(line)
            if section and _looks_like_title(title):
                headings.append({
                    "section": section,
                    "title": title,
                    "page": page.get("page"),
                    "source": "numbered_heading",
                })
    return headings


def remove_section_number(title: str) -> str:
    title = re.sub(r"^\d{1,2}-\d{1,3}-\d{1,3}\s+", "", title)
    title = re.sub(r"^\d+(?:\.\d+){1,3}\.?\s+", "", title)
    title = re.sub(r"^[IVXLCDM]+-\d+\s+", "", title, flags=re.I)
    title = re.sub(r"^[IVXLCDM]+\s*-\s+", "", title, flags=re.I)
    return _clean_line(title)


# -----------------------------------------------------------------------------
# Concept construction
# -----------------------------------------------------------------------------
def _chapter_title_from_toc(pages: Iterable[Dict[str, Any]]) -> Dict[str, str]:
    """Extract simple chapter titles such as '5 TERMINAL SERVICING'."""
    mapping: Dict[str, str] = {}
    for page in pages:
        if not _page_is_structure(str(page.get("text", ""))):
            continue
        for line in _nonempty_lines(page.get("text", "")):
            m = re.match(r"^(\d{1,2})\s+([A-Z][A-Z0-9 /&,'-]{2,100})$", line)
            if m:
                mapping[m.group(1)] = _clean_line(m.group(2))
    return mapping


def _page_role(text: str, is_subject_start: bool = False) -> str:
    text = str(text or "")
    if _page_is_structure(text):
        return "structure"
    if HIGHLIGHTS_RE.search(text) and not is_subject_start:
        return "highlights"

    has_figure = bool(FIGURE_RE.search(text) or FIGURE_ID_RE.search(text))
    has_table_words = bool(re.search(r"\b(?:TABLE|table)\b", text))
    has_prose = len(re.findall(r"\b[A-Za-z]{4,}\b", text)) >= 25

    if is_subject_start and has_figure and has_prose:
        return "subject_start_mixed"
    if is_subject_start:
        return "subject_start"
    if has_figure and has_prose:
        return "figure_mixed"
    if has_figure:
        return "figure"
    if has_table_words:
        return "table"
    if has_prose:
        return "continuation"
    return "diagram_or_sparse"


def detect_content_type(page_text: str) -> str:
    """Return a coarse role used by the chunker."""
    return _page_role(page_text)


def _canonical_title_for_section(section: str, headings_by_section: Dict[str, Dict[str, Any]]) -> str:
    heading = headings_by_section.get(section)
    if heading:
        return remove_section_number(heading["title"])
    return section


def build_concepts(headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build one concept per *document-native section/subject code*.

    Repeated occurrences of the same subject code are continuation pages, not
    new concepts. This is the critical difference from the old implementation.
    """
    concepts: List[Dict[str, Any]] = []
    by_section: Dict[str, Dict[str, Any]] = {}

    for heading in headings:
        section = heading.get("section")
        if not section:
            continue
        page = int(heading.get("page"))
        title = remove_section_number(heading.get("title", section))

        if section in by_section:
            concept = by_section[section]
            if page not in concept["pages"]:
                concept["pages"].append(page)
            # Prefer a useful title over a code/footer artifact.
            if title != section and len(title) > len(concept["concept"]):
                concept["concept"] = title
            continue

        chapter = section.split("-")[0]
        concept = {
            "section": section,
            "concept": title,
            "pages": [page],
            "concept_index": len(concepts),
            "chapter": chapter,
            "chapter_title": None,
            "is_fallback": False,
            "source": heading.get("source", "document_structure"),
            "page_roles": {},
            "artifacts": [],
        }
        concepts.append(concept)
        by_section[section] = concept

    return concepts


# -----------------------------------------------------------------------------
# Fallback for documents without native subject codes.
# -----------------------------------------------------------------------------
def _strong_generic_heading(line: str) -> Optional[str]:
    line = _clean_line(line)
    if not _looks_like_title(line):
        return None
    m = ACADEMIC_NUMBER_RE.match(line)
    if m:
        return line
    # Only accept standalone all-caps headings with enough lexical content.
    if line.isupper() and 2 <= len(line.split()) <= 10 and len(line) >= 8:
        return line
    return None


def build_fallback_concepts(
    pages: List[Dict[str, Any]],
    numbered_concepts: List[Dict[str, Any]],
    pdf_path: Optional[str] = None,
    debug_pages: Optional[Iterable[int]] = None,
) -> List[Dict[str, Any]]:
    """Semantic fallback is intentionally conservative.

    For a technical manual with reliable subject anchors, return no fallback
    concepts: every continuation/figure page belongs to its current subject.
    For other documents, create concepts only from strong heading evidence.
    """
    profile = detect_document_profile(pages)
    if profile["profile"] == "technical_manual" and numbered_concepts:
        return []

    existing_pages = {p for c in numbered_concepts for p in c.get("pages", [])}
    fallback: List[Dict[str, Any]] = []

    for page in pages:
        page_no = int(page.get("page"))
        if page_no in existing_pages:
            continue
        if _page_is_structure(str(page.get("text", ""))):
            continue

        for line in _first_lines(str(page.get("text", "")), 18):
            title = _strong_generic_heading(line)
            if not title:
                continue
            fallback.append({
                "section": None,
                "concept": remove_section_number(title),
                "pages": [page_no],
                "concept_index": None,
                "chapter": None,
                "chapter_title": None,
                "is_fallback": True,
                "source": "conservative_fallback",
                "page_roles": {},
                "artifacts": [],
            })
            break

    return fallback


def merge_and_order_concepts(
    numbered_concepts: List[Dict[str, Any]],
    fallback_concepts: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    all_concepts = list(numbered_concepts) + list(fallback_concepts)
    all_concepts.sort(key=lambda c: (min(c.get("pages") or [10**9]), c.get("section") or ""))
    for idx, concept in enumerate(all_concepts):
        concept["concept_index"] = idx
    return all_concepts


# -----------------------------------------------------------------------------
# Page assignment: one forward pass, never an O(pages * concepts) search.
# -----------------------------------------------------------------------------
def assign_concepts_to_pages(
    pages: List[Dict[str, Any]],
    concepts: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    concepts_by_section = {
        c["section"]: c for c in concepts if c.get("section")
    }
    starts_by_page: Dict[int, Dict[str, Any]] = {}
    for c in concepts:
        pages_for_concept = c.get("pages") or []
        if not pages_for_concept:
            continue
        starts_by_page[min(pages_for_concept)] = c

    current: Optional[Dict[str, Any]] = None
    output: List[Dict[str, Any]] = []

    for page in sorted(pages, key=lambda p: int(p.get("page", 0))):
        page_no = int(page.get("page"))
        text = str(page.get("text", ""))

        # Strongest signal: a real subject-start anchor on this page.
        anchor = _find_tech_anchor_in_page(page)
        if anchor and anchor["section"] in concepts_by_section:
            current = concepts_by_section[anchor["section"]]

        # Generic fallback concepts start exactly on their detected page.
        if page_no in starts_by_page and starts_by_page[page_no].get("section") is None:
            current = starts_by_page[page_no]

        role = _page_role(text, is_subject_start=bool(anchor))

        page_data = {
            "page": page_no,
            "text": text,
            "concept": current.get("concept") if current else None,
            "section": current.get("section") if current else None,
            "concept_index": current.get("concept_index") if current else None,
            "content_type": role,
            "chapter": current.get("chapter") if current else None,
            "chapter_title": current.get("chapter_title") if current else None,
        }

        if current:
            current.setdefault("page_roles", {})[str(page_no)] = role
            if FIGURE_RE.search(text) or FIGURE_ID_RE.search(text):
                # Keep a compact artifact record for downstream metadata.
                captions = []
                for line in _nonempty_lines(text):
                    if "FIGURE" in line.upper() or "FIGURE-" in line.upper():
                        captions.append(line)
                current.setdefault("artifacts", []).append({
                    "page": page_no,
                    "type": "figure",
                    "captions": captions[:3],
                })

        output.append(page_data)

    return output


# -----------------------------------------------------------------------------
# Convenience API for debugging / runner integration.
# -----------------------------------------------------------------------------
def detect_document_concepts(
    pages: List[Dict[str, Any]],
    pdf_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the complete detector without depending on the rest of ingestion."""
    profile = detect_document_profile(pages)
    structure_pages = find_structure_pages(pages)
    structure_candidates = extract_structure_candidates(structure_pages)
    headings = find_numbered_headings(pages)
    numbered = build_concepts(headings)

    chapter_titles = _chapter_title_from_toc(pages)
    for concept in numbered:
        chapter = concept.get("chapter")
        concept["chapter_title"] = chapter_titles.get(chapter) if chapter else None

    fallback = build_fallback_concepts(pages, numbered, pdf_path=pdf_path)
    concepts = merge_and_order_concepts(numbered, fallback)
    page_map = assign_concepts_to_pages(pages, concepts)

    return {
        "profile": profile,
        "structure_pages": structure_pages,
        "structure_candidates": structure_candidates,
        "headings": headings,
        "numbered_concepts": numbered,
        "fallback_concepts": fallback,
        "concepts": concepts,
        "pages": page_map,
    }


__all__ = [
    "get_lines",
    "heading_score",
    "find_structure_pages",
    "extract_structure_candidates",
    "detect_document_profile",
    "get_section_number",
    "find_numbered_headings",
    "remove_section_number",
    "build_concepts",
    "detect_content_type",
    "build_fallback_concepts",
    "merge_and_order_concepts",
    "assign_concepts_to_pages",
    "detect_document_concepts",
]
