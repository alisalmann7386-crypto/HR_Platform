"""Conservative topic coverage, not entailment or calibrated confidence."""
import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

GENERIC_TERMS = set('''company employee employees policy policies request requested
available use need must may long soon standard applies eligible eligibility rate
days hours working work business purchase purchases stocks office tell say followed
temporary ahead before give gives handled handle submitted submit submission today
how many much can does do normally convene'''.split())
ALIASES = {'mfa': 'multi factor authentication', 'dispute': 'review',
           'annual': 'year', 'annually': 'year'}


def topic_terms(text):
    text = text.casefold()
    for term, replacement in ALIASES.items():text = re.sub(r'\b'+term+r'\b', replacement, text)
    return {re.sub(r'(?:ing|ed|es|s)$', '', word) for word in re.findall(r'[a-z]{3,}', text)
            if word not in ENGLISH_STOP_WORDS and word not in GENERIC_TERMS}


def assess_answerability(query, evidence):
    required = topic_terms(query)
    observed = topic_terms(' '.join(c.get('section', '')+' '+c['text'] for c in evidence))
    missing = sorted(required-observed)
    return {'supported': bool(required) and not missing, 'uncovered_terms': missing,
            'note': 'Topic coverage only; valid paraphrases may be rejected. Review policy conditions.'}
