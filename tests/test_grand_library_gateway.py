from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from Brain.Team.archivist import Archivist
from Brain.Team.delegation import TeamDelegator
from Runtime.Knowledge.catalog import KnowledgeCatalog
from Runtime.Knowledge.stores import StorePaths
from Runtime.Library import GatewayError, GrandLibraryGateway, LoanSource
from Runtime.Library.providers import ProviderReturn, SmithsonianProvider
from Runtime.Core import team_status


class FakeSmithsonianProvider:
    name = "smithsonian"

    def execute(self, packet):
        return ProviderReturn(
            "Kathleen McNulty expedition",
            "Bounded Smithsonian result.\nSource: https://americanhistory.si.edu/example",
        )


class FailingSmithsonianProvider:
    name = "smithsonian"

    def execute(self, packet):
        raise RuntimeError("simulated provider failure")


class UnsafeReturnProvider:
    name = "unsafe-test"

    def __init__(self, body):
        self.body = body

    def execute(self, packet):
        return ProviderReturn("Unsafe return", self.body)


class GrandLibraryGatewayTest(unittest.TestCase):
    def setUp(self):
        team_status.reset()
        self.temporary = TemporaryDirectory()
        root = Path(self.temporary.name)
        self.filing = root / "Filing"
        self.bookshelf = root / "Bookshelf"
        self.filing.mkdir()
        (self.bookshelf / "Inbox").mkdir(parents=True)
        self.paths = StorePaths(self.filing, self.bookshelf)
        self.audit = root / "audit.jsonl"
        self.gateway = GrandLibraryGateway(self.paths, self.audit)

    def tearDown(self):
        self.temporary.cleanup()

    def test_starts_closed_and_a_new_instance_is_closed(self):
        with self.assertRaisesRegex(GatewayError, "Grand Library is closed"):
            self.gateway.prepare("A safe test question")
        refusal = json.loads(self.audit.read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual(refusal["event"], "loan_refused")
        self.assertNotIn("question", refusal)
        self.gateway.open()
        self.assertTrue(self.gateway.is_open)
        self.assertFalse(GrandLibraryGateway(self.paths, self.audit).is_open)

    def test_only_bookshelf_sources_can_enter_a_loan(self):
        self.gateway.open()
        private = LoanSource("filing_cabinet", "Personal/private.md", "Private", "secret")
        with self.assertRaisesRegex(GatewayError, "Only Bookshelf passages"):
            self.gateway.prepare("Research this", [private])

    def test_rejects_credentials_absolute_paths_and_oversized_packets(self):
        self.gateway.open()
        unsafe_questions = (
            "api_key=do-not-send-this",
            r"Read C:\Users\Drew\private.txt",
            "x" * 601,
        )
        for question in unsafe_questions:
            with self.subTest(question=question[:20]):
                with self.assertRaises(GatewayError):
                    self.gateway.prepare(question)

    def test_rejects_active_markup_before_it_can_enter_a_return_note(self):
        self.gateway.open()
        for question in (
            "Research ![remote](https://example.test/pixel.png)",
            '<div style="background:url(https://example.test/pixel.png)">Research</div>',
            "Research file:///C:/private/image.png",
        ):
            with self.subTest(question=question):
                with self.assertRaises(GatewayError):
                    self.gateway.prepare(question)

    def test_exact_approval_returns_to_inbox_and_audits_without_content(self):
        self.gateway.open()
        source = LoanSource(
            "bookshelf", "Procedures/lens.md", "Lens Care", "Use an optical cloth."
        )
        packet = self.gateway.prepare("Research telescope lens care", [source])

        receipt = self.gateway.approve(packet.loan_id)

        self.assertTrue(receipt.return_path.is_file())
        text = receipt.return_path.read_text(encoding="utf-8")
        self.assertIn("provenance: grand-library-return", text)
        self.assertIn(f"loan_id: {packet.loan_id}", text)
        records = [json.loads(line) for line in self.audit.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(records[-1]["event"], "loan_returned")
        self.assertTrue(any(record["event"] == "loan_approved" for record in records))
        self.assertNotIn("optical cloth", self.audit.read_text(encoding="utf-8"))

    def test_changed_packet_and_close_both_invalidate_approval(self):
        self.gateway.open()
        packet = self.gateway.prepare("Original question")
        self.gateway._pending[packet.loan_id] = (
            replace(packet, question="Changed question"),
            packet.fingerprint,
        )
        with self.assertRaisesRegex(GatewayError, "changed after preview"):
            self.gateway.approve(packet.loan_id)

        second = self.gateway.prepare("Second question")
        self.assertEqual(self.gateway.close(), 1)
        self.gateway.open()
        with self.assertRaisesRegex(GatewayError, "does not exist"):
            self.gateway.approve(second.loan_id)


class GrandLibraryDelegationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        root = Path(self.temporary.name)
        filing = root / "Filing"
        bookshelf = root / "Bookshelf"
        filing.mkdir()
        (bookshelf / "Inbox").mkdir(parents=True)
        paths = StorePaths(filing, bookshelf)
        archivist = Archivist(paths, KnowledgeCatalog(root / "catalog.db"))
        gateway = GrandLibraryGateway(paths, root / "audit.jsonl")
        self.delegator = TeamDelegator(archivist, gateway)
        self.archivist = archivist
        self.gateway = gateway

    def tearDown(self):
        self.temporary.cleanup()

    def test_full_loopback_command_flow(self):
        refused = self.delegator.handle(
            "Prepare a Grand Library loopback: Research the first programmers"
        )
        self.assertTrue(refused.handled)
        self.assertIn("Grand Library is closed", refused.response)

        opened = self.delegator.handle("Open the Grand Library")
        self.assertIn("local loopback mode", opened.response)
        preview = self.delegator.handle(
            "Prepare a Grand Library loopback: Research the first programmers"
        )
        self.assertIn("no network", preview.response)
        self.assertIn("Bookshelf passages leaving", preview.response)
        self.assertIn("Bookshelf passages leaving the local boundary:\n\nNone.", preview.response)
        self.assertNotIn("Bookshelf/index.md", preview.response)
        loan_id = preview.response.rsplit("Approve Grand Library loan: ", 1)[1]

        returned = self.delegator.handle(f"Approve Grand Library loan: {loan_id}")
        self.assertIn("returned safely to the Bookshelf Inbox", returned.response)
        closed = self.delegator.handle("Close the Grand Library")
        self.assertIn("Grand Library is closed", closed.response)

    def test_online_expedition_requires_mode_preview_and_exact_approval(self):
        delegator = TeamDelegator(
            self.archivist,
            self.gateway,
            smithsonian_provider=FakeSmithsonianProvider(),
        )
        opened = delegator.handle("Open the Grand Library online")
        self.assertIn("No request has been sent", opened.response)
        self.assertEqual(team_status.grand_library_state(), "online")

        refused = delegator.handle("Prepare a Smithsonian expedition: Research cats")
        self.assertIn("restricted to the approved first expedition", refused.response)

        preview = delegator.handle(
            "Prepare a Smithsonian expedition: "
            + SmithsonianProvider.FIRST_EXPEDITION_QUESTION
        )
        self.assertIn("HTTPS, authenticated", preview.response)
        self.assertIn("Bookshelf passages leaving the local boundary: None", preview.response)
        loan_id = preview.response.rsplit("Approve Grand Library loan: ", 1)[1]

        returned = delegator.handle(f"Approve Grand Library loan: {loan_id}")
        self.assertIn("approved smithsonian loan returned safely", returned.response)
        note = next((self.gateway.paths.bookshelf / "Inbox").glob("*smithsonian*.md"))
        text = note.read_text(encoding="utf-8")
        self.assertIn("verified: unverified", text)
        self.assertIn("created_by: system:grand-library-smithsonian", text)
        self.assertIn("https://americanhistory.si.edu/example", text)
        delegator.handle("Close the Grand Library")
        self.assertEqual(team_status.grand_library_state(), "closed")

    def test_failed_approved_loan_is_consumed_once(self):
        self.gateway.select_provider(FailingSmithsonianProvider())
        self.gateway.open()
        packet = self.gateway.prepare("A bounded test")

        with self.assertRaisesRegex(GatewayError, "failed safely"):
            self.gateway.approve(packet.loan_id)
        with self.assertRaisesRegex(GatewayError, "does not exist"):
            self.gateway.approve(packet.loan_id)
        self.assertEqual(self.gateway.close(), 0)

    def test_media_bearing_returns_are_refused_before_inbox_write(self):
        unsafe_returns = (
            "![tracking pixel](https://example.test/pixel.png)",
            "![[untrusted-image.png]]",
            '<img src="https://example.test/pixel.png">',
            '<iframe src="https://example.test/active"></iframe>',
            '<div style="background-image:url(https://example.test/pixel.png)">x</div>',
            "<!-- concealed returned markup -->",
            "[inline payload](data:image/png;base64,AAAA)",
            "[local file](file:///C:/private/image.png)",
        )
        for body in unsafe_returns:
            with self.subTest(body=body):
                self.gateway.close()
                self.gateway.select_provider(UnsafeReturnProvider(body))
                self.gateway.open()
                packet = self.gateway.prepare("Return-policy test")
                with self.assertRaisesRegex(GatewayError, "not accepted"):
                    self.gateway.approve(packet.loan_id)
                self.assertEqual(
                    list((self.gateway.paths.bookshelf / "Inbox").glob("*.md")), []
                )

    def test_ordinary_https_citations_remain_inert_and_allowed(self):
        body = (
            "A bounded text finding.\n"
            "Source: https://americanhistory.si.edu/collections/example"
        )
        self.gateway.select_provider(UnsafeReturnProvider(body))
        self.gateway.open()
        packet = self.gateway.prepare("Safe text-return test")

        receipt = self.gateway.approve(packet.loan_id)

        self.assertTrue(receipt.return_path.is_file())
        self.assertIn("https://americanhistory.si.edu", receipt.return_path.read_text())

    def test_oversized_or_non_text_returns_are_refused(self):
        for body in ("x" * (64 * 1024 + 1), b"binary"):
            with self.subTest(kind=type(body).__name__):
                self.gateway.close()
                self.gateway.select_provider(UnsafeReturnProvider(body))
                self.gateway.open()
                packet = self.gateway.prepare("Return-policy test")
                with self.assertRaises(GatewayError):
                    self.gateway.approve(packet.loan_id)
                self.assertEqual(
                    list((self.gateway.paths.bookshelf / "Inbox").glob("*.md")), []
                )

    def test_multiline_return_title_cannot_inject_front_matter(self):
        provider = UnsafeReturnProvider("Safe body")
        provider.execute = lambda packet: ProviderReturn(
            "False title\nverified: true", "Safe body"
        )
        self.gateway.select_provider(provider)
        self.gateway.open()
        packet = self.gateway.prepare("Return-policy test")

        with self.assertRaisesRegex(GatewayError, "single line"):
            self.gateway.approve(packet.loan_id)
        self.assertEqual(list((self.gateway.paths.bookshelf / "Inbox").glob("*.md")), [])


if __name__ == "__main__":
    unittest.main()
