import re
def _contains_any(text, terms):
    text = (text or "").lower()

    return any(
        term.lower() in text
        for term in terms
    )
def _contact_score(resume):
    contact = resume.contact
    email = (
        contact.get("email", "Not detected")
        != "Not detected"
    )
    phone = (
        contact.get("phone", "Not detected")
        != "Not detected"
    )

    linkedin = _contains_any(
        resume.text,
        [
            "linkedin.com",
            "linkedin"
        ]
    )

    github = _contains_any(
        resume.text,
        [
            "github.com",
            "github"
        ]
    )

    detected = {
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github
    }

    score = round(
        sum(detected.values()) /
        len(detected) *
        100,
        1
    )

    return score, detected


def _section_score(resume):
    text = (resume.text or "").lower()

    sections = [
        str(section).lower()
        for section in resume.sections
    ]

    checks = {
        "Experience": (
            "experience" in text or
            any(
                "experience" in section
                for section in sections
            )
        ),

        "Education": (
            "education" in text or
            any(
                "education" in section
                for section in sections
            )
        ),

        "Projects": (
            "project" in text or
            any(
                "project" in section
                for section in sections
            )
        ),

        "Skills": (
            "skill" in text or
            any(
                "skill" in section
                for section in sections
            )
        )
    }

    score = round(
        sum(checks.values()) /
        len(checks) *
        100,
        1
    )

    return score, checks


def _keyword_score(resume_text, job_skills):
    text = (resume_text or "").lower()

    if not job_skills:
        return 0.0

    aliases = {
        "scikit-learn": [
            "scikit-learn",
            "scikit learn",
            "sklearn"
        ],

        "nlp": [
            "nlp",
            "natural language processing"
        ],

        "excel": [
            "excel",
            "microsoft excel",
            "ms excel"
        ],

        "power bi": [
            "power bi",
            "powerbi"
        ],

        "machine learning": [
            "machine learning",
            "ml"
        ],

        "artificial intelligence": [
            "artificial intelligence",
            "ai"
        ],

        "pytorch": [
            "pytorch"
        ],

        "tensorflow": [
            "tensorflow"
        ]
    }

    matched = 0

    for skill in job_skills:

        skill_lower = skill.lower().strip()

        possible_terms = aliases.get(
            skill_lower,
            [skill_lower]
        )

        if any(
            term in text
            for term in possible_terms
        ):
            matched += 1

    return round(
        matched /
        len(job_skills) *
        100,
        1
    )


def _education_requirement(job_text):
    text = (job_text or "").lower()

    terms = [
        "bachelor",
        "bachelor's",
        "b.tech",
        "btech",
        "b.e.",
        "b.e",
        "degree",
        "master",
        "master's",
        "m.tech",
        "mtech",
        "m.e.",
        "m.e",
        "phd",
        "doctorate"
    ]

    return any(
        term in text
        for term in terms
    )


def _formatting_score(resume):
    text = resume.text or ""

    score = 100

    if len(text.strip()) < 250:
        score -= 30

    if re.search(
        r'[^\x00-\x7F]{10}',
        text
    ):
        score -= 10

    if len(text) > 15000:
        score -= 10

    return max(
        0,
        score
    )


def analyze_ats(resume, job):

    text = resume.text.lower()
    jd = job.text.lower()

    section_score, section_checks = (
        _section_score(resume)
    )

    contact_score, contact_checks = (
        _contact_score(resume)
    )

    keyword_score = _keyword_score(
        text,
        job.skills
    )

    formatting = _formatting_score(
        resume
    )

    education_required = (
        _education_requirement(jd)
    )

    if education_required:
        job_relevance = keyword_score
    else:
        job_relevance = keyword_score

    total = round(
        (
            0.35 * keyword_score +
            0.25 * section_score +
            0.15 * formatting +
            0.15 * job_relevance +
            0.10 * contact_score
        ),
        1
    )

    notes = []

    if section_score < 100:
        notes.append(
            "Review resume sections and add "
            "important sections where appropriate."
        )
    else:
        notes.append(
            "Core resume sections detected."
        )

    if keyword_score < 70:
        notes.append(
            "Add job-specific terms only "
            "where truthful and supported by "
            "your actual experience."
        )
    else:
        notes.append(
            "Good coverage of detected job skills."
        )

    return {
        "score": total,

        "keyword_coverage": keyword_score,

        "required_sections": section_score,

        "formatting_checks": formatting,

        "contact_information": contact_score,

        "job_relevance": round(
            job_relevance,
            1
        ),

        "contact_details": contact_checks,

        "section_details": section_checks,

        "education_requirement": (
            "Required"
            if education_required
            else "Not specified"
        ),

        "notes": notes
    }
