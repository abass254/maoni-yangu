from __future__ import annotations

import csv
import io
import json
import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session, joinedload

from ..auth import get_current_user
from ..database import get_db
from ..models import Answer, Question, Response as SurveyResponse, Survey, User
from ..templates import (
    DEFAULT_TEMPLATE_TITLES,
    create_australia_refugee_visa_survey,
    create_canada_refugee_visa_survey,
    create_germany_refugee_visa_survey,
    create_kenya_elections_survey,
    create_uk_refugee_visa_survey,
    is_refugee_wizard_survey,
    refugee_wizard_sections,
)
from ..schemas import (
    PublicSurveyOut,
    QuestionIn,
    QuestionOut,
    ResponseOut,
    ResponseSubmit,
    SurveyCreate,
    SurveyListItem,
    SurveyOut,
    SurveyResultsOut,
    SurveyUpdate,
    AnswerOut,
    WizardCompleteRequest,
    WizardDraftOut,
    WizardSectionOut,
    WizardStartRequest,
    WizardStepRequest,
)

router = APIRouter(tags=["surveys"])


def _new_public_id() -> str:
    return secrets.token_urlsafe(12)


def _options_list(raw: str) -> list[str]:
    try:
        data = json.loads(raw or "[]")
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _question_out(q: Question) -> QuestionOut:
    return QuestionOut(
        id=q.id,
        prompt=q.prompt,
        question_type=q.question_type,  # type: ignore[arg-type]
        options=_options_list(q.options_json),
        required=q.required,
        position=q.position,
    )


def _complete_response_count(survey: Survey) -> int:
    if survey.responses is None:
        return 0
    return sum(1 for r in survey.responses if (r.status or "complete") != "draft")


def _survey_out(survey: Survey) -> SurveyOut:
    return SurveyOut(
        id=survey.id,
        public_id=survey.public_id,
        title=survey.title,
        description=survey.description or "",
        status=survey.status,  # type: ignore[arg-type]
        collect_location=survey.collect_location,
        created_at=survey.created_at,
        updated_at=survey.updated_at,
        questions=[_question_out(q) for q in sorted(survey.questions, key=lambda x: x.position)],
        response_count=_complete_response_count(survey),
    )


def _replace_questions(db: Session, survey: Survey, questions: list[QuestionIn]) -> None:
    for existing in list(survey.questions):
        db.delete(existing)
    db.flush()
    for idx, q in enumerate(questions):
        if q.question_type == "multiple_choice" and len(q.options) < 2:
            raise HTTPException(
                status_code=400,
                detail="Multiple choice questions need at least 2 options",
            )
        if q.question_type == "rating" and not q.options:
            q.options = ["1", "2", "3", "4", "5"]
        survey.questions.append(
            Question(
                prompt=q.prompt.strip(),
                question_type=q.question_type,
                options_json=json.dumps(q.options),
                required=q.required,
                position=q.position if q.position else idx,
            )
        )


def _owned_survey(db: Session, survey_id: int, user: User) -> Survey:
    survey = (
        db.query(Survey)
        .options(joinedload(Survey.questions), joinedload(Survey.responses))
        .filter(Survey.id == survey_id, Survey.owner_id == user.id)
        .first()
    )
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey


