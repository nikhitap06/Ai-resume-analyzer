from dataclasses import dataclass, asdict
from .skill_extractor import extract_skills

@dataclass
class JobDescription:
    text: str
    skills: list
    sections: dict
    def to_dict(self): return asdict(self)

def parse_job_description(text):
    if not text or not text.strip(): raise ValueError('Job description cannot be empty.')
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    sections = {}
    current = 'general'
    for line in lines:
        low = line.lower().rstrip(':')
        if any(k in low for k in ('responsibil', 'qualif', 'require', 'preferred', 'education', 'experience', 'technology', 'skill')) and len(line) < 80:
            current = low.replace(' ', '_')
            sections.setdefault(current, [])
        else: sections.setdefault(current, []).append(line)
    return JobDescription(text=text.strip(), skills=extract_skills(text), sections={k:'\n'.join(v) for k,v in sections.items()})
