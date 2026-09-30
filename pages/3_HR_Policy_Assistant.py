import os
from pathlib import Path
import tempfile
import streamlit as st
from src.utils.config import INDEX,POLICIES
from src.utils.helpers import read_json
from src.utils.ui import title,guard,llm_toggle
from src.rag.vector_store import build_index
from src.rag.policy_agent import answer_question

def main():
    title('HR Policy Assistant','Source-backed policy retrieval with document, page, section and similarity evidence.')
    active=Path(st.session_state.get('session_policy_index',str(INDEX)))
    if (active/'metadata.json').exists():st.json(read_json(active/'metadata.json'),expanded=False)
    else:st.warning('Build the bundled policy index or upload policies below.')
    with st.expander('Upload policies or rebuild the index'):
        uploads=st.file_uploader('Policy PDFs',type=['pdf'],accept_multiple_files=True)
        backend=st.selectbox('Index engine',['semantic','lexical'])
        size=st.number_input('Chunk size (words)',50,500,140);overlap=st.number_input('Overlap (words)',0,100,25)
        st.caption('Uploaded policy indexes are isolated to this browser session and temporary directory. Bundled policies are unchanged.')
        if st.button('Build session index'):
            folder=Path(tempfile.mkdtemp(prefix='workforce_policy_'));source=folder/'policies';source.mkdir()
            if uploads:
                seen=set()
                for upload in uploads:
                    name=Path(upload.name).name
                    if name in seen:raise ValueError('Duplicate PDF names: rename documents before uploading.')
                    seen.add(name);data=upload.getvalue()
                    if len(data)>20*1024*1024:raise ValueError('Policy exceeds 20 MB.')
                    (source/name).write_bytes(data)
            else:source=POLICIES
            meta=build_index(source,folder/'index',backend,int(size),int(overlap));st.session_state['session_policy_index']=str(folder/'index');active=folder/'index';st.session_state.pop('policy_result',None);st.success(f'Indexed {meta["documents"]} documents / {meta["chunks"]} chunks.');st.json(meta)
    top_k=st.slider('Retrieved chunks',1,12,int(os.getenv('RAG_TOP_K',6)))
    minimum=st.slider('Minimum cosine similarity (heuristic; not confidence)',0.,1.,float(os.getenv('RAG_MIN_SIMILARITY',.30)),.01)
    query=st.text_area('Policy question',value=st.session_state.get('policy_query','Can an employee take medical leave followed by temporary work from home?'))
    llm=llm_toggle('policy_llm')
    if st.button('Retrieve policy evidence',type='primary'):
        with st.spinner('Retrieving evidence…'):result=answer_question(query,top_k,minimum,llm,active)
        st.session_state['policy_result']=result
    result=st.session_state.get('policy_result')
    if result:
        st.caption('Answer mode: '+result['mode']+' | Index: '+result['backend']);st.write(result['answer'])
        with st.expander('Retrieved Evidence',expanded=True):
            for i,source in enumerate(result['evidence'],1):
                st.markdown(f'**[{i}] {source["document_name"]} — page {source["page_number"]} — {source["section"]}**')
                st.caption(f'Cosine similarity: {source["similarity"]:.3f} | Chunk: {source["chunk_id"]}');st.write(source['text'])
    st.caption('The supplied six policies are fictional, version 1.0, with demo effective date 1 October 2026. Excerpts and answers do not grant approval. Similarity thresholds do not establish factual coverage.')
guard(main)
