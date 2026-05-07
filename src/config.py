import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def get_secret(name: str) -> Optional[str]:
    """Read configuration from environment variables or Streamlit secrets."""
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st

        value = st.secrets.get(name)
        return str(value) if value else None
    except Exception:
        return None


def has_secret(name: str) -> bool:
    return bool(get_secret(name))
