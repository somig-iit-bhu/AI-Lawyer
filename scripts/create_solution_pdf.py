"""Create the two-page NyayaSaathi solution document."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "nyayasaathi_solution_document.pdf"


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D8E0EA"))
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(18 * mm, 9 * mm, "NyayaSaathi | AI-powered consumer legal information prototype")
    canvas.drawRightString(192 * mm, 9 * mm, f"Page {document.page}")
    canvas.restoreState()


def section(title: str, body: str, heading: ParagraphStyle, normal: ParagraphStyle):
    return KeepTogether([paragraph(title, heading), Spacer(1, 2 * mm), paragraph(body, normal), Spacer(1, 4 * mm)])


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=20 * mm,
        title="NyayaSaathi Solution Document",
        author="NyayaSaathi Project",
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("SolutionTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=30, alignment=TA_CENTER, textColor=colors.HexColor("#102A43"), spaceAfter=3 * mm)
    subtitle = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=10.5, leading=14, alignment=TA_CENTER, textColor=colors.HexColor("#52606D"), spaceAfter=8 * mm)
    heading = ParagraphStyle("SectionHeading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=colors.HexColor("#0B5CAD"), spaceBefore=1 * mm, spaceAfter=1 * mm)
    normal = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=9.4, leading=13.2, textColor=colors.HexColor("#243B53"))
    small = ParagraphStyle("Small", parent=normal, fontSize=8.5, leading=11.5)
    card_title = ParagraphStyle("CardTitle", parent=normal, fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=colors.HexColor("#102A43"))
    story = []

    story.extend([paragraph("NyayaSaathi", title), paragraph("Multilingual, retrieval-grounded consumer legal assistant for India", subtitle)])
    story.append(section("1. Problem and solution", "Everyday consumer disputes - defective goods, refund denials, misleading listings and marketplace issues - are difficult to navigate because users need plain-language guidance, not a dense statute. NyayaSaathi is a modular assistant that accepts English, Hindi and Hinglish, preserves the user’s facts, retrieves relevant consumer-law material, and responds with cautious, source-grounded next steps.", heading, normal))
    story.append(section("2. User experience", "The Streamlit application is designed as a chat rather than a document search page. It maintains a case summary, asks for missing information, shows a conversational legal-information response, and keeps retrieved source excerpts in expandable citation panels. A separate drafting tab can produce a reviewable consumer complaint, refund demand, or case-summary draft only from confirmed facts.", heading, normal))
    architecture = [
        [paragraph("Layer", card_title), paragraph("What it does", card_title)],
        [paragraph("Ingestion", normal), paragraph("Inspects local PDFs with PyMuPDF, records provenance, handles bilingual pages conservatively, cleans repeated headers/footers, and produces section-aware chunks.", small)],
        [paragraph("Retrieval", normal), paragraph("Uses multilingual E5 embeddings, normalized FAISS cosine search, BM25 term matching, persistent metadata, and a compatibility manifest.", small)],
        [paragraph("Reasoning", normal), paragraph("Separates confirmed facts, allegations and missing information; sends only retrieved legal excerpts plus structured case facts to the configured LLM.", small)],
        [paragraph("Safety", normal), paragraph("Requires citations, rejects citations not present in retrieved sources, avoids invented facts, and exposes uncertainty and professional-help guidance.", small)],
    ]
    table = Table(architecture, colWidths=[36 * mm, 138 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6F0FA")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D7E6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([paragraph("3. Architecture", heading), Spacer(1, 2 * mm), table, PageBreak()])

    story.extend([paragraph("Implementation, safety and validation", title), paragraph("A practical, configurable foundation for a trustworthy legal-information experience", subtitle)])
    story.append(section("4. Configurable and reproducible", "All changing behavior is centralized in configuration: embedding model, local cache mode, retrieval depth and hybrid weights, LLM provider/model/key-variable name, source metadata and safety flags. API keys live only in a local .env file. Changing the embedding model or chunking configuration requires an index rebuild, which the manifest enforces.", heading, normal))
    story.append(section("5. Evidence of working behavior", "The current corpus contains six local consumer-law PDFs. The pipeline inspected and parsed all six, then built an aligned FAISS index with 178 de-duplicated English-indexable chunks and 384-dimensional vectors. Automated tests cover configuration, bilingual-page handling, stable chunking and FAISS integrity. A live Gemini smoke test produced a complete answer to a defective-phone refund scenario with practical steps, evidence checklist and validated retrieved citations.", heading, normal))
    story.append(section("6. Guardrails and limitations", "NyayaSaathi is a legal-information prototype, not a lawyer or a filing service. It does not claim that a source is current without verification, does not consolidate amendments automatically, and does not invent deadlines, amounts, identities or case facts. Mixed-language pages are retained for review; only reliable substantive English blocks are used for the English index. OCR, rental-dispute expansion, voice input and document uploads remain explicit future enhancements.", heading, normal))
    roadmap = [
        [paragraph("Next step", card_title), paragraph("Outcome", card_title)],
        [paragraph("Source verification", normal), paragraph("Add verified official URLs, titles, document types and legal-status metadata in config/sources.yaml.", small)],
        [paragraph("Evaluation", normal), paragraph("Run fresh English, Hindi and Hinglish queries; retain raw retrieval and model outputs for review.", small)],
        [paragraph("Extension", normal), paragraph("Add OCR for scanned gazettes, source-status review, rental-dispute sources, and stronger citation/reranking evaluation.", small)],
    ]
    roadmap_table = Table(roadmap, colWidths=[42 * mm, 132 * mm], repeatRows=1)
    roadmap_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6F0FA")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D7E6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([paragraph("7. Recommended next steps", heading), Spacer(1, 2 * mm), roadmap_table, Spacer(1, 5 * mm), paragraph("Technology: Python, PyMuPDF, Sentence Transformers, FAISS CPU, Rank BM25, Pydantic, PyYAML, pytest, Streamlit and configurable Gemini/OpenAI-compatible generation.", small)])
    document.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build()
