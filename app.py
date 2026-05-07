import streamlit as st
import pandas as pd

from src.pdf_utils import extract_text_from_pdf
from src.claim_extractor import extract_claims
from src.web_search import live_web_search
from src.verifier import verify_claim
from src.report_utils import results_to_dataframe, generate_markdown_report


st.set_page_config(
    page_title="Fact-Check Agent",
    page_icon="✅",
    layout="wide"
)


def verdict_badge(verdict: str) -> str:
    if verdict == "Verified":
        return "✅ Verified"
    if verdict == "Inaccurate":
        return "⚠️ Inaccurate"
    if verdict == "False / No Evidence":
        return "❌ False / No Evidence"
    return "❓ Needs Review"


st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0;
    }
    .sub-title {
        font-size: 18px;
        color: #4b5563;
        margin-top: 8px;
    }
    .metric-card {
        background: #fff1f2;
        padding: 18px;
        border-radius: 18px;
        border: 1px solid #ffe4e6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<p class="main-title">Fact-Check Agent</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Upload a PDF. The system extracts factual claims, searches live web data, and flags inaccurate or unsupported statements.</p>',
    unsafe_allow_html=True
)

with st.sidebar:
    st.header("Settings")
    max_claims = st.slider("Maximum claims to verify", 3, 30, 10)
    max_sources = st.slider("Sources per claim", 3, 10, 5)
    st.info(
        "For best results, add OPENAI_API_KEY and TAVILY_API_KEY or SERPER_API_KEY in Streamlit secrets."
    )

uploaded_file = st.file_uploader("Upload PDF for automated fact-checking", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting PDF text..."):
        text = extract_text_from_pdf(uploaded_file)

    if not text:
        st.error("No readable text found in the PDF. Please upload a text-based PDF.")
        st.stop()

    with st.expander("Preview Extracted Text"):
        st.write(text[:5000])

    with st.spinner("Extracting factual claims..."):
        claims = extract_claims(text, max_claims=max_claims)

    if not claims:
        st.warning("No strong factual claims found. Try a PDF with stats, dates, numbers, or factual statements.")
        st.stop()

    st.subheader(f"Extracted Claims: {len(claims)}")

    for c in claims:
        st.markdown(f"- **Claim {c['claim_id']}:** {c['claim']}")

    if st.button("Verify Claims", type="primary"):
        results = []
        progress = st.progress(0)

        for idx, item in enumerate(claims, start=1):
            claim = item["claim"]
            query = f"verify factual claim latest reliable source: {claim}"

            with st.spinner(f"Verifying claim {idx}/{len(claims)}..."):
                evidence = live_web_search(query, max_results=max_sources)
                verdict = verify_claim(claim, evidence)

            sources = [
                e.get("url", "") for e in evidence
                if e.get("url")
            ]

            results.append({
                "Claim": claim,
                "Verdict": verdict_badge(verdict.get("verdict", "Needs Review")),
                "Confidence": verdict.get("confidence", ""),
                "Correct Fact": verdict.get("correct_fact", ""),
                "Explanation": verdict.get("explanation", ""),
                "Sources": "\n".join(sources[:max_sources])
            })

            progress.progress(idx / len(claims))

        df = results_to_dataframe(results)

        st.success("Fact-checking completed.")

        col1, col2, col3, col4 = st.columns(4)
        verdict_counts = df["Verdict"].value_counts().to_dict()

        with col1:
            st.metric("Verified", verdict_counts.get("✅ Verified", 0))
        with col2:
            st.metric("Inaccurate", verdict_counts.get("⚠️ Inaccurate", 0))
        with col3:
            st.metric("False / No Evidence", verdict_counts.get("❌ False / No Evidence", 0))
        with col4:
            st.metric("Needs Review", verdict_counts.get("❓ Needs Review", 0))

        st.subheader("Verification Report")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        markdown_report = generate_markdown_report(results).encode("utf-8")

        st.download_button(
            "Download CSV Report",
            data=csv,
            file_name="fact_check_report.csv",
            mime="text/csv"
        )

        st.download_button(
            "Download Markdown Report",
            data=markdown_report,
            file_name="fact_check_report.md",
            mime="text/markdown"
        )

else:
    st.info("Upload a PDF to begin.")
