import re

FILLER_WORDS = {
    "um", "uh", "like", "you", "know", "basically", "actually",
    "literally", "right", "okay", "so", "well", "just", "really",
    "kind", "sort", "mean", "guys", "thing", "stuff",
}

PROMO_MARKERS = (
    "sponsor", "sponsored", "this video is brought", "use my code",
    "link in the description", "subscribe", "hit the bell",
    "patreon", "free trial", "sign up", "discount",
)

POINT_MARKERS = (
    "first", "the key", "the point is", "what matters",
    "the reason", "研究", "studies show", "research shows",
    "here's how", "the problem is", "let me explain",
)


def _words(text: str) -> list[str]:
    """Split text into lowercase word tokens."""
    return re.findall(r"[a-z']+", text.lower())


def score_transcript(segments: list[dict], duration_seconds: int) -> dict:
    """Compute Signal Score and its components from a transcript."""
    all_words = []
    for s in segments:
        all_words.extend(_words(s["text"]))

    total = len(all_words) or 1

    filler_ratio = sum(1 for w in all_words if w in FILLER_WORDS) / total

    promo_seconds = 0
    for s in segments:
        low = s["text"].lower()
        if any(m in low for m in PROMO_MARKERS):
            promo_seconds += 5

    first_point_seconds = int(duration_seconds)
    for s in segments:
        low = s["text"].lower()
        if any(m in low for m in POINT_MARKERS):
            first_point_seconds = int(s["start"])
            break

    minutes = max(duration_seconds / 60, 1)
    unique = len(set(all_words))
    concept_density = unique / minutes

    repetition_ratio = 1 - (unique / total)

    return {
        "filler_ratio": round(filler_ratio, 4),
        "first_point_seconds": first_point_seconds,
        "promo_seconds": min(promo_seconds, duration_seconds),
        "concept_density": round(concept_density, 2),
        "repetition_ratio": round(repetition_ratio, 4),
    }


def signal_score(parts: dict, duration_seconds: int) -> float:
    """Combine components into a single 0-100 score."""
    filler = max(0.0, 1 - parts["filler_ratio"] / 0.25)
    repetition = max(0.0, 1 - parts["repetition_ratio"] / 0.85)
    density = min(parts["concept_density"] / 120, 1.0)
    promo = max(0.0, 1 - parts["promo_seconds"] / max(duration_seconds, 1) / 0.15)
    start = max(0.0, 1 - parts["first_point_seconds"] / 120)

    score = (
        filler * 25
        + density * 25
        + start * 20
        + repetition * 15
        + promo * 15
    )
    return round(score, 1)
