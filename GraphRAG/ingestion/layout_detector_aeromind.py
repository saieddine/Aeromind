"""AeroMind PDF layout and visual title detection utilities.

This module analyzes PDF typography and page geometry to identify likely
visual titles and extract page body text. It is intentionally domain-neutral
so it can be reused for Airbus/Boeing technical documents and other
AeroMind knowledge sources.
"""

import statistics


BULLET_SYMBOLS = (
    "•",
    "◦",
    "▪",
    "▫",
    "➢",
    "❑",
    "*",
)


def is_bold_font(font_name):
    if not font_name:
        return False

    font_name = font_name.lower()

    return (
        "bold" in font_name
        or "semibold" in font_name
        or "demi" in font_name
    )


def build_visual_lines(page):
    """
    Convert pdfplumber words into reconstructed visual lines.

    Output example:

    {
        "text": "What is Inner Class?",
        "top": 37.0,
        "relative_top": 0.069,
        "font_size": 39.96,
        "bold_ratio": 0.0
    }
    """

    words = page.extract_words(
        extra_attrs=["size", "fontname"]
    )

    if not words:
        return []

    # Sort visually:
    # top → bottom
    # left → right
    words = sorted(
        words,
        key=lambda word: (
            float(word["top"]),
            float(word["x0"])
        )
    )

    lines = []

    current_line = []
    current_top = None

    # A small tolerance is needed because words that visually
    # belong to the same line may have slightly different "top"
    # values in the PDF.
    line_tolerance = max(
        2.0,
        float(page.height) * 0.004
    )

    for word in words:

        word_top = float(word["top"])

        if current_top is None:
            current_line = [word]
            current_top = word_top
            continue

        if abs(word_top - current_top) <= line_tolerance:

            current_line.append(word)

        else:

            lines.append(
                create_line_data(
                    current_line,
                    page
                )
            )

            current_line = [word]
            current_top = word_top

    # Don't forget final line
    if current_line:

        lines.append(
            create_line_data(
                current_line,
                page
            )
        )

    return lines


def create_line_data(words, page):

    words = sorted(
        words,
        key=lambda word: float(word["x0"])
    )

    text = " ".join(
        word["text"]
        for word in words
    ).strip()

    font_sizes = [
        float(word.get("size", 0))
        for word in words
        if float(word.get("size", 0)) > 0
    ]

    if not font_sizes:
        average_font_size = 0
    else:
        average_font_size = sum(font_sizes) / len(font_sizes)

    bold_words = 0

    for word in words:

        if is_bold_font(
            word.get("fontname")
        ):
            bold_words += 1

    bold_ratio = (
        bold_words / len(words)
        if words
        else 0
    )

    top = min(
        float(word["top"])
        for word in words
    )

    return {
        "text": text,
        "top": top,
        "relative_top": top / float(page.height),
        "font_size": average_font_size,
        "bold_ratio": bold_ratio,
        "word_count": len(text.split())
    }


def get_typical_font_size(lines):
    """
    Estimate the normal/body font size of the page.

    We use the median instead of a fixed value such as 20 or 24,
    because every PDF can use different sizes.
    """

    sizes = []

    for line in lines:

        # Ignore footer area
        if line["relative_top"] > 0.90:
            continue

        if line["font_size"] > 0:

            # Add font once per word so large body paragraphs have
            # more influence than a short title.
            for _ in range(max(line["word_count"], 1)):

                sizes.append(
                    line["font_size"]
                )

    if not sizes:
        return 0

    return statistics.median(sizes)


def calculate_title_score(
    line,
    typical_font_size
):

    text = line["text"]

    if not text:
        return -999

    relative_top = line["relative_top"]
    word_count = line["word_count"]

    # ---------------------------------------------
    # Reject footer
    # ---------------------------------------------

    if relative_top > 0.90:
        return -999

    # ---------------------------------------------
    # Candidate should normally be in upper area
    # ---------------------------------------------

    if relative_top > 0.40:
        return -999

    score = 0.0

    # ---------------------------------------------
    # 1. FONT PROMINENCE
    # ---------------------------------------------

    if typical_font_size > 0:

        font_ratio = (
            line["font_size"]
            / typical_font_size
        )

        # Larger than normal body text
        if font_ratio >= 1.60:
            score += 4

        elif font_ratio >= 1.35:
            score += 3

        elif font_ratio >= 1.15:
            score += 1

    # ---------------------------------------------
    # 2. POSITION
    # ---------------------------------------------

    if relative_top <= 0.12:
        score += 3

    elif relative_top <= 0.20:
        score += 2

    elif relative_top <= 0.30:
        score += 1

    # ---------------------------------------------
    # 3. TITLE LENGTH
    # ---------------------------------------------

    if 2 <= word_count <= 12:
        score += 2

    elif word_count <= 18:
        score += 1

    # ---------------------------------------------
    # 4. BOLDNESS
    # ---------------------------------------------

    if line["bold_ratio"] >= 0.70:
        score += 1

    # ---------------------------------------------
    # 5. BULLET PENALTY
    # ---------------------------------------------

    stripped = text.strip()

    if stripped.startswith(BULLET_SYMBOLS):
        score -= 5

    return score


def extract_title_candidate(page):
    """
    Find the most likely visual title of a PDF page.

    IMPORTANT:
    This does NOT decide whether the title is a new concept.

    It only answers:

        "What looks like the page/slide title?"
    """

    lines = build_visual_lines(page)

    if not lines:
        return None

    typical_font_size = get_typical_font_size(
        lines
    )

    candidates = []

    for line in lines:

        score = calculate_title_score(
            line,
            typical_font_size
        )

        if score <= 0:
            continue

        candidate = line.copy()

        candidate["score"] = score

        if typical_font_size > 0:

            candidate["font_ratio"] = (
                line["font_size"]
                / typical_font_size
            )

        else:

            candidate["font_ratio"] = 0

        candidates.append(candidate)

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (
            -item["score"],
            item["relative_top"]
        )
    )

    return candidates[0]

def extract_page_body(page):

    lines = build_visual_lines(page)

    if not lines:
        return ""

    title_candidate = extract_title_candidate(
        page
    )

    title_text = None

    if title_candidate:
        title_text = title_candidate["text"]

    body_lines = []

    title_removed = False

    for line in lines:

        # Ignore footer
        if line["relative_top"] > 0.90:
            continue

        # Ignore visual title
        if (
            title_text
            and not title_removed
            and line["text"] == title_text
        ):
            title_removed = True
            continue

        body_lines.append(
            line["text"]
        )

    return "\n".join(
        body_lines
    )