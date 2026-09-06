"""Fishing Buddy's first bounded simulator duty."""

from Runtime.Fishing import FishingCodex


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
