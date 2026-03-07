"""Helpers for building consistent menu labels."""

from __future__ import annotations


def ensure_mnemonic(label: str, preferred: str | None = None) -> str:
    """Ensure a menu label contains a mnemonic marker ('&')."""
    if not label:
        return label

    # Keep any existing mnemonic or escaped ampersand untouched.
    if "&" in label:
        return label

    if preferred:
        idx = label.lower().find(preferred.lower())
        if idx >= 0:
            return f"{label[:idx]}&{label[idx:]}"

    for idx, char in enumerate(label):
        if char.isalnum():
            return f"{label[:idx]}&{label[idx:]}"

    return label
