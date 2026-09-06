import json
import tempfile
import unittest
from pathlib import Path

from Runtime.Voice.config import load_voice_config
from Runtime.Voice.controller import concise_spoken_return
from Runtime.Voice.devices import find_named_device, normalized_device_name


class FakeDevice:
    def __init__(self, name):
        self.name = name

    def description(self):
        return self.name


class VoiceFoundationTests(unittest.TestCase):
    def test_long_return_is_bounded_for_speech_but_not_text(self):
        original = "A useful answer " * 60
        spoken = concise_spoken_return(original, limit=100)
        self.assertLess(len(spoken), len(original))
        self.assertIn("full return is in the panel", spoken)

    def test_report_body_after_first_paragraph_is_not_dictated(self):
        spoken = concise_spoken_return("Here is the result.\n\nA very long report follows.")
        self.assertEqual("Here is the result.", spoken)

    def test_device_matching_uses_description_not_numeric_index(self):
        devices = [FakeDevice("Speakers"), FakeDevice("Desktop Microphone")]
        self.assertIs(devices[1], find_named_device(devices, "desktop microphone"))

    def test_unknown_device_is_not_silently_substituted(self):
        devices = [FakeDevice("An unrelated microphone")]
        self.assertIsNone(find_named_device(devices, "Desktop Microphone"))

    def test_cosmetic_windows_name_damage_does_not_break_binding(self):
        configured = "Desktop Microphone (Microsoft LifeCam HD-3000)"
        reported = "Desktop Microphone (Microsoft\ufffd LifeCam HD-3000)"
        self.assertEqual(
            normalized_device_name(configured), normalized_device_name(reported)
        )
        device = FakeDevice(reported)
        self.assertIs(device, find_named_device([device], configured))

    def test_config_resolves_models_from_project_root(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "voice.json"
            path.write_text(json.dumps({
                "enabled": False,
                "preferred_input": "Mic",
                "preferred_output": "Headphones",
                "fallback_output": "Speakers",
                "stt_model": "Data/Models/Voice/stt",
                "tts_model": "Data/Models/Voice/tts"
            }), encoding="utf-8")
            config = load_voice_config(path)
        self.assertFalse(config.enabled)
        self.assertFalse(config.stt_model.is_absolute() is False)
        self.assertEqual("F8", config.push_to_talk_key)


if __name__ == "__main__":
    unittest.main()
