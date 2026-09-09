import sys, os
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from src.skill_extractor import extract_skills
from src.semantic_matcher import calculate_similarity
from src.ats_analyzer import analyze_ats
from src.jd_parser import parse_job_description
from src.resume_parser import Resume

def test_skill_extraction_is_evidence_based():
    assert set(extract_skills('Built Python APIs with Docker and SQL')) == {'python','rest apis','docker','sql'} or set(extract_skills('Built Python APIs with Docker and SQL')) >= {'python','docker','sql'}

def test_similarity_contains_real_breakdown():
    r=calculate_similarity('Python SQL machine learning','Python SQL', ['python','sql','machine learning'],['python','sql'])
    assert 0 <= r['overall_match'] <= 100 and r['matching_skills']==['python','sql']

def test_ats_is_measurable():
    resume=Resume('x.pdf',1,'email a@b.com phone 1234567890 experience education projects skills python',{'experience':'x','education':'x','projects':'x','skills':'python'},{'name':'A','email':'a@b.com','phone':'1234567890'})
    ats=analyze_ats(resume,parse_job_description('Need Python and Docker'))
    assert ats['required_sections']==100 and ats['score'] >= 0

def test_empty_jd_rejected():
    try: parse_job_description('')
    except ValueError: return
    assert False
