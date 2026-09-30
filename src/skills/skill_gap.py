import pandas as pd
from src.utils.validators import require_columns
LEVELS={'Beginner':1,'Intermediate':2,'Advanced':3,'Expert':4}
def validate_skills(skills,requirements):
    require_columns(skills,['Employee_ID','Department','Job_Role','Skill','Skill_Level'])
    require_columns(requirements,['Role','Skill','Required_Level','Required_Employees','Priority'])
    for frame,columns in [(skills,['Employee_ID','Department','Job_Role','Skill']), (requirements,['Role','Skill','Priority'])]:
        for column in columns:
            if frame[column].isna().any() or frame[column].astype(str).str.strip().eq('').any():
                raise ValueError(f'{column} must not contain missing or blank values.')
    if not skills.Skill_Level.isin(LEVELS).all() or not requirements.Required_Level.isin(LEVELS).all():raise ValueError('Unknown proficiency level.')
    n=pd.to_numeric(requirements.Required_Employees,errors='coerce')
    if n.isna().any() or (n<0).any() or (n%1!=0).any():raise ValueError('Required_Employees must be nonnegative integers.')
    if requirements.duplicated(['Role','Skill']).any():raise ValueError('Role/Skill requirements must be unique.')

def skill_gaps(skills,requirements):
    validate_skills(skills,requirements);rows=[]
    for r in requirements.itertuples():
        eligible=skills[(skills.Skill==r.Skill)&(skills.Job_Role==r.Role)&(skills.Skill_Level.map(LEVELS)>=LEVELS[r.Required_Level])]
        available=eligible.Employee_ID.nunique();required=int(r.Required_Employees)
        rows.append({'Role':r.Role,'Skill':r.Skill,'Required_Level':r.Required_Level,'Required':required,'Available':available,'Gap':max(required-available,0),'Coverage':min(available/required,1.) if required else 1.,'Priority':r.Priority})
    return pd.DataFrame(rows)
