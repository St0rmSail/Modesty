"""Deterministic routing from Modesty to bounded Team duties."""

from dataclasses import dataclass
from pathlib import Path
import re

from Brain.Team.archivist import Archivist
from Brain.Team.librarian import Librarian, LibrarianError
from Runtime.Knowledge.catalog import KnowledgeCatalog
from Runtime.Knowledge.stores import KnowledgeStores
from Runtime.Library import GatewayError, GrandLibraryGateway
from Runtime.Library.credentials import CredentialStore
from Runtime.Library.providers import LoopbackProvider, SmithsonianProvider
from Runtime.Library.smithsonian import DEFAULT_KEY_PATH, SmithsonianAccess
from Runtime.Reading import ReadingCollection
from Runtime.Research.pending_reports import PendingReportStore
from Runtime.Core import team_status
from Runtime.Core.command_help import command_help
from Runtime.Time import ReminderStore, handle_schedule_command, handle_time_command


@dataclass(frozen=True)
class DelegationResult:
    handled: bool
    response: str = ""
    action: str | None = None


class TeamDelegator:
    """Recognise explicit duties without granting the language model tools."""

    FILE_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?archivist\s+to\s+file\s+"
        r"(?P<destination>privately|in\s+(?:the\s+)?filing\s+cabinet|"
        r"on\s+(?:the\s+)?bookshelf|in\s+(?:the\s+)?bookshelf)\s*:\s*(?P<content>.+)$",
        re.IGNORECASE | re.DOTALL,
    )
    AMBIGUOUS_FILE_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?archivist\s+to\s+file\b",
        re.IGNORECASE,
    )
    RETRIEVE_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?archivist\s+to\s+"
        r"(?:retrieve|find|look\s+for)\s*:\s*(?P<query>.+)$",
        re.IGNORECASE | re.DOTALL,
    )
    REVIEW_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?archivist\s+to\s+review\s*:\s*(?P<query>.+)$",
        re.IGNORECASE | re.DOTALL,
    )
    WORKBENCH_APPROVAL_PATTERN = re.compile(
        r"^approve\s+(?:the\s+)?archivist\s+to\s+move\s+to\s+workbench\s*:\s*(?P<filename>[^\r\n]+)$",
        re.IGNORECASE,
    )
    CLASSIFY_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?archivist\s+to\s+classify\s*:\s*(?P<query>.+)$",
        re.IGNORECASE | re.DOTALL,
    )
    COLLECTION_APPROVAL_PATTERN = re.compile(
        r"^approve\s+(?:the\s+)?archivist\s+to\s+file\s+in\s+"
        r"(?P<collection>projects|research|reference|procedures|media)\s*:\s*(?P<filename>[^\r\n]+)$",
        re.IGNORECASE,
    )
    LIBRARY_REINDEX_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?library\s+to\s+re[ -]?index\s*$",
        re.IGNORECASE,
    )
    LIBRARY_ASK_PATTERN = re.compile(
        r"^(?:please\s+)?ask\s+(?:the\s+)?library"
        r"(?:\s+(?:about|for))?\s*:?\s*(?P<query>.+)$",
        re.IGNORECASE | re.DOTALL,
    )
    GRAND_LIBRARY_OPEN_PATTERN = re.compile(
        r"^(?:please\s+)?open\s+(?:the\s+)?grand\s+lib(?:rary|arary)\s*$",
        re.IGNORECASE,
    )
    GRAND_LIBRARY_ONLINE_OPEN_PATTERN = re.compile(
        r"^(?:please\s+)?open\s+(?:the\s+)?grand\s+lib(?:rary|arary)\s+online\s*$",
        re.IGNORECASE,
    )
    GRAND_LIBRARY_CLOSE_PATTERN = re.compile(
        r"^(?:please\s+)?close\s+(?:the\s+)?grand\s+lib(?:rary|arary)\s*$",
        re.IGNORECASE,
    )
    LOOPBACK_PREPARE_PATTERN = re.compile(
        r"^(?:please\s+)?prepare\s+(?:a\s+)?grand\s+library\s+"
        r"loopback(?:\s+loan)?\s*:\s*(?P<question>.+)$",
        re.IGNORECASE | re.DOTALL,
    )
    SMITHSONIAN_PREPARE_PATTERN = re.compile(
        r"^(?:please\s+)?prepare\s+(?:a\s+)?smithsonian\s+expedition\s*:\s*"
        r"(?P<question>.+)$",
        re.IGNORECASE | re.DOTALL,
    )
    GRAND_LIBRARY_APPROVAL_PATTERN = re.compile(
        r"^approve\s+grand\s+library\s+loan\s*:\s*(?P<loan_id>GL-[A-Z0-9-]+)\s*$",
        re.IGNORECASE,
    )
    RESEARCHER_SCRIBBLEHUB_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?researcher(?:\s+to)?\s*:?\s*"
        r"what\s+are\s+the\s+latest\s+offerings\s+in\s+the\s+harem\s+category\??\s*$",
        re.IGNORECASE,
    )
    LIBRARIAN_INVENTORY_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?librarian\s+to\s+"
        r"(?:inventory|catalogue|catalog)\s+(?:the\s+)?stacks\s*$",
        re.IGNORECASE,
    )
    LIBRARIAN_EDITION_CATALOGUE_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?librarian\s+to\s+"
        r"(?:identify|catalogue|catalog)\s+(?:the\s+)?(?:works\s+and\s+editions|editions)\s*$",
        re.IGNORECASE,
    )
    LIBRARIAN_EDITION_REVIEW_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?librarian\s+to\s+"
        r"review\s+(?:the\s+)?edition\s+groups\s*$",
        re.IGNORECASE,
    )
    LIBRARIAN_DUPLICATE_PREPARE_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?librarian\s+to\s+prepare\s+"
        r"exact\s+duplicate\s+resolution\s*:\s*(?P<hash>[A-F0-9]{12,64})\s+"
        r"keep\s*:\s*(?P<path>[^\r\n]+)$",
        re.IGNORECASE,
    )
    LIBRARIAN_DUPLICATE_APPROVAL_PATTERN = re.compile(
        r"^approve\s+(?:the\s+)?librarian\s+duplicate\s+resolution\s*:\s*"
        r"(?P<resolution_id>DR-[A-F0-9]{8})\s*$",
        re.IGNORECASE,
    )
    LIBRARIAN_SHELVING_BATCH_PREPARE_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?librarian\s+to\s+prepare\s+"
        r"(?:a\s+)?bounded\s+intake\s+shelving\s+batch\s*$",
        re.IGNORECASE,
    )
    LIBRARIAN_SHELVING_BATCH_APPROVAL_PATTERN = re.compile(
        r"^approve\s+(?:the\s+)?librarian\s+shelving\s+batch\s*:\s*"
        r"(?P<batch_id>LB-[A-F0-9]{8})\s*$",
        re.IGNORECASE,
    )
    LIBRARIAN_METADATA_LIST_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?librarian\s+to\s+review\s+incomplete\s+metadata\s*$",
        re.IGNORECASE,
    )
    LIBRARIAN_REPAIR_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?librarian\s+to\s+"
        r"repair\s*:\s*(?P<filename>[^\r\n]+)$",
        re.IGNORECASE,
    )
    LIBRARIAN_INSPECT_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?librarian\s+to\s+"
        r"(?:inspect|examine|catalogue\s+and\s+read|catalog\s+and\s+read)\s*:\s*(?P<path>[^\r\n]+)$",
        re.IGNORECASE,
    )
    LIBRARIAN_FIND_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?librarian\s+to\s+"
        r"(?:find|search\s+the\s+stacks\s+for)\s*:\s*(?P<query>[^\r\n]+)$",
        re.IGNORECASE,
    )
    LIBRARIAN_SHELVE_PATTERN = re.compile(
        r"^approve\s+(?:the\s+)?librarian\s+shelving\s*:\s*(?P<shelving_id>LS-[A-F0-9]{8})\s*$",
        re.IGNORECASE,
    )
    LIBRARIAN_OPEN_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?librarian\s+to\s+open\s*:\s*"
        r"(?P<reference>.+?)(?:\s+at\s+(?P<chapter>(?:chapter\s+)?(?:\d+|[a-z]+)|prologue|epilogue))?\s*$",
        re.IGNORECASE,
    )
    LIBRARIAN_RESUME_PATTERN = re.compile(
        r"^(?:please\s+)?(?:ask\s+)?(?:the\s+)?librarian\s+to\s+resume\s*:\s*(?P<reference>[^\r\n]+)$",
        re.IGNORECASE,
    )
    LIBRARIAN_CONTINUE_PATTERN = re.compile(
        r"^(?:please\s+)?continue\s+reading\s*:\s*(?P<session_id>RP-[A-F0-9]{8})\s*$",
        re.IGNORECASE,
    )
    LIBRARIAN_MARK_PATTERN = re.compile(
        r"^(?:please\s+)?mark\s+my\s+place\s*:\s*(?P<session_id>RP-[A-F0-9]{8})\s*$",
        re.IGNORECASE,
    )
    HELP_PATTERN = re.compile(
        r"^(?:please\s+)?(?:help|show\s+(?:me\s+)?(?:the\s+)?commands|"
        r"what\s+commands\s+can\s+i\s+use|how\s+do\s+i\s+use\s+modesty)\??\s*$",
        re.IGNORECASE,
    )
    TOPIC_HELP_PATTERN = re.compile(
        r"^(?:please\s+)?(?:help(?:\s+me)?\s+with|show\s+(?:me\s+)?(?:the\s+)?)\s+"
        r"(?:the\s+)?(?P<topic>grand\s+library|researcher|librarian|briefings?|archivist|library|chat|conversation|time(?:\s+zones?)?|schedule|reminders?)"
        r"(?:\s+(?:commands?|please|again|help|open))?\??\s*$",
        re.IGNORECASE,
    )
    NATURAL_HELP_PATTERN = re.compile(
        r"^(?:please\s+)?(?:remind\s+me\s+(?:how\s+to|about)|"
        r"what(?:'s|\s+is)\s+the\s+command\s+for)\s+(?:open\s+|use\s+)?"
        r"(?:the\s+)?(?P<topic>grand\s+library|researcher|librarian|briefings?|archivist|library|chat|conversation|time(?:\s+zones?)?|schedule|reminders?)"
        r"(?:\s+(?:please|again))?\??\s*$",
        re.IGNORECASE,
    )
    HELP_FOLLOWUP_PATTERN = re.compile(
        r"^(?:the\s+)?(?:(?:one|section|commands?)\s+(?:about|for)\s+)?"
        r"(?P<topic>grand\s+library|researcher|librarian|briefings?|archivist|library|chat|conversation|time(?:\s+zones?)?|schedule|reminders?)"
        r"(?:\s+(?:please|thanks|thank\s+you|help))?\??\s*$",
        re.IGNORECASE,
    )
    GRACEFUL_EXIT_PATTERN = re.compile(
        r"^(?:bye|goodbye)(?:,?\s+modesty)?[.!]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_DUPLICATE_REVIEW_PATTERN = re.compile(
        r"^(?:please\s+)?(?:show|list|let\s+me\s+see)\s+(?:me\s+)?(?:the\s+)?(?:book\s+)?duplicates[.!]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_CATALOGUE_PATTERN = re.compile(
        r"^(?:please\s+)?(?:catalogue|catalog|identify)\s+(?:the\s+)?(?:books|stacks|collection)[.!]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_KEEP_COPY_PATTERN = re.compile(
        r"^(?:please\s+)?keep\s+(?P<choice>.+?\bcopy(?:\s+of\s+.+)?)?[.!]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_APPROVE_PATTERN = re.compile(
        r"^(?:yes|yes,?\s+(?:please|do\s+that)|do\s+that|go\s+ahead)[.!]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_SHELVING_BATCH_PATTERN = re.compile(
        r"^(?:please\s+)?(?:show\s+me\s+what\s+(?:can|is\s+ready\s+to)\s+be\s+shelved|"
        r"prepare\s+(?:the\s+)?next\s+shelf\s+batch|what\s+can\s+(?:the\s+)?librarian\s+shelve)[.!?]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_METADATA_LIST_PATTERN = re.compile(
        r"^(?:please\s+)?(?:show|list)\s+(?:me\s+)?(?:the\s+)?books?\s+(?:that\s+)?(?:need|needing)\s+metadata[.!?]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_METADATA_REVIEW_PATTERN = re.compile(
        r"^(?:please\s+)?review(?:\s+metadata\s+for)?\s+(?P<choice>.+?)[.!]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_METADATA_FIELD_PATTERN = re.compile(
        r"^(?:the\s+)?(?P<field>title|author)\s+is\s+(?P<value>.+?)[.!]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_METADATA_SAVE_PATTERN = re.compile(r"^(?:please\s+)?save\s+that[.!]?\s*$", re.IGNORECASE)
    NATURAL_METADATA_LEAVE_PATTERN = re.compile(r"^(?:please\s+)?leave\s+it[.!]?\s*$", re.IGNORECASE)
    NATURAL_SHELVE_THOSE_PATTERN = re.compile(
        r"^(?:please\s+)?(?:shelve\s+those|put\s+those\s+away)[.!]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_LEAVE_SHELF_ITEM_PATTERN = re.compile(
        r"^(?:please\s+)?leave\s+(?P<choice>.+?)\s+out[.!]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_OPEN_CHAPTER_PATTERN = re.compile(
        r"^(?:please\s+)?(?:open|read)\s+(?P<reference>.+?)\s+at\s+(?:chapter\s+)?"
        r"(?P<chapter>\d+|[a-z]+)[.!]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_RESUME_PATTERN = re.compile(
        r"^(?:please\s+)?resume\s+(?P<reference>.+?)[.!]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_CONTINUE_PATTERN = re.compile(
        r"^(?:please\s+)?(?:continue|keep\s+reading|read\s+on)[.!]?\s*$",
        re.IGNORECASE,
    )
    NATURAL_MARK_PATTERN = re.compile(
        r"^(?:please\s+)?(?:save|mark)\s+my\s+place[.!]?\s*$",
        re.IGNORECASE,
    )

    def __init__(
        self,
        archivist: Archivist | None = None,
        gateway: GrandLibraryGateway | None = None,
        smithsonian_provider=None,
        librarian: Librarian | None = None,
        pending_reports: PendingReportStore | None = None,
    ):
        if archivist is None:
            paths = KnowledgeStores().initialize()
            archivist = Archivist(paths, KnowledgeCatalog())
        self.archivist = archivist
        self.gateway = gateway or GrandLibraryGateway(archivist.paths)
        self.smithsonian_provider = smithsonian_provider or SmithsonianProvider(
            SmithsonianAccess(CredentialStore(DEFAULT_KEY_PATH))
        )
        self.librarian = librarian
        self.pending_reports = pending_reports or PendingReportStore()
        self.reminders = ReminderStore()
        self._help_active = False
        self._last_edition_groups = ()
        self._pending_duplicate_resolution_id = None
        self._pending_shelving_batch_id = None
        self._last_metadata_review_items = ()
        self._pending_metadata_review_id = None
        self._last_reading_session_id = None

    def _natural_librarian_command(self, message: str) -> str | DelegationResult | None:
        """Translate a small contextual vocabulary into existing audited operations."""

        text = message.strip()
        if self.NATURAL_DUPLICATE_REVIEW_PATTERN.match(text):
            return "Ask the Librarian to review edition groups"
        if self.NATURAL_CATALOGUE_PATTERN.match(text):
            return "Ask the Librarian to identify works and editions"
        if self.NATURAL_SHELVING_BATCH_PATTERN.match(text):
            return "Ask the Librarian to prepare a bounded Intake shelving batch"
        if self.NATURAL_METADATA_LIST_PATTERN.match(text):
            return "Ask the Librarian to review incomplete metadata"
        metadata_review = self.NATURAL_METADATA_REVIEW_PATTERN.match(text)
        if metadata_review and tuple(getattr(self, "_last_metadata_review_items", ()) or ()):
            choice = metadata_review.group("choice")
            tokens = self._choice_tokens(choice)
            items = tuple(getattr(self, "_last_metadata_review_items", ()) or ())
            matches = [
                item for item in items
                if tokens and tokens.issubset(self._choice_tokens(
                    f"{item.source_relative_path} {item.catalogued_title} {item.filename_title_suggestion}"
                ))
            ]
            if len(matches) != 1:
                if not matches:
                    return DelegationResult(True, "That description does not identify one of the displayed metadata items.")
                choices = "\n".join(f"- The Stacks/{item.source_relative_path}" for item in matches)
                return DelegationResult(True, "That description matches more than one displayed item:\n" + choices)
            try:
                draft = self.librarian.begin_metadata_review(matches[0].source_relative_path)
            except (LibrarianError, RuntimeError) as error:
                return DelegationResult(True, str(error))
            self._pending_metadata_review_id = draft.review_id
            return DelegationResult(True, self.librarian.metadata_review_draft_response(draft))
        metadata_field = self.NATURAL_METADATA_FIELD_PATTERN.match(text)
        if metadata_field:
            review_id = getattr(self, "_pending_metadata_review_id", None)
            if not review_id:
                return DelegationResult(True, "There is no active metadata review. Show me books needing metadata first.")
            try:
                draft = self.librarian.update_metadata_review(
                    review_id, metadata_field.group("field"), metadata_field.group("value")
                )
            except (LibrarianError, RuntimeError) as error:
                return DelegationResult(True, str(error))
            return DelegationResult(True, self.librarian.metadata_review_draft_response(draft))
        if self.NATURAL_METADATA_SAVE_PATTERN.match(text):
            review_id = getattr(self, "_pending_metadata_review_id", None)
            if not review_id:
                return DelegationResult(True, "There is no active metadata review to save.")
            try:
                draft = self.librarian.confirm_metadata_review(review_id)
            except (LibrarianError, RuntimeError) as error:
                return DelegationResult(True, str(error))
            self._pending_metadata_review_id = None
            return DelegationResult(
                True,
                f"Saved. Drew confirmed {draft.draft_title} — {draft.draft_author} for the unchanged exact source. "
                "The catalogue was updated; the book itself was not rewritten. It may now appear in an ordinary shelving preview.",
            )
        if self.NATURAL_METADATA_LEAVE_PATTERN.match(text):
            review_id = getattr(self, "_pending_metadata_review_id", None)
            if not review_id:
                return DelegationResult(True, "There is no active metadata review to leave.")
            try:
                draft = self.librarian.cancel_metadata_review(review_id)
            except (LibrarianError, RuntimeError) as error:
                return DelegationResult(True, str(error))
            self._pending_metadata_review_id = None
            return DelegationResult(True, f"The Librarian left The Stacks/{draft.source_relative_path} unchanged in Intake.")
        leave_item = self.NATURAL_LEAVE_SHELF_ITEM_PATTERN.match(text)
        if leave_item:
            batch_id = getattr(self, "_pending_shelving_batch_id", None)
            if not batch_id:
                return DelegationResult(True, "There is no reviewed Librarian shelving batch to revise.")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                removed, remaining = self.librarian.exclude_from_shelving_batch(
                    batch_id, leave_item.group("choice")
                )
            except (LibrarianError, RuntimeError) as error:
                return DelegationResult(True, str(error))
            ready = "\n".join(
                f"- The Stacks/{item.source_relative_path} -> The Stacks/Originals/{item.proposed_relative_path}"
                for item in remaining
            ) or "- None."
            return DelegationResult(
                True,
                f"The Librarian left {removed.title} out of this batch. It remains in Intake.\n\n"
                f"Updated Ready list ({len(remaining)}):\n{ready}\n\nNothing has moved.",
            )
        shelve_those = self.NATURAL_SHELVE_THOSE_PATTERN.match(text)
        if shelve_those:
            batch_id = getattr(self, "_pending_shelving_batch_id", None)
            if not batch_id:
                return DelegationResult(True, "There is no reviewed Librarian shelving batch waiting for approval.")
            return f"Approve Librarian shelving batch: {batch_id}"
        approval = self.NATURAL_APPROVE_PATTERN.match(text)
        if approval:
            duplicate_id = getattr(self, "_pending_duplicate_resolution_id", None)
            batch_id = getattr(self, "_pending_shelving_batch_id", None)
            if duplicate_id and batch_id:
                return DelegationResult(
                    True,
                    "Two Librarian actions are waiting. Say `shelve those` for the shelving batch, or name the duplicate choice again.",
                )
            if duplicate_id:
                return f"Approve Librarian duplicate resolution: {duplicate_id}"
            if batch_id:
                return f"Approve Librarian shelving batch: {batch_id}"
        mark = self.NATURAL_MARK_PATTERN.match(text)
        if mark:
            session_id = getattr(self, "_last_reading_session_id", None)
            if not session_id:
                return DelegationResult(True, "There is no active Librarian reading passage to mark.")
            return f"Mark my place: {session_id}"
        continuation = self.NATURAL_CONTINUE_PATTERN.match(text)
        if continuation:
            session_id = getattr(self, "_last_reading_session_id", None)
            if not session_id:
                return None
            return f"Continue reading: {session_id}"
        opened = self.NATURAL_OPEN_CHAPTER_PATTERN.match(text)
        if opened:
            return (
                f"Ask the Librarian to open: {opened.group('reference').strip()} "
                f"at Chapter {opened.group('chapter').strip()}"
            )
        resumed = self.NATURAL_RESUME_PATTERN.match(text)
        if resumed:
            return f"Ask the Librarian to resume: {resumed.group('reference').strip()}"
        keep = self.NATURAL_KEEP_COPY_PATTERN.match(text)
        if not keep:
            return None
        groups = tuple(getattr(self, "_last_edition_groups", ()) or ())
        if not groups:
            return DelegationResult(True, "Show me the duplicates first, so the Librarian has a visible reviewed set to choose from.")
        choice = keep.group("choice") or ""
        tokens = self._choice_tokens(choice)
        if not tokens:
            return DelegationResult(True, "Name enough of the displayed copy's folder or title to identify one exact path.")
        candidates = []
        for group in groups:
            for path, _, _ in group.files:
                path_tokens = self._choice_tokens(path)
                if tokens.issubset(path_tokens):
                    candidates.append((group, path))
        if len(candidates) != 1:
            if not candidates:
                return DelegationResult(True, "That description does not identify a displayed duplicate copy. Name its folder and title.")
            paths = "\n".join(f"- The Stacks/{path}" for _, path in candidates[:6])
            return DelegationResult(
                True,
                "That description matches more than one displayed copy. Please distinguish the title or folder:\n" + paths,
            )
        group, path = candidates[0]
        if group.evidence != "Exact SHA-256 duplicate":
            return DelegationResult(
                True,
                "Those copies are not byte-identical. The Librarian will not treat a shared identifier as permission to consolidate them.",
            )
        return f"Ask the Librarian to prepare exact duplicate resolution: {group.identity} keep: {path}"

    @staticmethod
    def _choice_tokens(value: str) -> set[str]:
        stop = {"the", "a", "an", "copy", "file", "of", "in", "from", "keep", "and", "please", "stacks", "intake"}
        return {token for token in re.findall(r"[a-z0-9]+", value.casefold()) if token not in stop}

    def handle(self, message: str) -> DelegationResult:
        natural_help = self.NATURAL_HELP_PATTERN.match(message.strip())
        if natural_help:
            self._help_active = True
            return DelegationResult(True, command_help(natural_help.group("topic")))
        topic_help = self.TOPIC_HELP_PATTERN.match(message.strip())
        if topic_help:
            self._help_active = True
            return DelegationResult(True, command_help(topic_help.group("topic")))
        if self.HELP_PATTERN.match(message.strip()):
            self._help_active = True
            return DelegationResult(True, command_help())
        help_followup = self.HELP_FOLLOWUP_PATTERN.match(message.strip())
        if getattr(self, "_help_active", False) and help_followup:
            return DelegationResult(True, command_help(help_followup.group("topic")))

        natural = self._natural_librarian_command(message)
        if isinstance(natural, DelegationResult):
            return natural
        if natural:
            message = natural

        if self.GRACEFUL_EXIT_PATTERN.match(message.strip()):
            return DelegationResult(True, "Goodbye, Drew.", "close_study")

        time_response = handle_time_command(message)
        if time_response is not None:
            return DelegationResult(True, time_response)

        schedule_response = handle_schedule_command(message, getattr(self, "reminders", None))
        if schedule_response is not None:
            return DelegationResult(True, schedule_response)

        if self.RESEARCHER_SCRIBBLEHUB_PATTERN.match(message.strip()):
            if not self.gateway.is_open or team_status.grand_library_state() != "online":
                return DelegationResult(
                    True,
                    "The Grand Library is closed. Open it online before I send the Researcher to Scribble Hub.",
                )
            team_status.set_member_state("researcher", "working")
            return DelegationResult(
                True,
                "The Researcher is opening the approved Scribble Hub discovery query in a local visible browser. "
                "Nothing has been filed or added to your account.",
                "research_scribblehub_latest_harem",
            )
        if self.LIBRARIAN_EDITION_CATALOGUE_PATTERN.match(message.strip()):
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                report = self.librarian.catalogue_editions()
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "ready")
            return DelegationResult(True, self.librarian.edition_catalogue_response(report))
        if self.LIBRARIAN_EDITION_REVIEW_PATTERN.match(message.strip()):
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                groups = self.librarian.edition_review_groups()
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "ready")
            self._last_edition_groups = groups
            return DelegationResult(True, self.librarian.edition_review_response(groups))
        if self.LIBRARIAN_METADATA_LIST_PATTERN.match(message.strip()):
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                items = self.librarian.metadata_review_items()
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "waiting" if items else "ready")
            self._last_metadata_review_items = items
            self._pending_metadata_review_id = None
            return DelegationResult(True, self.librarian.metadata_review_list_response(items))
        duplicate_prepare = self.LIBRARIAN_DUPLICATE_PREPARE_PATTERN.match(message.strip())
        if duplicate_prepare:
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                proposal = self.librarian.prepare_exact_duplicate_resolution(
                    duplicate_prepare.group("hash"), duplicate_prepare.group("path")
                )
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "waiting")
            self._pending_duplicate_resolution_id = proposal.resolution_id
            return DelegationResult(True, self.librarian.duplicate_resolution_response(proposal))
        duplicate_approval = self.LIBRARIAN_DUPLICATE_APPROVAL_PATTERN.match(message.strip())
        if duplicate_approval:
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                keep, archived = self.librarian.approve_exact_duplicate_resolution(
                    duplicate_approval.group("resolution_id")
                )
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "ready")
            self._pending_duplicate_resolution_id = None
            archived_text = "\n".join(f"- The Stacks/{path}" for path in archived)
            return DelegationResult(
                True,
                f"Approved. The canonical copy remains at The Stacks/{keep}.\n"
                f"The redundant exact copy or copies were retained in Archive:\n{archived_text}\n\n"
                "Nothing was deleted.",
            )
        if self.LIBRARIAN_SHELVING_BATCH_PREPARE_PATTERN.match(message.strip()):
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                proposal = self.librarian.prepare_shelving_batch()
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "waiting" if proposal.ready else "attention")
            self._pending_shelving_batch_id = proposal.batch_id if proposal.ready else None
            return DelegationResult(True, self.librarian.shelving_batch_response(proposal))
        batch_approval = self.LIBRARIAN_SHELVING_BATCH_APPROVAL_PATTERN.match(message.strip())
        if batch_approval:
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                destinations = self.librarian.approve_shelving_batch(batch_approval.group("batch_id"))
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "ready")
            self._pending_shelving_batch_id = None
            moved = "\n".join(f"- The Stacks/{path}" for path in destinations)
            return DelegationResult(
                True,
                f"Approved. The Librarian shelved {len(destinations)} unchanged original(s):\n{moved}\n\n"
                "Every source retained its recorded SHA-256 identity. Held-back items remain in Intake.",
            )
        if self.LIBRARIAN_INVENTORY_PATTERN.match(message.strip()):
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                report = self.librarian.inventory()
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "ready")
            return DelegationResult(
                True,
                "The Librarian completed a read-only catalogue of The Stacks Intake.\n\n"
                f"Files seen: {report.scanned}\n"
                f"Supported reading files: {report.supported}\n"
                f"Unsupported files retained untouched: {report.unsupported}\n"
                f"Items needing attention: {report.attention}\n"
                f"Exact duplicate groups: {report.duplicate_groups}\n"
                f"Stale catalogue entries removed: {report.stale_removed}\n\n"
                "No reading file was renamed, moved, repaired, converted, deleted, or published.",
            )
        inspect_match = self.LIBRARIAN_INSPECT_PATTERN.match(message.strip())
        if inspect_match:
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                inspection = self.librarian.inspect_book(inspect_match.group("path"))
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "waiting")
            return DelegationResult(True, self.librarian.inspection_report(inspection))
        find_match = self.LIBRARIAN_FIND_PATTERN.match(message.strip())
        if find_match:
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                hits = self.librarian.search_reading(find_match.group("query"))
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "ready")
            if not hits:
                return DelegationResult(True, "The Librarian found no matching passage in works she has inspected.")
            passages = "\n\n".join(
                f"{index}. {hit.title} — {hit.author}\n{hit.passage}\n"
                f"Source: The Stacks/{hit.source_relative_path} ({hit.section})"
                for index, hit in enumerate(hits, 1)
            )
            return DelegationResult(True, f"The Librarian found {len(hits)} matching passage(s):\n\n{passages}")
        shelve_match = self.LIBRARIAN_SHELVE_PATTERN.match(message.strip())
        if shelve_match:
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                destination = self.librarian.approve_shelving(shelve_match.group("shelving_id"))
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "ready")
            relative = destination.relative_to(self.librarian.paths.root).as_posix()
            return DelegationResult(
                True,
                f"Approved. The Librarian shelved the unchanged original at The Stacks/{relative}. "
                "Its recorded SHA-256 identity was preserved.",
            )
        open_match = self.LIBRARIAN_OPEN_PATTERN.match(message.strip())
        resume_match = self.LIBRARIAN_RESUME_PATTERN.match(message.strip())
        if open_match or resume_match:
            team_status.set_member_state("librarian", "working")
            match = open_match or resume_match
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                excerpt = self.librarian.open_reading(
                    match.group("reference"),
                    chapter=open_match.group("chapter") if open_match else "",
                    resume=resume_match is not None,
                )
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "waiting")
            self._last_reading_session_id = excerpt.session_id
            return DelegationResult(True, self.librarian.reading_response(excerpt))
        continue_match = self.LIBRARIAN_CONTINUE_PATTERN.match(message.strip())
        if continue_match:
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                excerpt = self.librarian.continue_reading(continue_match.group("session_id"))
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "waiting")
            self._last_reading_session_id = excerpt.session_id
            return DelegationResult(True, self.librarian.reading_response(excerpt))
        mark_match = self.LIBRARIAN_MARK_PATTERN.match(message.strip())
        if mark_match:
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                title, section = self.librarian.mark_reading_position(mark_match.group("session_id"))
            except (LibrarianError, RuntimeError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "ready")
            self._last_reading_session_id = None
            return DelegationResult(
                True,
                f"The Librarian marked your confirmed place in {title}, {section}. "
                "She will resume at the next unread text for this exact edition.",
            )
        repair_match = self.LIBRARIAN_REPAIR_PATTERN.match(message.strip())
        if repair_match:
            team_status.set_member_state("librarian", "working")
            try:
                if self.librarian is None:
                    self.librarian = Librarian(ReadingCollection().initialize())
                proposal = self.librarian.prepare_text_repair(repair_match.group("filename"))
                pending_store = getattr(self, "pending_reports", None) or PendingReportStore()
                self.pending_reports = pending_store
                try:
                    pending = pending_store.create(
                        f"Librarian repair — {proposal.source_relative_path}",
                        self.librarian.repair_briefing(proposal),
                        f"librarian:{proposal.repair_id}",
                    )
                except (OSError, ValueError):
                    self.librarian.resolve_repair(proposal.repair_id, keep=False)
                    raise
            except (LibrarianError, RuntimeError, ValueError) as error:
                team_status.set_member_state("librarian", "attention")
                return DelegationResult(True, str(error))
            team_status.set_member_state("librarian", "waiting")
            return DelegationResult(
                True,
                "The Librarian prepared a provisional repaired copy in The Stacks Workbench. "
                "The original is unchanged. Review the local Briefing, then choose Keep Repair or Toss Repair.",
                f"open_briefing:{pending.report_id}",
            )
        if self.GRAND_LIBRARY_ONLINE_OPEN_PATTERN.match(message.strip()):
            if self.gateway.is_open and self.gateway.provider.name != "smithsonian":
                return DelegationResult(
                    True,
                    "Close the Grand Library before changing from loopback to online mode.",
                )
            if not self.gateway.is_open:
                self.gateway.select_provider(self.smithsonian_provider)
            changed = self.gateway.open()
            team_status.set_grand_library_state("online")
            if changed:
                return DelegationResult(
                    True,
                    "The Grand Library is open for bounded online access. "
                    "No request has been sent; preparation and exact approval are still required.",
                )
            return DelegationResult(
                True, "The Grand Library is already open for bounded online access."
            )

        if self.GRAND_LIBRARY_OPEN_PATTERN.match(message.strip()):
            if self.gateway.is_open and self.gateway.provider.name != "loopback":
                return DelegationResult(
                    True,
                    "Close the Grand Library before changing from online to loopback mode.",
                )
            if not self.gateway.is_open:
                self.gateway.select_provider(LoopbackProvider())
            changed = self.gateway.open()
            team_status.set_grand_library_state("loopback")
            if changed:
                return DelegationResult(
                    True,
                    "The Grand Library is open in local loopback mode. "
                    "The internet remains disconnected; only bounded test loans can run.",
                )
            return DelegationResult(True, "The Grand Library is already open in local loopback mode.")

        if self.GRAND_LIBRARY_CLOSE_PATTERN.match(message.strip()):
            cancelled = self.gateway.close()
            team_status.set_grand_library_state("closed")
            detail = (
                f" {cancelled} pending loan{'s were' if cancelled != 1 else ' was'} cancelled."
                if cancelled else ""
            )
            return DelegationResult(
                True,
                f"The Grand Library is closed. No outbound loan can leave.{detail}",
            )

        approval = self.GRAND_LIBRARY_APPROVAL_PATTERN.match(message.strip())
        if approval:
            try:
                receipt = self.gateway.approve(approval.group("loan_id").upper())
            except GatewayError as error:
                return DelegationResult(True, str(error))
            return DelegationResult(
                True,
                f"The approved {self.gateway.provider.name} loan returned safely to the Bookshelf Inbox: "
                f"{receipt.return_path.name}\nLoan: {receipt.loan_id}",
            )

        smithsonian = self.SMITHSONIAN_PREPARE_PATTERN.match(message.strip())
        if smithsonian:
            if not self.gateway.is_open:
                try:
                    self.gateway.prepare(smithsonian.group("question"), ())
                except GatewayError as error:
                    return DelegationResult(True, str(error))
            if self.gateway.provider.name != "smithsonian":
                return DelegationResult(
                    True,
                    "The Grand Library is not in Smithsonian online mode. Close it, then open it online.",
                )
            question = smithsonian.group("question").strip()
            if question.casefold() != SmithsonianProvider.FIRST_EXPEDITION_QUESTION.casefold():
                return DelegationResult(
                    True,
                    "This provider is restricted to the approved first expedition: "
                    f"{SmithsonianProvider.FIRST_EXPEDITION_QUESTION}",
                )
            try:
                packet = self.gateway.prepare(question, ())
            except GatewayError as error:
                return DelegationResult(True, str(error))
            return DelegationResult(
                True,
                "\n".join(
                    (
                        "Smithsonian expedition preview:",
                        f"\nLoan: {packet.loan_id}",
                        "Provider: Smithsonian Open Access API (HTTPS, authenticated)",
                        f"Question leaving the local boundary: {packet.question}",
                        "Bookshelf passages leaving the local boundary: None.",
                        "Maximum returned records: 5",
                        "Return destination: Bookshelf Inbox (unverified quarantine)",
                        f"\nTo send this exact request, say: Approve Grand Library loan: {packet.loan_id}",
                    )
                ),
            )

        loopback = self.LOOPBACK_PREPARE_PATTERN.match(message.strip())
        if loopback:
            if not self.gateway.is_open:
                try:
                    self.gateway.prepare(loopback.group("question"), ())
                except GatewayError as error:
                    return DelegationResult(True, str(error))
            if self.gateway.provider.name != "loopback":
                return DelegationResult(
                    True,
                    "The Grand Library is not in local loopback mode. Close it before changing modes.",
                )
            question = loopback.group("question").strip()
            try:
                packet = self.gateway.prepare(question, ())
            except GatewayError as error:
                return DelegationResult(True, str(error))
            lines = [
                "Grand Library loopback loan preview:",
                f"\nLoan: {packet.loan_id}",
                f"Provider: {packet.provider} (local only; no network)",
                f"Question: {packet.question}",
                f"Packet size: {packet.size_bytes} bytes",
                "Bookshelf passages leaving the local boundary:",
            ]
            if packet.sources:
                for source in packet.sources:
                    lines.append(f"\nBookshelf/{source.relative_path}\n{source.passage}")
            else:
                lines.append("\nNone.")
            lines.append(f"\nTo send this exact packet, say: Approve Grand Library loan: {packet.loan_id}")
            return DelegationResult(True, "\n".join(lines))

        if self.LIBRARY_REINDEX_PATTERN.match(message.strip()):
            report = self.archivist.inventory(force_reindex=True)
            return DelegationResult(
                True,
                f"The Library index is current: {report.documents} document"
                f"{'s' if report.documents != 1 else ''} indexed; "
                f"{report.removed} stale entr{'ies' if report.removed != 1 else 'y'} removed; "
                f"{report.warnings} metadata warning{'s' if report.warnings != 1 else ''}.",
            )

        library_match = self.LIBRARY_ASK_PATTERN.match(message.strip())
        if library_match:
            query = library_match.group("query").strip()
            matches = self.archivist.ask_library(query)
            if not matches:
                return DelegationResult(
                    True,
                    f"The Library found no source passage matching '{query}'.",
                )
            lines = [
                f"The Library found {len(matches)} relevant passage"
                f"{'s' if len(matches) != 1 else ''}:"
            ]
            for index, match in enumerate(matches, 1):
                origin = "Private Filing Cabinet" if match.store == "filing_cabinet" else "Bookshelf"
                title = re.sub(r"[^\w]+", " ", match.title.casefold()).strip()
                passage = re.sub(r"[^\w]+", " ", match.passage.casefold()).strip()
                if title == passage:
                    lines.append(
                        f"\n{index}. {match.passage}\n"
                        f"Source: {origin}/{match.relative_path}"
                    )
                else:
                    lines.append(
                        f"\n{index}. {match.title}\n{match.passage}\n"
                        f"Source: {origin}/{match.relative_path}"
                    )
            return DelegationResult(True, "\n".join(lines))

        collection_approval = self.COLLECTION_APPROVAL_PATTERN.match(message.strip())
        if collection_approval:
            path = self.archivist.file_from_workbench(
                collection_approval.group("filename"),
                collection_approval.group("collection"),
            )
            return DelegationResult(
                True,
                f"Approved. The Archivist filed {path.name} in the Bookshelf {path.parent.name} collection.",
            )

        classify_match = self.CLASSIFY_PATTERN.match(message.strip())
        if classify_match:
            query = classify_match.group("query").strip()
            proposals = self.archivist.classify_workbench(query)
            if not proposals:
                return DelegationResult(True, f"The Archivist found no Workbench item matching '{query}'.")
            lines = [f"The Archivist classified {len(proposals)} matching Workbench item{'s' if len(proposals) != 1 else ''}:"]
            for proposal in proposals:
                lines.append(
                    f"\n{proposal.title}\nFile: {proposal.filename}\n{proposal.excerpt}\n"
                    f"Proposed collection: {proposal.collection}, because {proposal.reason}."
                )
            if len(proposals) == 1:
                lines.append(
                    f"\nTo approve, say: Approve the Archivist to file in {proposals[0].collection}: {proposals[0].filename}"
                )
            return DelegationResult(True, "\n".join(lines))

        approval_match = self.WORKBENCH_APPROVAL_PATTERN.match(message.strip())
        if approval_match:
            path = self.archivist.promote_to_workbench(approval_match.group("filename"))
            return DelegationResult(
                True,
                f"Approved. The Archivist moved {path.name} from the Bookshelf Inbox to Workbench.",
            )

        review_match = self.REVIEW_PATTERN.match(message.strip())
        if review_match:
            query = review_match.group("query").strip()
            reviews = self.archivist.review_bookshelf_inbox(query)
            if not reviews:
                return DelegationResult(True, f"The Archivist found no Bookshelf Inbox item matching '{query}'.")
            lines = [f"The Archivist reviewed {len(reviews)} matching Inbox item{'s' if len(reviews) != 1 else ''}:"]
            for review in reviews:
                metadata = "metadata is structurally complete" if review.metadata_ok else "metadata needs attention"
                verification = review.verified or "not stated"
                lines.append(
                    f"\n{review.title}\nFile: {review.filename}\n"
                    f"Type: {review.document_type or 'not stated'}; verification: {verification}; {metadata}.\n"
                    f"{review.excerpt}\nRecommendation: promote to Workbench for evaluation."
                )
            if len(reviews) == 1:
                lines.append(
                    f"\nTo approve, say: Approve the Archivist to move to Workbench: {reviews[0].filename}"
                )
            return DelegationResult(True, "\n".join(lines))

        file_match = self.FILE_PATTERN.match(message.strip())
        if file_match:
            destination = file_match.group("destination").casefold()
            store = "bookshelf" if "bookshelf" in destination else "filing_cabinet"
            path = self.archivist.file_note(store, file_match.group("content"))
            label = "Bookshelf Inbox" if store == "bookshelf" else "private Filing Cabinet Inbox"
            return DelegationResult(True, f"The Archivist has filed that in the {label}: {path.name}")

        retrieve_match = self.RETRIEVE_PATTERN.match(message.strip())
        if retrieve_match:
            query = retrieve_match.group("query").strip()
            matches = self.archivist.retrieve(query)
            if not matches:
                return DelegationResult(True, f"The Archivist found nothing matching '{query}'.")
            lines = [f"The Archivist found {len(matches)} matching document{'s' if len(matches) != 1 else ''}:"]
            for match in matches:
                origin = "Filing Cabinet" if match.store == "filing_cabinet" else "Bookshelf"
                lines.append(f"\n{match.title} — {origin}/{match.relative_path}\n{match.excerpt}")
            return DelegationResult(True, "\n".join(lines))

        if self.AMBIGUOUS_FILE_PATTERN.match(message.strip()):
            return DelegationResult(
                True,
                "Should the Archivist file that privately in the Filing Cabinet, or on the shared Bookshelf?",
            )
        return DelegationResult(False)
