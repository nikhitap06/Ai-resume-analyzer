import re
from .embeddings import EmbeddingModel, cosine_similarity


def _pct(x):
    return round(max(0, min(1, x)) * 100, 1)


def _normalize_skill(skill):
    skill = skill.lower().strip()

    replacements = {
        "scikit learn": "scikit-learn",
        "scikitlearn": "scikit-learn",
        "natural language processing": "nlp",
        "ms excel": "excel",
        "microsoft excel": "excel",
        "powerbi": "power bi",
        "python programming": "python"
    }

    return replacements.get(skill, skill)


def _education_level(text):
    text = (text or "").lower()

    patterns = {
        "phd": [
            r"\bph\.?d\b",
            r"\bdoctorate\b",
            r"\bdoctoral\b"
        ],

        "master": [
            r"\bm\.?\s*tech\b",
            r"\bm\.?\s*e\b",
            r"\bmca\b",
            r"\bmba\b",
            r"\bmaster(?:'s)?\b",
            r"\bpostgraduate\b"
        ],

        "bachelor": [
            r"\bb\.?\s*tech\b",
            r"\bb\.?\s*e\b",
            r"\bbca\b",
            r"\bbba\b",
            r"\bbachelor(?:'s)?\b",
            r"\bundergraduate\b"
        ]
    }

    for level, values in patterns.items():

        for pattern in values:

            if re.search(pattern, text):
                return level

    return None


def _job_requires_education(job_text):

    text = (job_text or "").lower()

    education_patterns = [

        r"\bbachelor(?:'s)?\s+(?:degree|in)\b",

        r"\bb\.?\s*tech\b",

        r"\bb\.?\s*e\b",

        r"\bbtech\b",

        r"\bm\.?\s*tech\b",

        r"\bmtech\b",

        r"\bm\.?\s*e\b",

        r"\bmaster(?:'s)?\s+(?:degree|in)\b",

        r"\bundergraduate\s+degree\b",

        r"\bpostgraduate\s+degree\b",

        r"\bph\.?d\b",

        r"\bdoctorate\b"
    ]

    return any(
        re.search(
            pattern,
            text
        )
        for pattern in education_patterns
    )


def _education_match(
    resume_text,
    job_text
):

    if not _job_requires_education(job_text):

        return None

    resume_level = _education_level(
        resume_text
    )

    if resume_level is None:

        return 0.0

    job_text = job_text.lower()

    if any(
        term in job_text
        for term in [
            "phd",
            "ph.d",
            "doctorate",
            "doctoral"
        ]
    ):

        return (
            100.0
            if resume_level == "phd"
            else 0.0
        )

    if any(
        term in job_text
        for term in [
            "master",
            "master's",
            "m.tech",
            "mtech",
            "m.e",
            "m.e.",
            "postgraduate"
        ]
    ):

        return (
            100.0
            if resume_level in [
                "master",
                "phd"
            ]
            else 0.0
        )

    if any(
        term in job_text
        for term in [
            "bachelor",
            "bachelor's",
            "b.tech",
            "btech",
            "b.e",
            "b.e.",
            "undergraduate"
        ]
    ):

        return (
            100.0
            if resume_level in [
                "bachelor",
                "master",
                "phd"
            ]
            else 0.0
        )

    return None


def _experience_score(resume_text):

    text = (resume_text or "").lower()

    experience_terms = [
        "intern",
        "internship",
        "experience",
        "worked",
        "developer",
        "engineer",
        "analyst",
        "research",
        "professional experience"
    ]

    matches = sum(
        1
        for term in experience_terms
        if term in text
    )

    if matches == 0:
        return 0.0

    if matches == 1:
        return 50.0

    return 100.0


def _project_score(
    resume_text,
    job_text,
    embedder
):

    resume_lower = (
        resume_text or ""
    ).lower()

    project_terms = [
        "project",
        "projects",
        "built",
        "developed",
        "implemented",
        "created",
        "deployed"
    ]

    project_present = any(
        term in resume_lower
        for term in project_terms
    )

    if not project_present:

        return 0.0

    resume_vector = embedder.encode(
        (resume_text or "")[:3000]
    )[0]

    job_vector = embedder.encode(
        (job_text or "")[:3000]
    )[0]

    similarity = cosine_similarity(
        resume_vector,
        job_vector
    )

    similarity = max(
        0,
        similarity
    )

    return _pct(similarity)


def calculate_similarity(
    resume_text,
    job_text,
    resume_skills=None,
    job_skills=None,
    embedder=None
):

    embedder = (
        embedder
        or EmbeddingModel()
    )

    resume_text = (
        resume_text or ""
    )

    job_text = (
        job_text or ""
    )

    vectors = embedder.encode(
        [
            resume_text,
            job_text
        ]
    )

    semantic_similarity = cosine_similarity(
        vectors[0],
        vectors[1]
    )

    semantic = _pct(
        (semantic_similarity + 1) / 2
    )

    resume_skills_normalized = {
        _normalize_skill(skill)
        for skill in (
            resume_skills or []
        )
    }

    job_skills_normalized = {
        _normalize_skill(skill)
        for skill in (
            job_skills or []
        )
    }

    if job_skills_normalized:

        matching_skills = (
            resume_skills_normalized
            &
            job_skills_normalized
        )

        technical = _pct(
            len(matching_skills)
            /
            len(job_skills_normalized)
        )

        missing_skills = (
            job_skills_normalized
            -
            resume_skills_normalized
        )

    else:

        matching_skills = set()

        missing_skills = set()

        technical = 0.0


    experience = _experience_score(
        resume_text
    )


    project = _project_score(
        resume_text,
        job_text,
        embedder
    )


    education = _education_match(
        resume_text,
        job_text
    )


    education_for_score = (
        education
        if education is not None
        else 0.0
    )


    semantic_weight = 0.45
    technical_weight = 0.30
    experience_weight = 0.10
    project_weight = 0.10
    education_weight = 0.05


    if education is None:

        total_weight = (
            semantic_weight
            +
            technical_weight
            +
            experience_weight
            +
            project_weight
        )

        overall = (
            semantic_weight * semantic
            +
            technical_weight * technical
            +
            experience_weight * experience
            +
            project_weight * project
        ) / total_weight

    else:

        total_weight = (
            semantic_weight
            +
            technical_weight
            +
            experience_weight
            +
            project_weight
            +
            education_weight
        )

        overall = (
            semantic_weight * semantic
            +
            technical_weight * technical
            +
            experience_weight * experience
            +
            project_weight * project
            +
            education_weight * education_for_score
        ) / total_weight


    overall = round(
        overall,
        1
    )


    return {
        "semantic_match": semantic,

        "technical_skill_match": technical,

        "experience_match": experience,

        "project_relevance": project,

        "education_match": education,

        "overall_match": overall,

        "matching_skills": sorted(
            matching_skills
        ),

        "missing_skills": sorted(
            missing_skills
        )
    }
