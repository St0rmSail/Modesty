"""Transport providers for the Grand Library Gateway."""

from dataclasses import dataclass

from Runtime.Library.models import LoanPacket


@dataclass(frozen=True)
class ProviderReturn:
    title: str
    body: str


class LoopbackProvider:
    """Exercise the complete transport contract without using a network."""

    name = "loopback"

    def execute(self, packet: LoanPacket) -> ProviderReturn:
        count = len(packet.sources)
        body = (
            "The local loopback provider received the exact approved loan packet. "
            f"It contained {count} Bookshelf passage{'s' if count != 1 else ''}. "
            "No network request was made."
        )
        return ProviderReturn(
            title=f"Grand Library loopback receipt {packet.loan_id}",
            body=body,
        )
