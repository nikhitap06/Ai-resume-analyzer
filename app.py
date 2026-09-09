import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from src.resume_parser import parse_resume
from src.jd_parser import parse_job_description
from src.rag_pipeline import analyze
from src.report_generator import generate_report

st.set_page_config(page_title='AI Resume Analyzer', page_icon='📄', layout='wide')
st.title('AI Resume Analyzer')
st.caption('RAG-based resume and job matching with transparent retrieval, semantic scoring, and grounded recommendations.')
with st.sidebar:
    st.header('Inputs')
    uploaded=st.file_uploader('Upload resume (PDF)',type=['pdf'])
    jd_file=st.file_uploader('Optional job description file',type=['txt','md'])
    jd=st.text_area('Paste job description',value=jd_file.getvalue().decode('utf-8') if jd_file else '',height=260)
    run=st.button('Analyze Resume',type='primary',use_container_width=True)
if run:
    if not uploaded: st.error('Please upload a PDF resume.')
    elif not jd.strip(): st.error('Please paste or upload a job description.')
    else:
        try:
            with st.spinner('Parsing, embedding, retrieving, and analyzing...'):
                resume=parse_resume(uploaded.getvalue(),uploaded.name); job=parse_job_description(jd); result=analyze(resume,job)
            st.success(f'Analyzed {resume.filename} ({resume.pages} page(s)).')
            m=result['match']; a=result['ats']
            c=st.columns(4)
            c[0].metric('Overall match',f'{m["overall_match"]}%'); c[1].metric('Semantic match',f'{m["semantic_match"]}%'); c[2].metric('ATS score',f'{a["score"]}/100'); c[3].metric('Retrieved chunks',len(result['retrieved']))
            st.subheader('Score breakdown')
            st.dataframe({'Metric':['Technical skill','Experience','Project relevance','Education'],'Score':[m['technical_skill_match'],m['experience_match'],m['project_relevance'],m['education_match']]},hide_index=True,use_container_width=True)
            col1,col2=st.columns(2)
            with col1:
                st.subheader('Skill analysis'); st.write('**Matching:** '+(', '.join(m['matching_skills']) or 'None detected')); st.write('**Missing:** '+(', '.join(m['missing_skills']) or 'None detected')); st.write('**Job skills detected:** '+(', '.join(job.skills) or 'None detected'))
            with col2:
                st.subheader('ATS checks'); st.json(a)
            st.subheader('AI recommendations'); st.info(f"Generation mode: {result['recommendations'].get('mode','LLM')}"); st.write(result['recommendations'].get('summary',''))
            for key in ('strengths','skill_gaps','ats_improvements','resume_recommendations','project_recommendations'):
                vals=result['recommendations'].get(key,[])
                if vals: st.markdown(f'**{key.replace("_"," ").title()}**'); st.write('\n'.join(f'- {v}' for v in vals))
            st.subheader('Retrieved Context — RAG transparency')
            for x in result['retrieved']:
                with st.expander(f"{x['metadata'].get('source')} · similarity {x['similarity']}"):
                    st.caption(x['metadata'].get('section')); st.write(x['text'])
            report=generate_report(resume,job,result)
            st.download_button('Download analysis report',report,'resume_analysis.md','text/markdown')
        except Exception as e: st.error(str(e))
else:
    st.info('Upload a resume and paste a target job description to begin. Uploaded content is processed in memory and is not written to disk by the app.')
