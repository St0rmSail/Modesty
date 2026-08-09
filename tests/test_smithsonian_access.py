import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.error import HTTPError

from Runtime.Library.credentials import CredentialError, CredentialStore
from Runtime.Library.smithsonian import SmithsonianAccess, SmithsonianError


class FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, _limit):
        return self.payload


class SmithsonianAccessTest(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        root = Path(self.temporary.name)
        self.key_path = root / "Secrets" / "smithsonian.dpapi"
        self.audit_path = root / "audit.jsonl"
        self.store = CredentialStore(
            self.key_path,
            protect=lambda value: b"protected:" + value[::-1],
            unprotect=lambda value: value.removeprefix(b"protected:")[::-1],
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_stores_only_protected_material_and_round_trips(self):
        secret = "private-test-key"
        self.store.store(secret)
        self.assertTrue(self.store.exists)
        self.assertNotIn(secret.encode(), self.key_path.read_bytes())
        self.assertEqual(self.store.load(), secret)
        self.assertTrue(self.store.remove())
        self.assertFalse(self.store.exists)

    def test_missing_and_damaged_credentials_fail_closed(self):
        with self.assertRaisesRegex(CredentialError, "No Smithsonian API key"):
            self.store.load()
        self.key_path.parent.mkdir()
        self.key_path.write_text("not a credential", encoding="utf-8")
        with self.assertRaisesRegex(CredentialError, "unknown format"):
            self.store.load()

    def test_validation_uses_https_key_and_audits_no_secret_or_response(self):
        secret = "private-test-key"
        self.store.store(secret)
        observed = {}

        def opener(request, timeout):
            observed["url"] = request.full_url
            observed["timeout"] = timeout
            return FakeResponse(b'{"response":{"message":"authenticated"}}')

        receipt = SmithsonianAccess(self.store, self.audit_path, opener).validate(timeout=3)

        self.assertEqual(receipt.provider, "smithsonian")
        self.assertTrue(observed["url"].startswith("https://api.si.edu/"))
        self.assertIn("api_key=private-test-key", observed["url"])
        record = json.loads(self.audit_path.read_text(encoding="utf-8"))
        self.assertEqual(record["event"], "smithsonian_validation_succeeded")
        self.assertNotIn(secret, self.audit_path.read_text(encoding="utf-8"))
        self.assertNotIn("authenticated", self.audit_path.read_text(encoding="utf-8"))

    def test_http_failure_is_sanitized_and_audited(self):
        self.store.store("private-test-key")

        def opener(request, timeout):
            raise HTTPError(request.full_url, 403, "Forbidden", {}, None)

        with self.assertRaisesRegex(SmithsonianError, "rejected") as raised:
            SmithsonianAccess(self.store, self.audit_path, opener).validate()
        self.assertNotIn("private-test-key", str(raised.exception))
        record = json.loads(self.audit_path.read_text(encoding="utf-8"))
        self.assertEqual(record["status"], 403)


if __name__ == "__main__":
    unittest.main()
