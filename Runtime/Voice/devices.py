"""Qt shared-mode device discovery, capture, and playback."""

from array import array
from pathlib import Path
import re
import unicodedata

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QObject, QUrl, Signal
from PySide6.QtMultimedia import (
    QAudioFormat,
    QAudioOutput,
    QAudioSource,
    QMediaDevices,
    QMediaPlayer,
)


def normalized_device_name(name: str) -> str:
    plain = unicodedata.normalize("NFKD", name).casefold()
    return " ".join(re.findall(r"[a-z0-9]+", plain))


def find_named_device(devices, preferred_name: str):
    wanted = normalized_device_name(preferred_name)
    for device in devices:
        if normalized_device_name(device.description()) == wanted:
            return device
    return None


class MicrophoneCapture(QObject):
    def __init__(self, preferred_name: str, parent=None):
        super().__init__(parent)
        self.preferred_name = preferred_name
        self.source = None
        self.buffer = None

    def start(self) -> bool:
        device = find_named_device(QMediaDevices.audioInputs(), self.preferred_name)
        if device is None:
            return False
        audio_format = QAudioFormat()
        audio_format.setSampleRate(16000)
        audio_format.setChannelCount(1)
        audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)
        if not device.isFormatSupported(audio_format):
            audio_format = device.preferredFormat()
        self.buffer = QBuffer(self)
        self.buffer.setData(QByteArray())
        self.buffer.open(QIODevice.OpenModeFlag.ReadWrite)
        self.source = QAudioSource(device, audio_format, self)
        self.source.start(self.buffer)
        self.audio_format = audio_format
        return True

    def stop(self) -> tuple[list[float], int]:
        if self.source is None or self.buffer is None:
            return [], 16000
        self.source.stop()
        raw = bytes(self.buffer.data())
        sample_rate = self.audio_format.sampleRate()
        self.source.deleteLater()
        self.buffer.close()
        self.source = None
        self.buffer = None
        if self.audio_format.sampleFormat() != QAudioFormat.SampleFormat.Int16:
            raise RuntimeError("The selected microphone does not support 16-bit PCM capture.")
        values = array("h")
        values.frombytes(raw[: len(raw) - (len(raw) % 2)])
        return [value / 32768.0 for value in values], sample_rate


class VoicePlayer(QObject):
    finished = Signal()

    def __init__(self, preferred_name: str, fallback_name: str, parent=None):
        super().__init__(parent)
        self.preferred_name = preferred_name
        self.fallback_name = fallback_name
        self.audio_output = QAudioOutput(self)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.mediaStatusChanged.connect(self._media_status)
        self.active_name = ""
        self.used_fallback = False

    def select_output(self) -> bool:
        devices = QMediaDevices.audioOutputs()
        device = find_named_device(devices, self.preferred_name)
        self.used_fallback = device is None
        if device is None:
            device = find_named_device(devices, self.fallback_name)
        if device is None:
            return False
        self.audio_output.setDevice(device)
        self.active_name = device.description()
        return True

    def play(self, path: Path) -> bool:
        if not self.select_output():
            return False
        self.player.setSource(QUrl.fromLocalFile(str(path)))
        self.player.play()
        return True

    def stop(self):
        self.player.stop()

    def _media_status(self, status):
        if status in (
            QMediaPlayer.MediaStatus.EndOfMedia,
            QMediaPlayer.MediaStatus.InvalidMedia,
        ):
            self.finished.emit()
