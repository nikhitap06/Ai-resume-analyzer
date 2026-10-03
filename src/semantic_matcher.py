import re
import numpy as np
from .embeddings import EmbeddingModel, cosine_similarity


def _pct(x):
    return round(max(0, min(1, x)) * 100, 1)


def _normalize_skill(skill):
    skill = skill.lower().strip()

    replacements = {
        "scikit learn": "scikit-learn",
        "scikitlearn": "scikit-learn",
        "natural language processing": "nlp",
        "machine learning": "machine learning",
        "artificial intelligence": "artificial intelligence",
        "power bi": "power bi",
        "ms excel": "excel",
        "microsoft excel": "excel",
        "pytorch": "pytorch",
        "tensorflow": "tensorflow",
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
            r"\bm\.?tech\b",
            r"\bm\.?e\b",
            r"\bmca\b",
            r"\bmba\b",
            r"\bmaster(?:'s)?\b",
            r"\bpostgraduate\b"
        ],
        "bachelor": [
            r"\bb\.?tech\b",
            r"\bb\.?e\b",
            r"\bbca\b",
            r"\bbba\b",
            r"\bbachelor(?:'s)?\b",
            r"\bundergraduate\b",
            r"\bdegree\b"
        ]
    }

    for level, values in patterns.items():
        for pattern in values:
            if re.search(pattern, text):
                return level

    return None


def _job_requires_education(job_text):
    text = (job_text or "").lower()

    education_terms = [
        "bachelor",
        "bachelor's",
        "b.tech",
        "btech",
        "b.e.",
        "b.e",
        "undergraduate",
        "master",
        "master's",
        "m.tech",
        "mtech",
        "m.e.",
        "m.e",
        "postgraduate",
        "phd",
        "doctorate",
        "degree"
    ]

    return any(term in text for term in education_terms)


def _education_match(resume_text, job_text):
    if not _job_requires_education(job_text):
        return None

    resume_level = _education_level(resume_text)

    if resume_level is None:
        return 0.0

    job_text = job_text.lower()

    if any(
        term in job_text
        for term in [
            "phd",
            "doctorate",
            "doctoral"
        ]
    ):
        return 100.0 if resume_level == "phd" else 0.0

    if any(
        term in job_text
        for term in [
            "master",
            "master's",
            "m.tech",
            "mtech",
            "m.e.",
            "m.e",
            "postgraduate"
        ]
    ):
        return 100.0 if resume_level in ["master", "phd"] else 0.0

    if any(
        term in job_text
        for term in [
            "bachelor",
            "bachelor's",
            "b.tech",
            "btech",
            "b.e.",
            "b.e",
            "undergraduate",
            "degree"
        ]
    ):
        return 100.0 if resume_level in ["bachelor", "master", "phd"] else 0.0

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
        1 for term in experience_terms
        if term in text
    )

    if matches == 0:
        return 0.0

    if matches == 1:
        return 50.0

    return 100.0


def _project_score(resume_text, job_text, embedder):
    resume_lower = (resume_text or "").lower()

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

    similarity = max(0, similarity)

    return _pct(similarity)


def calculate_similarity(
    resume_text,
    job_text,
    resume_skills=None,
    job_skills=None,
    embedder=None
):

    embedder = embedder or EmbeddingModel()

    resume_text = resume_text or ""
    job_text = job_text or ""

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
        for skill in (resume_skills or [])
    }

    job_skills_normalized = {
        _normalize_skill(skill)
        for skill in (job_skills or [])
    }

    if job_skills_normalized:

        matching_skills = (
            resume_skills_normalized &
            job_skills_normalized
        )

        technical = _pct(
            len(matching_skills) /
            len(job_skills_normalized)
        )

        missing_skills = (
            job_skills_normalized -
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

    weights = {
        "semantic": 0.45,
        "technical": 0.30,
        "experience": 0.10,
        "project": 0.10,
        "education": 0.05
    }

    active_weights = dict(weights)

    if education is None:
        active_weights.pop("education")

    total_weight = sum(
        active_weights.values()
    )

    overall = (
        weights["semantic"] * semantic +
        weights["technical"] * technical +
        weights["experience"] * experience +
        weights["project"] * project +
        (
            weights["education"] *
            education_for_score
        )
    )

    if education is None:
        overall = (
            weights["semantic"] * semantic +
            weights["technical"] * technical +
            weights["experience"] * experience +
            weights["project"] * project
        )

    overall = round(
        overall / total_weight,
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
