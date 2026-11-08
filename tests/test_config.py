from pathlib import Path
import pytest
from src.config import Settings, load_settings

def test_project_settings_validate():
    assert load_settings().chunking.max_tokens == 650

def test_invalid_chunk_settings_are_rejected():
    with pytest.raises(ValueError):
        Settings.model_validate({"chunking": {"target_tokens": 700, "max_tokens": 650, "overlap_tokens": 60}})
