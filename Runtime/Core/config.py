"""
config.py
=========

Purpose:
    Holds Modesty's knowledge of where everything lives.

Author:
    Andrew & ChatGPT

Build:
    0.0.6
"""

from pathlib import Path

# --------------------------------------------------
# Root Folder
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------
# Runtime
# --------------------------------------------------

RUNTIME = ROOT / "Runtime"
LOGS = RUNTIME / "Logs"

# --------------------------------------------------
# Data
# --------------------------------------------------

DATA = ROOT / "Data"

OBSIDIAN = DATA / "Obsidian"
VECTORDB = DATA / "VectorDB"
OCR = DATA / "OCR"
KNOWLEDGE = DATA / "Knowledge"