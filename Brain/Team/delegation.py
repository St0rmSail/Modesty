"""Deterministic routing from Modesty to bounded Team duties."""

from dataclasses import dataclass
from pathlib import Path
import re

from Brain.Team.archivist import Archivist
from Runtime.Knowledge.catalog import KnowledgeCatalog
from Runtime.Knowledge.stores import KnowledgeStores


@dataclass(frozen=True)
class DelegationResult:
    handled: bool
    response: str = ""


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

    def __init__(self, archivist: Archivist | None = None):
        if archivist is None:
            paths = KnowledgeStores().initialize()
            archivist = Archivist(paths, KnowledgeCatalog())
        self.archivist = archivist

    def handle(self, message: str) -> DelegationResult:
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
