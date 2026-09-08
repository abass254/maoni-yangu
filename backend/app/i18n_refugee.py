"""Bilingual (en/so) content for refugee visa intake templates."""

from __future__ import annotations

from typing import Literal

Lang = Literal["en", "so"]

REFUGEE_KEYS = ("canada", "germany", "uk", "australia")

COUNTRY_LABELS: dict[str, dict[Lang, str]] = {
    "canada": {"en": "Canada", "so": "Kanada"},
    "germany": {"en": "Germany", "so": "Jarmalka"},
    "uk": {"en": "United Kingdom (UK)", "so": "Boqortooyada Midowday (UK)"},
    "australia": {"en": "Australia", "so": "Australia"},
}

AGENCIES = {
    "canada": "IRCC",
    "germany": "BAMF",
    "uk": "UKVI / Home Office",
    "australia": "Home Affairs",
}

TITLES: dict[str, dict[Lang, str]] = {
    "canada": {
        "en": "Refugee Visa Intake — Canada",
        "so": "Codsiga Fiisaha Qaxootiga — Kanada",
    },
    "germany": {
        "en": "Refugee Visa Intake — Germany",
        "so": "Codsiga Fiisaha Qaxootiga — Jarmalka",
    },
    "uk": {
        "en": "Refugee Visa Intake — UK",
        "so": "Codsiga Fiisaha Qaxootiga — UK",
    },
    "australia": {
        "en": "Refugee Visa Intake — Australia",
        "so": "Codsiga Fiisaha Qaxootiga — Australia",
    },
}

PATHWAYS: dict[str, dict[Lang, list[str]]] = {
    "canada": {
        "en": [
            "Refugee protection",
            "Family / private sponsorship",
            "Organization sponsorship",
            "Humanitarian / urgent protection visa",
            "Not sure — I need guidance",
        ],
        "so": [
            "Ilaalin qaxooti (refugee protection)",
            "Is-dejin qoys / sponsor qoys",
            "Is-dejin hay'ad / private sponsorship",
            "Fiiso bini'aadantinimo / urgent protection",
            "Ma hubo — waxaan rabaa hagid",
        ],
    },
    "germany": {
        "en": [
            "Asylum / refugee protection (BAMF)",
            "Resettlement",
            "Family reunification",
            "Humanitarian / urgent protection visa",
            "Not sure — I need guidance",
        ],
        "so": [
            "Asyl / ilaalin qaxooti (BAMF)",
            "Is-dejin (resettlement)",
            "Is-dejin qoys / family reunification",
            "Fiiso bini'aadantinimo / urgent protection",
            "Ma hubo — waxaan rabaa hagid",
        ],
    },
    "uk": {
        "en": [
            "Asylum / refugee protection (Home Office)",
            "UK Resettlement Scheme",
            "Family reunion",
            "Humanitarian / urgent protection visa",
            "Not sure — I need guidance",
        ],
        "so": [
            "Asylum / ilaalin qaxooti (Home Office)",
            "UK Resettlement Scheme",
            "Is-dejin qoys / family reunion",
            "Fiiso bini'aadantinimo / urgent protection",
            "Ma hubo — waxaan rabaa hagid",
        ],
    },
    "australia": {
        "en": [
            "Refugee / humanitarian visa (Home Affairs)",
            "Resettlement",
            "Family sponsorship",
            "Humanitarian / urgent protection visa",
            "Not sure — I need guidance",
        ],
        "so": [
            "Refugee / humanitarian visa (Home Affairs)",
            "Is-dejin (resettlement)",
            "Is-dejin qoys / family sponsorship",
            "Fiiso bini'aadantinimo / urgent protection",
            "Ma hubo — waxaan rabaa hagid",
        ],
    },
}

WIZARD_SECTIONS: dict[Lang, list[tuple[str, str, range]]] = {
    "en": [
        ("bio", "1. Personal details", range(0, 8)),
        ("situation", "2. Current situation", range(8, 12)),
        ("protection", "3. Protection claim", range(12, 16)),
        ("documents", "4. Documents & history", range(16, 19)),
        ("support", "5. Support & contact", range(19, 26)),
    ],
    "so": [
        ("bio", "1. Macluumaadka shakhsiyeed", range(0, 8)),
        ("situation", "2. Xaaladdaada hadda", range(8, 12)),
        ("protection", "3. Sababta ilaalinta", range(12, 16)),
        ("documents", "4. Dukumeentiyada iyo taariikhda", range(16, 19)),
        ("support", "5. Caawimada iyo xiriirka", range(19, 26)),
    ],
}


