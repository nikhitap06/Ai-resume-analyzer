import re

def analyze_ats(resume, job):
    text=resume.text.lower(); jd=job.text.lower()
    sections=resume.sections
    required=['experience','education','project','skill']
    required_score=100*sum(any(k in s for s in sections) for k in required)/len(required)
    contacts=100 if resume.contact['email']!='Not detected' and resume.contact['phone']!='Not detected' else 50 if resume.contact['email']!='Not detected' else 0
    keyword_score=100*sum(1 for s in job.skills if s in text)/len(job.skills) if job.skills else 0
    formatting=100
    if len(text)<250: formatting-=30
    if re.search(r'[^\x00-\x7F]{10}', resume.text): formatting-=10
    job_rel=keyword_score
    total=round(.35*keyword_score+.25*required_score+.15*formatting+.15*job_rel+.10*contacts,1)
    return {'score':total,'keyword_coverage':round(keyword_score,1),'required_sections':round(required_score,1),'formatting_checks':max(0,formatting),'contact_information':contacts,'job_relevance':round(job_rel,1),'notes':['Add missing required sections.' if required_score<100 else 'Core sections detected.','Add job-specific terms only where truthful.' if keyword_score<70 else 'Good coverage of detected job skills.']}
