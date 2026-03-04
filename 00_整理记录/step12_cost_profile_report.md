# Step12 成本画像与复现对齐报告

## 环境
- timestamp_utc: 2026-03-04T08:25:13Z
- os: Linux-6.8.0-71-generic-x86_64-with-glibc2.39
- python: 3.12.3
- cpu_cores: 2
- mem_total_gib: 1.922

## 数据与图规模
- file_total: 151
- char_total: 128968
- document_units: 317
- clause_total: 2022
- strict_high nodes/edges: 2494/4868
- strict_all nodes/edges: 2892/5742
- neo4j nodes/edges: 2892/10610

## 产物体量（MB）
| artifact | size_mb |
|---|---:|
| step8_iter1_mb | 12.049 |
| step8_2_iter1_mb | 1.634 |
| step9_iter1_mb | 0.098 |
| step5_mentions_mb | 1.689 |
| step5_definitions_mb | 0.137 |
| step5_triples_mb | 0.536 |

## 脚本耗时
| id | elapsed_sec | return_code |
|---|---:|---:|
| step5_normalize_validate_costprobe | 0.469 | 0 |
| step6_gold_iaa_costprobe | 0.189 | 0 |
| step8_2_query_pack_costprobe | 0.343 | 0 |
| step9_query_eval | 0.342 | 0 |
| step9_gate_eval | 0.042 | 0 |

## 备注
- Benchmarks are measured on cached intermediate artifacts and include script runtime only.
- Step4 full UIE inference cost is not included in this report.
