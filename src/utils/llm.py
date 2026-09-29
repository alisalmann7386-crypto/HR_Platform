"""Optional OpenAI-compatible chat transport. No secrets or raw text logged."""
import os
import requests

def available(): return os.getenv('LLM_PROVIDER','none') != 'none' and bool(os.getenv('LLM_API_KEY')) and bool(os.getenv('LLM_MODEL'))
def complete(system, user):
    if not available(): raise ValueError('Configure LLM_PROVIDER, LLM_MODEL and LLM_API_KEY in .env.')
    provider = os.getenv('LLM_PROVIDER')
    base = {'groq':'https://api.groq.com/openai/v1','mistral':'https://api.mistral.ai/v1','openai':'https://api.openai.com/v1'}.get(provider, os.getenv('LLM_BASE_URL',''))
    if not base.startswith('https://'): raise ValueError('LLM_BASE_URL must be an HTTPS OpenAI-compatible endpoint.')
    try:
        response = requests.post(base.rstrip('/') + '/chat/completions', headers={'Authorization': 'Bearer ' + os.environ['LLM_API_KEY']}, json={'model':os.environ['LLM_MODEL'],'temperature':0,'messages':[{'role':'system','content':system},{'role':'user','content':user}]},timeout=45)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.RequestException as e:
        raise RuntimeError('LLM request failed. Check provider, model, quota and network; no response was used.') from None
