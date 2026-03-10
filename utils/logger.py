"""
SCP Wiki WYSIWYG Editor
Copyright (C) 2026 Zichen Wang (wasd243)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License v3.0.

This program comes with ABSOLUTELY NO WARRANTY.
"""

import datetime

from formats.wikidot.wikidot_parser import HAS_FTML

VERSION = "v2.0.0-beta.1"
ENGINE = "FTML + PyQt6"
EDITOR = "SCP Wiki WYSIWYG Editor"


def _timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")

def log(stage, message):
    """
    通用日志函数
    """

    print(f"[{_timestamp()}] [{stage}] {message}")


def log_ok(message):
    print(f"[{_timestamp()}] [ OK ] {message}")


def log_warn(message):
    print(f"[{_timestamp()}] [WARN] {message}")


def log_error(message):
    print(f"[{_timestamp()}] [ERR ] {message}")