"""Session state management utilities for Streamlit."""

from typing import Any

import streamlit as st


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "aap_url": "",
        "aap_token": "",
        "verify_ssl": False,
        "aap_connected": False,
        "analysis_data": None,
        "last_analysis_time": None,
        "current_org": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_session(key: str, default: Any = None) -> Any:
    """Get value from session state.

    Args:
        key: Session state key
        default: Default value if key doesn't exist

    Returns:
        Session state value or default
    """
    return st.session_state.get(key, default)


def set_session(key: str, value: Any):
    """Set value in session state.

    Args:
        key: Session state key
        value: Value to set
    """
    st.session_state[key] = value


def is_connected() -> bool:
    """Check if AAP connection is established.

    Returns:
        True if connected, False otherwise
    """
    return st.session_state.get("aap_connected", False)


def get_connection_config() -> dict:
    """Get AAP connection configuration from session.

    Returns:
        Dictionary with connection parameters
    """
    return {
        "url": st.session_state.get("aap_url", ""),
        "token": st.session_state.get("aap_token", ""),
        "verify_ssl": st.session_state.get("verify_ssl", False),
    }


def clear_analysis_cache():
    """Clear cached analysis data."""
    if "analysis_data" in st.session_state:
        st.session_state.analysis_data = None
    if "last_analysis_time" in st.session_state:
        st.session_state.last_analysis_time = None
