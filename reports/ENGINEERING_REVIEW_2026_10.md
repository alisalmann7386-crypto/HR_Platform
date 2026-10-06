# WorkforceAI engineering review — 7 October 2026 (India)

## Scope and outcome

Reviewed the actual GitHub checkout at `0c8c4b3b615012ff1fbb130d77e831b519cf8d41`. The earlier conversation's local changes were never published and the temporary workspace had been removed. This implementation was rebuilt against the current repository and independently tested; historical test counts were not reused as current evidence.

The baseline passed 62 tests but still contained the reproduced defects below. The changes preserve the existing models, dataset, training pipeline and core workflows. This is an improved demonstration system, not a certification that every possible bug is eliminated or that the app is suitable for confidential production HR use.

## Findings and fixes

| Severity | File / path | Cause / effect | Fix implemented |
|---|---|---|---|
| High | `src/rag/policy_agent.py` | A fabricated claim passed when accompanied by a genuine quote. The probe displayed automatic leave approval despite a manager-approval requirement. | Validate citations and display selected full source excerpts; discard unchecked generated interpretations. Invalid citations abstain; provider failures return labeled extractive evidence. |
| High | `pages/2_Interview_Agent.py`, `src/interview/session.py` | Position-based widget identities attached state to the wrong question after removal, and hidden widgets lost drafts. Old analysis could remain visible after answer edits. | Stable interview/question IDs, independent draft storage, isolated report snapshots, and display checks against the analyzed question and answer. |
| High | `src/recruitment/resume_parser.py` | A References section was treated as continued professional experience, crediting another person's AWS/Docker skills. | Recognize unsupported section boundaries and inline professional headings. |
| Medium | `src/recruitment/jd_parser.py`, `src/recruitment/skill_extractor.py` | Requirement-first descriptions lost the first skill. A negated first occurrence hid a later positive skill mention. | Preserve requirement-first input and inspect successive alias occurrences with local negation checks. |
| High | `src/recruitment/matcher.py` | Missing projects removed their weight from the denominator, which could improve the score. | Keep required project alignment active with zero evidenced credit and an explicit unknown warning. |
| High | `src/utils/validators.py`, `pages/4_Attrition_Intelligence.py` | Invalid ordinal/count values and contradictory tenure values were accepted, including `JobLevel=999`. | Domain, integer and related-field validation; warnings outside observed training ranges. |
| High | `src/utils/llm.py`, `src/interview/response_analyzer.py`, `src/interview/question_generator.py` | Provider outages escaped, malformed transport content was not normalized, report types were incompletely checked, and local fallbacks were not clearly identified. | Sanitize transport failures, validate response structure/evidence, and label local fallback questions and analysis. |
| High | `src/rag/vector_store.py`, `src/rag/bootstrap.py` | Incomplete/corrupt index artifacts could be reused; concurrent reads/rebuilds could observe inconsistent files. | File locking, checksums/count checks, isolated builds, atomic publication and rollback. Chunk settings/version now invalidate old indexes. |
| High | `src/rag/chunker.py` | Word-based chunks can exceed the encoder token budget and silently lose their ending during encoding. | Token-budget splitting including heading/special tokens; exact source spans/citations retained; bounded overlap and rejection of unrepresentable headings. |
| High | `pages/3_HR_Policy_Assistant.py` | Semantic initialization ran before fallback controls, blocking offline recovery. | Render engine choice first and handle setup failure; lexical mode remains accessible. Separate bundled indexes by engine. |
| Medium | `pages/1_Recruitment_Intelligence.py`, `pages/3_HR_Policy_Assistant.py` | Changed inputs could be shown with old results without clear provenance. | Fingerprint recruitment inputs; retain the submitted policy question/settings and show stale-result warnings. |
| Medium / security | `src/rag/uploads.py` | Temporary policy files lacked consistent failed-build/replacement cleanup and aggregate bounds. | Per-session locations, 20 files / 20 MB each / 50 MB total bounds, cleanup on failure/replacement/logout, explicit deletion and opportunistic 24-hour idle expiry. |
| High / deployment | `requirements.txt`, `requirements-lock.txt`, `src/attrition/predict.py`, CI | Broad version ranges could drift from saved-model versions; the old lock contradicted the ReportLab range and included unrelated browser tooling. CPU installation differed between local/cloud paths. | Pin model-sensitive dependencies and tested runtime versions; use CPU PyTorch on Linux; regenerate the lock; validate model versions before deserialization; align CI installation. |
| Medium / configuration | `src/rag/bootstrap.py` | Automatic index setup ignored documented chunk-size environment settings. | Apply environment settings when explicit arguments are absent; test the resulting metadata. |
| Medium / evaluation | `scripts/evaluate_policy.py` | “Abstention” was calculated from empty retrieval rather than actual answer behavior. | Evaluate the answer mode and separately report supported answer coverage and unsupported abstention. |
| Security improvement | `src/utils/access.py`, `src/utils/ui.py`, `app.py` | No application access gate or page-role enforcement existed. Unexpected exception details were shown directly. | Optional scrypt sign-in, viewer/reviewer/admin page rules, in-process failed-login limiting, logout cleanup and confidential-mode fail-closed checks. Unexpected failures show generic messages and log only the error type. |
| UI/UX | `assets/workforce.css`, `src/utils/theme.py`, `app.py`, Home/Dashboard | Flat navigation, repeated cards, a long chart feed and a generic blue theme obscured tasks; “AI insights” described rule-based output. | Charcoal/sage design, task-based landing page, grouped navigation, dashboard tabs, accurate discussion-prompt labeling, mobile automatic sidebar and improved caption contrast. |

