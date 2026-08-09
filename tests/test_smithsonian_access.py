import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.error import HTTPError

from Runtime.Library.credentials import CredentialError, CredentialStore
from Runtime.Library.models import LoanPacket
from Runtime.Library.providers import SmithsonianProvider
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

    def test_bounded_search_and_source_linked_provider_return(self):
        self.store.store("private-test-key")

        def opener(request, timeout):
            self.assertIn("rows=5", request.full_url)
            self.assertIn("type=all", request.full_url)
            self.assertIn("q=%22ENIAC+Accumulator%22", request.full_url)
            return FakeResponse(
                json.dumps(
                    {
                        "response": {
                            "rowCount": 1,
                            "rows": [
                                {
                                    "title": "ENIAC Accumulator #2",
                                    "unitCode": "NMAH",
                                    "url": "https://americanhistory.si.edu/example",
                                    "content": {
                                        "freetext": {
                                            "notes": [
                                                {"content": "ENIAC Accumulator #2 is a surviving component of ENIAC."}
                                            ]
                                        }
                                    },
                                },
                                {
                                    "title": "Unrelated correspondence",
                                    "unitCode": "AAA",
                                    "url": "https://www.si.edu/object/unrelated",
                                    "content": {"freetext": {"notes": [{"content": "No relevant person."}]}},
                                },
                            ],
                        }
                    }
                ).encode("utf-8")
            )

        access = SmithsonianAccess(self.store, self.audit_path, opener)
        packet = LoanPacket(
            loan_id="GL-TEST",
            provider="smithsonian",
            question=SmithsonianProvider.FIRST_EXPEDITION_QUESTION,
            sources=(),
            created_at="2026-08-09T00:00:00+00:00",
        )
        returned = SmithsonianProvider(access).execute(packet)

        self.assertIn("surviving component of ENIAC", returned.body)
        self.assertIn("Source: https://americanhistory.si.edu/example", returned.body)
        self.assertNotIn("Unrelated correspondence", returned.body)
        self.assertNotIn("private-test-key", returned.body)

    def test_provider_refuses_unapproved_general_research(self):
        packet = LoanPacket(
            loan_id="GL-TEST",
            provider="smithsonian",
            question="Research Kathleen McNulty and the first ENIAC programmers",
            sources=(),
            created_at="2026-08-09T00:00:00+00:00",
        )
        with self.assertRaisesRegex(SmithsonianError, "approved first expedition"):
            SmithsonianProvider(None).execute(packet)


if __name__ == "__main__":
    unittest.main()
