from __future__ import annotations

import json
import secrets

from sqlalchemy.orm import Session

from .models import Question, Survey, User


def _new_public_id() -> str:
    return secrets.token_urlsafe(12)


def _create_survey_from_questions(
    db: Session,
    user: User,
    *,
    title: str,
    description: str,
    questions: list[dict],
    collect_location: bool = True,
    language: str = "en",
) -> Survey:
    survey = Survey(
        public_id=_new_public_id(),
        owner_id=user.id,
        title=title,
        description=description,
        collect_location=collect_location,
        language="so" if language == "so" else "en",
        status="draft",
    )
    db.add(survey)
    db.flush()

    for idx, q in enumerate(questions):
        survey.questions.append(
            Question(
                prompt=q["prompt"],
                question_type=q["question_type"],
                options_json=json.dumps(q["options"]),
                required=q["required"],
                position=idx,
            )
        )

    db.flush()
    return survey


JOB_APPLICATION_QUESTIONS: list[dict] = [
    {
        "prompt": "Full name",
        "question_type": "text",
        "options": [],
        "required": True,
    },
    {
        "prompt": "Email address",
        "question_type": "text",
        "options": [],
        "required": True,
    },
    {
        "prompt": "Phone number",
        "question_type": "text",
        "options": [],
        "required": True,
    },
    {
        "prompt": "Position you are applying for",
        "question_type": "text",
        "options": [],
        "required": True,
    },
    {
        "prompt": "Years of relevant experience",
        "question_type": "multiple_choice",
        "options": ["Less than 1 year", "1–2 years", "3–5 years", "6–10 years", "10+ years"],
        "required": True,
    },
    {
        "prompt": "Highest education level completed",
        "question_type": "multiple_choice",
        "options": [
            "High school",
            "Diploma / Certificate",
            "Bachelor's degree",
            "Master's degree",
            "Doctorate",
            "Other",
        ],
        "required": True,
    },
    {
        "prompt": "Are you currently employed?",
        "question_type": "multiple_choice",
        "options": ["Yes", "No", "Prefer not to say"],
        "required": True,
    },
    {
        "prompt": "When can you start?",
        "question_type": "multiple_choice",
        "options": ["Immediately", "Within 2 weeks", "Within 1 month", "More than 1 month"],
        "required": True,
    },
    {
        "prompt": "Expected salary / compensation (optional)",
        "question_type": "text",
        "options": [],
        "required": False,
    },
    {
        "prompt": "Briefly describe your relevant skills and experience",
        "question_type": "text",
        "options": [],
        "required": True,
    },
    {
        "prompt": "Why do you want this role?",
        "question_type": "text",
        "options": [],
        "required": True,
    },
    {
        "prompt": "How would you rate your overall fit for this role?",
        "question_type": "rating",
        "options": ["1", "2", "3", "4", "5"],
        "required": True,
    },
    {
        "prompt": "How did you hear about this opportunity?",
        "question_type": "multiple_choice",
        "options": [
            "Company website",
            "Job board",
            "Social media",
            "Referral / friend",
            "Other",
        ],
        "required": False,
    },
]


KENYA_ELECTIONS_QUESTIONS: list[dict] = [
    {
        "prompt": "Which county do you live in?",
        "question_type": "text",
        "options": [],
        "required": True,
    },
    {
        "prompt": "What is your age group?",
        "question_type": "multiple_choice",
        "options": ["18–24", "25–34", "35–44", "45–54", "55–64", "65+"],
        "required": True,
    },
    {
        "prompt": "Are you a registered voter with IEBC?",
        "question_type": "multiple_choice",
        "options": ["Yes", "No", "Not sure", "Prefer not to say"],
        "required": True,
    },
    {
        "prompt": "How likely are you to vote in the upcoming Kenyan elections?",
        "question_type": "multiple_choice",
        "options": [
            "Very likely",
            "Somewhat likely",
            "Not sure yet",
            "Somewhat unlikely",
            "Very unlikely",
        ],
        "required": True,
    },
    {
        "prompt": "What is the most important issue that will influence your vote?",
        "question_type": "multiple_choice",
        "options": [
            "Cost of living / economy",
            "Jobs / unemployment",
            "Corruption / governance",
            "Healthcare",
            "Education",
            "Security / safety",
            "Infrastructure / roads",
            "Agriculture / food security",
            "Other",
        ],
        "required": True,
    },
    {
        "prompt": "How informed do you feel about the candidates and their agendas?",
        "question_type": "rating",
        "options": ["1", "2", "3", "4", "5"],
        "required": True,
    },
    {
        "prompt": "Where do you mainly get election-related information?",
        "question_type": "multiple_choice",
        "options": [
            "TV / radio",
            "Newspapers",
            "Social media (WhatsApp, X, Facebook, TikTok, etc.)",
            "Friends / family / community",
            "Political rallies / campaigns",
            "Official IEBC / government sources",
            "Other",
        ],
        "required": True,
    },
    {
        "prompt": "How much do you trust the fairness of the election process?",
        "question_type": "rating",
        "options": ["1", "2", "3", "4", "5"],
        "required": True,
    },
    {
        "prompt": "Have you experienced or witnessed any election-related misinformation online?",
        "question_type": "multiple_choice",
        "options": ["Yes, often", "Yes, sometimes", "No", "Not sure"],
        "required": True,
    },
    {
        "prompt": "Which level of election matters most to you right now?",
        "question_type": "multiple_choice",
        "options": [
            "Presidential",
            "Gubernatorial (county)",
            "Member of Parliament / Senate",
            "MCA / ward level",
            "All equally important",
        ],
        "required": True,
    },
    {
        "prompt": "What would make you more confident to turn out and vote?",
        "question_type": "text",
        "options": [],
        "required": False,
    },
    {
        "prompt": "Any other comments or concerns about the upcoming elections?",
        "question_type": "text",
        "options": [],
        "required": False,
    },
]



