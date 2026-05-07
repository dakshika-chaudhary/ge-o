from typing import List, Dict
import pandas as pd


def results_to_dataframe(results: List[Dict]) -> pd.DataFrame:
    return pd.DataFrame(results)


def generate_markdown_report(results: List[Dict]) -> str:
    lines = ["# Fact-Check Report", ""]

    summary = {}
    for row in results:
        verdict = row.get("Verdict", "Unknown")
        summary[verdict] = summary.get(verdict, 0) + 1

    lines.append("## Summary")
    for verdict, count in summary.items():
        lines.append(f"- **{verdict}:** {count}")

    lines.append("")
    lines.append("## Detailed Results")

    for idx, row in enumerate(results, start=1):
        lines.append(f"### Claim {idx}")
        lines.append(f"**Claim:** {row.get('Claim', '')}")
        lines.append(f"**Verdict:** {row.get('Verdict', '')}")
        lines.append(f"**Confidence:** {row.get('Confidence', '')}")
        if row.get("Correct Fact"):
            lines.append(f"**Correct Fact:** {row.get('Correct Fact')}")
        lines.append(f"**Explanation:** {row.get('Explanation', '')}")
        lines.append(f"**Sources:** {row.get('Sources', '')}")
        lines.append("")

    return "\n".join(lines)
