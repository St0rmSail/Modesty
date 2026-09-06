"""Replaceable local speech engines. Raw microphone audio is never written to disk."""

from pathlib import Path
import wave


class VoiceEngineError(RuntimeError):
    pass


class LocalSpeechEngines:
    def __init__(self, stt_model: Path, tts_model: Path):
        self.stt_model = stt_model
        self.tts_model = tts_model
        self._recognizer = None
        self._speaker = None

    def _load_recognizer(self):
        if self._recognizer is not None:
            return self._recognizer
        try:
            import sherpa_onnx

            self._recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
                encoder=str(self.stt_model / "base.en-encoder.int8.onnx"),
                decoder=str(self.stt_model / "base.en-decoder.int8.onnx"),
                tokens=str(self.stt_model / "base.en-tokens.txt"),
                language="en",
                task="transcribe",
                num_threads=4,
                provider="cpu",
            )
        except (ImportError, RuntimeError, ValueError) as error:
            raise VoiceEngineError(f"Local speech recognition is unavailable: {error}") from error
        return self._recognizer

    def transcribe(self, samples: list[float], sample_rate: int) -> str:
        if not samples:
            return ""
        recognizer = self._load_recognizer()
        stream = recognizer.create_stream()
        stream.accept_waveform(sample_rate, samples)
        recognizer.decode_stream(stream)
        return stream.result.text.strip()

    def _load_speaker(self):
        if self._speaker is not None:
            return self._speaker
        try:
            import sherpa_onnx

            kokoro = sherpa_onnx.OfflineTtsKokoroModelConfig(
                model=str(self.tts_model / "model.onnx"),
                voices=str(self.tts_model / "voices.bin"),
                tokens=str(self.tts_model / "tokens.txt"),
                data_dir=str(self.tts_model / "espeak-ng-data"),
                dict_dir=str(self.tts_model / "dict"),
                lexicon=str(self.tts_model / "lexicon-us-en.txt"),
            )
            model = sherpa_onnx.OfflineTtsModelConfig(
                kokoro=kokoro, num_threads=4, provider="cpu", debug=False
            )
            self._speaker = sherpa_onnx.OfflineTts(
                sherpa_onnx.OfflineTtsConfig(model=model)
            )
        except (ImportError, RuntimeError, ValueError) as error:
            raise VoiceEngineError(f"Local speech is unavailable: {error}") from error
        return self._speaker

    def synthesize(self, text: str, destination: Path, speaker_id: int, speed: float):
        audio = self._load_speaker().generate(text, sid=speaker_id, speed=speed)
        destination.parent.mkdir(parents=True, exist_ok=True)
        pcm = bytearray()
        for sample in audio.samples:
            value = max(-1.0, min(1.0, float(sample)))
            pcm.extend(int(value * 32767).to_bytes(2, "little", signed=True))
        with wave.open(str(destination), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(audio.sample_rate)
            output.writeframes(pcm)
