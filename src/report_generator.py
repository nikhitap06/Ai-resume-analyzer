from datetime import datetime

def generate_report(resume, job, result):
    m,a,r=result['match'],result['ats'],result['recommendations']
    lines=[f'# Resume Analysis Report\n\nGenerated: {datetime.utcnow().isoformat()}Z\n\n## Summary\n{r.get("summary","")}\n\n## Scores\n\n| Metric | Score |\n|---|---:|\n| Overall match | {m["overall_match"]}% |\n| Semantic match | {m["semantic_match"]}% |\n| Technical skill match | {m["technical_skill_match"]}% |\n| ATS readiness | {a["score"]}/100 |\n\n## Skills\n\n**Matching:** {", ".join(m["matching_skills"]) or "None detected"}\n\n**Missing:** {", ".join(m["missing_skills"]) or "None detected"}\n\n## Recommendations\n']
    for key in ('strengths','skill_gaps','ats_improvements','resume_recommendations','project_recommendations'):
        lines.append(f'### {key.replace("_"," ").title()}')
        lines.extend(f'- {x}' for x in r.get(key,[]))
    lines += ['\n## Retrieved Context\n']
    for x in result['retrieved']: lines.append(f'- **{x["metadata"].get("source")}** ({x["similarity"]}): {x["text"]}')
    return '\n'.join(lines)