def description_for(key: str, lang: Lang) -> str:
    country = COUNTRY_LABELS[key][lang]
    agency = AGENCIES[key]
    if lang == "so":
        return (
            f"Foomka horudhaca ee ururinta macluumaadka dadka raadsanaya ilaalin "
            f"qaxooti / fiiso bini'aadantinimo {country}. Goobta waa in la daaraa ka hor "
            f"intaadan buuxin. Kani ma aha foomka rasmiga ah ee {agency}, mana aha talo sharci."
        )
    return (
        f"Intake form for people seeking refugee protection / a humanitarian visa for "
        f"{country}. Location must be enabled before you fill this form. "
        f"This is not an official {agency} form and is not legal advice."
    )


def _questions_en(country: str, pathways: list[str]) -> list[dict]:
    return [
        {"prompt": "Full name (as on your documents)", "question_type": "text", "options": [], "required": True},
        {"prompt": "Date of birth (DD/MM/YYYY)", "question_type": "text", "options": [], "required": True},
        {
            "prompt": "Gender",
            "question_type": "multiple_choice",
            "options": ["Male", "Female", "Prefer not to say"],
            "required": True,
        },
        {"prompt": "Country of birth", "question_type": "text", "options": [], "required": True},
        {"prompt": "Nationality / citizenship(s)", "question_type": "text", "options": [], "required": True},
        {
            "prompt": "Marital status",
            "question_type": "multiple_choice",
            "options": [
                "Single",
                "Married",
                "Common-law / partnered",
                "Divorced",
                "Widowed",
                "Prefer not to say",
            ],
            "required": True,
        },
        {
            "prompt": "Number of family members travelling with you or dependent on you",
            "question_type": "multiple_choice",
            "options": ["Just me", "1–2", "3–4", "5 or more"],
            "required": True,
        },
        {
            "prompt": "Names and ages of dependent family members (if any)",
            "question_type": "text",
            "options": [],
            "required": False,
        },
        {
            "prompt": "Where do you live now? (country + city / camp)",
            "question_type": "text",
            "options": [],
            "required": True,
        },
        {
            "prompt": "Current residence status",
            "question_type": "multiple_choice",
            "options": [
                "Refugee camp / UNHCR",
                "City — I have legal residence status",
                "City — I do not have legal residence status",
                "Immigration detention",
                "Other",
            ],
            "required": True,
        },
        {
            "prompt": "Do you have UNHCR (or equivalent) registration?",
            "question_type": "multiple_choice",
            "options": ["Yes", "No", "Not sure", "Application in progress"],
            "required": True,
        },
        {
            "prompt": "UNHCR registration / case number (if you have one)",
            "question_type": "text",
            "options": [],
            "required": False,
        },
        {
            "prompt": "Main reason you are seeking protection / refugee status?",
            "question_type": "multiple_choice",
            "options": [
                "Political persecution",
                "War / conflict",
                "Religious persecution",
                "Gender-based persecution",
                "Ethnic / clan persecution",
                "Persecution for opinion / belief",
                "Personal risk / targeted threat",
                "Other",
            ],
            "required": True,
        },
        {
            "prompt": f"Briefly explain why you need protection in {country}",
            "question_type": "text",
            "options": [],
            "required": True,
        },
        {
            "prompt": "Can you safely return to your home country?",
            "question_type": "multiple_choice",
            "options": ["No", "Yes", "Not sure"],
            "required": True,
        },
        {
            "prompt": "If not, what risk do you face?",
            "question_type": "text",
            "options": [],
            "required": False,
        },
        {
            "prompt": "Do you have a passport or identity document?",
            "question_type": "multiple_choice",
            "options": [
                "Valid passport",
                "Expired passport",
                "Other ID card",
                "No documents",
            ],
            "required": True,
        },
        {
            "prompt": "Have you previously applied for a visa / protection in another country?",
            "question_type": "multiple_choice",
            "options": [
                "No",
                "Yes — approved",
                "Yes — refused",
                "Yes — still pending",
            ],
            "required": True,
        },
        {
            "prompt": "If yes, which country and what was the outcome?",
            "question_type": "text",
            "options": [],
            "required": False,
        },
        {
            "prompt": "Type of support you are seeking",
            "question_type": "multiple_choice",
            "options": pathways,
            "required": True,
        },
        {
            "prompt": "Current urgency / risk level",
            "question_type": "rating",
            "options": ["1", "2", "3", "4", "5"],
            "required": True,
        },
        {
            "prompt": "Phone or WhatsApp number we can reach you on",
            "question_type": "text",
            "options": [],
            "required": True,
        },
        {"prompt": "Email (if you have one)", "question_type": "text", "options": [], "required": False},
        {"prompt": "Languages you speak", "question_type": "text", "options": [], "required": True},
        {
            "prompt": "Do you need an interpreter when speaking with the case team?",
            "question_type": "multiple_choice",
            "options": ["Yes", "No", "Sometimes"],
            "required": True,
        },
        {
            "prompt": "Anything else important you want the case team to know",
            "question_type": "text",
            "options": [],
            "required": False,
        },
    ]


