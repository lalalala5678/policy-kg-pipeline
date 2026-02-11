# Step 1: Domain Schema Definition and Full-Corpus Readthrough

## 1. Objective
The objective of Step 1 is to define a controllable and evaluable domain schema for downstream extraction and policy graph construction. The schema must be evidence-driven and compatible with later UIE extraction, normalization, and graph reasoning stages.

## 2. Data Scope
- Input corpus: all policy `.txt` files under:
- `01_鐢典环鏀跨瓥`
- `02_鐢佃兘鏇夸唬涓庢竻娲佸彇鏆朻
- Total files processed: 151
- Sampling policy: no sampling; full-corpus processing only.

## 3. Method
### 3.1 Full-corpus decoding and reading
- Files were read at byte level.
- Decode strategy:
- UTF-8 strict decode first.
- GBK fallback only when UTF-8 decode fails.
- Outcome: all 151 files were decodable as UTF-8 under strict mode.

### 3.2 Corpus profiling
- A per-file extraction profile was generated for metadata, mechanism, and hard-parameter signals.
- Artifacts:
- `00_鏁寸悊璁板綍/policy_readthrough_profile.json`
- `00_鏁寸悊璁板綍/policy_readthrough_summary.json`

### 3.3 Evidence-driven schema construction
- Schema fields were introduced only when supported by corpus evidence.
- Covered dimensions:
- Metadata: issuing org, dates, region, target group, policy level, document number
- Mechanisms: TOU pricing, tiered/differential pricing, subsidy, task/assessment, technology route
- Hard parameters: time windows, price delta, price value, subsidy amount, thresholds, tier labels

### 3.4 Hard-parameter pattern verification
- Verified with full-text matches:
- Time windows (for example `08:00-11:00`, `23:00-07:00`)
- Percentage forms (for example directional and plain `%`)
- Monetary forms (for example `鍏?鍗冪摝鏃禶, `鍏?鎴穈, `涓囧厓`)
- Threshold forms (tier labels and kWh thresholds)

## 4. Outputs
- Schema: `结果文件夹/schema_v1.yaml` (current version: 1.4)
- Step report: `00_鏁寸悊璁板綍/schema_step1_readthrough_report.md`
- Change log: `00_鏁寸悊璁板綍/schema_change_log.md`
- Profiling data:
- `00_鏁寸悊璁板綍/policy_readthrough_profile.json`
- `00_鏁寸悊璁板綍/policy_readthrough_summary.json`

## 5. Key Summary Statistics
- docs_with_policy_meta_org: 72
- docs_with_policy_meta_date: 128
- docs_with_scope_region: 140
- docs_with_target_group: 140
- docs_with_mechanism_tou: 56
- docs_with_mechanism_tier: 46
- docs_with_mechanism_subsidy: 29
- docs_with_mechanism_task: 68
- docs_with_mechanism_tech: 54
- docs_with_param_time_window: 37
- docs_with_param_price_delta: 43
- docs_with_param_subsidy_amount: 45
- docs_with_param_threshold: 49

## 6. v1.2 Consistency Fixes
- UIE prompt boundary corrected:
- Prompt now contains only visible text fields.
- Internal fields are generated in postprocessing.
- Evidence model tightened:
- `evidence_scope` narrowed to `document|clause`.
- Explicit coordinate convention retained as `[start, end)`.
- Clause segmentation made explicit:
- Added `clause_segmentation` config for stable clause construction.
- Parameter model stabilized:
- Split into `ParameterDefinition` (canonical value) and `ParameterMention` (occurrence evidence).
- Added mechanism binding aid:
- `mechanism_anchor_clause_id` and related consistency gate.
- Reproducibility improved:
- Added explicit `canonical_key_spec` (`sha256`, template, formatting rules).

## 7. v1.3 Extraction-Interface Fixes
- Removed `clause_text` from prompt output schema to avoid input-output echo artifacts.
- Adopted two-stage extraction prompts:
- `uie_document_prompt_v1` for document-level metadata.
- `uie_clause_prompt_v1` for clause-level mechanism and parameter mentions.
- Restricted `ParameterMention.evidence_scope` to `clause` only.
- Added `mechanism_instantiation_spec` to define deterministic mechanism instance keys and merge rules.
- Replaced event trigger examples with Chinese trigger lexicon.
- Extended clause segmentation with additional numbering variants and table-row fallback.

## 8. Boundaries
- Step 1 defines schema and evidence baseline; it does not provide final extraction accuracy claims.
- Some filename-level metadata is truncated and requires body-level recovery.
- Unit and temporal conflicts are intentionally deferred to Step 3 normalization and validation.

## 9. v1.4 Adaptation Fixes
- Resolved clause enum conflict by adding `table_row_clause` to `Clause.clause_type`.
- Added compiled-text preprocessing contract:
- split `02_鐢佃兘鏇夸唬涓庢竻娲佸彇鏆?02_姹囨€绘嫾鎺?*.txt` by `<h2>file:` before extraction.
- Expanded mechanism typing:
- added `general_price_adjustment` for generic price reduction/adjustment policies.
- Expanded parameter typing and normalization for policy-engineering content:
- `area_subsidy_amount`, `capacity_threshold`, `tonnage_threshold`.
- Added unit normalization for `鍏?骞虫柟绫砢, `鍏?搴, `鍗冧紡瀹?鍗冪摝/鍏嗙摝`, `钂稿惃/杞介噸鍚?鎬诲惃/鍚ㄧ骇`.
- Added deterministic postprocessing rule block `parameter_type_mapping_rules`.
