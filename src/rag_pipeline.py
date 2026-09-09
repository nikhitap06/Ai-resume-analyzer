from .vector_store import VectorStore, index_knowledge_base
from .retriever import retrieve_context, format_context
from .semantic_matcher import calculate_similarity
from .ats_analyzer import analyze_ats
from .llm import generate_recommendations

def analyze(resume, job):
    store=VectorStore(); index_knowledge_base(store)
    query=f'{job.text}\nResume skills: {", ".join(job.skills)}'
    retrieved=retrieve_context(query,store,8)
    context=format_context(retrieved)
    match=calculate_similarity(resume.text,job.text, __import__('src.skill_extractor',fromlist=['extract_skills']).extract_skills(resume.text),job.skills)
    ats=analyze_ats(resume,job)
    rec=generate_recommendations(resume,job,match,ats,context)
    return {'match':match,'ats':ats,'retrieved':retrieved,'recommendations':rec}