def _questions_so(country: str, pathways: list[str]) -> list[dict]:
    return [
        {
            "prompt": "Magacaaga buuxa (sida uu ku qoran yahay dukumeentigaaga)",
            "question_type": "text",
            "options": [],
            "required": True,
        },
        {"prompt": "Taariikhda dhalashada (QQ/BB/SSSS)", "question_type": "text", "options": [], "required": True},
        {
            "prompt": "Jinsiga",
            "question_type": "multiple_choice",
            "options": ["Lab", "Dhedig", "Waxaan doorbidayaa inaan sheegin"],
            "required": True,
        },
        {"prompt": "Waddanka aad ku dhalatay", "question_type": "text", "options": [], "required": True},
        {"prompt": "Jinsiyadda(ha) aad haysato", "question_type": "text", "options": [], "required": True},
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
        {"prompt": "Iimayl (haddii aad haysato)", "question_type": "text", "options": [], "required": False},
        {"prompt": "Luqadaha aad ku hadasho", "question_type": "text", "options": [], "required": True},
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


def get_refugee_pack(key: str, lang: Lang = "en") -> dict:
    if key not in REFUGEE_KEYS:
        raise KeyError(key)
    lang = "so" if lang == "so" else "en"
    country = COUNTRY_LABELS[key][lang]
    pathways = PATHWAYS[key][lang]
    questions = (
        _questions_so(country, pathways) if lang == "so" else _questions_en(country, pathways)
    )
    return {
        "key": key,
        "language": lang,
        "title": TITLES[key][lang],
        "description": description_for(key, lang),
        "questions": questions,
    }


def refugee_key_from_title(title: str) -> str | None:
    for key in REFUGEE_KEYS:
        for lang in ("en", "so"):
            if title == TITLES[key][lang]:
                return key
    if title.startswith("Refugee Visa Intake —"):
        tail = title.split("—", 1)[-1].strip().lower()
        mapping = {
            "canada": "canada",
            "germany": "germany",
            "uk": "uk",
            "united kingdom (uk)": "uk",
            "australia": "australia",
        }
        return mapping.get(tail)
    if title.startswith("Codsiga Fiisaha Qaxootiga"):
        if "Kanada" in title:
            return "canada"
        if "Jarmalka" in title:
            return "germany"
        if "Australia" in title:
            return "australia"
        if "UK" in title:
            return "uk"
    return None


def all_refugee_titles() -> set[str]:
    titles: set[str] = set()
    for key in REFUGEE_KEYS:
        titles.add(TITLES[key]["en"])
        titles.add(TITLES[key]["so"])
    return titles


def is_refugee_wizard_survey(title: str) -> bool:
    return refugee_key_from_title(title) is not None


def refugee_wizard_sections(questions: list, lang: Lang = "en") -> list[dict]:
    lang = "so" if lang == "so" else "en"
    ordered = sorted(questions, key=lambda q: q.position)
    sections: list[dict] = []
    for section_id, title, positions in WIZARD_SECTIONS[lang]:
        ids = [ordered[i].id for i in positions if i < len(ordered)]
        if ids:
            sections.append({"id": section_id, "title": title, "question_ids": ids})
    covered = {qid for s in sections for qid in s["question_ids"]}
    leftover = [q.id for q in ordered if q.id not in covered]
    if leftover:
        extra_title = (
            f"{len(sections) + 1}. Other questions"
            if lang == "en"
            else f"{len(sections) + 1}. Su'aalo kale"
        )
        sections.append({"id": "extra", "title": extra_title, "question_ids": leftover})
    return sections
