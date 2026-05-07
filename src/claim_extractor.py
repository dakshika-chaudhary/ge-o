import re
from typing import List, Dict


CLAIM_PATTERNS = [
    r"\b\d+(\.\d+)?\s?%",
    r"\b(19|20)\d{2}\b",
    r"\$[\d,.]+",
    r"₹[\d,.]+",
    r"\b\d+(\.\d+)?\s?(million|billion|trillion|crore|lakh|k|m|bn|tb)\b",
    r"\b\d+(\.\d+)?\s?(users|customers|companies|countries|employees|revenue|market share|growth|CAGR)\b",
    r"\b(first|largest|smallest|highest|lowest|fastest|leading|number one|#1)\b",
]


def clean_sentence(sentence: str) -> str:
    sentence = re.sub(r"\s+", " ", sentence)
    return sentence.strip(" -•\n\t")


def split_into_sentences(text: str) -> List[str]:
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [clean_sentence(p) for p in parts if len(clean_sentence(p)) > 20]


def is_claim(sentence: str) -> bool:
    lower = sentence.lower()
    if len(sentence.split()) < 5:
        return False
    return any(re.search(pattern, lower, flags=re.IGNORECASE) for pattern in CLAIM_PATTERNS)


def extract_claims(text: str, max_claims: int = 20) -> List[Dict]:
    """Extract factual claims likely needing verification."""
    sentences = split_into_sentences(text)
    claims = []
    seen = set()

    for sentence in sentences:
        if is_claim(sentence):
            key = sentence.lower()
            if key not in seen:
                claims.append({
                    "claim_id": len(claims) + 1,
                    "claim": sentence
                })
                seen.add(key)

        if len(claims) >= max_claims:
            break

    return claims
