def workforce_insights(summary,gaps,skills):
    statements=[]
    for row in summary.itertuples():
        roles=set(skills.loc[skills.Department==row.Department,'Job_Role'])
        subset=gaps[(gaps.Role.isin(roles))&(gaps.Gap>0)].sort_values('Gap',ascending=False)
        names=', '.join(subset.Skill.head(3).tolist()) or 'none in configured role targets'
        statements.append(f'{row.Department}: {row.Elevated_Signals}/{row.Employees} records have elevated model signals. Related synthetic role-capacity gaps: {names}. Synthetic mean training is {row.Synthetic_Training_Hours:.1f} hours, attendance {row.Synthetic_Attendance_Rate:.1%}, and performance {row.Synthetic_Performance_Score:.1f}/5. These auxiliary values demonstrate joins, not causes or real employee evidence. Possible human review: workload context and voluntary development opportunities.')
    return statements
