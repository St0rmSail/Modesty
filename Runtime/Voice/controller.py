"""Bounded push-to-talk coordinator for the existing text conversation path."""

import tempfile
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

from Runtime.Voice.config import load_voice_config
from Runtime.Voice.devices import MicrophoneCapture, VoicePlayer
from Runtime.Voice.engines import LocalSpeechEngines


def concise_spoken_return(text: str, limit: int = 420) -> str:
    """Keep speech useful without reading a report or long citation aloud."""
    paragraph = text.strip().split("\n\n", 1)[0].replace("\n", " ")
    if len(paragraph) <= limit:
        return paragraph
    shortened = paragraph[:limit].rsplit(" ", 1)[0].rstrip(" ,;:")
    return f"{shortened}. The full return is in the panel."


class _TranscriptionWorker(QThread):
    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, engines, samples, sample_rate):
        super().__init__()
        self.engines = engines
        self.samples = samples
        self.sample_rate = sample_rate

    def run(self):
        try:
            self.succeeded.emit(self.engines.transcribe(self.samples, self.sample_rate))
        except Exception as error:
            self.failed.emit(str(error))


class _SpeechWorker(QThread):
    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, engines, text, path, speaker_id, speed):
        super().__init__()
        self.engines = engines
        self.text = text
        self.path = path
        self.speaker_id = speaker_id
        self.speed = speed

    def run(self):
        try:
            self.engines.synthesize(self.text, self.path, self.speaker_id, self.speed)
            self.succeeded.emit(str(self.path))
        except Exception as error:
            self.failed.emit(str(error))


class VoiceController(QObject):
    state_changed = Signal(str)
    transcript_ready = Signal(str)
    notice = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_voice_config()
        self.enabled = self.config.enabled
        self.capture = MicrophoneCapture(self.config.preferred_input, self)
        self.player = VoicePlayer(
            self.config.preferred_output, self.config.fallback_output, self
        )
        self.engines = LocalSpeechEngines(self.config.stt_model, self.config.tts_model)
        self.worker = None
        self.speech_worker = None
        self.speech_path = Path(tempfile.gettempdir()) / "modesty-spoken-return.wav"
        self.player.finished.connect(self._speech_finished)

    def toggle_enabled(self):
        self.enabled = not self.enabled
        if not self.enabled:
            self.cancel()
        self.state_changed.emit("MIC READY" if self.enabled else "MIC OFF")

    def begin_push_to_talk(self):
        if not self.enabled or self.worker is not None:
            return
        self.player.stop()
        if not self.capture.start():
            self.enabled = False
            self.state_changed.emit("MIC OFF")
            self.notice.emit("Preferred microphone unavailable. Voice remains safely off.")
            return
        self.state_changed.emit("LISTENING — release to send")

    def end_push_to_talk(self):
        if self.capture.source is None:
            return
        try:
            samples, sample_rate = self.capture.stop()
        except RuntimeError as error:
            self.state_changed.emit("MIC READY" if self.enabled else "MIC OFF")
            self.notice.emit(str(error))
            return
        self.state_changed.emit("TRANSCRIBING")
        self.worker = _TranscriptionWorker(self.engines, samples, sample_rate)
        self.worker.succeeded.connect(self._transcribed)
        self.worker.failed.connect(self._failed)
        self.worker.finished.connect(self._transcription_finished)
        self.worker.start()

    def speak(self, text: str):
        if not self.enabled or not text.strip() or self.speech_worker is not None:
            return
        self.state_changed.emit("PREPARING SPEECH")
        spoken_text = concise_spoken_return(text)
        self.speech_worker = _SpeechWorker(
            self.engines,
            spoken_text,
            self.speech_path,
            self.config.provisional_speaker_id,
            self.config.speech_speed,
        )
        self.speech_worker.succeeded.connect(self._play_speech)
        self.speech_worker.failed.connect(self._failed)
        self.speech_worker.finished.connect(self._speech_worker_finished)
        self.speech_worker.start()

    def cancel(self):
        if self.capture.source is not None:
            self.capture.stop()
        self.player.stop()
        self.state_changed.emit("MIC READY" if self.enabled else "MIC OFF")

    def _transcribed(self, text: str):
        if text:
            self.transcript_ready.emit(text)
            self.state_changed.emit("THINKING")
        else:
            self.notice.emit("I did not catch any speech. Text chat remains available.")
            self.state_changed.emit("MIC READY")

    def _play_speech(self, path: str):
        if not self.player.play(Path(path)):
            self.notice.emit("No approved playback device is available. The reply remains in text.")
            self.state_changed.emit("MIC READY")
            return
        if self.player.used_fallback:
            self.notice.emit(
                f"Headphones unavailable. Voice is using {self.player.active_name}; Windows defaults were not changed."
            )
        self.state_changed.emit("SPEAKING — press Stop to interrupt")

    def _speech_finished(self):
        self.state_changed.emit("MIC READY" if self.enabled else "MIC OFF")
        try:
            self.speech_path.unlink(missing_ok=True)
        except OSError:
            pass

    def _failed(self, message: str):
        self.notice.emit(message)
        self.state_changed.emit("MIC READY" if self.enabled else "MIC OFF")

    def _transcription_finished(self):
        self.worker.deleteLater()
        self.worker = None

    def _speech_worker_finished(self):
        self.speech_worker.deleteLater()
        self.speech_worker = None
