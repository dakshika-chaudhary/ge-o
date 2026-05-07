import re
import json
from typing import List, Dict
from openai import OpenAI

from src.config import get_secret


def evidence_to_text(evidence: List[Dict]) -> str:
    lines = []
    for i, item in enumerate(evidence, start=1):
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        url = item.get("url", "")
        lines.append(f"[{i}] {title}\nSnippet: {snippet}\nURL: {url}")
    return "\n\n".join(lines)


def _years_in(text: str) -> List[str]:
    return re.findall(r"\b(?:19|20)\d{2}\b", text)


def _important_words(claim: str) -> List[str]:
    stop_words = {
        "there", "their", "which", "would", "about", "market", "users",
        "claim", "became", "crossed", "successfully", "launched",
        "founded", "released",
    }
    return [
        word
        for word in re.findall(r"[a-zA-Z]{5,}", claim.lower())
        if word not in stop_words
    ]


def verify_with_openai(claim: str, evidence: List[Dict]) -> Dict:
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        return {}

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a strict fact-checking agent.

Verify this claim using only the provided web evidence.

Claim:
{claim}

Web Evidence:
{evidence_to_text(evidence)}

Return only valid JSON with:
{{
  "verdict": "Verified" | "Inaccurate" | "False / No Evidence" | "Needs Review",
  "confidence": number from 0 to 100,
  "correct_fact": "corrected factual statement if available, otherwise empty string",
  "explanation": "short explanation"
}}

Rules:
- Verified: evidence strongly supports the claim.
- Inaccurate: claim has outdated/wrong number/date but evidence gives correct value.
- False / No Evidence: evidence contradicts claim or no reliable evidence supports it.
- Needs Review: evidence is weak or mixed.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You verify factual claims and return strict JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        content = response.choices[0].message.content.strip()
        content = re.sub(r"^```json|```$", "", content).strip()
        data = json.loads(content)
        return data
    except Exception as exc:
        return {
            "_llm_error": str(exc)
        }


def simple_rule_verification(claim: str, evidence: List[Dict]) -> Dict:
    """Fallback verifier when no OpenAI key exists."""
    if not evidence:
        return {
            "verdict": "False / No Evidence",
            "confidence": 30,
            "correct_fact": "",
            "explanation": "No web evidence found for this claim."
        }

    evidence_text = " ".join([
        f"{x.get('title','')} {x.get('snippet','')}" for x in evidence
    ]).lower()

    claim_years = _years_in(claim)
    evidence_years = sorted(set(_years_in(evidence_text)))
    year_match = all(year in evidence_text for year in claim_years)

    important_words = _important_words(claim)
    word_hits = sum(1 for w in important_words if w in evidence_text)
    score = int((word_hits / max(len(important_words), 1)) * 100)

    if score >= 60 and year_match:
        verdict = "Verified"
        confidence = min(85, score)
        explanation = "Several important terms and stated year/figures appear in the retrieved web evidence."
    elif score >= 60 and claim_years and evidence_years:
        verdict = "Inaccurate"
        confidence = min(80, score)
        shown_years = ", ".join(evidence_years[:5])
        explanation = (
            "The retrieved evidence appears to discuss the same topic, but it "
            f"does not support the claimed year(s): {', '.join(claim_years)}. "
            f"Evidence mentions year(s): {shown_years}."
        )
    elif score >= 35:
        verdict = "Needs Review"
        confidence = max(45, score)
        explanation = "Some related evidence was found, but it does not clearly confirm all figures."
    else:
        verdict = "False / No Evidence"
        confidence = 35
        explanation = "Retrieved evidence does not clearly support this claim."

    return {
        "verdict": verdict,
        "confidence": confidence,
        "correct_fact": "",
        "explanation": explanation
    }


def verify_claim(claim: str, evidence: List[Dict]) -> Dict:
    result = verify_with_openai(claim, evidence)
    llm_error = result.pop("_llm_error", "") if result else ""
    if result:
        return result

    fallback = simple_rule_verification(claim, evidence)
    if llm_error:
        fallback["explanation"] = (
            f"{fallback['explanation']} OpenAI verification was unavailable, "
            "so this verdict used rule-based evidence matching."
        )
    return fallback
