"""Explicit separation of confirmed facts, allegations, and missing details."""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class FactStatus(str, Enum):
    CONFIRMED = "confirmed"
    ALLEGED = "alleged"
    MISSING = "missing"
    CORRECTED = "corrected"


class CaseFact(BaseModel):
    key: str
    value: str | int | float | date | None = None
    status: FactStatus
    source_message_id: str | None = None
    note: str | None = None


class EvidenceItem(BaseModel):
    name: str
    available: bool = False
    description: str | None = None


class TimelineEvent(BaseModel):
    date: str | None = None
    description: str
    status: FactStatus = FactStatus.ALLEGED


class CaseMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    role: str = Field(pattern="^(user|assistant)$")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CaseState(BaseModel):
    case_id: str = Field(default_factory=lambda: str(uuid4()))
    issue_type: str | None = None
    preferred_language: str = "auto"
    facts: dict[str, CaseFact] = Field(default_factory=dict)
    timeline: list[TimelineEvent] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    messages: list[CaseMessage] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


class FactExtraction(BaseModel):
    issue_type: str | None = None
    facts: list[CaseFact] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
