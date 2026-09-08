from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

QuestionType = Literal["text", "multiple_choice", "rating"]
SurveyStatus = Literal["draft", "published"]
LocationStatus = Literal["granted", "denied", "skipped", "unavailable"]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class QuestionIn(BaseModel):
    prompt: str
    question_type: QuestionType
    options: list[str] = []
    required: bool = True
    position: int = 0


class QuestionOut(BaseModel):
    id: int
    prompt: str
    question_type: QuestionType
    options: list[str]
    required: bool
    position: int

    model_config = {"from_attributes": True}


class SurveyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    collect_location: bool = True
    questions: list[QuestionIn] = []


class SurveyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: SurveyStatus | None = None
    collect_location: bool | None = None
    questions: list[QuestionIn] | None = None


class SurveyOut(BaseModel):
    id: int
    public_id: str
    title: str
    description: str
    status: SurveyStatus
    collect_location: bool
    created_at: datetime
    updated_at: datetime
    questions: list[QuestionOut]
    response_count: int = 0

    model_config = {"from_attributes": True}


class SurveyListItem(BaseModel):
    id: int
    public_id: str
    title: str
    description: str
    status: SurveyStatus
    collect_location: bool
    created_at: datetime
    updated_at: datetime
    question_count: int
    response_count: int


class PublicSurveyOut(BaseModel):
    public_id: str
    title: str
    description: str
    collect_location: bool
    questions: list[QuestionOut]
    wizard: bool = False
    sections: list["WizardSectionOut"] = []


class WizardSectionOut(BaseModel):
    id: str
    title: str
    question_ids: list[int]


class AnswerIn(BaseModel):
    question_id: int
    value: str


class ResponseSubmit(BaseModel):
    answers: list[AnswerIn]
    latitude: float | None = None
    longitude: float | None = None
    accuracy: float | None = None
    location_status: LocationStatus = "skipped"


class WizardStartRequest(BaseModel):
    answers: list[AnswerIn]
    latitude: float | None = None
    longitude: float | None = None
    accuracy: float | None = None
    location_status: LocationStatus = "skipped"


class WizardStepRequest(BaseModel):
    edit_token: str
    answers: list[AnswerIn]


class WizardCompleteRequest(BaseModel):
    edit_token: str


class WizardDraftOut(BaseModel):
    ok: bool = True
    response_id: int
    edit_token: str
    status: str
    step_saved: bool = True


class AnswerOut(BaseModel):
    question_id: int
    prompt: str
    question_type: QuestionType
    value: str


class ResponseOut(BaseModel):
    id: int
    submitted_at: datetime
    latitude: float | None
    longitude: float | None
    accuracy: float | None
    location_status: LocationStatus
    answers: list[AnswerOut]


class SurveyResultsOut(BaseModel):
    survey: SurveyOut
    responses: list[ResponseOut]
    total: int
