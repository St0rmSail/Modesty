"""Secure setup and bounded authentication validation for Smithsonian access."""

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from getpass import getpass
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from Runtime.Library.credentials import CredentialError, CredentialStore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KEY_PATH = PROJECT_ROOT / "Data" / "Secrets" / "smithsonian_api_key.dpapi"
DEFAULT_AUDIT_PATH = PROJECT_ROOT / "Data" / "grand_library_audit.jsonl"


class SmithsonianError(RuntimeError):
    """Smithsonian access failed without exposing credential material."""


@dataclass(frozen=True)
class ValidationReceipt:
    provider: str = "smithsonian"
    endpoint: str = "stats"


class SmithsonianAccess:
    """Make bounded requests to the Smithsonian Open Access API."""

    STATS_ENDPOINT = "https://api.si.edu/openaccess/api/v1.0/stats"
    SEARCH_ENDPOINT = "https://api.si.edu/openaccess/api/v1.0/search"
    MAX_RESPONSE_BYTES = 1_000_000

    def __init__(self, credentials: CredentialStore, audit_path=DEFAULT_AUDIT_PATH, opener=urlopen):
        self.credentials = credentials
        self.audit_path = Path(audit_path)
        self._opener = opener

    def validate(self, timeout: float = 15.0) -> ValidationReceipt:
        document = self._get_json(
            self.STATS_ENDPOINT, {}, timeout, "smithsonian_validation_failed"
        )
        if not isinstance(document.get("response"), dict):
            self._audit("smithsonian_validation_failed", reason="unexpected_schema")
            raise SmithsonianError("The Smithsonian returned an unexpected validation response.")
        self._audit("smithsonian_validation_succeeded", endpoint="stats")
        return ValidationReceipt()

    def search(self, query: str, rows: int = 5, timeout: float = 20.0) -> dict:
        """Return one bounded Smithsonian search response without persisting it."""
        query = query.strip()
        if not query or len(query) > 200:
            raise SmithsonianError("The Smithsonian search query is invalid.")
        if not 1 <= rows <= 5:
            raise SmithsonianError("The Smithsonian search result limit is invalid.")
        document = self._get_json(
            self.SEARCH_ENDPOINT,
            {
                "q": query,
                "start": 0,
                "rows": rows,
                "sort": "relevancy",
                "type": "all",
                "row_group": "objects",
            },
            timeout,
            "smithsonian_request_failed",
        )
        response = document.get("response")
        if not isinstance(response, dict) or not isinstance(response.get("rows"), list):
            raise SmithsonianError("The Smithsonian returned an unexpected search response.")
        return response

    def _get_json(
        self,
        endpoint: str,
        parameters: dict,
        timeout: float,
        failure_event: str,
    ) -> dict:
        api_key = self.credentials.load()
        url = f"{endpoint}?{urlencode({**parameters, 'api_key': api_key})}"
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "Modesty-Library-Gateway/0.12",
            },
        )
        try:
            with self._opener(request, timeout=timeout) as response:
                payload = response.read(self.MAX_RESPONSE_BYTES + 1)
        except HTTPError as error:
            self._audit(failure_event, reason="http_error", status=error.code)
            raise SmithsonianError(
                "The Smithsonian rejected the request. Check the stored API key."
            ) from None
        except (URLError, TimeoutError, OSError) as error:
            self._audit(failure_event, reason="network_error")
            raise SmithsonianError(
                "The Smithsonian request could not reach the service safely."
            ) from None
        if len(payload) > self.MAX_RESPONSE_BYTES:
            self._audit(failure_event, reason="response_too_large")
            raise SmithsonianError("The Smithsonian response was unexpectedly large.")
        try:
            document = json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            self._audit(failure_event, reason="invalid_json")
            raise SmithsonianError("The Smithsonian returned an invalid response.") from error
        if not isinstance(document, dict):
            raise SmithsonianError("The Smithsonian returned an unexpected response.")
        return document

    def _audit(self, event: str, **details):
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event": event,
            "provider": "smithsonian",
            **details,
        }
        with self.audit_path.open("a", encoding="utf-8", newline="\n") as audit:
            audit.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Manage Modesty's Smithsonian API access.")
    parser.add_argument("action", choices=("store", "status", "validate", "remove"))
    args = parser.parse_args(argv)
    store = CredentialStore(DEFAULT_KEY_PATH)
    try:
        if args.action == "store":
            store.store(getpass("Smithsonian API key (input hidden): "))
            print("Smithsonian API key encrypted for this Windows user and stored locally.")
        elif args.action == "status":
            state = "stored locally" if store.exists else "not stored"
            print(f"Smithsonian API key: {state}.")
        elif args.action == "remove":
            removed = store.remove()
            print("Stored Smithsonian API key removed." if removed else "No Smithsonian API key was stored.")
        else:
            SmithsonianAccess(store).validate()
            print("Smithsonian authentication validated. No expedition material was retrieved or filed.")
    except (CredentialError, SmithsonianError) as error:
        print(f"Validation stopped safely: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
