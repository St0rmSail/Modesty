"""Reusable evidence contract for bounded Researcher investigations."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Investigation:
    subject: str
    source_url: str
    observed_facts: tuple[str, ...]
    reported_evidence: tuple[str, ...]
    cautions: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    recommendation: str
    retrieved_at: str

    def validate(self) -> "Investigation":
        if not self.subject.strip(): raise ValueError("An investigation needs a subject.")
        if not self.source_url.startswith("https://"): raise ValueError("An investigation needs an HTTPS source.")
        if not self.observed_facts: raise ValueError("An investigation needs observed evidence.")
        if self.recommendation not in {"promising", "mixed", "unlikely", "insufficient"}: raise ValueError("Unknown recommendation strength.")
        return self


def render_investigation(investigation: Investigation) -> str:
    item = investigation.validate()
    lines = [item.subject, "", f"Recommendation: {item.recommendation.upper()}", "", "Observed on the source page:", *(f"- {fact}" for fact in item.observed_facts), "", "Reader-reported evidence:", *(f"- {evidence}" for evidence in item.reported_evidence)]
    if not item.reported_evidence: lines.append("- No bounded review evidence was available.")
    lines.extend(("", "Cautions and conflicts:")); lines.extend(f"- {value}" for value in item.cautions)
    if not item.cautions: lines.append("- No explicit caution was visible in the bounded evidence.")
    lines.extend(("", "Missing evidence:")); lines.extend(f"- {value}" for value in item.missing_evidence)
    if not item.missing_evidence: lines.append("- None identified in this bounded pass.")
    lines.extend(("", f"Source: {item.source_url}", f"Retrieved: {item.retrieved_at}", "", "Nothing has been filed or added to an account."))
    return "\n".join(lines)
