"""Loads versioned prompt files from the configured project path."""
from pathlib import Path
from src.config import PROJECT_ROOT

def load_prompt(path: str) -> str:
    prompt_path = Path(path)
    if not prompt_path.is_absolute(): prompt_path = PROJECT_ROOT / prompt_path
    if not prompt_path.exists(): raise FileNotFoundError(f"Configured prompt does not exist: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8").strip()
