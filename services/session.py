
import streamlit as st


def get_access_token() -> str:
    """Return the access token for this Streamlit session."""

    token = st.session_state.get("access_token")

    if not token:
        raise RuntimeError(
            "No authenticated session is available."
        )

    return token
