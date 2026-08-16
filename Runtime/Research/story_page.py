"""Small transport boundary for visible story-page evidence."""

import json


def decode_story_evidence(value) -> dict:
    """Accept only a JSON object from the embedded browser."""
    if not isinstance(value, str):
        return {}
    decoded = json.loads(value)
    return decoded if isinstance(decoded, dict) else {}
