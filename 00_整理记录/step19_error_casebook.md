# Step19 失败样例与修复前后对照

- case_count: 5

## Case 1: misbinding_repair
- mention_id: `pm_d7282f721172198cfb3d`
- clause_id: `6ed6029ec536fdcb1c28233730ac3cff649d9109667a7f16206c20af41b9b4dc#clause_0001`
- clause_text_snippet: 峰谷价差在蒙西电网大风季分别上浮68%、下浮52%，小风季上浮54%、下浮56%，蒙东电网峰谷价差上浮68%、下浮52%。
- before:
  - method: no_rebind
  - mechanism_type: tou_pricing
  - bind_reason: step4_fallback
  - strict_high: False
  - bind_confidence: 0.59
- after:
  - method: full
  - mechanism_type: general_price_adjustment
  - bind_reason: keyword_plus_prior
  - strict_high: True
  - bind_confidence: 0.995321
- why_it_matters: Mechanism binding recovered under full pipeline; candidate rebind and guards improve high-confidence usability.

## Case 2: misbinding_repair
- mention_id: `pm_8d915af43ffd39358e83`
- clause_id: `7a29f52e1059b42ef81433d215f1c22c31c3949674d53979a4d2d151a5bb6cee#clause_0002`
- clause_text_snippet: 根据电力供需状况，峰段电价上浮64%，谷段电价下浮59%，并实施季节性电价调整。
- before:
  - method: no_rebind
  - mechanism_type: tou_pricing
  - bind_reason: step4_fallback
  - strict_high: False
  - bind_confidence: 0.59
- after:
  - method: full
  - mechanism_type: general_price_adjustment
  - bind_reason: keyword_plus_prior
  - strict_high: True
  - bind_confidence: 0.636453
- why_it_matters: Mechanism binding recovered under full pipeline; candidate rebind and guards improve high-confidence usability.

## Case 3: misbinding_repair
- mention_id: `pm_3748301617851d4fa447`
- clause_id: `7a29f52e1059b42ef81433d215f1c22c31c3949674d53979a4d2d151a5bb6cee#clause_0002`
- clause_text_snippet: 根据电力供需状况，峰段电价上浮64%，谷段电价下浮59%，并实施季节性电价调整。
- before:
  - method: no_rebind
  - mechanism_type: tou_pricing
  - bind_reason: step4_fallback
  - strict_high: False
  - bind_confidence: 0.59
- after:
  - method: full
  - mechanism_type: general_price_adjustment
  - bind_reason: keyword_plus_prior
  - strict_high: True
  - bind_confidence: 0.636453
- why_it_matters: Mechanism binding recovered under full pipeline; candidate rebind and guards improve high-confidence usability.

## Case 4: unit_normalization_repair
- mention_id: `pm_eefe6865bfcda03de881`
- clause_id: `9f3a13c9638cc5c7deb8ecad47f6052f7b19aa02e4514ce8b2b5376c00e60c86#clause_0001`
- clause_text_snippet: 根据用电量，电价分为三档：每月210度及以下的第一档电价为0.5469元/度；
- before:
  - raw_value: 0.5469
  - raw_unit: 元/度
  - normalization_rule: yuan_per_degree_to_yuan_per_kwh
- after:
  - norm_value: 0.5469
  - norm_unit: yuan_per_kwh
  - canonical_key: 6cb81aff9d4ab10b03e73c0c245e06c96f231eeab1af328068142f452b6d4d38
- why_it_matters: Unit harmonization converts heterogeneous expressions into canonical units for cross-document comparability.

## Case 5: semantic_collision_flagged
- mention_id: `pm_7ef0ba7053b731bc4dc9`
- clause_id: `00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0000`
- clause_text_snippet: <h2>file:《关于全面加强生态环境保护坚决打好污染防治攻坚战的实施意见》.txt</h2>
2018-06-24 《关于全面加强生态环境保护坚决打好污染防治攻坚战的实施意见》
全国细颗粒物（PM2.5）未达标地级及以上城市浓度比2015年下降18%以上，地级及以上城市空气质量优良天数比率达到80%以上；
- before:
  - edge_id: edge_9797adb5e0b07a441840d1b5
  - conflict_type: semantic_collision
  - risk_level: high
  - alt_candidates_count: 1
- after:
  - action: flagged_for_review
  - support_count: 1
  - conflict_count: 0
- why_it_matters: Semantic collision is transformed into graph edge signal, enabling risk-aware review without hiding ambiguous facts.
