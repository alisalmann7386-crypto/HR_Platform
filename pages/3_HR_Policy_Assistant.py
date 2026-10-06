import os
from pathlib import Path
import streamlit as st
from src.utils.config import INDEX
from src.utils.helpers import read_json
from src.utils.ui import title, guard, llm_toggle
from src.rag.vector_store import validate_index
from src.rag.uploads import build_session_index, remove_session_index, cleanup_expired, touch_session
from src.rag.bootstrap import ensure_policy_index
from src.rag.policy_agent import answer_question


def main():
    title('HR Policy Assistant','Ask a question and inspect its document, page, section and retrieved evidence.')
    cleanup_expired()
    backend=st.selectbox('Index engine',['semantic','lexical'],index=1 if os.getenv('EMBEDDING_BACKEND')=='lexical' else 0)
    bundled=INDEX if backend=='semantic' else INDEX.with_name(INDEX.name+'_lexical')
    if 'session_policy_index' in st.session_state and not Path(st.session_state['session_policy_index']).exists():
        st.session_state.pop('session_policy_index',None)
        st.session_state.pop('policy_result',None)
        st.info('Session policies expired or were removed; use the bundled library or upload again.')
    ready=False
    active=Path(st.session_state.get('session_policy_index',str(bundled)))
    if 'session_policy_index' not in st.session_state:
        try:
            with st.spinner('Preparing policy evidence…'):
                ensure_policy_index(output=bundled,backend=backend)
            ready=True
        except (RuntimeError,ValueError,OSError):
            st.warning('Policy setup unavailable. Select lexical mode for offline use, or check model/download access.')
    else:
        touch_session(active)
        try:validate_index(active);ready=True
        except (ValueError,OSError,RuntimeError,KeyError):st.warning('Session index is incomplete. Rebuild or delete it.')
    if ready:
        meta=read_json(active/'metadata.json')
        st.metric('Indexed policy documents',meta['documents'])
        st.caption('Active index engine: '+meta['backend'])
        with st.expander('Index details and document inventory'):
            st.write(', '.join(sorted(meta['source_hashes'])))
            st.json(meta)
    with st.expander('Upload policies or rebuild index'):
        uploads=st.file_uploader('Policy PDFs',type=['pdf'],accept_multiple_files=True)
        size=st.number_input('Chunk size (words)',50,500,140)
        overlap=st.number_input('Overlap (words)',0,100,25)
        st.caption('New indexes are isolated to this browser session. The bundled policies remain available.')
        if st.button('Build session index'):
            with st.spinner('Extracting policy evidence…'):
                new_index,meta=build_session_index(uploads,backend,int(size),int(overlap))
            old=st.session_state.get('session_policy_index')
            st.session_state['session_policy_index']=str(new_index)
            if old:remove_session_index(old)
            st.session_state.pop('policy_result',None)
            st.rerun()
    if st.session_state.get('session_policy_index') and st.button('Delete session policies'):
        remove_session_index(st.session_state.pop('session_policy_index'))
        st.session_state.pop('policy_result',None)
        st.rerun()
    top_k=st.slider('Retrieved chunks',1,12,int(os.getenv('RAG_TOP_K',6)))
    minimum=st.slider('Minimum cosine similarity (heuristic)',0.,1.,float(os.getenv('RAG_MIN_SIMILARITY',.30)),.01)
    query=st.text_area('Ask a policy question',value=st.session_state.get('policy_query','Can an employee take medical leave followed by temporary work from home?'))
    llm=llm_toggle('policy_llm')
    if st.button('Retrieve policy evidence',type='primary',disabled=not ready):
        with st.spinner('Searching policy pages and checking sources…'):
            result=answer_question(query,top_k,minimum,llm,active)
            result['submitted_query']=query
            result['settings']=[top_k,minimum,llm,str(active)]
            st.session_state['policy_result']=result
    result=st.session_state.get('policy_result')
    if result:
        if result.get('submitted_query')!=query or result.get('settings')!=[top_k,minimum,llm,str(active)]:
            st.warning('Inputs changed. The answer below belongs to the previous submission; retrieve again to update it.')
        with st.chat_message('user'):
            st.write(result.get('submitted_query','Previous question'))
        with st.chat_message('assistant'):
            st.caption('Answer mode: '+result['mode']+' · Index: '+result['backend'])
            st.write(result['answer'])
        st.subheader('Relevant source sections')
        for i,source in enumerate(result['evidence'],1):
            with st.container(border=True):
                st.write(f"**[{i}] {source['document_name']}** · Page {source['page_number']}")
                st.caption(f"{source['section']} · cosine similarity {source['similarity']:.3f}")
        with st.expander('Retrieved Evidence',expanded=False):
            for i,source in enumerate(result['evidence'],1):
                st.write(f"**[{i}] {source['document_name']} — page {source['page_number']} — {source['section']}**")
                st.caption(f"Chunk: {source['chunk_id']} · similarity: {source['similarity']:.3f}")
                st.write(source['text'])
    st.caption('These six policies are fictional demos. Excerpts never grant approval; similarities are not confidence scores.')


guard(main)
