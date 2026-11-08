"""Optional, user-maintained source metadata; never infer URLs or legal status."""
from __future__ import annotations
from pathlib import Path
import yaml

def load_source_registry(path: Path) -> dict[str, dict]:
    if not path.exists(): return {}
    with path.open("r", encoding="utf-8") as file:
        payload = yaml.safe_load(file) or {}
    entries = payload.get("sources", [])
    if not isinstance(entries, list): raise ValueError("config/sources.yaml: 'sources' must be a list")
    registry: dict[str, dict] = {}
    for entry in entries:
        filename = entry.get("filename")
        if not filename: raise ValueError("Every configured source requires a filename")
        registry[filename] = entry
    return registry
