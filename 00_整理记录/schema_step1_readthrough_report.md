# Step1 Readthrough and Schema Report

Updated at: 2026-02-09

## 1) Corpus coverage and method
- Scope: full readthrough of all policy `.txt` files in corpus groups.
- Total policy files processed: 151.
- Decode strategy:
- UTF-8 strict decode first.
- GBK fallback only when UTF-8 decode fails.
- Output artifacts:
- `policy_readthrough_profile.json` (per-file hit profile)
- `policy_readthrough_summary.json` (global summary)

## 2) Summary evidence from full corpus
- file_count: 151
- encoding_utf8: 151
- total_chars: 128968
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

## 3) Hard-parameter evidence patterns found
- Time windows: `08:00-11:00`, `23:00-07:00`, `19:30-21:30`
- Percentages: directional percent forms and plain percent forms (for example `20%`, `55%`, `100%`)
- Price values: `0.49 yuan/kWh`, `0.02 yuan/kWh` (normalized from raw CN units)
- Subsidy amounts: `600 yuan/household`, `1500 yuan/household`, `16.2 ten_thousand_yuan`
- Thresholds: tier labels (tier1/tier2/tier3), kWh thresholds, comparative thresholds

All examples above were extracted from corpus text matches, not inferred.

## 4) Step1 output
- Main schema file: `schema_v1.yaml` (version 1.4)
- Coverage in schema:
- Metadata: issuer, dates, region, target, policy level, document number
- Mechanisms: TOU pricing, tiered pricing, differential/penalty pricing, subsidy, task/assessment, technology route
- Parameter modeling: `ParameterDefinition` + `ParameterMention` split
- Graph relations: policy-mechanism, mechanism-parameter_definition, clause-parameter_mention, mention-definition, policy-policy

## 5) v1.1 baseline fixes (consistency pass)
- Fixed prompt/schema mismatch:
- Added `document_no` to `PolicyDocument`
- Replaced single `effective_date` prompt field with `effective_start_date` and `effective_end_date`
- Unified prompt fields with schema attributes and added `compatibility_aliases`
- Fixed evidence coordinate ambiguity:
- Added `evidence_coordinate_system` with scope-specific anchor rules and `[start, end)` convention
- Added required evidence fields on mention records: `evidence_scope`, `evidence_anchor_id`
- Fixed parameter granularity ambiguity:
- Replaced single `Parameter` with:
- `ParameterDefinition` for canonical normalized values
- `ParameterMention` for concrete text occurrences and evidence
- Updated relation set to enforce mention-to-definition linkage

## 6) Known limits
- Some filenames are truncated; document number or full title may need body-level recovery.
- Corpus mixes regulatory notices and strategy/program docs, so mechanism fields are not guaranteed in every file.
- Unit and temporal ambiguities still require Step3 normalization and consistency checks.

## 7) v1.2 update note
- Prompt boundary tightened: UIE prompt now only includes directly visible text fields.
- Internal fields (`param_type`, normalized values, evidence ids/spans, canonical_key) are generated in postprocessing.
- Evidence scope narrowed to `document|clause`; sentence scope is removed for current phase.
- Added `clause_segmentation` config to reduce annotation/segmentation drift.
- Added mechanism anchor (`mechanism_anchor_clause_id`) and binding consistency gate.
- Added explicit canonical key generation spec (`sha256`, fixed template, fixed formatting).

## 8) v1.3 update note
- Removed `clause_text` from UIE prompt output fields.
- Switched to two-stage prompts:
- `uie_document_prompt_v1` for document-level metadata.
- `uie_clause_prompt_v1` for clause-level mechanism/parameter extraction.
- Restricted mention evidence scope to `clause` only to avoid anchor ambiguity.
- Added `mechanism_instantiation_spec` to standardize mechanism instance creation and merge.
- Replaced event trigger examples with Chinese trigger lexicon.
- Enhanced `clause_segmentation` with numbering variants and table-row fallback strategy.

## 9) v1.4 update note
- Fixed enum consistency: added `table_row_clause` into `Clause.clause_type`.
- Added preprocessing split contract for compiled files in `02_汇总拼接` using `<h2>file:` anchor.
- Added mechanism type `general_price_adjustment` for non-TOU generic price adjustment policies.
- Expanded parameter schema for engineering-style policy constraints:
- `area_subsidy_amount`, `capacity_threshold`, `tonnage_threshold`.
- Expanded normalization for:
- `元/度` -> `yuan_per_kwh`
- `元/平方米` -> `yuan_per_sqm`
- capacity units (`kVA/kW/MW/万千瓦`)
- tonnage units (`蒸吨/载重吨/总吨/吨级/万吨`)
- Added quality gates:
- `clause_type_enum_alignment`
- `compiled_file_split_consistency`
