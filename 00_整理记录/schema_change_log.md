# Schema Change Log

## 2026-02-09 (v1.4 priority updates)
### Why this update
- Land the four post-check priorities into executable extraction workflow and schema constraints.

### Changes
- `Document-level compensation and arbitration`
- Added `document_level_compensation_rules` for `issue_date`, `doc_type`, `document_no`.
- Added explicit arbitration policy: body wins on conflict, filename fills only missing values, and conflicts must be logged.
- Added quality gate `document_filename_conflict_arbitration`.
- `Task-clause structuring`
- Added clause-level structured fields:
- `task_subject`, `task_action`, `task_deadline`, `task_assessment`.
- Added `task_clause_structuring_rules` (trigger, subject/action/deadline/assessment extraction specs).
- Added quality gate `task_clause_structuring_completeness`.
- Extended `uie_clause_prompt_v1` with task-structure fields.
- `Priority implementation artifacts`
- Added scripts:
- `00_整理记录/scripts/policy_extraction_utils.py`
- `00_整理记录/scripts/run_priority_updates.py`
- Added unit test:
- `00_整理记录/tests/test_postprocess_normalizer.py`
- Added generated reports:
- `schema_v1_4_fit_check_after_priority_updates.json/.md`

### Notes
- Priority3 evaluation currently uses `uie_proxy_keyword_baseline` as preflight evaluation mode.
- The evaluation set and metrics pipeline can be reused with real UIE predictions directly.

## 2026-02-09 (v1.4)
### Why this update
- Fix one hard inconsistency between clause segmentation output and clause enum.
- Improve fit for non-electricity-price policy texts (clean heating, port shore power, engineering/task policies).
- Reduce extraction drift in compiled `uni*.txt` policy bundles.

### Changes
- `Clause type consistency`
- Added `table_row_clause` into `Clause.clause_type` enum.
- Added quality gate `clause_type_enum_alignment`.
- `Mechanism typing`
- Added `general_price_adjustment` into `Mechanism.mechanism_type` to represent generic price reduction/adjustment policies that are not TOU/tiered/differential.
- Extended `PriceAdjustEvent.trigger_examples` with Chinese terms `下调`, `降价`.
- `Parameter typing and units`
- Extended `ParameterDefinition.param_type`:
- `area_subsidy_amount`, `capacity_threshold`, `tonnage_threshold`.
- Extended `norm_unit`:
- `yuan_per_sqm`, `kw`, `mw`, `kva`, `ton`, `ton_per_hour`, `deadweight_ton`, `sqm`.
- Added normalization blocks:
- `area_based_value`, `capacity_value`, `tonnage_value`.
- Added `元/度` detection in monetary normalization and normalize to `yuan_per_kwh`.
- Added `parameter_type_mapping_rules` to make type assignment deterministic after UIE extraction.
- `Compiled file preprocessing`
- Added `pre_ingestion_split.compiled_policy_files`:
- split anchor: `<h2>file:...`
- applies to: `02_电能替代与清洁取暖/02_汇总拼接/*.txt`
- adds deterministic chunk id template for traceable document split.
- Added quality gate `compiled_file_split_consistency`.
- `Clause segmentation`
- Added list marker regex support for `1)` and `一是` style clauses.

### Backward compatibility
- Kept v1.3 prompt interfaces unchanged:
- `uie_document_prompt_v1`
- `uie_clause_prompt_v1`
- Added compatibility aliases:
- `元/度 -> norm_unit=yuan_per_kwh`
- `元/平方米 -> param_type=area_subsidy_amount`
- `降价/下调电价 -> mechanism_type=general_price_adjustment`

## 2026-02-03 (v1.3)
### Why this update
- Remove non-text output fields from UIE prompts.
- Resolve scope conflict between `ParameterMention` and clause-level binding.
- Split extraction into document-level and clause-level prompts.
- Strengthen mechanism instantiation reproducibility.
- Improve Chinese event trigger usability and clause segmentation robustness.

