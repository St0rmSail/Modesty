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

# External knowledge stores are configured in Config/knowledge_stores.json.
# The legacy Data/Obsidian and Data/Knowledge paths above are placeholders only.
KNOWLEDGE_STORES_CONFIG = ROOT / "Config" / "knowledge_stores.json"
READING_COLLECTION_CONFIG = ROOT / "Config" / "reading_collection.json"
