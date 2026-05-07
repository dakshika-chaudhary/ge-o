import os
import requests
from typing import List, Dict
from duckduckgo_search import DDGS
from dotenv import load_dotenv

load_dotenv()


def _get_secret(name: str):
    """Read key from env or Streamlit secrets if available."""
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        return st.secrets.get(name)
    except Exception:
        return None


def search_tavily(query: str, max_results: int = 5) -> List[Dict]:
    api_key = _get_secret("TAVILY_API_KEY")
    if not api_key:
        return []

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "include_answer": True,
        "include_raw_content": False,
        "max_results": max_results,
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()

        results = []
        if data.get("answer"):
            results.append({
                "title": "Tavily Answer",
                "url": "",
                "snippet": data["answer"]
            })

        for item in data.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", "")
            })
        return results[:max_results]
    except Exception:
        return []


def search_serper(query: str, max_results: int = 5) -> List[Dict]:
    api_key = _get_secret("SERPER_API_KEY")
    if not api_key:
        return []

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json={"q": query}, timeout=20)
        response.raise_for_status()
        data = response.json()
        organic = data.get("organic", [])

        return [{
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", "")
        } for item in organic[:max_results]]
    except Exception:
        return []


def search_duckduckgo(query: str, max_results: int = 5) -> List[Dict]:
    try:
        with DDGS() as ddgs:
            rows = list(ddgs.text(query, max_results=max_results))
        return [{
            "title": item.get("title", ""),
            "url": item.get("href", ""),
            "snippet": item.get("body", "")
        } for item in rows]
    except Exception:
        return []


def live_web_search(query: str, max_results: int = 5) -> List[Dict]:
    """Search web using Tavily, then Serper, then DuckDuckGo fallback."""
    results = search_tavily(query, max_results=max_results)
    if results:
        return results

    results = search_serper(query, max_results=max_results)
    if results:
        return results

    return search_duckduckgo(query, max_results=max_results)