## Verification

- Baseline: **62 passed**.
- Current full suite: **106 passed**; three upstream SHAP pending-deprecation warnings.
- Offline suite in a clean copy with an empty Hugging Face cache: **98 passed, 7 semantic tests deselected** before the final environment-setting regression; that additional regression also passed offline. No semantic tests are claimed to run without model files.
- Fresh Python 3.12 environment installed successfully. `pip check` found no broken dependencies; the resolved lock dry-run succeeded.
- **71 Python files** parsed and **45 src modules** imported.
- Clean-copy deployment smoke: saved Logistic Regression loaded, six policy documents indexed and six evidence chunks retrieved.
- Real browser: desktop landing page, dashboard and 390-pixel mobile landing page rendered; nine dashboard charts present, no Streamlit exception panels, no mobile horizontal overflow. Mobile screenshot inspected after switching the sidebar to automatic mode.
- Streamlit localhost health: HTTP **200**, body `ok`.
- Policy benchmark, 26 author-curated fictional cases: source Recall@5 **1.0**, supported coverage **22/22**, unsupported abstention **4/4**. This is not an independent claim-faithfulness benchmark.
- Recruitment benchmark, 39 author-curated cases: extraction precision **0.9855**, recall **0.9714**; semantic alignment precision **0.9565**, recall **1.0**. These non-perfect results remain visible.
- Diff self-review, whitespace check and changed-file credential-pattern scan completed. Models and training data were not replaced. No actual provider credentials were used.

Browser screenshots: [desktop overview](screenshots/overview-desktop.png), [desktop dashboard](screenshots/dashboard-desktop.png), [mobile overview](screenshots/overview-mobile.png).

One regression mock initially rejected keyword arguments before it could simulate the intended provider failure; its signature was corrected. Browser automation initially searched for an exact accessible link name that included an icon; the selector was corrected. Neither failure was suppressed in application code.

## What more to improve, in priority order

1. **Independent quality evaluation.** Expand resumes, job descriptions and policy questions with human-reviewed examples: paraphrases, unsupported topics, negation, tables, unconventional headings and conditions spanning passages. The remaining extraction/alignment benchmark errors are not “fixed” by changing their labels.
2. **Production security and records.** Before using confidential data, integrate organizational identity/MFA, durable audit records, tenant isolation, a retention policy and scheduled cleanup. The optional gate and in-memory rate limit are demonstration controls, not an enterprise security boundary.
3. **Actual hosted validation.** Run Community Cloud memory/cold-start checks and a live-provider smoke test with fictional inputs. Local success does not establish remote resource capacity or provider quality. Python 3.12 and repository-root `app.py` are the tested setup; host secrets are manual configuration.
4. **Recruitment evidence quality.** Broaden the skill ontology, add OCR/table extraction if needed, distinguish required versus preferred experience more deeply, and show explicit uncertainty for ambiguous sections. Do not convert heuristic scores into automatic hiring recommendations.
5. **RAG relevance.** Evaluate alternative retrieval/reranking and condition-aware neighboring passages against the expanded benchmark. The current lexical topic gate may reject valid paraphrases; similarity is not confidence and source text alone is not legal/HR interpretation.
6. **Performance.** Profile concurrent users and larger documents before optimizing repeated index validation, model initialization and eager chart rendering. Preserve isolation and integrity checks when adding caches.
7. **Product workflow.** If required by the project scope, add consent-aware saved review histories, audited reviewer comments and accessible PDF summaries. Current session drafts are ephemeral, not durable HR records.

## Manual setup and release limits

- Install the revised dependencies before loading saved models. No retraining is required.
- Configure `WORKFORCE_AUTH_ENABLED` and `workforce_users` hashes/roles in host secrets if enabling sign-in; README gives the interactive hash command. Never commit the actual secrets file.
- Optional live LLM use needs a provider, model and API key. Enabling the checkbox sends submitted content to that provider.
- Semantic mode requires model files or a first download. Offline policy mode is explicitly lexical.
- This branch is intended for a pull request. Pushing it does not update a Streamlit deployment tracking `main`; merge/deployment is a separate step.
- Actual Community Cloud deployment, independent real-world HR validation and live-provider quality remain unverified. Browser observations apply to the tested Chromium desktop/mobile viewports, not every browser/device.
