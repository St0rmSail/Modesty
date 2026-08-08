"""In-process truthful state for enabled Team members."""


_enabled_members = {"archivist"}
_member_states = {member: "offline" for member in _enabled_members}
_core_ready = False


def reset():
    global _core_ready
    _core_ready = False
    for member in _enabled_members:
        _member_states[member] = "offline"


def set_member_state(member: str, state: str):
    if member not in _enabled_members:
        raise ValueError(f"Unknown enabled Team member: {member}")
    if state not in {"ready", "working", "waiting", "attention", "offline"}:
        raise ValueError(f"Unknown Team state: {state}")
    _member_states[member] = state


def member_state(member: str) -> str:
    return _member_states.get(member, "offline")


def set_core_ready(ready: bool):
    global _core_ready
    _core_ready = bool(ready)


def system_ready() -> bool:
    return _core_ready and all(
        state in {"ready", "working", "waiting"} for state in _member_states.values()
    )
