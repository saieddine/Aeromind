"""AeroMind document concept and section detector.

Adapted from the NPU Academic Assistant ingestion pipeline.
Preserves numbered technical sections, semantic fallback boundaries,
content types, concept ordering, and page-level metadata while removing
NPU-specific package imports.
"""

import re
import pdfplumber

from rag.ingestion.layout_detector_aeromind import (
    extract_title_candidate,
    extract_page_body
)

from rag.ingestion.semantic_boundary_aeromind import (
    calculate_boundary_signals,
    starts_new_concept
)


# ==================================================
# GET ALL TEXT LINES
# ==================================================

def get_lines(pages):

    all_lines = []

    for page in pages:

        text = page["text"]

        lines = text.split("\n")

        for line in lines:

            line = line.strip()

            if line:

                all_lines.append({
                    "text": line,
                    "page": page["page"]
                })

    return all_lines


# ==================================================
# HEADING SCORE
# ==================================================

def heading_score(line):

    score = 0

    text = line["text"]

    word_count = len(
        text.split()
    )

    if word_count <= 10:
        score += 1

    if text.isupper():
        score += 1

    if re.match(
        r"^\d+(\.\d+)*\.?\s+",
        text
    ):
        score += 2

    return score


# ==================================================
# FIND STRUCTURE PAGES
# ==================================================

def find_structure_pages(pages):

    structure_pages = []

    for page in pages:

        text = page["text"].lower()

        if (
            "contents" in text
            or "table of contents" in text
            or "outline" in text
        ):
            structure_pages.append(
                page
            )

    return structure_pages


# ==================================================
# EXTRACT STRUCTURE CANDIDATES
# ==================================================

def extract_structure_candidates(
    structure_pages
):

    candidates = []

    for page in structure_pages:

        lines = page["text"].split(
            "\n"
        )

        for line in lines:

            line = line.strip()

            line = line.lstrip(
                "•*- "
            )

            if re.match(
                r"^\d+(\.\d+)*\.?\s",
                line
            ):

                if line not in candidates:

                    candidates.append(
                        line
                    )

    return candidates


# ==================================================
# FIND HEADING CANDIDATES
# ==================================================

def find_heading_candidates(pages):

    candidates = []

    lines = get_lines(
        pages
    )

    for line in lines:

        score = heading_score(
            line
        )

        if score >= 1:

            print(
                f"{line['text']} "
                f"| page: {line['page']} "
                f"| score: {score}"
            )

    return candidates


# ==================================================
# GET SECTION NUMBER
# ==================================================

