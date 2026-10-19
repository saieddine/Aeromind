import re


def clean_text(pages):
    """
    Clean extracted PDF text while preserving page metadata.
    """

    cleaned_pages = []

    for page in pages:
        text = page.get("text", "")

        if not text:
            continue

        text = text.strip()
        text = text.replace("\t", " ")
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        cleaned_page = page.copy()
        cleaned_page["text"] = text

        cleaned_pages.append(cleaned_page)

    return cleaned_pages


