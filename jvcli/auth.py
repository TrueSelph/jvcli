"""Authentication module for the CLI."""

import json
import os

TOKEN_FILE = os.path.expanduser("~/.jvcli_token")


def save_token(token: str, namespaces: dict, email: str) -> None:
    """Save the token to a file."""
    data = {"token": token, "namespaces": clean_namespaces(namespaces), "email": email}
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f)


def load_token() -> dict:
    """Load the token from a file."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
            return data
    return {}


def delete_token() -> None:
    """Delete the token file."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


def clean_namespaces(namespaces: dict) -> dict:
    """Clean up the namespaces dict."""
    for k, v in namespaces.items():
        if k == "default":
            namespaces[k] = v.replace("@", "")
        if k == "groups":
            v = [group.replace("@", "") for group in v]
            namespaces[k] = v
    return namespaces


def load_namespaces() -> str:
    """Load the namespaces from the token."""
    token = load_token()
    return token.get("namespaces", {}).get("default", "anonymous")
