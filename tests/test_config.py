from __future__ import annotations

import json
import unittest
from pathlib import Path

from tetrio_env.config import ConfigError, load_keymap, load_session_config


class ConfigTests(unittest.TestCase):
    def test_load_default_session_config(self) -> None:
        config = load_session_config()

        self.assertEqual(config.browser, "chrome")
        self.assertEqual(config.capture_fps, 60)
        self.assertTrue(config.safe_mode)

    def test_load_keymap_contains_all_actions(self) -> None:
        keymap = load_keymap()

        self.assertEqual(keymap["left"], "left")
        self.assertEqual(keymap["hard_drop"], "space")
        self.assertIn("noop", keymap)

    def test_load_keymap_fails_with_missing_action(self) -> None:
        temp_dir = Path(__file__).parent / "fixtures"
        temp_dir.mkdir(parents=True, exist_ok=True)
        bad_keymap = temp_dir / "bad_keymap.json"
        bad_keymap.write_text(json.dumps({"left": "left"}), encoding="utf-8")

        try:
            with self.assertRaises(ConfigError):
                load_keymap(bad_keymap)
        finally:
            bad_keymap.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
