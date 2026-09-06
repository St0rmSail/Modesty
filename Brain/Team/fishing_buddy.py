"""Fishing Buddy's first bounded simulator duty."""

from Runtime.Fishing import AnglerObservationStore, AnglerSaveInspector, FishingCodex, RF4AlmanacImporter


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
