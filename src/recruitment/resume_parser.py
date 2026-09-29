import re
from src.utils.file_utils import extract_text
from src.recruitment.skill_extractor import extract_skills, TOOLS

SECTION_NAMES={'skills':['skills','technical skills','tools','technologies'], 'experience':['experience','work experience','employment','professional experience'], 'projects':['projects','relevant projects','personal projects'], 'education':['education','qualifications'], 'certifications':['certifications','certificates'], 'domains':['domains','domain experience']}
SENSITIVE_LINE=re.compile(r'\b(gender|religion|caste|race|ethnicity|marital|disability|date of birth|nationality|sexual orientation|political|male|female)\b',re.I)
def sections(text):
    out={k:[] for k in SECTION_NAMES}; current=None
    for line in text.splitlines():
        line=line.strip()
        if not line or SENSITIVE_LINE.search(line): continue
        clean=line.strip(': ').lower()
        found=next((k for k,names in SECTION_NAMES.items() if clean in names),None)
        if found: current=found;continue
        # Ignore headers/contact and unsupported sections; only recognized professional content used.
        if '@' in line or re.search(r'https?://|linkedin.com|github.com|\+?\d[\d ()-]{8,}',line):continue
        if current: out[current].append(line)
    return out

def parse_resume(text,candidate_id='Candidate 01'):
    sec=sections(text)
    relevant='\n'.join('\n'.join(v) for v in sec.values())
    if not relevant: raise ValueError('No professional sections found. Add headings such as Skills, Experience, Projects and Education.')
    evidence=extract_skills(relevant)
    ex=' '.join(sec['experience'])
    years=re.findall(r'(\d+(?:\.\d+)?)\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience',ex,re.I)
    return {'candidate_id':candidate_id,'skills':[e['skill'] for e in evidence], 'skill_evidence':evidence,'experience_years':max(map(float,years)) if years else None,'experience_evidence':sec['experience'],'projects':sec['projects'],'education':sec['education'],'certifications':sec['certifications'],'tools':[e['skill'] for e in evidence if e['skill'] in TOOLS],'domains':sec['domains'],'professional_text':relevant,'warnings':['Rule-based section extraction: verify dates, experience, negation and evidence. Unknown is not zero.']}

def parse_file(source,candidate_id='Candidate 01'): return parse_resume(extract_text(source),candidate_id)