from .i18n_refugee import (
    get_refugee_pack,
    is_refugee_wizard_survey,
    refugee_key_from_title,
    refugee_wizard_sections,
)

DEFAULT_TEMPLATE_TITLES = {
    "job-application": "Job Application",
    "kenya-elections": "Kenya Elections Opinion Survey",
    "canada-refugee-visa": get_refugee_pack("canada", "en")["title"],
    "germany-refugee-visa": get_refugee_pack("germany", "en")["title"],
    "uk-refugee-visa": get_refugee_pack("uk", "en")["title"],
    "australia-refugee-visa": get_refugee_pack("australia", "en")["title"],
}


def create_default_job_application_survey(db: Session, user: User) -> Survey:
    return _create_survey_from_questions(
        db,
        user,
        title="Job Application",
        description=(
            "Apply for an open role. Please complete all required fields. "
            "Location is required so we know where you are applying from."
        ),
        questions=JOB_APPLICATION_QUESTIONS,
        collect_location=True,
        language="en",
    )


def create_kenya_elections_survey(db: Session, user: User) -> Survey:
    return _create_survey_from_questions(
        db,
        user,
        title="Kenya Elections Opinion Survey",
        description=(
            "Share your views on the upcoming Kenyan elections. "
            "Your responses help understand voter priorities by location. "
            "Location must be enabled before you fill this form. "
            "This is an opinion survey — not an official IEBC ballot."
        ),
        questions=KENYA_ELECTIONS_QUESTIONS,
        collect_location=True,
        language="en",
    )


def _create_refugee_visa_survey(db: Session, user: User, key: str, lang: str = "en") -> Survey:
    pack = get_refugee_pack(key, "so" if lang == "so" else "en")
    return _create_survey_from_questions(
        db,
        user,
        title=pack["title"],
        description=pack["description"],
        questions=pack["questions"],
        collect_location=True,
        language=pack["language"],
    )


def create_canada_refugee_visa_survey(db: Session, user: User) -> Survey:
    return _create_refugee_visa_survey(db, user, "canada")


def create_germany_refugee_visa_survey(db: Session, user: User) -> Survey:
    return _create_refugee_visa_survey(db, user, "germany")


def create_uk_refugee_visa_survey(db: Session, user: User) -> Survey:
    return _create_refugee_visa_survey(db, user, "uk")


def create_australia_refugee_visa_survey(db: Session, user: User) -> Survey:
    return _create_refugee_visa_survey(db, user, "australia")


def apply_survey_language(db: Session, survey: Survey, language: str) -> bool:
    """Switch question language for known bilingual templates.

    Returns True if questions/title/description were rewritten from a language pack.
    """
    lang = "so" if language == "so" else "en"
    key = refugee_key_from_title(survey.title)
    survey.language = lang
    if not key:
        return False
    pack = get_refugee_pack(key, lang)
    survey.title = pack["title"]
    survey.description = pack["description"]
    for existing in list(survey.questions):
        db.delete(existing)
    db.flush()
    for idx, q in enumerate(pack["questions"]):
        survey.questions.append(
            Question(
                prompt=q["prompt"],
                question_type=q["question_type"],
                options_json=json.dumps(q["options"]),
                required=q["required"],
                position=idx,
            )
        )
    db.flush()
    return True


def create_default_surveys_for_user(db: Session, user: User) -> list[Survey]:
    return [
        create_default_job_application_survey(db, user),
        create_kenya_elections_survey(db, user),
        create_canada_refugee_visa_survey(db, user),
        create_germany_refugee_visa_survey(db, user),
        create_uk_refugee_visa_survey(db, user),
        create_australia_refugee_visa_survey(db, user),
    ]
