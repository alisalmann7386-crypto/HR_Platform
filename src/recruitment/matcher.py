import numpy as np
from src.utils.embeddings import encode
from src.recruitment.skill_extractor import canonical
DEFAULT_WEIGHTS={'mandatory':40,'preferred':15,'experience':20,'projects':15,'education':10}

def match_skills(required,candidate,backend='semantic'):
    available=candidate['skills']; evidence={x['skill']:x['evidence'] for x in candidate['skill_evidence']}
    if backend=='semantic' and required and available: sims=encode(required) @ encode(available).T
    else: sims=None
    rows=[]
    for i,req in enumerate(required):
        exact=next((s for s in available if canonical(req)==canonical(s)),None)
        if exact: best=exact;score=1.;kind='Strong';method='Canonical alias match'
        elif available and sims is not None:
            j=int(np.argmax(sims[i]));best=available[j];score=float(sims[i,j]);kind='Partial' if score>=.55 else 'Not evidenced';method='Embedding cosine; related concept requires review'
        else:best=None;score=0.;kind='Not evidenced';method='No canonical match'
        rows.append({'requirement':req,'matched_skill':best if kind!='Not evidenced' else None,'similarity':round(score,4),'status':kind,'credit':1. if kind=='Strong' else .5 if kind=='Partial' else 0.,'evidence':evidence.get(best,'') if kind!='Not evidenced' else '', 'method':method})
    return rows

def analyze(candidate,jd,weights=None,backend='semantic'):
    weights=weights or DEFAULT_WEIGHTS
    if any(v<0 for v in weights.values()) or sum(weights.values())<=0:raise ValueError('Weights must be nonnegative and total more than zero.')
    mandatory=match_skills(jd['mandatory_skills'],candidate,backend); preferred=match_skills(jd['preferred_skills'],candidate,backend)
    components={};unknown=[];details={}
    for name,rows in [('mandatory',mandatory),('preferred',preferred)]:
        if rows:components[name]=float(np.mean([r['credit'] for r in rows]))
    if jd['minimum_experience'] is not None:
        if candidate['experience_years'] is None: unknown.append('Experience requires manual verification');components['experience']=0.
        else:components['experience']=min(candidate['experience_years']/max(jd['minimum_experience'],.1),1.)
    if candidate['projects'] and jd['responsibilities']:
        if backend=='semantic':
            sims=encode(candidate['projects']) @ encode(jd['responsibilities']).T
            components['projects']=float(np.clip(sims.max(axis=0),0,1).mean())
            details['projects']=[{'requirement':r,'evidence':candidate['projects'][int(sims[:,i].argmax())],'cosine':float(sims[:,i].max())} for i,r in enumerate(jd['responsibilities'])]
        else:unknown.append('Project semantic alignment unavailable in lexical mode')
    requirements=jd['education_requirements']+jd['certification_requirements']
    edu=candidate['education']+candidate['certifications']
    if requirements:
        if edu and backend=='semantic':
            sim=encode(requirements)@encode(edu).T;components['education']=float(np.clip(sim.max(axis=1),0,1).mean())
            details['education']=[{'requirement':r,'evidence':edu[int(sim[i].argmax())],'cosine':float(sim[i].max())} for i,r in enumerate(requirements)]
        else:components['education']=0.;unknown.append('Education/certifications need manual verification')
    denominator=sum(weights.get(k,0) for k in components)
    score=100*sum(weights.get(k,0)*v for k,v in components.items())/denominator if denominator else None
    return {'candidate_id':candidate['candidate_id'],'job_title':jd['job_title'],'job_relevance_score':round(score,1) if score is not None else None,'mandatory':mandatory,'preferred':preferred,'matched_skills':[x['requirement'] for x in mandatory+preferred if x['status']=='Strong'],'missing_skills':[x['requirement'] for x in mandatory+preferred if x['status']=='Not evidenced'],'components':components,'evidence':details,'unknowns':unknown,'weights':weights,'active_weight_total':denominator,'backend':backend,'note':'Heuristic evidence alignment, not probability of success or competence. Unknown evidence gets zero credit, not a conclusion of inability. Human recruiter review required.'}
