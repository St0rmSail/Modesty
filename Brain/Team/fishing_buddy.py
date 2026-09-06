"""Fishing Buddy's first bounded simulator duty."""

import re

from Runtime.Fishing import (
    AnglerObservationStore, AnglerSaveInspector, FishingCodex, RF4AlmanacImporter,
    RF4CodexQuestions,
)


class FishingBuddy:
    def __init__(self, codex: FishingCodex | None = None):
        self.codex = codex or FishingCodex()

    def inspect_simulators(self) -> str:
        discoveries = self.codex.inspect()
        lines = ["The Fishing Buddy checked the four simulator desks.", ""]
        for item in discoveries:
            state = f"FOUND - {item.installation}" if item.installed else "NOT FOUND"
            lines.append(f"- {item.name}: {state}")
            lines.append(f"  Progress access: {item.data_status}")
            if item.data_path:
                lines.append(f"  Candidate data path: {item.data_path}")
        angler = next(item for item in discoveries if item.key == "call-of-the-wild-the-angler")
        next_step = (
            "The Angler is the safest first adapter candidate because a local save location is visible; "
            "its format still requires a separate read-only review before any contents are interpreted."
            if angler.data_path
            else "No game exposes a verified progress source yet; adapter work remains held pending a separate read-only review."
        )
        lines.extend(("", f"Next safe adapter: {next_step}", "", "Private local codex foundations are ready. No save, account, game process, or network service was changed."))
        return "\n".join(lines)

    def inspect_angler_save(self) -> str:
        report = AnglerSaveInspector().inspect()
        if not report.account_found:
            return "The Fishing Buddy found no local Call of the Wild: The Angler save account. Nothing was changed."
        formats: dict[str, int] = {}
        for item in report.containers:
            formats[item.format] = formats.get(item.format, 0) + 1
        format_lines = "\n".join(f"- {name}: {count}" for name, count in sorted(formats.items()))
        return "\n".join((
            "The Fishing Buddy completed a read-only inspection of The Angler's save containers.",
            "",
            report.status,
            f"Recovery snapshots matching the current primary save: {report.duplicate_snapshots}",
            "",
            format_lines,
            "",
            "No file was copied, decoded, edited, restored, deleted, or filed. The candidate remains unverified for progress extraction.",
        ))

    def begin_angler_observation(self) -> str:
        report = AnglerObservationStore().begin()
        return (
            f"The Fishing Buddy recorded a content-free baseline for {len(report.containers)} The Angler save files. "
            "You may now play normally. Close the game cleanly before asking her to compare the observation. "
            "No save content was decoded or changed."
        )

    def compare_angler_observation(self) -> str:
        difference = AnglerObservationStore().compare()
        lines = ["The Fishing Buddy compared The Angler observation with its baseline."]
        if not (difference.changed or difference.added or difference.removed):
            lines.append("No bounded save container changed.")
        else:
            if difference.changed:
                lines.append("Changed: " + ", ".join(difference.changed))
            if difference.added:
                lines.append("Added: " + ", ".join(difference.added))
            if difference.removed:
                lines.append("Removed: " + ", ".join(difference.removed))
        if difference.structural:
            lines.extend(("", "Changed byte regions (4 KiB content-free fingerprints):"))
            for item in difference.structural:
                displayed = ", ".join(item.byte_ranges[:8])
                if len(item.byte_ranges) > 8:
                    displayed += f", plus {len(item.byte_ranges) - 8} more range(s)"
                lines.append(
                    f"- {item.relative_path}: {item.changed_blocks}/{item.total_blocks} blocks; bytes {displayed}"
                )
        lines.append("Only relative filenames, sizes, and block hashes were compared; no field meaning was inferred.")
        return "\n".join(lines)

    def import_rf4_almanac(self) -> str:
        report = RF4AlmanacImporter(self.codex).import_catalogue()
        checked = ", ".join(report.integrity_species)
        return "\n".join((
            "The Fishing Buddy imported the RF4 Tackle Box fish catalogue into the private RF4 codex.",
            "",
            f"Species: {report.species}",
            f"Distinct baits: {report.baits} ({report.bait_links} species links)",
            f"Locations: {report.locations} ({report.location_links} species links)",
            f"Five-species integrity check passed: {checked}",
            "",
            "Every imported claim is labelled RF4 community reference at the weakest evidence rank. "
            "No personal progress, live catches, hotspots, recipes, or other games were changed.",
        ))

    def answer_rf4_question(self, question: str) -> str:
        brief = RF4CodexQuestions(self.codex).lookup(question)
        if brief is None:
            return (
                "The Fishing Buddy could not identify one RF4 species confidently from that question. "
                "Try the fish's full name; she will not guess between similar species."
            )
        query = question.casefold()
        correction = (
            f"I matched that approximately to {brief.species_name}. "
            if brief.approximate_match else ""
        )
        source_note = (
            f"Source: {brief.source_title} ({brief.source_locator}); "
            f"{brief.confidence.replace('_', ' ')}."
        )
        if "trophy" in query:
            trophy = self._weight(brief.trophy_weight_grams)
            super_trophy = self._weight(brief.super_trophy_weight_grams)
            return (
                f"{correction}{brief.species_name}: trophy {trophy}; super trophy {super_trophy}.\n"
                f"{source_note}"
            )
        if re.search(r"\bwhere\b|\bwhich (?:lake|water|location)\b", query):
            waters = self._short_list(brief.locations)
            return f"{correction}For {brief.species_name}, the RF4 seed catalogue lists: {waters}.\n{source_note}"
        bait_question = re.search(r"\bwould\s+(.+?)\s+work\s+for\b", query)
        if bait_question:
            proposed = bait_question.group(1).strip(" ?.,")
            proposed = re.sub(r"^(?:a|an|the)\s+", "", proposed)
            normal = RF4CodexQuestions._normalise(proposed)
            matches = [
                bait for bait in brief.baits
                if normal and (
                    normal in RF4CodexQuestions._normalise(bait)
                    or RF4CodexQuestions._normalise(bait) in normal
                )
            ]
            if matches:
                answer = f"Yes - the community seed list includes {', '.join(matches)} for {brief.species_name}."
            else:
                answer = (
                    f"The current community seed does not list {proposed} for {brief.species_name}. "
                    "That is not proof that it cannot work."
                )
            return f"{correction}{answer}\n{source_note}"
        if re.search(r"\b(?:bait|use|catch with|works? for)\b", query):
            baits = self._short_list(brief.baits)
            hook = f" Hook guidance: {brief.hook_guidance}." if brief.hook_guidance else ""
            return f"{correction}For {brief.species_name}, try {baits}.{hook}\n{source_note}"
        lines = [f"{correction}{brief.species_name} in RF4:"]
        if brief.locations:
            lines.append("Waters: " + self._short_list(brief.locations))
        if brief.baits:
            lines.append("Suggested baits: " + self._short_list(brief.baits))
        lines.append(
            f"Trophy: {self._weight(brief.trophy_weight_grams)}; "
            f"super trophy: {self._weight(brief.super_trophy_weight_grams)}"
        )
        activity = "; ".join(value for value in (brief.activity, brief.active_time) if value)
        if activity:
            lines.append("Activity: " + activity)
        if brief.hook_guidance:
            lines.append("Hook guidance: " + brief.hook_guidance)
        if brief.depth_guidance:
            lines.append("Depth: " + brief.depth_guidance)
        if brief.notes:
            lines.append("Community note: " + brief.notes)
        lines.append(source_note)
        return "\n".join(lines)

    @staticmethod
    def _weight(grams: int | None) -> str:
        if grams is None:
            return "not yet established"
        if grams < 1000:
            return f"{grams} g"
        kilograms = grams / 1000
        return f"{kilograms:g} kg"

    @staticmethod
    def _short_list(values: tuple[str, ...], maximum: int = 8) -> str:
        if not values:
            return "not yet established"
        shown = ", ".join(values[:maximum])
        remaining = len(values) - maximum
        return shown + (f", plus {remaining} more" if remaining > 0 else "")
