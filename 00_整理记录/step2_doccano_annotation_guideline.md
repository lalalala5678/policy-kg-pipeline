# Step2 标注规范（doccano）

更新时间：2026-02-09

## 1. 目标与输入
- 目标：完成 Step2「样本文档抽样与标注规范」，为后续 UIE 两阶段抽取提供可训练数据。
- 输入语料：`01_电价政策/*.txt` 与 `02_电能替代与清洁取暖/01_政策文本/*.txt`。
- 已排除目录：`02_电能替代与清洁取暖/02_汇总拼接`、`02_电能替代与清洁取暖/03_原始压缩包`。
- 抽样主题：分时电价、阶梯电价、差别电价、补贴补助、岸电、清洁取暖。

## 2. 项目拆分（建议建两个 doccano 项目）

### 项目 A：`policy_doc_level_ie`
- 任务类型：`Sequence Labeling`
- 导入文件：`00_整理记录/step2_doccano_seed_doc_level.jsonl`
- 标注对象：文档级元信息（title 区块 + 正文前段）

#### 标签集合（项目 A）
- `ISSUE_DATE`：发文日期（如“2024年7月5日”）
- `DOCUMENT_NO`：文号（如“发改能源〔2016〕1054号”）
- `ISSUING_ORG`：发文机关（可多机构）
- `REGION`：适用地区（全国/省/市/区县）
- `TARGET_GROUP`：适用对象（居民用户、工商业用户、港口企业等）
- `EFFECTIVE_START_DATE`：实施起始日期
- `EFFECTIVE_END_DATE`：实施结束日期

### 项目 B：`policy_clause_level_ie`
- 任务类型：`Sequence Labeling`（第一轮）+ `Relation Extraction`（第二轮，可选）
- 导入文件：`00_整理记录/step2_doccano_seed_clause_level.jsonl`
- 标注对象：条款级机制与参数信息

#### 标签集合（项目 B）
- `MECHANISM_TYPE`：机制词（分时/阶梯/差别/补贴/岸电/清洁取暖/任务考核）
- `CLAUSE_TYPE`：条款类别触发词（定义/价格规则/补贴规则/执行规则/任务考核等）
- `RAW_VALUE`：原始参数值（含数值）
- `RAW_UNIT`：原始单位（元/度、万元/村、% 等）
- `DIRECTION`：方向词（上浮、下浮、提高、降低）
- `CONDITION_TEXT`：条件片段（“对…用户”“在…期间”）
- `TASK_SUBJECT`：任务主体（部门/单位）
- `TASK_ACTION`：动作（推进/组织/落实/实施/考核）
- `TASK_DEADLINE`：期限（到 2025 年、2024 年底前）
- `TASK_ASSESSMENT`：考核/验收片段

#### 关系集合（项目 B，第二轮可启用）
- `CLAUSE_SUPPORTS_MECHANISM`：`Clause -> Mechanism`
- `MECHANISM_HAS_PARAMETER_MENTION`：`Mechanism -> RAW_VALUE/RAW_UNIT`
- `MECHANISM_APPLIES_TO_TARGET`：`Mechanism -> TARGET_GROUP`
- `MECHANISM_APPLIES_TO_REGION`：`Mechanism -> REGION`

## 3. 标注边界规则（强约束）
- 只标注原文可见内容，不做推断补写。
- 最小可区分原则：尽量短 span，不吞并无关词。
- 日期/文号必须完整闭合，不能只标一部分。
- 数值与单位拆开标注：`RAW_VALUE` 与 `RAW_UNIT`分离。
- 条件片段优先就近截取，不跨越整段。
- 重复出现的同值可多次标注，后处理再去重。
- `SOURCE_PATH/TITLE/THEME` 头部行是导入辅助信息，不作为政策实体标注。

## 4. 冲突裁决规则
- 文号冲突：正文优先，标题/文件名仅补缺。
- 日期冲突：发文日期优先于发布时间描述，实施日期单独标注为 `EFFECTIVE_*`。
- 机制冲突：同条款可多机制并存，分别标注并在关系层拆分。
- 参数冲突：同条款同指标多个值（如分档）全部标注，后处理按条件拆分。
- 无参数条款：仍标 `MECHANISM_TYPE` 与任务字段，保证“无数值文本”可计算。

## 5. 质检标准（用于门禁）
- `span_valid_rate >= 99%`：span 起止合法、无越界。
- `required_field_non_empty >= 95%`：元信息核心字段不空（日期/机构至少一个）。
- `double_annotated_agreement >= 0.85`：双人抽检一致性（Cohen's kappa 或 F1）。
- `relation_consistency >= 95%`：关系端点实体类型匹配。

## 6. 示例（用于标注培训）

### 示例 A：文档级（Sequence Labeling）
文本片段：
`国家发展改革委关于进一步完善分时电价机制的通知（2021年7月29日）`

建议标注：
- `ISSUING_ORG`: `国家发展改革委`
- `MECHANISM_TYPE`: `分时电价机制`
- `ISSUE_DATE`: `2021年7月29日`

### 示例 B：条款级参数
文本片段：
`峰段电价在平段基础上上浮20%，谷段下浮30%。`

建议标注：
- `MECHANISM_TYPE`: `峰段电价`、`谷段`
- `DIRECTION`: `上浮`、`下浮`
- `RAW_VALUE`: `20`、`30`
- `RAW_UNIT`: `%`

### 示例 C：任务条款
文本片段：
`各地发展改革部门应于2025年底前完成清洁取暖改造验收。`

建议标注：
- `TASK_SUBJECT`: `各地发展改革部门`
- `TASK_ACTION`: `完成`
- `TASK_DEADLINE`: `2025年底前`
- `TASK_ASSESSMENT`: `验收`
- `MECHANISM_TYPE`: `清洁取暖改造`

## 7. 已提供种子文件
- `00_整理记录/step2_doccano_seed_doc_level.jsonl`：文档级待标注种子（38 条）
- `00_整理记录/step2_doccano_seed_clause_level.jsonl`：条款级待标注种子（42 条）
- `00_整理记录/step2_doccano_labeled_examples.jsonl`：带弱标签示例（12 条，训练前需人工复核）

## 8. 执行顺序建议
1. 先标项目 A（文档级），锁定元信息字段一致性。
2. 再标项目 B（条款级），优先机制词与参数，再补任务字段。
3. 最后做关系标注与冲突裁决，产出训练集 `train/dev/test` 划分。
