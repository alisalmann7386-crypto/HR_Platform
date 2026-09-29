import re
from src.recruitment.skill_extractor import extract_skills

def parse_jd(text):
    if not text.strip(): raise ValueError('Enter a job description.')
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    fields={'mandatory_skills':[],'preferred_skills':[],'responsibilities':[],'domain_requirements':[],'education_requirements':[],'certification_requirements':[]}
    aliases={'mandatory_skills':['mandatory','required skills','requirements','must have'],'preferred_skills':['preferred','nice to have'],'responsibilities':['responsibilities'],'domain_requirements':['domain'],'education_requirements':['education'],'certification_requirements':['certification']}
    current='mandatory_skills'
    for line in lines[1:]:
        found=next((k for k,words in aliases.items() if any(line.lower().startswith(a) for a in words)),None)
        if found:
            current=found
            line=line.split(':',1)[1] if ':' in line else ''
        if line: fields[current].append(line)
    for key in ['mandatory_skills','preferred_skills']:
        fields[key]=[s['skill'] for s in extract_skills('\n'.join(fields[key]))]
    years=re.search(r'(\d+(?:\.\d+)?)\+?\s*years?',text,re.I)
    return dict(job_title=re.sub(r'^(?:role|job title):\s*','',lines[0],flags=re.I),minimum_experience=float(years.group(1)) if years else None,raw_text=text,**fields)
