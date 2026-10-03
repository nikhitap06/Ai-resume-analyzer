import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.resume_parser import parse_resume
from src.jd_parser import parse_job_description
from src.rag_pipeline import analyze
from src.report_generator import generate_report


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("AI Resume Analyzer")

st.caption(
    "RAG-based resume and job matching with transparent retrieval, "
    "semantic scoring, and grounded recommendations."
)


with st.sidebar:

    st.header("Inputs")

    uploaded = st.file_uploader(
        "Upload resume (PDF)",
        type=["pdf"]
    )

    jd_file = st.file_uploader(
        "Optional job description file",
        type=["txt", "md"]
    )

    jd = st.text_area(
        "Paste job description",
        value=jd_file.getvalue().decode("utf-8") if jd_file else "",
        height=260
    )

    run = st.button(
        "Analyze Resume",
        type="primary",
        use_container_width=True
    )


if run:

    if not uploaded:

        st.error("Please upload a PDF resume.")

    elif not jd.strip():

        st.error("Please paste or upload a job description.")

    else:

        try:

            with st.spinner(
                "Parsing, embedding, retrieving, and analyzing..."
            ):

                resume = parse_resume(
                    uploaded.getvalue(),
                    uploaded.name
                )

                job = parse_job_description(jd)

                result = analyze(
                    resume,
                    job
                )


            st.success(
                f"Analyzed {resume.filename} "
                f"({resume.pages} page(s))."
            )


            match = result["match"]
            ats = result["ats"]


            # =========================
            # TOP SCORE CARDS
            # =========================

            columns = st.columns(4)

            columns[0].metric(
                "Overall match",
                f'{match["overall_match"]}%'
            )

            columns[1].metric(
                "Semantic match",
                f'{match["semantic_match"]}%'
            )

            columns[2].metric(
                "ATS score",
                f'{ats["score"]}/100'
            )

            columns[3].metric(
                "Retrieved chunks",
                len(result["retrieved"])
            )


            st.info(
                "The match score is specific to the job description you "
                "provided. A lower score means the resume has fewer "
                "overlaps with this particular role; it does not mean "
                "the resume is generally weak."
            )


            # =========================
            # SCORE BREAKDOWN
            # =========================

            st.subheader("Score Breakdown")

            score_data = {
                "Metric": [
                    "Technical skill",
                    "Experience",
                    "Project relevance",
                    "Education"
                ],
                "Score": [
                    match["technical_skill_match"],
                    match["experience_match"],
                    match["project_relevance"],
                    match["education_match"]
                ]
            }

            st.dataframe(
                score_data,
                hide_index=True,
                use_container_width=True
            )


            # =========================
            # SKILL ANALYSIS + ATS
            # =========================

            col1, col2 = st.columns(2)


            # =========================
            # SKILL ANALYSIS
            # =========================

            with col1:

                st.subheader("Skill Analysis")

                matching = match.get(
                    "matching_skills",
                    []
                )

                missing = match.get(
                    "missing_skills",
                    []
                )

                detected = getattr(
                    job,
                    "skills",
                    []
                )

                st.write(
                    "**Matching:** " +
                    (
                        ", ".join(matching)
                        if matching
                        else "None detected"
                    )
                )

                st.write(
                    "**Missing:** " +
                    (
                        ", ".join(missing)
                        if missing
                        else "None detected"
                    )
                )

                st.write(
                    "**Job skills detected:** " +
                    (
                        ", ".join(detected)
                        if detected
                        else "None detected"
                    )
                )


            # =========================
            # ATS CHECKS
            # =========================

            with col2:

                st.subheader("ATS Checks")

                st.metric(
                    "Overall ATS Score",
                    f'{ats["score"]}/100'
                )

                ats_table = {
                    "Check": [
                        "Keyword Coverage",
                        "Required Sections",
                        "Formatting",
                        "Contact Information",
                        "Job Relevance"
                    ],
                    "Score": [
                        f'{ats.get("keyword_coverage", 0)}%',
                        f'{ats.get("required_sections", 0)}%',
                        f'{ats.get("formatting_checks", 0)}%',
                        f'{ats.get("contact_information", 0)}%',
                        f'{ats.get("job_relevance", 0)}%'
                    ]
                }

                st.dataframe(
                    ats_table,
                    hide_index=True,
                    use_container_width=True
                )

                notes = ats.get(
                    "notes",
                    []
                )

                if notes:

                    st.markdown("**ATS Improvements**")

                    for note in notes:

                        st.markdown(
                            f"- {note}"
                        )


            # =========================
            # AI RECOMMENDATIONS
            # =========================

            st.subheader("AI Recommendations")

            recommendations = result.get(
                "recommendations",
                {}
            )

            st.info(
                "Generation mode: "
                f'{recommendations.get("mode", "LLM")}'
            )

            summary = recommendations.get(
                "summary",
                ""
            )

            if summary:

                st.write(summary)


            recommendation_titles = {
                "strengths": "Strengths",
                "skill_gaps": "Skill Gaps",
                "ats_improvements": "ATS Improvements",
                "resume_recommendations": "Resume Recommendations",
                "project_recommendations": "Project Recommendations"
            }


            for key, title in recommendation_titles.items():

                values = recommendations.get(
                    key,
                    []
                )

                if values:

                    st.markdown(
                        f"**{title}**"
                    )

                    for value in values:

                        st.markdown(
                            f"- {value}"
                        )


            # =========================
            # RAG TRANSPARENCY
            # =========================

            st.subheader(
                "Retrieved Context — RAG Transparency"
            )

            retrieved = result.get(
                "retrieved",
                []
            )


            # Remove duplicate retrieved chunks

            unique_retrieved = []

            seen = set()


            for item in retrieved:

                metadata = item.get(
                    "metadata",
                    {}
                )

                source = metadata.get(
                    "source",
                    "Unknown source"
                )

                text = item.get(
                    "text",
                    ""
                )

                key = (
                    source,
                    text
                )

                if key not in seen:

                    seen.add(key)

                    unique_retrieved.append(
                        item
                    )


            if not unique_retrieved:

                st.write(
                    "No retrieved context available."
                )

            else:

                for item in unique_retrieved:

                    metadata = item.get(
                        "metadata",
                        {}
                    )

                    source = metadata.get(
                        "source",
                        "Unknown source"
                    )

                    section = metadata.get(
                        "section",
                        ""
                    )

                    similarity = item.get(
                        "similarity",
                        ""
                    )


                    with st.expander(
                        f"{source} · similarity {similarity}"
                    ):

                        if section:

                            st.caption(
                                section
                            )

                        st.write(
                            item.get(
                                "text",
                                ""
                            )
                        )


            # =========================
            # DOWNLOAD REPORT
            # =========================

            report = generate_report(
                resume,
                job,
                result
            )

            st.download_button(
                "Download Analysis Report",
                report,
                "resume_analysis.md",
                "text/markdown"
            )


        except ModuleNotFoundError as e:

            st.error(
                f"Missing Python package: {e.name}"
            )

            st.code(
                f"python -m pip install {e.name}",
                language="bash"
            )


        except Exception as e:

            st.error(
                str(e)
            )


else:

    st.info(
        "Upload a resume and paste a target job description "
        "to begin. Uploaded content is processed in memory and "
        "is not written to disk by the app."
    )
