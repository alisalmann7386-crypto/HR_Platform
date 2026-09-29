import _bootstrap
import numpy as np
import pandas as pd
from src.attrition.preprocessing import load_data,features
from src.utils.config import IBM,DATA
from src.utils.helpers import save_json

def generate():
    rng=np.random.default_rng(42);df=load_data(IBM);folder=DATA/'workforce';folder.mkdir(exist_ok=True)
    # No attrition labels, age, gender, marital status, salary or performance targets used.
    pools={'Sales':['Sales','CRM','Excel','SQL','Data Analysis','Communication'], 'Human Resources':['Excel','Communication','Project Management','Data Analysis','SQL'], 'Research & Development':['Python','SQL','Machine Learning','PyTorch','RAG','LLMs','Docker','MLOps','AWS','Laboratory Methods','Research']}
    rows=[];projects=[]
    for r in df.itertuples():
        pool=pools[r.Department]
        for skill in rng.choice(pool,size=min(4,len(pool)),replace=False):
            rows.append({'Employee_ID':r.Employee_ID,'Employee_Name':'Demo '+r.Employee_ID,'Department':r.Department,'Job_Role':r.JobRole,'Skill':skill,'Skill_Level':rng.choice(['Beginner','Intermediate','Advanced'],p=[.3,.5,.2]),'Years_Experience':int(rng.integers(0,6)),'Synthetic':True})
        projects.append({'Employee_ID':r.Employee_ID,'Project':'Demo '+r.Department+' initiative','Skill':pool[0],'Synthetic':True})
    pd.DataFrame(rows).to_csv(folder/'employee_skills.csv',index=False);pd.DataFrame(projects).to_csv(folder/'projects.csv',index=False)
    pd.DataFrame({'Employee_ID':df.Employee_ID,'Performance_Score':rng.integers(2,6,len(df)),'Synthetic':True}).to_csv(folder/'performance.csv',index=False)
    pd.DataFrame({'Employee_ID':df.Employee_ID,'Attendance_Rate':rng.uniform(.82,1,len(df)).round(3),'Synthetic':True}).to_csv(folder/'attendance.csv',index=False)
    pd.DataFrame({'Employee_ID':df.Employee_ID,'Training_Hours':rng.integers(0,61,len(df)),'Courses_Completed':rng.integers(0,5,len(df)),'Synthetic':True}).to_csv(folder/'training.csv',index=False)
    requirements=[]
    for role,group in df.groupby('JobRole'):
        dep=group.Department.mode()[0]
        for skill in pools[dep][:3]+pools[dep][-2:]:
            requirements.append({'Role':role,'Skill':skill,'Required_Level':'Intermediate','Required_Employees':max(5,int(len(group)*.45)),'Priority':'High','Synthetic':True})
    pd.DataFrame(requirements).drop_duplicates(['Role','Skill']).to_csv(folder/'role_skill_requirements.csv',index=False)
    features(df).assign(Employee_ID=df.Employee_ID).head(10).to_csv(DATA/'processed/employee_upload_example.csv',index=False)
    save_json(folder/'provenance.json',{'random_state':42,'synthetic':True,'source_id':'IBM EmployeeNumber mapped to EMP-<number>','note':'All auxiliary skill, project, performance, attendance, training and future-capacity values are invented demonstration data; they are not model training features.'})
    print('Generated synthetic auxiliary datasets for',len(df),'employees.')
if __name__=='__main__':generate()
