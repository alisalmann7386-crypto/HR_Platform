import os
from pathlib import Path
import tempfile
import streamlit as st
from src.utils.config import INDEX, POLICIES
from src.utils.helpers import read_json
from src.utils.ui import title, guard, llm_toggle
from src.rag.vector_store import build_index
from src.rag.bootstrap import ensure_policy_index
from src.rag.policy_agent import answer_question


def main():
    title('HR Policy Assistant','Ask a question and inspect its document, page, section and retrieved evidence.')
    if 'session_policy_index' not in st.session_state:
        with st.spinner('Preparing the bundled policy index (first visit may download MiniLM)…'):
            ensure_policy_index()
    active=Path(st.session_state.get('session_policy_index',str(INDEX)))
    if (active/'metadata.json').exists():
        meta=read_json(active/'metadata.json')
        st.metric('Indexed policy documents',meta['documents'])
        with st.expander('Index details and document inventory'):
            st.write(', '.join(sorted(meta['source_hashes'])))
            st.json(meta)
    else:st.warning('No policy index found. Build one from the PDFs below.')
    with st.expander('Upload policies or rebuild index'):
        uploads=st.file_uploader('Policy PDFs',type=['pdf'],accept_multiple_files=True)
        backend=st.selectbox('Index engine',['semantic','lexical'])
        size=st.number_input('Chunk size (words)',50,500,140)
        overlap=st.number_input('Overlap (words)',0,100,25)
        st.caption('New indexes are isolated to this browser session. The bundled policies remain available.')
        if st.button('Build session index'):
            folder=Path(tempfile.mkdtemp(prefix='workforce_policy_'));source=folder/'policies';source.mkdir()
            if uploads:
                seen=set()
                for upload in uploads:
                    name=Path(upload.name).name
                    if name in seen:raise ValueError('Duplicate PDF names: rename documents first.')
                    seen.add(name);data=upload.getvalue()
                    if len(data)>20*1024*1024:raise ValueError('Policy exceeds 20 MB.')
                    (source/name).write_bytes(data)
            else:source=POLICIES
            with st.spinner('Extracting pages and generating policy embeddings…'):
                meta=build_index(source,folder/'index',backend,int(size),int(overlap))
            st.session_state['session_policy_index']=str(folder/'index');active=folder/'index'
            st.session_state.pop('policy_result',None)
            st.success(f"Indexed {meta['documents']} documents / {meta['chunks']} chunks.")
    top_k=st.slider('Retrieved chunks',1,12,int(os.getenv('RAG_TOP_K',6)))
    minimum=st.slider('Minimum cosine similarity (heuristic)',0.,1.,float(os.getenv('RAG_MIN_SIMILARITY',.30)),.01)
    query=st.text_area('Ask a policy question',value=st.session_state.get('policy_query','Can an employee take medical leave followed by temporary work from home?'))
    llm=llm_toggle('policy_llm')
    if st.button('Retrieve policy evidence',type='primary'):
        with st.spinner('Searching policy pages and checking sources…'):
            st.session_state['policy_result']=answer_question(query,top_k,minimum,llm,active)
    result=st.session_state.get('policy_result')
    if result:
        with st.chat_message('user'):
            st.write(query)
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
