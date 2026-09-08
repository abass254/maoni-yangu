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
        response_count=len(survey.responses) if survey.responses is not None else 0,
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
            response_count=len(s.responses),
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


@router.get("/public/surveys/{public_id}", response_model=PublicSurveyOut)
def get_public_survey(public_id: str, db: Session = Depends(get_db)):
    survey = (
        db.query(Survey)
        .options(joinedload(Survey.questions))
        .filter(Survey.public_id == public_id, Survey.status == "published")
        .first()
    )
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found or not published")
    return PublicSurveyOut(
        public_id=survey.public_id,
        title=survey.title,
        description=survey.description or "",
        collect_location=survey.collect_location,
        questions=[_question_out(q) for q in sorted(survey.questions, key=lambda x: x.position)],
    )


@router.post("/public/surveys/{public_id}/responses", response_model=dict[str, Any])
def submit_response(
    public_id: str,
    body: ResponseSubmit,
    request: Request,
    db: Session = Depends(get_db),
):
    survey = (
        db.query(Survey)
        .options(joinedload(Survey.questions))
        .filter(Survey.public_id == public_id, Survey.status == "published")
        .first()
    )
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found or not published")

    questions_by_id = {q.id: q for q in survey.questions}
    answered_ids = {a.question_id for a in body.answers}

    for q in survey.questions:
        if q.required and q.id not in answered_ids:
            raise HTTPException(status_code=400, detail=f"Missing answer for: {q.prompt}")

    for ans in body.answers:
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

    response = SurveyResponse(
        survey_id=survey.id,
        latitude=lat,
        longitude=lng,
        accuracy=acc,
        location_status=loc_status,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(response)
    db.flush()
    for ans in body.answers:
        db.add(
            Answer(
                response_id=response.id,
                question_id=ans.question_id,
                value=(ans.value or "").strip(),
            )
        )
    db.commit()
    return {"ok": True, "response_id": response.id}


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
        .filter(SurveyResponse.survey_id == survey.id)
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
        .filter(SurveyResponse.survey_id == survey.id)
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