def get_section_number(text):

    # Example:
    # 6.1
    # 6.1.5
    # 2.14

    match = re.match(
        r"^(\d+(?:\.\d+)+)\.?\s+",
        text
    )

    if match:
        return match.group(1)


    # Example:
    # I-1
    # II-3

    match = re.match(
        r"^([IVXLCDM]+-\d+)\s+",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1)


    # Example:
    # I - Introduction
    # II - Gaussian Elimination

    match = re.match(
        r"^([IVXLCDM]+)\s*-\s+",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return None


# ==================================================
# FIND NUMBERED HEADINGS
# ==================================================

def find_numbered_headings(pages):

    headings = []

    lines = get_lines(
        pages
    )

    for line in lines:

        section_number = (
            get_section_number(
                line["text"]
            )
        )

        if section_number:

            heading = {
                "section": section_number,
                "title": line["text"],
                "page": line["page"]
            }

            headings.append(
                heading
            )

    return headings


# ==================================================
# REMOVE SECTION NUMBER
# ==================================================

def remove_section_number(title):

    # ----------------------------------
    # Format 1
    # 6.1.1 The Interface Concept
    # 2.14 Don't Care Conditions
    # ----------------------------------

    title = re.sub(
        r"^\d+(?:\.\d+)+\.?\s+",
        "",
        title
    )


    # ----------------------------------
    # Format 2
    # I-1 Discovering
    # I-2 Meaning
    # ----------------------------------

    title = re.sub(
        r"^[IVXLCDM]+-\d+\s+",
        "",
        title,
        flags=re.IGNORECASE
    )


    # ----------------------------------
    # Format 3
    # I - Introduction
    # II - Gaussian Elimination
    # ----------------------------------

    title = re.sub(
        r"^[IVXLCDM]+\s*-\s+",
        "",
        title,
        flags=re.IGNORECASE
    )

    return title.strip()


# ==================================================
# BUILD NUMBERED CONCEPTS
# ==================================================

def build_concepts(headings):

    concepts = []

    for heading in headings:

        section = heading[
            "section"
        ]

        existing_concept = None

        for concept in concepts:

            if (
                concept["section"]
                == section
            ):

                existing_concept = (
                    concept
                )

                break


        # ----------------------------------
        # SAME NUMBERED CONCEPT
        # ----------------------------------

        if existing_concept:

            if (
                heading["page"]
                not in existing_concept[
                    "pages"
                ]
            ):

                existing_concept[
                    "pages"
                ].append(
                    heading["page"]
                )


        # ----------------------------------
        # NEW NUMBERED CONCEPT
        # ----------------------------------

        else:

            concept = {
                "section": section,

                "concept": (
                    remove_section_number(
                        heading["title"]
                    )
                ),

                "pages": [
                    heading["page"]
                ],

                "concept_index": (
                    len(concepts)
                )
            }

            concepts.append(
                concept
            )

    return concepts


# ==================================================
# DETECT CONTENT TYPE
# ==================================================

def detect_content_type(page_text):
    text_lower = page_text.lower()

    structure_markers = [
        "table of contents",
        "contents",
        "outline",
        "agenda",
    ]

    question_markers = [
        "questions",
        "top hat question",
        "quiz",
        "self check",
        "check your understanding",
    ]

    review_markers = [
        "recap",
        "summary",
        "review",
    ]

    # ----------------------------------
    # STRUCTURE
    # ----------------------------------

    for marker in structure_markers:
        if marker in text_lower:
            return "structure"

    # ----------------------------------
    # QUESTION
    # ----------------------------------

    for marker in question_markers:
        if marker in text_lower:
            return "question"

    # ----------------------------------
    # REVIEW
    # ----------------------------------

    for marker in review_markers:
        if marker in text_lower:
            return "review"

    # ----------------------------------
    # NORMAL TEACHING MATERIAL
    # ----------------------------------

    return "concept"

    # ----------------------------------
    # STRUCTURE
    # ----------------------------------

    for marker in structure_markers:

        if marker in text_lower:
            return "structure"


    # ----------------------------------
    # QUESTION
    # ----------------------------------

    for marker in question_markers:

        if marker in text_lower:
            return "question"


    # ----------------------------------
    # REVIEW
    # ----------------------------------

    for marker in review_markers:

        if marker in text_lower:
            return "review"


    # ----------------------------------
    # NORMAL TEACHING MATERIAL
    # ----------------------------------

    return "concept"


# ==================================================
# BUILD SEMANTIC FALLBACK CONCEPTS
# ==================================================

def build_fallback_concepts(
    pages,
    numbered_concepts,
    pdf_path,
    debug_pages=None
):

    fallback_concepts = []

    current_concept = None

    current_concept_pages = []

    if debug_pages is None:
        debug_pages = set()
    else:
        debug_pages = set(
            debug_pages
        )


    # ==================================================
    # OPEN ORIGINAL PDF
    # ==================================================

    with pdfplumber.open(
        pdf_path
    ) as pdf:

        # ==============================================
        # PROCESS EACH PAGE IN ORDER
        # ==============================================

        for page_data in pages:

            page_number = (
                page_data["page"]
            )


            # ==========================================
            # 1. CHECK PRIMARY NUMBERED CONCEPTS
            # ==========================================

            numbered_concept = None

            for concept in numbered_concepts:

                if (
                    page_number
                    in concept["pages"]
                ):

                    numbered_concept = (
                        concept
                    )

                    break


            # ==========================================
            # NUMBERED CONCEPT FOUND
            # ==========================================

            if (
                numbered_concept
                is not None
            ):

                # --------------------------------------
                # Different numbered concept
                # --------------------------------------

                if (
                    current_concept is None
                    or
                    current_concept[
                        "concept"
                    ]
                    !=
                    numbered_concept[
                        "concept"
                    ]
                ):

                    current_concept = (
                        numbered_concept
                    )

                    current_concept_pages = [
                        page_number
                    ]


                # --------------------------------------
                # Same numbered concept continues
                # --------------------------------------

                else:

                    if (
                        page_number
                        not in
                        current_concept_pages
                    ):

                        current_concept_pages.append(
                            page_number
                        )

                # Numbered detector is authoritative.
                # Do NOT run fallback.

                continue


            # ==========================================
            # 2. CHECK CONTENT TYPE
            # ==========================================

            page_text = (
                page_data["text"]
            )

            content_type = (
                detect_content_type(
                    page_text
                )
            )


            # Structure / question / review pages
            # should not create teaching concepts.

            if (
                content_type
                != "concept"
            ):

                continue


            # ==========================================
            # 3. GET ORIGINAL PDF PAGE
            # ==========================================

            pdf_page = pdf.pages[
                page_number - 1
            ]


            # ==========================================
            # 4. FIND VISUAL TITLE
            # ==========================================

            title_candidate = (
                extract_title_candidate(
                    pdf_page
                )
            )


            # If no visual title is detected,
            # treat conservatively as continuation.

            if not title_candidate:

                if (
                    current_concept
                    is not None
                    and page_number
                    not in
                    current_concept_pages
                ):

                    current_concept_pages.append(
                        page_number
                    )

                continue


            title = (
                title_candidate[
                    "text"
                ].strip()
            )


            # ==========================================
            # 5. EXTRACT CLEAN BODY
            # ==========================================

            body = extract_page_body(
                pdf_page
            )


            if not body:

                if (
                    current_concept
                    is not None
                    and page_number
                    not in
                    current_concept_pages
                ):

                    current_concept_pages.append(
                        page_number
                    )

                continue


            # ==========================================
            # 6. NEED EXISTING CONCEPT
            # ==========================================

            if current_concept is None:

                # There is no old concept yet,
                # so semantic comparison is impossible.

                continue


            current_concept_title = (
                current_concept[
                    "concept"
                ]
            )


            # ==========================================
            # 7. BUILD CURRENT CONCEPT PROTOTYPE
            # ==========================================

            prototype_parts = [
                current_concept_title
            ]


            for concept_page_number in (
                current_concept_pages
            ):

                concept_pdf_page = (
                    pdf.pages[
                        concept_page_number
                        - 1
                    ]
                )

                concept_body = (
                    extract_page_body(
                        concept_pdf_page
                    )
                )

                if concept_body:

                    prototype_parts.append(
                        concept_body
                    )


            current_concept_prototype = (
                "\n\n".join(
                    prototype_parts
                )
            )


            # ==========================================
            # 8. CALCULATE THREE SEMANTIC SIGNALS
            # ==========================================

            signals = (
                calculate_boundary_signals(
                    title=title,
                    body=body,

                    current_concept_title=(
                        current_concept_title
                    ),

                    current_concept_prototype=(
                        current_concept_prototype
                    )
                )
            )


            # ==========================================
            # 9. MAKE SEMANTIC DECISION
            # ==========================================

            decision = (
                starts_new_concept(
                    title_body=(
                        signals[
                            "title_body"
                        ]
                    ),

                    continuity=(
                        signals[
                            "continuity"
                        ]
                    ),

                    title_concept=(
                        signals[
                            "title_concept"
                        ]
                    )
                )
            )


            # ==========================================
            # OPTIONAL DEBUG OUTPUT
            # ==========================================

            if (
                page_number
                in debug_pages
            ):

                boundary_gap = (
                    signals[
                        "title_body"
                    ]
                    -
                    signals[
                        "continuity"
                    ]
                )

                print(
                    "\n"
                    + "=" * 70
                )

                print(
                    f"DEBUG PAGE "
                    f"{page_number}"
                )

                print(
                    "=" * 70
                )

                print(
                    "TITLE:",
                    title
                )

                print(
                    "CURRENT CONCEPT:",
                    current_concept_title
                )

                print(
                    "CURRENT CONCEPT PAGES:",
                    current_concept_pages
                )

                print(
                    "TITLE ↔ BODY:",
                    signals[
                        "title_body"
                    ]
                )

                print(
                    "BODY ↔ CURRENT CONCEPT:",
                    signals[
                        "continuity"
                    ]
                )

                print(
                    "TITLE ↔ CURRENT CONCEPT:",
                    signals[
                        "title_concept"
                    ]
                )

                print(
                    "BOUNDARY GAP:",
                    boundary_gap
                )

                print(
                    "DECISION:",
                    decision
                )


            # ==========================================
            # 10. NEW FALLBACK CONCEPT
            # ==========================================

            if decision is True:

                fallback_concept = {

                    "section": None,

                    "concept": title,

                    "pages": [
                        page_number
                    ],

                    "is_fallback": True
                }


                fallback_concepts.append(
                    fallback_concept
                )


                # New concept becomes active.

                current_concept = (
                    fallback_concept
                )


                # Reset prototype.

                current_concept_pages = [
                    page_number
                ]

                continue


            # ==========================================
            # 11. CONTINUATION OR UNCERTAIN
            # ==========================================

            # False → continuation
            # None  → uncertain
            #
            # For V1:
            # uncertain is conservatively treated
            # as continuation.

            if (
                page_number
                not in
                current_concept_pages
            ):

                current_concept_pages.append(
                    page_number
                )


    # ==================================================
    # RETURN FALLBACK RESULTS
    # ==================================================

    return fallback_concepts


# ==================================================
# MERGE NUMBERED + FALLBACK CONCEPTS
# ==================================================

def merge_and_order_concepts(
    numbered_concepts,
    fallback_concepts
):

    all_concepts = []

    for concept in numbered_concepts:

        all_concepts.append(
            concept
        )

    for concept in fallback_concepts:

        all_concepts.append(
            concept
        )


    # Sort according to first page.

    all_concepts.sort(
        key=lambda concept:
        concept["pages"][0]
    )


    # Rebuild concept indexes.

    for index, concept in enumerate(
        all_concepts
    ):

        concept[
            "concept_index"
        ] = index


    return all_concepts


# ==================================================
# ASSIGN CONCEPTS TO ALL PAGES
# ==================================================

def assign_concepts_to_pages(
    pages,
    concepts
):

    pages_with_concepts = []

    current_concept = None


    for page in pages:

        page_text = (
            page["text"]
        )

        page_number = (
            page["page"]
        )

        content_type = (
            detect_content_type(
                page_text
            )
        )


        # ==========================================
        # CHECK WHETHER A NEW CONCEPT STARTS HERE
        # ==========================================

        for concept in concepts:

            section = (
                concept["section"]
            )


            # --------------------------------------
            # NUMBERED CONCEPT
            # --------------------------------------

            if section is not None:

                pattern = (
                    rf"^"
                    rf"{re.escape(section)}"
                    rf"\.?\s+"
                )

                if re.search(
                    pattern,
                    page_text,
                    re.MULTILINE
                ):

                    current_concept = (
                        concept
                    )


            # --------------------------------------
            # FALLBACK CONCEPT
            # --------------------------------------

            else:

                # For fallback concepts, use the
                # exact detected starting page.
                #
                # This is safer than searching the
                # title string everywhere.

                if (
                    page_number
                    in concept["pages"]
                ):

                    current_concept = (
                        concept
                    )


        # ==========================================
        # BUILD PAGE DATA
        # ==========================================

        page_data = {

            "page": page_number,

            "text": page_text,

            "concept": (
                current_concept[
                    "concept"
                ]
                if current_concept
                else None
            ),

            "section": (
                current_concept[
                    "section"
                ]
                if current_concept
                else None
            ),

            "concept_index": (
                current_concept[
                    "concept_index"
                ]
                if current_concept
                else None
            ),

            "content_type": (
                content_type
            )
        }


        pages_with_concepts.append(
            page_data
        )


    return pages_with_concepts