@router.get("/surveys", response_model=list[SurveyListItem])
def list_surveys(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    surveys = (
        db.query(Survey)
        .options(joinedload(Survey.questions), joinedload(Survey.responses))
        .filter(Survey.owner_id == user.id)
        .order_by(Survey.updated_at.desc())
        .all()
    )
    return [
        SurveyListItem(
            id=s.id,
            public_id=s.public_id,
            title=s.title,
            description=s.description or "",
            status=s.status,  # type: ignore[arg-type]
            collect_location=s.collect_location,
            created_at=s.created_at,
            updated_at=s.updated_at,
            question_count=len(s.questions),
            response_count=_complete_response_count(s),
        )
        for s in surveys
    ]


@router.post("/surveys", response_model=SurveyOut)
def create_survey(
    body: SurveyCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    survey = Survey(
        public_id=_new_public_id(),
        owner_id=user.id,
        title=body.title.strip(),
        description=body.description.strip(),
        collect_location=body.collect_location,
        status="draft",
    )
    db.add(survey)
    db.flush()
    if body.questions:
        _replace_questions(db, survey, body.questions)
    db.commit()
    survey = _owned_survey(db, survey.id, user)
    return _survey_out(survey)


@router.post("/surveys/templates/kenya-elections", response_model=SurveyOut)
def create_kenya_elections_template(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add the Kenya Elections Opinion Survey draft for the current user."""
    existing = (
        db.query(Survey)
        .filter(
            Survey.owner_id == user.id,
            Survey.title == "Kenya Elections Opinion Survey",
        )
        .first()
    )
    if existing:
        return _survey_out(_owned_survey(db, existing.id, user))
    survey = create_kenya_elections_survey(db, user)
    db.commit()
    return _survey_out(_owned_survey(db, survey.id, user))


def _get_or_create_named_template(
    db: Session,
    user: User,
    *,
    title: str,
    factory,
) -> SurveyOut:
    existing = (
        db.query(Survey)
        .filter(Survey.owner_id == user.id, Survey.title == title)
        .first()
    )
    if existing:
        return _survey_out(_owned_survey(db, existing.id, user))
    survey = factory(db, user)
    db.commit()
    return _survey_out(_owned_survey(db, survey.id, user))


@router.post("/surveys/templates/canada-refugee-visa", response_model=SurveyOut)
def create_canada_refugee_visa_template(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_or_create_named_template(
        db,
        user,
        title=DEFAULT_TEMPLATE_TITLES["canada-refugee-visa"],
        factory=create_canada_refugee_visa_survey,
    )


@router.post("/surveys/templates/germany-refugee-visa", response_model=SurveyOut)
def create_germany_refugee_visa_template(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_or_create_named_template(
        db,
        user,
        title=DEFAULT_TEMPLATE_TITLES["germany-refugee-visa"],
        factory=create_germany_refugee_visa_survey,
    )


@router.post("/surveys/templates/uk-refugee-visa", response_model=SurveyOut)
def create_uk_refugee_visa_template(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_or_create_named_template(
        db,
        user,
        title=DEFAULT_TEMPLATE_TITLES["uk-refugee-visa"],
        factory=create_uk_refugee_visa_survey,
    )


@router.post("/surveys/templates/australia-refugee-visa", response_model=SurveyOut)
def create_australia_refugee_visa_template(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_or_create_named_template(
        db,
        user,
        title=DEFAULT_TEMPLATE_TITLES["australia-refugee-visa"],
        factory=create_australia_refugee_visa_survey,
    )


@router.get("/surveys/{survey_id}", response_model=SurveyOut)
def get_survey(
    survey_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _survey_out(_owned_survey(db, survey_id, user))


@router.put("/surveys/{survey_id}", response_model=SurveyOut)
def update_survey(
    survey_id: int,
    body: SurveyUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    survey = _owned_survey(db, survey_id, user)
    if body.title is not None:
        survey.title = body.title.strip()
    if body.description is not None:
        survey.description = body.description.strip()
    if body.collect_location is not None:
        survey.collect_location = body.collect_location
    if body.status is not None:
        if body.status == "published" and not survey.questions:
            raise HTTPException(status_code=400, detail="Add at least one question before publishing")
        survey.status = body.status
    if body.questions is not None:
        _replace_questions(db, survey, body.questions)
    db.commit()
    return _survey_out(_owned_survey(db, survey_id, user))


@router.delete("/surveys/{survey_id}")
def delete_survey(
    survey_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    survey = _owned_survey(db, survey_id, user)
    db.delete(survey)
    db.commit()
    return {"ok": True}


def _published_survey(db: Session, public_id: str) -> Survey:
    survey = (
        db.query(Survey)
        .options(joinedload(Survey.questions))
        .filter(Survey.public_id == public_id, Survey.status == "published")
        .first()
    )
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found or not published")
    return survey


def _validate_answer_values(
    questions_by_id: dict[int, Question],
    answers: list,
    *,
    require_present: bool,
) -> None:
    answered_ids = {a.question_id for a in answers}
    if require_present:
        for q in questions_by_id.values():
            if q.required and q.id not in answered_ids:
                raise HTTPException(status_code=400, detail=f"Missing answer for: {q.prompt}")

    for ans in answers:
        q = questions_by_id.get(ans.question_id)
        if not q:
            raise HTTPException(status_code=400, detail=f"Unknown question id {ans.question_id}")
        value = (ans.value or "").strip()
        if q.required and not value:
            raise HTTPException(status_code=400, detail=f"Answer required for: {q.prompt}")
        if q.question_type == "multiple_choice":
            options = _options_list(q.options_json)
            if value and value not in options:
                raise HTTPException(status_code=400, detail=f"Invalid option for: {q.prompt}")
        if q.question_type == "rating" and value:
            options = _options_list(q.options_json) or ["1", "2", "3", "4", "5"]
            if value not in options:
                raise HTTPException(status_code=400, detail=f"Invalid rating for: {q.prompt}")


def _upsert_answers(db: Session, response_id: int, answers: list) -> None:
    existing = {
        a.question_id: a
        for a in db.query(Answer).filter(Answer.response_id == response_id).all()
    }
    for ans in answers:
        value = (ans.value or "").strip()
        row = existing.get(ans.question_id)
        if row:
            row.value = value
        else:
            db.add(
                Answer(
                    response_id=response_id,
                    question_id=ans.question_id,
                    value=value,
                )
            )


def _require_location(survey: Survey, body: Any) -> tuple[float | None, float | None, float | None, str]:
    lat = body.latitude if survey.collect_location else None
    lng = body.longitude if survey.collect_location else None
    acc = body.accuracy if survey.collect_location else None
    loc_status = body.location_status if survey.collect_location else "skipped"
    if survey.collect_location:
        if loc_status != "granted" or lat is None or lng is None:
            raise HTTPException(
                status_code=400,
                detail="Location must be enabled before submitting this survey",
            )
    elif loc_status != "granted":
        lat, lng, acc = None, None, None
    return lat, lng, acc, loc_status


def _draft_response(
    db: Session,
    survey: Survey,
    response_id: int,
    edit_token: str,
) -> SurveyResponse:
    response = (
        db.query(SurveyResponse)
        .filter(
            SurveyResponse.id == response_id,
            SurveyResponse.survey_id == survey.id,
            SurveyResponse.edit_token == edit_token,
        )
        .first()
    )
    if not response:
        raise HTTPException(status_code=404, detail="Draft not found")
    if (response.status or "complete") != "draft":
        raise HTTPException(status_code=400, detail="This response is already complete")
    return response


@router.get("/public/surveys/{public_id}", response_model=PublicSurveyOut)
def get_public_survey(public_id: str, db: Session = Depends(get_db)):
    survey = _published_survey(db, public_id)
    questions = [_question_out(q) for q in sorted(survey.questions, key=lambda x: x.position)]
    wizard = is_refugee_wizard_survey(survey.title)
    sections = (
        [WizardSectionOut(**s) for s in refugee_wizard_sections(survey.questions)]
        if wizard
        else []
    )
    return PublicSurveyOut(
        public_id=survey.public_id,
        title=survey.title,
        description=survey.description or "",
        collect_location=survey.collect_location,
        questions=questions,
        wizard=wizard,
        sections=sections,
    )


@router.post("/public/surveys/{public_id}/responses", response_model=dict[str, Any])
def submit_response(
    public_id: str,
    body: ResponseSubmit,
    request: Request,
    db: Session = Depends(get_db),
):
    survey = _published_survey(db, public_id)
    questions_by_id = {q.id: q for q in survey.questions}
    _validate_answer_values(questions_by_id, body.answers, require_present=True)
    lat, lng, acc, loc_status = _require_location(survey, body)

    response = SurveyResponse(
        survey_id=survey.id,
        latitude=lat,
        longitude=lng,
        accuracy=acc,
        location_status=loc_status,
        status="complete",
        user_agent=request.headers.get("user-agent"),
    )
    db.add(response)
    db.flush()
    _upsert_answers(db, response.id, body.answers)
    db.commit()
    return {"ok": True, "response_id": response.id}


@router.post(
    "/public/surveys/{public_id}/responses/start",
    response_model=WizardDraftOut,
)
def start_wizard_response(
    public_id: str,
    body: WizardStartRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    survey = _published_survey(db, public_id)
    if not is_refugee_wizard_survey(survey.title):
        raise HTTPException(status_code=400, detail="This survey is not a wizard flow")

    sections = refugee_wizard_sections(survey.questions)
    if not sections:
        raise HTTPException(status_code=400, detail="No wizard sections configured")
    first_ids = set(sections[0]["question_ids"])
    questions_by_id = {q.id: q for q in survey.questions if q.id in first_ids}
    for ans in body.answers:
        if ans.question_id not in first_ids:
            raise HTTPException(
                status_code=400,
                detail="First step may only include bio-section answers",
            )
    _validate_answer_values(questions_by_id, body.answers, require_present=True)
    lat, lng, acc, loc_status = _require_location(survey, body)

    edit_token = secrets.token_urlsafe(24)
    response = SurveyResponse(
        survey_id=survey.id,
        latitude=lat,
        longitude=lng,
        accuracy=acc,
        location_status=loc_status,
        status="draft",
        edit_token=edit_token,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(response)
    db.flush()
    _upsert_answers(db, response.id, body.answers)
    db.commit()
    return WizardDraftOut(
        response_id=response.id,
        edit_token=edit_token,
        status="draft",
    )


@router.patch(
    "/public/surveys/{public_id}/responses/{response_id}",
    response_model=WizardDraftOut,
)
def save_wizard_step(
    public_id: str,
    response_id: int,
    body: WizardStepRequest,
    db: Session = Depends(get_db),
):
    survey = _published_survey(db, public_id)
    response = _draft_response(db, survey, response_id, body.edit_token)
    questions_by_id = {q.id: q for q in survey.questions}
    allowed = set(questions_by_id.keys())
    for ans in body.answers:
        if ans.question_id not in allowed:
            raise HTTPException(status_code=400, detail=f"Unknown question id {ans.question_id}")
    # Only validate values present in this step (not the whole survey)
    step_questions = {
        qid: questions_by_id[qid]
        for qid in {a.question_id for a in body.answers}
        if qid in questions_by_id
    }
    _validate_answer_values(step_questions, body.answers, require_present=True)
    _upsert_answers(db, response.id, body.answers)
    db.commit()
    return WizardDraftOut(
        response_id=response.id,
        edit_token=body.edit_token,
        status="draft",
    )


@router.post(
    "/public/surveys/{public_id}/responses/{response_id}/complete",
    response_model=WizardDraftOut,
)
def complete_wizard_response(
    public_id: str,
    response_id: int,
    body: WizardCompleteRequest,
    db: Session = Depends(get_db),
):
    from ..models import utcnow

    survey = _published_survey(db, public_id)
    response = _draft_response(db, survey, response_id, body.edit_token)
    existing_answers = {
        a.question_id: a
        for a in db.query(Answer).filter(Answer.response_id == response.id).all()
    }
    questions_by_id = {q.id: q for q in survey.questions}
    for q in survey.questions:
        if not q.required:
            continue
        row = existing_answers.get(q.id)
        if not row or not (row.value or "").strip():
            raise HTTPException(status_code=400, detail=f"Missing answer for: {q.prompt}")

    if survey.collect_location:
        if response.location_status != "granted" or response.latitude is None:
            raise HTTPException(
                status_code=400,
                detail="Location must be saved on the first step before completing",
            )

    response.status = "complete"
    response.submitted_at = utcnow()
    db.commit()
    return WizardDraftOut(
        response_id=response.id,
        edit_token=body.edit_token,
        status="complete",
    )


@router.get("/surveys/{survey_id}/results", response_model=SurveyResultsOut)
def get_results(
    survey_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    survey = _owned_survey(db, survey_id, user)
    responses = (
        db.query(SurveyResponse)
        .options(joinedload(SurveyResponse.answers))
        .filter(
            SurveyResponse.survey_id == survey.id,
            SurveyResponse.status != "draft",
        )
        .order_by(SurveyResponse.submitted_at.desc())
        .all()
    )
    questions_by_id = {q.id: q for q in survey.questions}
    out_responses: list[ResponseOut] = []
    for r in responses:
        answers_out: list[AnswerOut] = []
        for a in r.answers:
            q = questions_by_id.get(a.question_id)
            if not q:
                continue
            answers_out.append(
                AnswerOut(
                    question_id=a.question_id,
                    prompt=q.prompt,
                    question_type=q.question_type,  # type: ignore[arg-type]
                    value=a.value,
                )
            )
        out_responses.append(
            ResponseOut(
                id=r.id,
                submitted_at=r.submitted_at,
                latitude=r.latitude,
                longitude=r.longitude,
                accuracy=r.accuracy,
                location_status=r.location_status,  # type: ignore[arg-type]
                answers=answers_out,
            )
        )
    return SurveyResultsOut(
        survey=_survey_out(survey),
        responses=out_responses,
        total=len(out_responses),
    )


@router.get("/surveys/{survey_id}/export.csv")
def export_csv(
    survey_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    survey = _owned_survey(db, survey_id, user)
    questions = sorted(survey.questions, key=lambda q: q.position)
    responses = (
        db.query(SurveyResponse)
        .options(joinedload(SurveyResponse.answers))
        .filter(
            SurveyResponse.survey_id == survey.id,
            SurveyResponse.status != "draft",
        )
        .order_by(SurveyResponse.submitted_at.asc())
        .all()
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    header = [
        "response_id",
        "submitted_at",
        "latitude",
        "longitude",
        "accuracy",
        "location_status",
    ] + [f"q{q.id}:{q.prompt}" for q in questions]
    writer.writerow(header)

    for r in responses:
        by_q = {a.question_id: a.value for a in r.answers}
        row = [
            r.id,
            r.submitted_at.isoformat() if r.submitted_at else "",
            r.latitude if r.latitude is not None else "",
            r.longitude if r.longitude is not None else "",
            r.accuracy if r.accuracy is not None else "",
            r.location_status,
        ] + [by_q.get(q.id, "") for q in questions]
        writer.writerow(row)

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="survey-{survey.public_id}-results.csv"'
        },
    )
