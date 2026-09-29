import re
SKILLS = {
 'Python':['python'],'SQL':['sql'],'PostgreSQL':['postgresql','postgres'],
 'Machine Learning':['machine learning','ml'],'Deep Learning':['deep learning'],
 'NLP':['natural language processing','nlp'],'LLMs':['large language model','large language models','llm','llms'],
 'Computer Vision':['computer vision','cv'],'PyTorch':['pytorch'],'TensorFlow':['tensorflow','keras'],
 'Docker':['docker','containerization'],'Kubernetes':['kubernetes','k8s'],'AWS':['aws','amazon web services'],
 'MLOps':['mlops','ml operations'],'RAG':['rag','retrieval augmented generation','retrieval-augmented generation'],
 'LangChain':['langchain'],'ChromaDB':['chromadb','chroma'],'FAISS':['faiss'],
 'Git':['git'],'FastAPI':['fastapi'],'Streamlit':['streamlit'],'Pandas':['pandas'],
 'Scikit-learn':['scikit-learn','sklearn'],'Java':['java'],'C++':['c++'],
 'JavaScript':['javascript'],'React':['react','reactjs'],'Excel':['excel'],
 'Power BI':['power bi','powerbi'],'Tableau':['tableau'],'Statistics':['statistics','statistical analysis'],
 'Communication':['stakeholder communication','technical communication'],'Project Management':['project management'],
 'Sales':['sales'],'CRM':['crm'],'Laboratory Methods':['laboratory methods'], 'Research':['research'],
 'Data Analysis':['data analysis','data analytics'],'Data Engineering':['data engineering'],
 'Airflow':['airflow'],'Spark':['spark'],'Azure':['azure'],'GCP':['gcp','google cloud']}
TOOLS={'PyTorch','TensorFlow','Docker','Kubernetes','AWS','LangChain','ChromaDB','FAISS','Git','FastAPI','Streamlit','Pandas','Scikit-learn','React','Excel','Power BI','Tableau','Airflow','Spark','Azure','GCP'}
def extract_skills(text):
    result=[]
    for skill, aliases in SKILLS.items():
        for alias in aliases:
            # CV is ambiguous (curriculum vitae); accept the full phrase only in resumes.
            if alias == 'cv': continue
            match=re.search(r'(?<![\w])'+re.escape(alias)+r'(?![\w])',text,re.I)
            if match:
                start=text.rfind('\n',0,match.start())+1;end=text.find('\n',match.end());end=len(text) if end<0 else end
                evidence=text[start:end].strip()
                if re.search(r'\b(no|not|without)\s+(?:\w+\s+){0,2}'+re.escape(alias),evidence,re.I): continue
                result.append({'skill':skill,'evidence':evidence,'alias':match.group()});break
    return result

def canonical(skill):
    for key,aliases in SKILLS.items():
        if skill.casefold() in [key.casefold()]+[x.casefold() for x in aliases]: return key
    return skill.strip()
