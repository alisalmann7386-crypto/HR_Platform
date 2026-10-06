"""Keep interview identities and drafts independent of temporary widgets."""
from uuid import uuid4


def new_interview(candidate_id, questions):
    return {'candidate_id': candidate_id, 'interview_id': uuid4().hex,
            'questions': [dict(q, question_id=uuid4().hex) for q in questions]}


def widget_keys(pack, question):
    suffix = f"{pack['candidate_id']}_{pack['interview_id']}_{question['question_id']}"
    return {kind: f'{kind}_{suffix}' for kind in ['question_edit', 'answer', 'notes']}


def clear_interview_widgets(state, candidate_id=None):
    prefixes = tuple(f'{kind}_{candidate_id}_' if candidate_id else f'{kind}_'
                     for kind in ['question_edit', 'answer', 'notes'])
    for key in list(state):
        if key.startswith(prefixes):del state[key]


def save_draft(state, pack, question):
    question['draft'] = {kind: state.get(key, '') for kind, key in widget_keys(pack, question).items()}
    edited = question['draft']['question_edit'].strip()
    if edited:question['question'] = edited


def restore_draft(state, pack, question):
    defaults = {'question_edit': question['question'], 'answer': '', 'notes': ''}
    keys = widget_keys(pack, question)
    for kind, key in keys.items():
        if key not in state:state[key] = question.get('draft', {}).get(kind, defaults[kind])
    return keys
