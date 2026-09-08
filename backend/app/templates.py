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
) -> Survey:
    survey = Survey(
        public_id=_new_public_id(),
        owner_id=user.id,
        title=title,
        description=description,
        collect_location=collect_location,
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


# Intake forms for case workers helping applicants prepare refugee /
# humanitarian pathways. Not official government forms and not legal advice.


def _refugee_visa_questions(
    country: str,
    *,
    pathways: list[str],
) -> list[dict]:
    return [
        {
            "prompt": "Magacaaga buuxa (sida uu ku qoran yahay dukumeentigaaga)",
            "question_type": "text",
            "options": [],
            "required": True,
        },
        {
            "prompt": "Taariikhda dhalashada (QQ/BB/SSSS)",
            "question_type": "text",
            "options": [],
            "required": True,
        },
        {
            "prompt": "Jinsiga",
            "question_type": "multiple_choice",
            "options": ["Lab", "Dhedig", "Waxaan doorbidayaa inaan sheegin"],
            "required": True,
        },
        {
            "prompt": "Waddanka aad ku dhalatay",
            "question_type": "text",
            "options": [],
            "required": True,
        },
        {
            "prompt": "Jinsiyadda(ha) aad haysato",
            "question_type": "text",
            "options": [],
            "required": True,
        },
        {
            "prompt": "Xaaladdaaga qoyska",
            "question_type": "multiple_choice",
            "options": [
                "Celin",
                "Guursaday / Guursatay",
                "Wada noolaan (common-law)",
                "Kala tagay",
                "Carmaalka / Carmalka",
                "Waxaan doorbidayaa inaan sheegin",
            ],
            "required": True,
        },
        {
            "prompt": "Tirada xubnaha qoyska ee kula soconaya ama ku tiirsan",
            "question_type": "multiple_choice",
            "options": ["Keliya aniga", "1–2", "3–4", "5 ama ka badan"],
            "required": True,
        },
        {
            "prompt": "Magacyada iyo da'da xubnaha qoyska ee ku tiirsan (haddii ay jiraan)",
            "question_type": "text",
            "options": [],
            "required": False,
        },
        {
            "prompt": "Hadda meeshee ku nooshahay? (waddan + magaalada / xerada)",
            "question_type": "text",
            "options": [],
            "required": True,
        },
        {
            "prompt": "Xaaladdaada hadda ee degenaanshaha",
            "question_type": "multiple_choice",
            "options": [
                "Xero qaxooti / UNHCR",
                "Magaalo — sharciga deganaanshaha waan hayaa",
                "Magaalo — sharciga deganaanshaha ma hayaa",
                "Xabsiga socdaalka / haynta",
                "Meel kale",
            ],
            "required": True,
        },
        {
            "prompt": "Ma haysaa diiwaangelin UNHCR ama hay'ad qaxooti oo la mid ah?",
            "question_type": "multiple_choice",
            "options": ["Haa", "Maya", "Ma hubo", "Codsi ayaa socda"],
            "required": True,
        },
        {
            "prompt": "Lambarka diiwaangelinta UNHCR / case number (haddii aad haysato)",
            "question_type": "text",
            "options": [],
            "required": False,
        },
        {
            "prompt": "Maxaa ugu weyn ee kaa dhigay inaad raadsato ilaalin / qaxootinimo?",
            "question_type": "multiple_choice",
            "options": [
                "Cadaadis siyaasadeed",
                "Dagaal / colaad",
                "Cabudhin diineed",
                "Cadaadis jinsi / jinsiyeed",
                "Cadaadis koox / qabiil",
                "Cadaadis ku salaysan ra'yi",
                "Khalad shaqsiyeed / khatar gaar ah",
                "Wax kale",
            ],
            "required": True,
        },
        {
            "prompt": f"Si kooban u qor sababta aad uga baahan tahay ilaalin {country}",
            "question_type": "text",
            "options": [],
            "required": True,
        },
        {
            "prompt": "Ma ku soo noqon kartaa waddankaaga ammaan?",
            "question_type": "multiple_choice",
            "options": ["Maya", "Haa", "Ma hubo"],
            "required": True,
        },
        {
            "prompt": "Haddii aysan suurtagal ahayn, maxaa khatar ah?",
            "question_type": "text",
            "options": [],
            "required": False,
        },
        {
            "prompt": "Ma haysaa baasaboor ama dukumeenti aqoonsi?",
            "question_type": "multiple_choice",
            "options": [
                "Baasaboor shaqeynaya",
                "Baasaboor dhacay",
                "Kaadh aqoonsi / ID kale",
                "Wax dukumeenti ah ma haysto",
            ],
            "required": True,
        },
        {
            "prompt": "Ma hore u codsatay fiiso / ilaalin waddan kale?",
            "question_type": "multiple_choice",
            "options": [
                "Maya",
                "Haa — waa la aqbalay",
                "Haa — waa la diiday",
                "Haa — weli socota",
            ],
            "required": True,
        },
        {
            "prompt": "Haddii haa, sheeg waddanka iyo natiijada",
            "question_type": "text",
            "options": [],
            "required": False,
        },
        {
            "prompt": "Nooca caawimada aad raadinayso",
            "question_type": "multiple_choice",
            "options": pathways,
            "required": True,
        },
        {
            "prompt": "Heerka degdegga / khatarta hadda",
            "question_type": "rating",
            "options": ["1", "2", "3", "4", "5"],
            "required": True,
        },
        {
            "prompt": "Telefoon ama WhatsApp aad kaga soo xiriiri karto",
            "question_type": "text",
            "options": [],
            "required": True,
        },
        {
            "prompt": "Iimayl (haddii aad haysato)",
            "question_type": "text",
            "options": [],
            "required": False,
        },
        {
            "prompt": "Luqadaha aad ku hadasho",
            "question_type": "text",
            "options": [],
            "required": True,
        },
        {
            "prompt": "Ma u baahan tahay turjubaan marka la kula hadlayo?",
            "question_type": "multiple_choice",
            "options": ["Haa", "Maya", "Mararka qaarkood"],
            "required": True,
        },
        {
            "prompt": "Wax kale oo muhiim ah oo aad rabto inaad la wadaagto kooxda kiiska",
            "question_type": "text",
            "options": [],
            "required": False,
        },
    ]


CANADA_REFUGEE_VISA_QUESTIONS = _refugee_visa_questions(
    "Kanada",
    pathways=[
        "Ilaalin qaxooti (refugee protection)",
        "Is-dejin qoys / sponsor qoys",
        "Is-dejin hay'ad / private sponsorship",
        "Fiiso bini'aadantinimo / urgent protection",
        "Ma hubo — waxaan rabaa hagid",
    ],
)

GERMANY_REFUGEE_VISA_QUESTIONS = _refugee_visa_questions(
    "Jarmalka",
    pathways=[
        "Asyl / ilaalin qaxooti (BAMF)",
        "Is-dejin (resettlement)",
        "Is-dejin qoys / family reunification",
        "Fiiso bini'aadantinimo / urgent protection",
        "Ma hubo — waxaan rabaa hagid",
    ],
)

UK_REFUGEE_VISA_QUESTIONS = _refugee_visa_questions(
    "Boqortooyada Midowday (UK)",
    pathways=[
        "Asylum / ilaalin qaxooti (Home Office)",
        "UK Resettlement Scheme",
        "Is-dejin qoys / family reunion",
        "Fiiso bini'aadantinimo / urgent protection",
        "Ma hubo — waxaan rabaa hagid",
    ],
)

AUSTRALIA_REFUGEE_VISA_QUESTIONS = _refugee_visa_questions(
    "Australia",
    pathways=[
        "Refugee / humanitarian visa (Home Affairs)",
        "Is-dejin (resettlement)",
        "Is-dejin qoys / family sponsorship",
        "Fiiso bini'aadantinimo / urgent protection",
        "Ma hubo — waxaan rabaa hagid",
    ],
)


DEFAULT_TEMPLATE_TITLES = {
    "job-application": "Job Application",
    "kenya-elections": "Kenya Elections Opinion Survey",
    "canada-refugee-visa": "Codsiga Fiisaha Qaxootiga — Kanada",
    "germany-refugee-visa": "Codsiga Fiisaha Qaxootiga — Jarmalka",
    "uk-refugee-visa": "Codsiga Fiisaha Qaxootiga — UK",
    "australia-refugee-visa": "Codsiga Fiisaha Qaxootiga — Australia",
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
    )


def _create_refugee_visa_survey(
    db: Session,
    user: User,
    *,
    title: str,
    country: str,
    agency: str,
    questions: list[dict],
) -> Survey:
    return _create_survey_from_questions(
        db,
        user,
        title=title,
        description=(
            f"Foomka horudhaca ee ururinta macluumaadka dadka raadsanaya ilaalin "
            f"qaxooti / fiiso bini'aadantinimo {country}. Goobta waa in la daaraa ka hor "
            f"intaadan buuxin. Kani ma aha foomka rasmiga ah ee {agency}, mana aha talo sharci."
        ),
        questions=questions,
        collect_location=True,
    )


def create_canada_refugee_visa_survey(db: Session, user: User) -> Survey:
    return _create_refugee_visa_survey(
        db,
        user,
        title=DEFAULT_TEMPLATE_TITLES["canada-refugee-visa"],
        country="Kanada",
        agency="IRCC",
        questions=CANADA_REFUGEE_VISA_QUESTIONS,
    )


def create_germany_refugee_visa_survey(db: Session, user: User) -> Survey:
    return _create_refugee_visa_survey(
        db,
        user,
        title=DEFAULT_TEMPLATE_TITLES["germany-refugee-visa"],
        country="Jarmalka",
        agency="BAMF",
        questions=GERMANY_REFUGEE_VISA_QUESTIONS,
    )


def create_uk_refugee_visa_survey(db: Session, user: User) -> Survey:
    return _create_refugee_visa_survey(
        db,
        user,
        title=DEFAULT_TEMPLATE_TITLES["uk-refugee-visa"],
        country="Boqortooyada Midowday (UK)",
        agency="UKVI / Home Office",
        questions=UK_REFUGEE_VISA_QUESTIONS,
    )


def create_australia_refugee_visa_survey(db: Session, user: User) -> Survey:
    return _create_refugee_visa_survey(
        db,
        user,
        title=DEFAULT_TEMPLATE_TITLES["australia-refugee-visa"],
        country="Australia",
        agency="Home Affairs",
        questions=AUSTRALIA_REFUGEE_VISA_QUESTIONS,
    )


def create_default_surveys_for_user(db: Session, user: User) -> list[Survey]:
    return [
        create_default_job_application_survey(db, user),
        create_kenya_elections_survey(db, user),
        create_canada_refugee_visa_survey(db, user),
        create_germany_refugee_visa_survey(db, user),
        create_uk_refugee_visa_survey(db, user),
        create_australia_refugee_visa_survey(db, user),
    ]
