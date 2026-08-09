"""Fail-closed Grand Library transport foundations."""

__all__ = ["GatewayError", "GrandLibraryGateway", "LoanPacket", "LoanSource"]


def __getattr__(name):
    """Load public gateway types only when requested, keeping module CLIs isolated."""
    if name in ("GatewayError", "GrandLibraryGateway"):
        from Runtime.Library.gateway import GatewayError, GrandLibraryGateway

        return {"GatewayError": GatewayError, "GrandLibraryGateway": GrandLibraryGateway}[name]
    if name in ("LoanPacket", "LoanSource"):
        from Runtime.Library.models import LoanPacket, LoanSource

        return {"LoanPacket": LoanPacket, "LoanSource": LoanSource}[name]
    raise AttributeError(name)
