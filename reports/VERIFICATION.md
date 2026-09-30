# Verification record

## Repository review — 30 September 2026

Reviewed GitHub main at `22253c59bded77dd524f6be763feb3ff5a3d27fc` in a fresh Python 3.12 environment.

Fixed repeat reads of uploaded documents; stale interview analysis, answers and notes after candidate replacement; stale answer display after policy-index replacement; malformed LLM JSON handling; missing/blank workforce identity validation; and the skill graph's forced white background. Interview analysis is now displayed only beside its matching question. Attrition IDs are trimmed before duplicate validation.

Validation: **57 tests passed**, including semantic matching/retrieval, all Streamlit page checks, saved model predictions, SHAP, and 17 added regression cases. `pip check`, Python compilation, `git diff --check`, and a changed-file credential-pattern scan passed. Three third-party SHAP/Matplotlib deprecation warnings remain.

No model retraining was needed for these input/session fixes; saved test predictions still match the loaded model. Live external LLM calls and browser visual inspection were not verified in this review. LLM malformed-response behavior was tested using mocked outputs.

Reproduce from the repository root after installing requirements and building the policy index:

```bash
python -m pytest -q
```

The following section records the original build, including its original 40-test count.

## Original build: executed successfully

- Created a clean Python 3.12 virtual environment and installed the application requirements. `pip check`: no broken requirements.
- Inspected the uploaded IBM CSV: 1,470 rows and 35 original columns. Read all six supplied two-page policy PDFs; no policy contents were replaced.
- Generated training-split EDA, distributions and correlations; full-data audit reports dimensions, missingness, duplicates and target counts.
- Trained Logistic Regression, LightGBM, weighted LightGBM and SMOTE+LightGBM with five-fold training-only CV. Saved four model artifacts, actual comparison, experiments and threshold sweep.
- Selected Logistic Regression by validation average precision; selected threshold 0.35 by validation F1. Test evaluated after selection: accuracy 0.8552, precision 0.5526, recall 0.5833, F1 0.5676, ROC-AUC 0.8288, average precision 0.6413. No test-driven tuning.
- Verified unique/disjoint split IDs, training-only preprocessing statistics, unknown-category transformation, saved-pipeline reload and exact match with saved test probabilities.
- Generated seed-42 auxiliary skills, projects, performance, attendance, training and role requirements using IBM Employee_ID values. Verified one-to-one summary joins and no unknown employee IDs.
- Generated two fictional PDF and DOCX resume pairs. Tested both formats and visually inspected a rendered sample PDF.
- Built the actual MiniLM/FAISS semantic policy index: 6 documents, 12 pages, 72 chunks, 384 embedding dimensions, 140-word chunk size and 25-word overlap.
- Verified semantic skill comparison and medical-leave-to-WFH retrieval across both source documents. Tested chunk metadata, unsupported-query abstention, lexical fallback and invalid LLM citation rejection.
- Verified selected-model LinearSHAP and weighted LightGBM TreeSHAP additivity in log-odds units.
- Launched Streamlit; HTTP health returned 200 when checked within the same runtime process/network scope.
- Streamlit AppTest rendered Home plus every module and information page. Exercised recruitment analysis, recruitment-to-interview handoff and report creation, manual prediction and policy retrieval.
- Final suite: **40 passed**, with three third-party SHAP/Matplotlib pending-deprecation warnings, no failing tests. Exact output: `reports/test_results.txt`.
- Python compilation and final repository checks completed before commit. Git ignore rules exclude API environment files, credentials, caches, virtual environments and vector_store.

## Remaining unverified or deliberately limited

- Live Groq/Mistral/OpenAI-compatible generation was not executed: no provider API key/model was supplied. Optional transport and JSON/citation validation exist; mocked failure tests are not live provider validation.
- Browser screenshots and visual browser QA could not complete: Chromium startup was blocked by the execution sandbox's socket restriction. AppTest and server health passed; no screenshot or browser interaction success is fabricated.
- Public hosting/deployment was not requested or performed. Streamlit configuration and deployment instructions are included.
- No enterprise external validation, fairness audit, calibrated probabilities, causal analysis or forecast-horizon claim. Synthetic auxiliary data does not establish real workforce findings.

## Reproduction

Run the README commands from the repository root. The semantic tests need the downloaded embedding model and built policy index. `pytest -m 'not semantic'` can be used for local core checks when offline. Do not repeatedly optimize against the saved test labels.
