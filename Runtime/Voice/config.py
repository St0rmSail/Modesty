"""Portable Voice preferences; endpoint numbers are deliberately never stored."""

import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "Config" / "voice.json"


@dataclass(frozen=True)
class VoiceConfig:
    enabled: bool
    push_to_talk_key: str
    preferred_input: str
    preferred_output: str
    fallback_output: str
    stt_model: Path
    tts_model: Path
    provisional_voice: str
    provisional_speaker_id: int
    speech_speed: float


def _project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def load_voice_config(path: Path = CONFIG_PATH) -> VoiceConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    return VoiceConfig(
        enabled=bool(data.get("enabled", False)),
        push_to_talk_key=str(data.get("push_to_talk_key", "F8")),
        preferred_input=str(data["preferred_input"]),
        preferred_output=str(data["preferred_output"]),
        fallback_output=str(data["fallback_output"]),
        stt_model=_project_path(str(data["stt_model"])),
        tts_model=_project_path(str(data["tts_model"])),
        provisional_voice=str(data.get("provisional_voice", "provisional")),
        provisional_speaker_id=int(data.get("provisional_speaker_id", 0)),
        speech_speed=float(data.get("speech_speed", 1.0)),
    )
