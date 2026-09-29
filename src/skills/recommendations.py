def suggestions(gaps):
    return [f'{r.Role}: {r.Skill} has {r.Available} qualified employees for a synthetic target of {r.Required} (gap {r.Gap}). Discuss voluntary training, mentoring, project rotations or targeted recruitment.' for r in gaps[gaps.Gap>0].sort_values('Gap',ascending=False).itertuples()]
