import os, json

def generate_recommendations(resume, job, match, ats, retrieved_context):
    if not retrieved_context: raise ValueError('Generation requires retrieved context; no documents were retrieved.')
    api_key=os.getenv('OPENAI_API_KEY')
    if not api_key:
        return {'mode':'local fallback','summary':f"The resume has a {match['overall_match']}% calculated match. Recommendations below are evidence-based checks; configure OPENAI_API_KEY for contextual LLM prose.", 'strengths':match['matching_skills'], 'skill_gaps':match['missing_skills'], 'ats_improvements':ats['notes'], 'resume_recommendations':['Quantify outcomes in experience and project bullets.','Mirror relevant job terminology only when supported by the resume.'], 'project_recommendations':['Emphasize existing projects that demonstrate the matching skills.']}
    from openai import OpenAI
    client=OpenAI(api_key=api_key)
    prompt=f'''You are a resume advisor. Use ONLY candidate evidence; do not invent skills or projects. Retrieved context is mandatory and is included below. Return valid JSON with keys summary, strengths, skill_gaps, ats_improvements, resume_recommendations, project_recommendations.\nRESUME:\n{resume.text[:10000]}\nJOB:\n{job.text[:8000]}\nCALCULATED MATCH:\n{json.dumps(match)}\nATS:\n{json.dumps(ats)}\nRETRIEVED CONTEXT:\n{retrieved_context}'''
    r=client.chat.completions.create(model=os.getenv('OPENAI_MODEL','gpt-4o-mini'),temperature=.2,response_format={'type':'json_object'},messages=[{'role':'system','content':'You produce grounded resume analysis.'},{'role':'user','content':prompt}])
    data=json.loads(r.choices[0].message.content); data['mode']='OpenAI'; return data
