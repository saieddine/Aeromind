"""AeroMind retrieval utilities.

Small text-processing and scoring helpers used by the QA retriever.
These functions are domain-independent and therefore require only
light adaptation for AeroMind.
"""

import re

def normalize_text(text):

    text = text.lower()

    text = text.replace("-", " ")

    text = re.sub(r"[^\w\s]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()

def get_important_tokens(text):

    normalized = normalize_text(text)

    words = normalized.split()

    stop_words = {
        "what",
        "is",
        "are",
        "the",
        "a",
        "an",
        "does",
        "do",
        "how",
        "why",
        "mean",
        "of",
        "in",
        "to",
        "for"
    }

    important = []

    for word in words : 
        if word not in stop_words:
            important.append(word)

    return important

def lexical_coverage(question, candidate_text):

    question_tokens = get_important_tokens(question)

    candidate_normalized = normalize_text(candidate_text)

    if not question_tokens:
        return 0.0

    matched = 0

    for token in question_tokens:
        if token in candidate_normalized.split():
            matched +=1

    return matched / len(question_tokens)

def calculate_fallback_score(distance, lexical_score):
    semantic_score = 1- distance

    final_score = (semantic_score * 0.7 + lexical_score * 0.3)

    return final_score