# auth_state.py
"""Holds the current login token in memory and provides auth headers for requests."""

_token = None


def set_token(token: str) -> None:
    global _token
    _token = token


def clear_token() -> None:
    global _token
    _token = None


def get_headers() -> dict:
    """Return the Authorization header to attach to every API request."""
    if _token is None:
        return {}
    return {"Authorization": f"Bearer {_token}"}