### Changes
- `UIE prompts`
- Removed `clause_text` from prompt output fields.
- Replaced mixed prompt with:
- `uie_document_prompt_v1` (document-level metadata extraction)
- `uie_clause_prompt_v1` (clause-level mechanism and parameter extraction)
- Kept internal fields in `postprocess_generated_fields`.
- `ParameterMention scope`
- Restricted `evidence_scope` to `["clause"]` only.
- Updated `evidence_anchor_id` semantics to `clause_id` only.
- `Mechanism binding`
- Added `mechanism_instantiation_spec` with deterministic instance key and merge rules.
- Retained `mechanism_anchor_clause_id` and `mechanism_anchor_clause`.
- `Event trigger examples`
- Replaced English triggers with Chinese trigger lexicon (unicode-escaped form).
- `Clause segmentation`
- Added more numbering patterns: `（一）`, `1.`, `一、`.
- Added `table_row_fallback` for line+column structured rows.
- `Quality gates`
- Updated anchor consistency gate to clause-only scope in v1.3.

### Backward compatibility
- Added alias mapping from `uie_schema_prompt_v1_2` to `uie_document_prompt_v1 + uie_clause_prompt_v1`.
- Kept legacy alias entries; old pipelines can migrate incrementally.

## 2026-02-03 (v1.2)
### Why this update
- Remove non-text-native fields from UIE prompt.
- Solidify clause-only evidence workflow (no sentence scope in this phase).
- Add stronger mechanism-clause binding.
- Make canonical key generation reproducible.

### Changes
- `UIE prompt contract`
- Replaced `uie_schema_prompt_v1_1` with `uie_schema_prompt_v1_2`.
- Prompt now keeps only visible text fields:
- `title`, `document_no`, dates, org/region/target names, mechanism fields, clause fields, raw value fields.
- Added `postprocess_generated_fields`:
- `param_type`, `norm_*`, evidence fields, `canonical_key`.
- `Evidence scope`
- Restricted `ParameterMention.evidence_scope` to `document|clause`.
- Updated anchor rule: `evidence_anchor_id` must be `policy_id` or `clause_id`.
- Added `clause_segmentation` config block to standardize clause construction.
- `Mechanism binding`
- Added `Mechanism.mechanism_anchor_clause_id`.
- Added relation `mechanism_anchor_clause (Mechanism -> Clause)`.
- Added gate `mechanism_binding_consistency`.
- `Canonical key reproducibility`
- Added `canonical_key_spec`:
- algorithm: `sha256`
- encoding: `utf-8`
- fixed input template and value formatting rules.
- Added gate `canonical_key_reproducibility`.

### Backward compatibility
- Added compatibility aliases from `uie_schema_prompt_v1_1` to `uie_schema_prompt_v1_2`.
- Kept old alias mappings for legacy field names.

## 2026-02-03 (v1.1)
### Why this update
- Fix prompt/schema field mismatches.
- Define evidence span coordinate system explicitly.
- Separate canonical parameter values from parameter mentions.

### Changes
- `PolicyDocument`
- Added `document_no`.
- `UIE prompt`
- Replaced `effective_date` with `effective_start_date` and `effective_end_date`.
- Renamed prompt fields to align with schema attribute names.
- Added `compatibility_aliases` for old names.
- `Evidence model`
- Added `evidence_coordinate_system` section.
- Defined offset basis and `[start, end)` span convention.
- Added scope-based anchor requirements (`document|clause|sentence`).
- `Parameter model`
- Replaced old single `Parameter` concept with:
- `ParameterDefinition` (normalized canonical value)
- `ParameterMention` (raw text occurrence + evidence)
- Updated relations:
- `mechanism_has_parameter_definition`
- `clause_has_parameter_mention`
- `parameter_mention_refers_to_definition`
- `mention_in_policy`
- `mention_supports_mechanism`
- `Quality gates`
- Added `prompt_schema_alignment` and `evidence_anchor_consistency`.
- Updated evidence gate to validate mention-level evidence.

### Backward compatibility
- Kept alias mapping for old prompt names in `compatibility_aliases`.
- Existing downstream code should migrate from `Parameter` to `ParameterDefinition` + `ParameterMention`.
