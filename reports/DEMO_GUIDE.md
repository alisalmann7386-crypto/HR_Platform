# WorkforceAI — 7–10 minute demonstration

1. **Home and Dashboard (1 minute):** introduce the six modules. Show 1,470 historical synthetic records and explain Employee_ID joins. Auxiliary fields and capacities are invented, not real HR evidence.
2. **Recruitment (1.5 minutes):** leave the fictional demo checkbox enabled and use the bundled ML Engineer JD. Select semantic matching and Analyze qualifications. Compare mandatory/preferred evidence and project similarities. Open the parsed JD. Explain configurable weights and input-order comparison; no hire/reject labels.
3. **Interview (1 minute):** select Candidate 01 and Generate interview. Show the RAG project question. For overfitting, paste: "Training accuracy is high but validation accuracy is low. I would use cross-validation and regularization such as dropout, then check a held-out set." Inspect concept coverage, note that local mode does not prove correctness, add interviewer notes and export a report.
4. **Policy assistant (1.5 minutes):** ask "Can an employee take medical leave followed by temporary work from home?" Show the actual Leave and WFH chunks with pages and sections. Explain separate approval, capacity to work and exceptions as stated in the PDFs. No API means exact excerpts, visibly labeled. Optional configured LLM synthesis is a separate mode.
5. **Attrition (1 minute):** select an employee, show the probability and attention band. Explain positive/negative SHAP contributions in log-odds and that they are not causes. Try manual entry or `data/processed/employee_upload_example.csv` and export.
6. **Model Performance (1 minute):** compare all four actual validation results. Logistic Regression won under validation average precision. Threshold 0.35 was selected on validation, not test. Explain test precision, recall, F1, ROC-AUC and average precision.
7. **Skill graph (1 minute):** filter department/role/employee. Hover nodes and inspect edges. Explain distinct employee counting and required proficiency. Show role gaps and voluntary training options. Graph display filters do not silently change the full capacity calculation.
8. **Return to Dashboard (30 seconds):** show joined performance, attendance, training, skill gaps and model estimates. Use the policy investigation link. Emphasize evidence for human review.

## Before presenting

- Install requirements, ensure model artifacts exist and build the semantic policy index.
- Open every page once to warm local caches; first MiniLM download requires internet.
- The packaged models are trained already. Use notebooks or CLI only if reproducing the experiments.
- Optional LLM: configure your provider/model/key in `.env`, then enable the page checkbox. Do not expose the file or provider credential in screenshots.
- Use only the included fictional candidate files during a public demonstration.
- Read `VERIFICATION.md` for actual tested paths and unverified external-provider behavior.
