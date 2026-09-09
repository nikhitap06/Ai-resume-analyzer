import numpy as np
from .embeddings import EmbeddingModel, cosine_similarity

def _pct(x): return round(max(0,min(1,x))*100,1)

def calculate_similarity(resume_text, job_text, resume_skills=None, job_skills=None, embedder=None):
    embedder=embedder or EmbeddingModel()
    vectors=embedder.encode([resume_text,job_text])
    semantic=_pct((cosine_similarity(vectors[0],vectors[1])+1)/2)
    rs=set(resume_skills or []); js=set(job_skills or [])
    technical=_pct(len(rs&js)/len(js)) if js else 0
    experience=_pct(min(1, len((resume_text or '').split())/250))
    project=_pct(cosine_similarity(embedder.encode(resume_text[:3000])[0], embedder.encode(job_text[:3000])[0])**0.5 if resume_text and job_text else 0)
    education=100.0 if any(x in (resume_text or '').lower() for x in ('bachelor','master','phd','degree')) else 0.0
    overall=round(.45*semantic+.30*technical+.10*experience+.10*project+.05*education,1)
    return {'semantic_match':semantic,'technical_skill_match':technical,'experience_match':experience,'project_relevance':project,'education_match':education,'overall_match':overall,'matching_skills':sorted(rs&js),'missing_skills':sorted(js-rs)}
