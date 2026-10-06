"""Optional demo access gate. Deploy behind organizational identity for real HR data."""
import hashlib
import hmac
import os
import secrets
import threading
import time
from src.utils.config import ROOT

ROLES = {'viewer', 'reviewer', 'admin'}
VIEWER_PAGES = {'pages/0_Home.py', 'pages/5_Workforce_Dashboard.py', 'pages/7_Model_Performance.py', 'pages/8_Project_Information.py'}
_ATTEMPTS = {}
_LOCK = threading.Lock()


def password_hash(password):
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt),n=16384,r=8,p=1).hex()
    return f'scrypt${salt}${digest}'


def verify_password(password, encoded):
    try:
        algorithm,salt,digest = encoded.split('$')
        if algorithm!='scrypt' or len(salt)!=32 or len(digest)!=128:return False
        actual = hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt),n=16384,r=8,p=1)
        return hmac.compare_digest(actual,bytes.fromhex(digest))
    except (ValueError,TypeError,AttributeError):return False


def allowed_page(role, page):
    return role in {'reviewer','admin'} or (role=='viewer' and page in VIEWER_PAGES)


def authenticate(username, password, accounts, now=None):
    now = time.time() if now is None else now
    key = username if username in accounts else '<unknown>'
    with _LOCK:
        count,until = _ATTEMPTS.get(key,(0,0))
        if until>now:return None
        if until:count=0
        account = accounts.get(username,{})
        if account.get('role') in ROLES and verify_password(password,account.get('password_hash','')):
            _ATTEMPTS.pop(key,None)
            return account['role']
        count += 1
        _ATTEMPTS[key] = (count,now+300 if count>=5 else 0)
        return None


def clear_private_session(state):
    if state.get('session_policy_index'):
        from src.rag.uploads import remove_session_index
        try:remove_session_index(state['session_policy_index'])
        except (OSError,ValueError):pass
    state.clear()


def require_access(render_controls=True):
    import streamlit as st
    enabled = os.getenv('WORKFORCE_AUTH_ENABLED','false').lower()=='true'
    if os.getenv('WORKFORCE_DATA_MODE','demo').lower()=='confidential' and not enabled:
        st.error('Confidential mode requires configured access protection. Enable WORKFORCE_AUTH_ENABLED and configure accounts.')
        st.stop()
    if not enabled:return 'admin'
    try:accounts = st.secrets['workforce_users']
    except (KeyError,FileNotFoundError):
        st.error('Access protection is enabled but workforce_users accounts are not configured in host secrets.')
        st.stop()
    identity = st.session_state.get('access_identity')
    if identity:
        current = accounts.get(identity['username'],{})
        if current.get('role')!=identity['role'] or current.get('password_hash')!=identity['credential_hash']:
            clear_private_session(st.session_state)
            st.rerun()
        if render_controls:
            st.sidebar.caption('Access role: '+identity['role'])
            if st.sidebar.button('Sign out'):
                clear_private_session(st.session_state)
                st.rerun()
        return identity['role']
    st.title('WorkforceAI · Sign in')
    with st.form('access_login'):
        username = st.text_input('Username')
        password = st.text_input('Password',type='password')
        submitted = st.form_submit_button('Sign in')
    if submitted:
        role = authenticate(username,password,accounts)
        if role:
            st.session_state['access_identity'] = {'username':username,'role':role,'credential_hash':accounts[username]['password_hash']}
            st.rerun()
        st.error('Sign-in failed. Repeated failures are temporarily limited.')
    st.stop()
