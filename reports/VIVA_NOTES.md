# Viva notes

**Why LightGBM?** It models nonlinear tabular relationships and feature interactions efficiently. It is compared honestly with Logistic Regression, which won this run.

**Why not accuracy alone?** A majority-class predictor can look accurate while missing most attrition examples. Show recall, precision, F1 and average precision.

**Why three splits?** Training fits parameters; validation selects the experiment and threshold; test estimates held-out performance after those decisions.

**What is leakage?** Information from evaluation records influences fitting or selection. Examples include fitting the imputer on all records or applying SMOTE before splitting. This project fits preprocessing and oversampling inside training folds.

**How do embeddings work?** A pretrained encoder maps text to a numerical vector. Cosine compares normalized vector directions. Related wording can be close, but closeness does not prove a skill.

**Why RAG?** Retrieve the relevant source passages before answering. Here document, page and section metadata are preserved; generated citations and quotations are validated.

**What is FAISS?** A vector similarity search library. This small corpus uses exact inner-product search over normalized vectors rather than an approximate index.

**What is SHAP?** It allocates a model prediction's deviation from a baseline across features under the chosen explainer assumptions. Here values are log-odds contributions; they are not causal effects.

**Why a graph?** Employee–skill–role relationships are naturally many-to-many. A graph lets the reviewer inspect paths and connected capabilities.

**How are sources connected?** IBM EmployeeNumber becomes Employee_ID; auxiliary summaries join one-to-one; skills join one-to-many. Candidate records pass directly from recruitment to interview.

**What remains limited?** Small synthetic data, bounded parsing, uncalibrated estimates, heuristic skill matching, optional unverified live LLM, and missing enterprise security controls.
