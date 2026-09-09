import re

SKILLS = {
 'python':['python'], 'sql':['sql'], 'machine learning':['machine learning','ml'], 'deep learning':['deep learning'], 'nlp':['nlp','natural language processing'], 'pandas':['pandas'], 'numpy':['numpy'], 'scikit-learn':['scikit-learn','sklearn'], 'tensorflow':['tensorflow'], 'pytorch':['pytorch'], 'fastapi':['fastapi'], 'flask':['flask'], 'django':['django'], 'rest apis':['rest api','restful api','rest apis'], 'docker':['docker'], 'kubernetes':['kubernetes','k8s'], 'aws':['aws','amazon web services'], 'azure':['azure'], 'gcp':['gcp','google cloud'], 'git':['git','github'], 'linux':['linux'], 'spark':['spark','apache spark'], 'airflow':['airflow'], 'postgresql':['postgresql','postgres'], 'mongodb':['mongodb'], 'tableau':['tableau'], 'power bi':['power bi'], 'streamlit':['streamlit'], 'react':['react'], 'java':['java'], 'c++':['c++'], 'excel':['excel'], 'rag':['rag','retrieval augmented generation'], 'llm':['llm','large language model'], 'transformers':['transformers'], 'graphql':['graphql']
}

def extract_skills(text):
    text = text or ''
    low = text.lower()
    found = []
    for canonical, aliases in SKILLS.items():
        if any(re.search(r'(?<![a-z0-9])'+re.escape(a)+r'(?![a-z0-9])', low) for a in aliases): found.append(canonical)
    return sorted(found)

def skill_evidence(text, skills):
    low = (text or '').lower()
    return {s: low.find(s) >= 0 for s in skills}
