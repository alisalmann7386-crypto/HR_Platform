# WorkforceAI — B.Tech project report outline

## Chapter 1 — Introduction

### Background and motivation
Explain fragmentation across recruitment documents, policy PDFs, employee tables and workforce skill records. A single chatbot does not provide ML validation, source traceability or graph capacity analysis.

### Problem statement
Design an integrated, reproducible platform that turns heterogeneous HR inputs into inspectable decision-support evidence while retaining human authority.

### Objectives and scope
Document the six modules, shared candidate records and Employee_ID joins. Limit the demonstration to synthetic IBM records, synthetic auxiliary data and fictional policy documents. Exclude automated employment decisions and production enterprise access controls.

## Chapter 2 — Literature Review

Organize a comparison matrix: research area; verified paper; dataset; method; evaluation; limitations; relation to WorkforceAI.

1. HR analytics and workforce information integration. [Insert verified academic reference.]
2. Employee attrition prediction and imbalanced classification. [Insert verified academic reference.]
3. Resume–job matching, information extraction and semantic similarity. [Insert verified academic reference.]
4. Sentence embeddings and cosine similarity. [Insert verified academic reference.]
5. LLMs in HR, appropriate boundaries and human oversight. [Insert verified academic reference.]
6. Retrieval-Augmented Generation and source-grounded answering. [Insert verified academic reference.]
7. Graph-based skill representation and capacity planning. [Insert verified academic reference.]
8. Explainable AI and SHAP. [Insert verified academic reference.]

Do not invent authors, titles, publication years, DOIs or numerical results. Verify and read each selected publication before citing it. Official library documentation can support implementation details, not replace an academic literature review.

## Chapter 3 — System Analysis and Design

### Functional requirements
PDF/DOCX extraction, structured JD parsing, configurable job relevance, candidate comparison, interview questions/report, PDF policy ingestion, citation display, manual/batch inference, SHAP, graph filters, skill gaps and unified dashboards.

### Non-functional requirements
Modularity, deterministic splits, reproducibility, readable UI, explicit errors, no credential hardcoding, evidence traceability and no automated personnel action.

### Architecture and data flow
Use the README Mermaid diagram and the in-app architecture. Explain candidate session records, Employee_ID one-to-one auxiliary joins and one-to-many skill edges. Include use cases for HR reviewer, interviewer and student demonstrator. Explain local versus optional external LLM processing.

### Module design
Map each input/output contract to its source package. Add a table for feature schema, policy metadata and skill graph node/edge types.

## Chapter 4 — Methodology

1. Dataset audit; exact row count, missingness, duplicates, constants and target balance.
2. Identity mapping and feature exclusions; remaining proxy-bias limitations.
3. Stratified train/validation/test separation and training-only exploratory relationships.
4. ColumnTransformer, median/mode imputation, one-hot encoding, scaling and train-only fitting.
5. Logistic Regression and gradient boosting; why LightGBM is an experiment, not an assumed winner.
6. Class weighting and SMOTE inside training folds; fractional one-hot synthetic examples as a limitation.
7. Five-fold CV, validation average precision selection and F1 threshold sweep.
8. Sentence-transformer embeddings, L2 normalization and cosine similarity; explain exact alias versus related-skill evidence.
9. Section-aware policy chunking, FAISS search and persistent metadata.
10. Extractive policy mode versus optional LLM synthesis; valid citations do not guarantee entailment.
11. SHAP linear/tree explainers, additivity and log-odds units; no causal interpretation.
12. NetworkX graph construction, distinct employees, proficiency thresholds and capacity-gap formula.
13. Multi-source integration and strict synthetic-data labeling.

## Chapter 5 — Implementation

Describe every page and major module. Include representative function signatures and a short data example, not full source listings. Explain `.env`, CLI scripts, error handling, serialization, UI session state and no-API demo behavior. Include screenshots and describe the exact tested environment from the lockfile.

## Chapter 6 — Experiments and Results

- Dataset: 1,470 rows; split 1,029 / 220 / 221.
- Four-model validation table from `reports/model_comparison.csv`.
- Five-fold means and standard deviations from `cross_validation.csv`.
- Operating-threshold trade-off from `threshold_analysis.csv`.
- Selected model: Logistic Regression, threshold 0.35.
- Final test: accuracy 0.8552, precision 0.5526, recall 0.5833, F1 0.5676, ROC-AUC 0.8288, average precision 0.6413.
- Confusion matrix: TN 168, FP 17, FN 15, TP 21.
- Explain why these results do not establish enterprise readiness; no test-driven tuning.
- Global and local SHAP plots with units and model labels.
- RAG example: medical leave followed by temporary WFH. Check Leave section 5.1 (page 2) and WFH section 3.1 (page 1), plus adjacent exceptions. Show retrieved evidence rather than inventing a generated answer.
- Negative RAG example: unsupported astronomical query should abstain; distinguish that from a related policy question with absent detail.
- Recruitment example: canonical NLP alias, partial semantic match, missing requirement, project evidence.
- Skill capacity example with level filtering and duplicate-ID protection; results are synthetic demonstration capacities.
- Automated test and UI verification results from `VERIFICATION.md`.
- Optional live LLM integration remains unverified until a provider key is supplied. Do not substitute mocked tests for a live-generation evaluation.

## Chapter 7 — Limitations and Ethical Considerations

Small synthetic dataset; no forecast horizon; uncalibrated probabilities; demographic proxies; parsing gaps; heuristic matching weights; uncertain LLM interpretation; fictional policies; prompt injection; missing production access controls; confidentiality and data retention; synthetic auxiliary data is not predictive evidence. Employment decisions remain with authorized humans.

## Chapter 8 — Conclusion and Future Scope

Discuss the demonstrated contribution: shared records and evidence connect ML, NLP/RAG and graph analytics. Separate implemented behavior from future extensions: HRMS integration, temporal models, external validation/calibration, fairness analysis, hybrid retrieval, Neo4j, access controls, audit logs, cloud deployment and MLOps.

## Appendices

Installation commands; environment variable table without values; exact feature list and split manifest; data dictionary; test inventory; demonstration script; repository commit information; AI-assistance disclosure if required by the institution.
