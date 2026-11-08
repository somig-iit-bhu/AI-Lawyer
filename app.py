"""Chat-first Streamlit interface for the NyayaSaathi legal-information prototype."""
from __future__ import annotations

from dataclasses import dataclass

import streamlit as st
from dotenv import load_dotenv

from src.case.models import CaseState
from src.case.service import CaseService
from src.config import PROJECT_ROOT, load_settings
from src.llm.factory import create_provider
from src.retrieval.retriever import LegalRetriever
from src.services.case_intake import CaseIntakeService
from src.services.document_drafting import DocumentDraftingService, DraftKind
from src.services.legal_answer import LegalAnswerService


@dataclass
class ChatTurn:
    role: str
    content: str
    sources: list[dict] | None = None


@st.cache_resource(show_spinner=False)
def get_runtime():
    """Load heavyweight local models once per Streamlit server, not once per chat rerun."""
    settings = load_settings()
    provider = create_provider(settings.llm)
    return settings, provider, LegalRetriever(settings)


def initialize_state() -> None:
    if "case" not in st.session_state:
        st.session_state.case = CaseState()
    if "chat_turns" not in st.session_state:
        st.session_state.chat_turns = [ChatTurn(role="assistant", content="Hello — I can help you understand a consumer issue in English, Hindi, or Hinglish. Tell me what happened, who the seller or service provider was, and what outcome you want.")]


def reset_chat() -> None:
    st.session_state.case = CaseState()
    st.session_state.chat_turns = [ChatTurn(role="assistant", content="New case started. What consumer issue would you like to discuss?")]


def render_sources(sources: list[dict]) -> None:
    with st.expander(f"Legal sources used ({len(sources)})"):
        for index, source in enumerate(sources, 1):
            label = f"[{index}] {source['source_file']}, p. {source['page_start']}"
            if source.get("section"):
                label += f" — {source['section']}"
            st.markdown(f"**{label}**")
            st.caption(source["text"][:900] + ("…" if len(source["text"]) > 900 else ""))


def render_history() -> None:
    for turn in st.session_state.chat_turns:
        with st.chat_message(turn.role):
            st.markdown(turn.content)
            if turn.sources:
                render_sources(turn.sources)


def render_case_summary(case: CaseState) -> None:
    with st.sidebar:
        st.subheader("Case summary")
        st.caption(f"Case ID: {case.case_id}")
        st.write(f"Issue: {case.issue_type or 'Not identified yet'}")
        if case.facts:
            with st.expander("Facts saved from this chat"):
                for fact in case.facts.values():
                    st.markdown(f"- **{fact.key.replace('_', ' ').title()}:** {fact.value} _({fact.status.value})_")
        if case.missing_information:
            st.warning("Helpful details still missing")
            for item in case.missing_information:
                st.caption(f"• {item}")
        st.divider()
        if st.button("Start a new chat", use_container_width=True):
            reset_chat()
            st.rerun()


def format_answer(answer) -> str:
    text = answer.answer.strip()
    if answer.practical_next_steps:
        text += "\n\n**Practical next steps**\n" + "\n".join(f"- {step}" for step in answer.practical_next_steps)
    if answer.evidence_checklist:
        text += "\n\n**Useful evidence**\n" + "\n".join(f"- {item}" for item in answer.evidence_checklist)
    if answer.uncertainty:
        text += f"\n\n**What remains uncertain:** {answer.uncertainty}"
    if answer.professional_help_recommended:
        text += "\n\nConsider speaking with a qualified lawyer or consumer-rights advisor before filing a formal case."
    return text


def main() -> None:
    load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=False)
    st.set_page_config(page_title="NyayaSaathi", page_icon="⚖️", layout="wide")
    initialize_state()
    st.title("⚖️ NyayaSaathi")
    st.caption("Consumer-law information for India · Not a substitute for a qualified legal professional")
    case: CaseState = st.session_state.case
    render_case_summary(case)
    try:
        settings, provider, retriever = get_runtime()
    except Exception as error:
        st.error(f"Configuration is incomplete: {error}")
        st.info("Create E:\\Projects\\AI Lawyer\\.env with the API key named by `llm.api_key_env`, then restart Streamlit.")
        return
    chat_tab, draft_tab = st.tabs(["Chat", "Draft a document"])
    with chat_tab:
        render_history()
        prompt = st.chat_input("Describe your issue — English, Hindi, or Hinglish")
        if prompt:
            st.session_state.chat_turns.append(ChatTurn(role="user", content=prompt))
            with st.chat_message("user"):
                st.markdown(prompt)
            case_service = CaseService()
            user_message = case_service.add_user_message(case, prompt)
            intake = CaseIntakeService(provider, "config/prompts/case_extraction_v1.md")
            answer_service = LegalAnswerService(retriever, provider, "config/prompts/rag_answer_v1.md", settings.safety)
            with st.chat_message("assistant"):
                with st.spinner("Reviewing the facts and legal sources..."):
                    try:
                        extraction = intake.extract(case, prompt)
                        case_service.apply_extraction(case, extraction, user_message.message_id)
                        answer, sources = answer_service.answer(case, prompt)
                        rendered = format_answer(answer)
                        st.markdown(rendered)
                        render_sources(sources)
                        st.session_state.chat_turns.append(ChatTurn(role="assistant", content=rendered, sources=sources))
                    except Exception as error:
                        message = f"I couldn't prepare a grounded legal response yet: {error}"
                        st.error(message)
                        st.session_state.chat_turns.append(ChatTurn(role="assistant", content=message))
    with draft_tab:
        st.subheader("Create a reviewable draft")
        st.caption("Only confirmed or corrected facts are sent to the drafting service. Missing information is shown as [TO BE PROVIDED].")
        selected = st.selectbox("Document type", [item.value for item in DraftKind])
        if st.button("Generate draft", use_container_width=True):
            try:
                service = DocumentDraftingService(provider, "config/prompts/document_draft_v1.md")
                draft = service.draft(DraftKind(selected), case, [])
                st.text_area("Draft preview", draft.body, height=360)
                st.download_button("Download draft", draft.body, file_name=f"{draft.kind.value}.txt", mime="text/plain")
            except Exception as error:
                st.error(f"Unable to generate the draft: {error}")


if __name__ == "__main__":
    main()
