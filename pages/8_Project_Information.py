import streamlit as st
from src.utils.ui import title
from src.utils.config import ROOT

title('Project Information','B.Tech Computer Science / Data Science • reproducibility, methodology and viva support')
st.graphviz_chart('digraph {rankdir=TB; node [shape=box,style=rounded]; Sources [label="Resumes, jobs, policies, employee records\nSkills, performance, attendance, training"]; Processing [label="Validation and processing\nEmployee_ID integration"]; ML [label="Attrition ML + SHAP"]; NLP [label="Semantic matching + interview + RAG"]; Graph [label="Skill graph + capacity gaps"]; Dashboard [label="Workforce intelligence dashboard"]; Human [label="Human HR review"]; Sources->Processing; Processing->ML;Processing->NLP;Processing->Graph;ML->Dashboard;NLP->Dashboard;Graph->Dashboard;Dashboard->Human;}')
st.markdown("""### What you can explain in your viva
- Stratified splitting, fitted preprocessing and leakage prevention.
- Logistic Regression versus LightGBM, class weighting and SMOTE.
- Why average precision, recall and F1 matter for imbalanced labels.
- Sentence embeddings, cosine similarity and evidence-aware matching.
- Section-aware policy chunking, FAISS retrieval and source verification.
- SHAP log-odds contributions versus causal explanations.
- NetworkX relationships and distinct-employee skill capacity.
- Joining heterogeneous datasets through Employee_ID.

### Boundaries
IBM data and auxiliary datasets are synthetic. Policies are fictional. The prototype has no enterprise authentication, authorization or audit controls. Do not deploy it with real confidential employee information. Semantic similarity is evidence alignment, not proof of competence. Optional LLM outputs require human checking.
""")
for file in ['README.md','reports/project_report_outline.md','reports/DEMO_GUIDE.md']:
    path=ROOT/file
    if path.exists():
        with st.expander(path.name):st.markdown(path.read_text())
