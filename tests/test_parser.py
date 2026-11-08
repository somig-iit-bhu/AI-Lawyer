from src.ingestion.cleaner import clean_text
from src.ingestion.language_filter import classify_page
from src.ingestion.section_parser import split_sections

def test_mixed_language_is_retained_for_review():
    language, review, warnings = classify_page("Refund denied. रिफंड अस्वीकार।", "en")
    assert language == "mixed" and review and warnings

def test_legal_section_marker_is_preserved():
    sections = split_sections("Section 2. Definitions\nWords retain their legal meaning.")
    assert sections[0].identifier == "section 2"

def test_cleaner_preserves_numbering():
    assert "Section 2" in clean_text("Section 2\n\n\nDefinitions")
