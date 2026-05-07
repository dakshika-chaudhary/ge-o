# Fact-Check Agent — PDF Claim Verification Web App

A deployed-ready Streamlit web app that uploads a PDF, extracts factual claims, verifies them against live web sources, and flags each claim as:

- ✅ Verified
- ⚠️ Inaccurate
- ❌ False / No Evidence
- ❓ Needs Review

This project is designed for marketing-content fact checking, especially outdated or hallucinated statistics, dates, financial figures, technical claims, and numerical statements.

---

## Features

### 1. PDF Claim Extraction
- Upload any PDF.
- Extracts text using `pypdf`.
- Identifies claim-like sentences containing:
  - percentages
  - dates / years
  - money / financial figures
  - numbers / rankings
  - market-size or growth statements
  - technical metrics

### 2. Live Web Verification
- Uses live web search through:
  - Tavily API if `TAVILY_API_KEY` is configured
  - Serper Google Search API if `SERPER_API_KEY` is configured
  - DuckDuckGo fallback if no API key is available

### 3. AI-Assisted Verdict
- Uses OpenAI if `OPENAI_API_KEY` is available.
- Falls back to rule-based evidence matching if no LLM key is configured.
- Provides:
  - verdict
  - confidence score
  - corrected fact
  - explanation
  - source URLs

### 4. Report Generation
- Interactive table in app.
- Download CSV report.
- Download Markdown report.

---

## Tech Stack

- Python
- Streamlit
- pypdf
- requests
- duckduckgo-search
- pandas
- optional OpenAI API
- optional Tavily / Serper web search APIs

---

## Folder Structure

```txt
factcheck_web_app/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── sample_trap_document.md
│
├── src/
│   ├── __init__.py
│   ├── pdf_utils.py
│   ├── claim_extractor.py
│   ├── web_search.py
│   ├── verifier.py
│   └── report_utils.py
│
└── .streamlit/
    └── config.toml
```

---

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/factcheck-web-app.git
cd factcheck-web-app
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add API Keys

Create a `.env` file or use Streamlit secrets.

```bash
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
SERPER_API_KEY=your_serper_key
```

At least one live-search method is recommended. If no search API key is provided, DuckDuckGo fallback will be used.

### 5. Run App

```bash
streamlit run app.py
```

---

## Streamlit Cloud Deployment

1. Push this project to GitHub.
2. Go to Streamlit Community Cloud.
3. Click **New App**.
4. Select your repo.
5. Main file path:

```txt
app.py
```

6. Add secrets in Streamlit Cloud:

```toml
OPENAI_API_KEY = "your_openai_key"
TAVILY_API_KEY = "your_tavily_key"
SERPER_API_KEY = "your_serper_key"
```

7. Deploy and copy your live URL.

---

## Render Deployment

Use this command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

---

## Submission Format

Use this email format:

```txt
Hi Dakshika,

Please find my submission details below:

Deployed App Link:
https://your-app.streamlit.app

GitHub Repository:
https://github.com/your-username/factcheck-web-app

Demo Video:
https://drive.google.com/your-demo-video-link

Thanks,
Anjali
```

---

## Notes

- The app is designed to flag fake or outdated statistics.
- Best accuracy is achieved when API keys are configured.
- For production usage, prefer Tavily/Serper + OpenAI for stronger verification.
