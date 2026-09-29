def summarize(result):
    return {'strong_matches':result['matched_skills'],'not_evidenced':result['missing_skills'],'needs_review':result['unknowns'],'evidence':result['mandatory']+result['preferred'],'interpretation':result['note']}
