"""Minimal CLI entrypoint for local baseline validation."""

from __future__ import annotations

import argparse

from tetrio_env.config import load_session_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TETR.IO common environment")
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Optional path to session config JSON file",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    config = load_session_config(args.config)

    print("tetrio-common-env baseline")
    print(f"browser={config.browser}")
    print(f"resolution={config.base_resolution.width}x{config.base_resolution.height}")
    print(f"capture_fps={config.capture_fps}")
    print(f"safe_mode={config.safe_mode}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
