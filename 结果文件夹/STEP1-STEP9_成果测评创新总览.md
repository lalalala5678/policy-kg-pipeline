# STEP1-STEP9 创新方法与全指标总览（完整版）
更新时间：2026-02-12 15:28:28 CST

用途：论文写作、项目归档、外部评审统一口径

## 文档说明
- 本文档按 Step1-Step9 逐步给出：`创新方法` + `全指标`。
- “全指标”采用对应评测/门禁 JSON 的完整转录，避免人工摘录漏项。
- 若同一步存在多个评测报告，全部并列纳入。

## Step1：领域 Schema 定义与全量读通
### 创新方法
- 全量语料（非抽样）解码与证据扫描，先构建“语料可观测事实”再反推 Schema 字段。
- 采用 `UTF-8 strict -> GBK fallback` 解码策略，并保留解码统计，避免编码噪声误导字段设计。
- 将参数建模拆分为 `ParameterDefinition`（规范定义）与 `ParameterMention`（出现证据），从 Step1 即保证后续图谱可追溯。
- 明确 `canonical_key_spec`、`clause_segmentation`、`evidence_scope` 等协议项，为 Step3-Step9 一致性打底。

### 全指标
#### Step1 全量读通汇总指标
来源：`00_整理记录/policy_readthrough_summary.json`

```json
{
  "file_count": 151,
  "encoding_utf8": 151,
  "encoding_gbk": 0,
  "total_chars": 128968,
  "avg_chars": 854.09,
  "docs_with_policy_meta_org": 72,
  "total_hits_policy_meta_org": 202,
  "docs_with_policy_meta_date": 128,
  "total_hits_policy_meta_date": 381,
  "docs_with_scope_region": 140,
  "total_hits_scope_region": 1273,
  "docs_with_target_group": 140,
  "total_hits_target_group": 1717,
  "docs_with_mechanism_tou": 56,
  "total_hits_mechanism_tou": 335,
  "docs_with_mechanism_tier": 46,
  "total_hits_mechanism_tier": 111,
  "docs_with_mechanism_subsidy": 29,
  "total_hits_mechanism_subsidy": 591,
  "docs_with_mechanism_task": 68,
  "total_hits_mechanism_task": 485,
  "docs_with_mechanism_tech": 54,
  "total_hits_mechanism_tech": 1255,
  "docs_with_param_time_window": 37,
  "total_hits_param_time_window": 246,
  "docs_with_param_price_delta": 43,
  "total_hits_param_price_delta": 110,
  "docs_with_param_subsidy_amount": 45,
  "total_hits_param_subsidy_amount": 389,
  "docs_with_param_threshold": 49,
  "total_hits_param_threshold": 262
}
```

## Step2：主题抽样与标注规范
### 创新方法
- 采用“主题规则命中 + 路径优先 + 年份均衡”的抽样机制，避免训练样本集中于单年份或单文体。
- 文档级与条款级双视角标注模板并行设计，直接对接 Step4 UIE 与 Step5 归一化链路。
- 通过去重样本池统一多主题重叠文档，降低重复标注开销。

### 全指标
#### Step2 抽样与标注池指标
来源：`00_整理记录/step2_theme_sampling.json`

```json
{
  "generated_at": "2026-02-09 18:33:27",
  "scope": {
    "total_policy_docs": 147,
    "exclude_paths": [
      "02_电能替代与清洁取暖/02_汇总拼接/*.txt",
      "02_电能替代与清洁取暖/03_原始压缩包/*"
    ],
    "per_theme_target": 8,
    "themes_required": [
      "分时电价",
      "阶梯电价",
      "差别电价",
      "补贴补助",
      "岸电",
      "清洁取暖"
    ]
  },
  "theme_sampling": [
    {
      "theme_key": "tou_pricing",
      "theme_name_zh": "分时电价",
      "candidate_count": 53,
      "sampled_count": 8,
      "sampled_docs": [
        {
          "source_path": "01_电价政策/01_分时电价/2022年12月6日 河北发改委印发《关于明确居民峰谷分时电价政策的通知》.txt",
          "title": "2022年12月6日 河北发改委印发《关于明确居民峰谷分时电价政策的通知》",
          "year": 2022,
          "char_count": 465,
          "score": 51,
          "match_keywords": [
            "分时电价",
            "峰谷",
            "谷段"
          ]
        },
        {
          "source_path": "01_电价政策/01_分时电价/2021年12月14日 山西省发展和改革委员会关于完善分时电价机制有关事项的通知.txt",
          "title": "2021年12月14日 山西省发展和改革委员会关于完善分时电价机制有关事项的通知",
          "year": 2021,
          "char_count": 341,
          "score": 51,
          "match_keywords": [
            "分时电价",
            "尖峰",
            "峰谷",
            "时段电价"
          ]
        },
        {
          "source_path": "01_电价政策/01_分时电价/2024年8月27日 海南省发展和改革委员会关于调整电动汽车峰谷分时电价政策有关.txt",
          "title": "2024年8月27日 海南省发展和改革委员会关于调整电动汽车峰谷分时电价政策有关",
          "year": 2024,
          "char_count": 357,
          "score": 49,
          "match_keywords": [
            "分时电价",
            "峰谷",
            "平段",
            "谷段"
          ]
        },
        {
          "source_path": "01_电价政策/01_分时电价/2023年7月31日 广西壮族自治区发展和改革委员会关于优化峰谷分时电价机制的通.txt",
          "title": "2023年7月31日 广西壮族自治区发展和改革委员会关于优化峰谷分时电价机制的通",
          "year": 2023,
          "char_count": 295,
          "score": 47,
          "match_keywords": [
            "分时电价",
            "尖峰",
            "峰谷",
            "平段"
          ]
        },
        {
          "source_path": "01_电价政策/01_分时电价/2021年12月24日 天津市发展改革委关于峰谷分时电价政策有关事项的通知.txt",
          "title": "2021年12月24日 天津市发展改革委关于峰谷分时电价政策有关事项的通知",
          "year": 2021,
          "char_count": 331,
          "score": 51,
          "match_keywords": [
            "分时电价",
            "尖峰",
            "峰谷",
            "平段"
          ]
        },
        {
          "source_path": "01_电价政策/01_分时电价/2024年7月29日 黑龙江省发展和改革委员会关于进一步完善峰谷分时电价政策措施.txt",
          "title": "2024年7月29日 黑龙江省发展和改革委员会关于进一步完善峰谷分时电价政策措施",
          "year": 2024,
          "char_count": 343,
          "score": 45,
          "match_keywords": [
            "分时电价",
            "尖峰",
            "峰谷",
            "时段电价"
          ]
        },
        {
          "source_path": "01_电价政策/01_分时电价/2024年7月5日 甘肃省发展和改革委员会关于优化调整工商业等用户峰谷分时电价政.txt",
          "title": "2024年7月5日 甘肃省发展和改革委员会关于优化调整工商业等用户峰谷分时电价政",
          "year": 2024,
          "char_count": 400,
          "score": 43,
          "match_keywords": [
            "分时电价",
            "峰谷"
          ]
        },
        {
          "source_path": "01_电价政策/01_分时电价/2021年11月23日 广西壮族自治区发展和改革委员会关于完善我区峰谷分时电价机.txt",
          "title": "2021年11月23日 广西壮族自治区发展和改革委员会关于完善我区峰谷分时电价机",
          "year": 2021,
          "char_count": 337,
          "score": 43,
          "match_keywords": [
            "分时电价",
            "尖峰",
            "峰谷",
            "时段电价"
          ]
        }
      ]
    },
    {
      "theme_key": "tiered_pricing",
      "theme_name_zh": "阶梯电价",
      "candidate_count": 45,
      "sampled_count": 8,
      "sampled_docs": [
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2024年1月8日 湖南省发展改革委员会关于进一步完善居民阶梯电价制度的通知.txt",
          "title": "2024年1月8日 湖南省发展改革委员会关于进一步完善居民阶梯电价制度的通知",
          "year": 2024,
          "char_count": 354,
          "score": 44,
          "match_keywords": [
            "一户多人口",
            "第一档",
            "第三档",
            "第二档",
            "阶梯电价"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2012年6月15日 海南省物价局关于试行居民阶梯电价的通知.txt",
          "title": "2012年6月15日 海南省物价局关于试行居民阶梯电价的通知",
          "year": 2012,
          "char_count": 376,
          "score": 42,
          "match_keywords": [
            "第一档",
            "第三档",
            "第二档",
            "阶梯电价"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2016年10月11日 广西壮族自治区物价局关于调整居民生活用电阶梯电价政策有关.txt",
          "title": "2016年10月11日 广西壮族自治区物价局关于调整居民生活用电阶梯电价政策有关",
          "year": 2016,
          "char_count": 352,
          "score": 32,
          "match_keywords": [
            "第一档",
            "第三档",
            "第二档",
            "阶梯电价"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2021年4月29日 广东省发展改革委关于居民阶梯电价“一户多人口”政策有关事项.txt",
          "title": "2021年4月29日 广东省发展改革委关于居民阶梯电价“一户多人口”政策有关事项",
          "year": 2021,
          "char_count": 258,
          "score": 32,
          "match_keywords": [
            "一户多人口",
            "阶梯电价"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2023年12月27日 安徽省发展改革委关于居民阶梯电价“一户多人口”政策有关事.txt",
          "title": "2023年12月27日 安徽省发展改革委关于居民阶梯电价“一户多人口”政策有关事",
          "year": 2023,
          "char_count": 220,
          "score": 32,
          "match_keywords": [
            "一户多人口",
            "阶梯电价"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2019年7月9日 山东省发展和改革委员会关于居民阶梯电价制度有关事项的通知.txt",
          "title": "2019年7月9日 山东省发展和改革委员会关于居民阶梯电价制度有关事项的通知",
          "year": 2019,
          "char_count": 241,
          "score": 28,
          "match_keywords": [
            "第一档",
            "第三档",
            "第二档",
            "阶梯电价"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2013年6月17日 青海省发展和改革委员会关于试行居民阶梯电价的通知.txt",
          "title": "2013年6月17日 青海省发展和改革委员会关于试行居民阶梯电价的通知",
          "year": 2013,
          "char_count": 254,
          "score": 26,
          "match_keywords": [
            "第一档",
            "第三档",
            "第二档",
            "阶梯电价"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2018年12月29日 山东省发展改革委关于炼化和焦化企业生产用电实行阶梯电价政.txt",
          "title": "2018年12月29日 山东省发展改革委关于炼化和焦化企业生产用电实行阶梯电价政",
          "year": 2018,
          "char_count": 257,
          "score": 24,
          "match_keywords": [
            "阶梯电价"
          ]
        }
      ]
    },
    {
      "theme_key": "differential_pricing",
      "theme_name_zh": "差别电价",
      "candidate_count": 37,
      "sampled_count": 8,
      "sampled_docs": [
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2021年10月27日 广西壮族自治区发展和改革委员会关于我区高耗能企业执行差别.txt",
          "title": "2021年10月27日 广西壮族自治区发展和改革委员会关于我区高耗能企业执行差别",
          "year": 2021,
          "char_count": 287,
          "score": 25,
          "match_keywords": [
            "差别电价",
            "淘汰类",
            "限制类"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2020年10月 福建省发展和改革委员会关于完善钢铁、水泥和电解铝行业差别（阶梯.txt",
          "title": "2020年10月 福建省发展和改革委员会关于完善钢铁、水泥和电解铝行业差别（阶梯",
          "year": 2020,
          "char_count": 231,
          "score": 15,
          "match_keywords": [
            "差别电价",
            "淘汰类"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2012年6月15日 海南省物价局关于试行居民阶梯电价的通知.txt",
          "title": "2012年6月15日 海南省物价局关于试行居民阶梯电价的通知",
          "year": 2012,
          "char_count": 376,
          "score": 11,
          "match_keywords": [
            "差别电价"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2024年1月8日 湖南省发展改革委员会关于进一步完善居民阶梯电价制度的通知.txt",
          "title": "2024年1月8日 湖南省发展改革委员会关于进一步完善居民阶梯电价制度的通知",
          "year": 2024,
          "char_count": 354,
          "score": 11,
          "match_keywords": [
            "差别电价"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2016年10月11日 广西壮族自治区物价局关于调整居民生活用电阶梯电价政策有关.txt",
          "title": "2016年10月11日 广西壮族自治区物价局关于调整居民生活用电阶梯电价政策有关",
          "year": 2016,
          "char_count": 352,
          "score": 11,
          "match_keywords": [
            "差别电价"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2019年12月19日 黑龙江省关于出台“多人口”居民用电优惠新政的通知.txt",
          "title": "2019年12月19日 黑龙江省关于出台“多人口”居民用电优惠新政的通知",
          "year": 2019,
          "char_count": 265,
          "score": 11,
          "match_keywords": [
            "差别电价"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2018年12月29日 山东省发展改革委关于炼化和焦化企业生产用电实行阶梯电价政.txt",
          "title": "2018年12月29日 山东省发展改革委关于炼化和焦化企业生产用电实行阶梯电价政",
          "year": 2018,
          "char_count": 257,
          "score": 11,
          "match_keywords": [
            "差别电价"
          ]
        },
        {
          "source_path": "01_电价政策/02_阶梯与差别电价/2013年6月17日 青海省发展和改革委员会关于试行居民阶梯电价的通知.txt",
          "title": "2013年6月17日 青海省发展和改革委员会关于试行居民阶梯电价的通知",
          "year": 2013,
          "char_count": 254,
          "score": 11,
          "match_keywords": [
            "差别电价"
          ]
        }
      ]
    },
    {
      "theme_key": "subsidy",
      "theme_name_zh": "补贴补助",
      "candidate_count": 82,
      "sampled_count": 8,
      "sampled_docs": [
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《怀柔区2022年农村地区“减煤换煤”工程实方案》.txt",
          "title": "《怀柔区2022年农村地区“减煤换煤”工程实方案》",
          "year": 2022,
          "char_count": 1520,
          "score": 74,
          "match_keywords": [
            "补助",
            "补贴"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《运城市2022-2023年煤改电煤改气运行补贴办法》.txt",
          "title": "《运城市2022-2023年煤改电煤改气运行补贴办法》",
          "year": 2023,
          "char_count": 303,
          "score": 44,
          "match_keywords": [
            "补贴",
            "运行补贴"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《夏县2023-2024年度冬季清洁取暖“煤改电”“煤改气”运行补贴实施办法》.txt",
          "title": "《夏县2023-2024年度冬季清洁取暖“煤改电”“煤改气”运行补贴实施办法》",
          "year": 2024,
          "char_count": 154,
          "score": 36,
          "match_keywords": [
            "补贴",
            "运行补贴"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《2024-2025年咸阳市采暖季清洁取暖运行.txt",
          "title": "《2024-2025年咸阳市采暖季清洁取暖运行",
          "year": 2025,
          "char_count": 503,
          "score": 34,
          "match_keywords": [
            "补贴",
            "运行补贴"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《滨州市2019年清洁取暖建设推进实施方案》.txt",
          "title": "《滨州市2019年清洁取暖建设推进实施方案》",
          "year": 2019,
          "char_count": 787,
          "score": 22,
          "match_keywords": [
            "奖补",
            "补贴"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《关中地区铁腕治霾专项行动奖补办法》.txt",
          "title": "《关中地区铁腕治霾专项行动奖补办法》",
          "year": null,
          "char_count": 828,
          "score": 56,
          "match_keywords": [
            "奖励",
            "奖补",
            "补助",
            "补贴"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/关于完善新能源汽车推广应用财政补贴政策的通知.txt",
          "title": "关于完善新能源汽车推广应用财政补贴政策的通知",
          "year": null,
          "char_count": 1157,
          "score": 52,
          "match_keywords": [
            "奖励",
            "补贴"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/北京市农村地区清洁取暖设备更新工作指导意见.txt",
          "title": "北京市农村地区清洁取暖设备更新工作指导意见",
          "year": null,
          "char_count": 841,
          "score": 34,
          "match_keywords": [
            "补贴"
          ]
        }
      ]
    },
    {
      "theme_key": "shore_power",
      "theme_name_zh": "岸电",
      "candidate_count": 66,
      "sampled_count": 8,
      "sampled_docs": [
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《关于进一步共同推进船舶靠港使用岸电工作的通知》.txt",
          "title": "《关于进一步共同推进船舶靠港使用岸电工作的通知》",
          "year": null,
          "char_count": 919,
          "score": 148,
          "match_keywords": [
            "岸电",
            "岸电系统",
            "港口",
            "船舶",
            "靠港"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/洋浦港鼓励靠泊船舶使用岸电扶持暂行办法.txt",
          "title": "洋浦港鼓励靠泊船舶使用岸电扶持暂行办法",
          "year": null,
          "char_count": 739,
          "score": 134,
          "match_keywords": [
            "岸电",
            "港口",
            "船舶",
            "靠港"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/交通运输部 国家发展改革委 国家能源局 国家电网有限公司关于进一步推进长江经济带船舶靠港使用岸电的通知.txt",
          "title": "交通运输部 国家发展改革委 国家能源局 国家电网有限公司关于进一步推进长江经济带船舶靠港使用岸电的通知",
          "year": null,
          "char_count": 853,
          "score": 124,
          "match_keywords": [
            "岸电",
            "港口",
            "船舶",
            "靠港"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《关于进一步推进长江经济带船舶靠港使用岸电的通知》.txt",
          "title": "《关于进一步推进长江经济带船舶靠港使用岸电的通知》",
          "year": null,
          "char_count": 686,
          "score": 116,
          "match_keywords": [
            "岸电",
            "港口",
            "船舶",
            "靠港"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《交通运输部办公厅关于加快长江干线推进靠港船舶使用岸电和推广液化天然气船舶应用的指导意见》.txt",
          "title": "《交通运输部办公厅关于加快长江干线推进靠港船舶使用岸电和推广液化天然气船舶应用的指导意见》",
          "year": null,
          "char_count": 359,
          "score": 96,
          "match_keywords": [
            "岸电",
            "港口",
            "船舶",
            "靠港"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《关于示范推进国际航线集装箱船舶和邮轮靠港使用岸电.txt",
          "title": "《关于示范推进国际航线集装箱船舶和邮轮靠港使用岸电",
          "year": null,
          "char_count": 430,
          "score": 86,
          "match_keywords": [
            "岸电",
            "港口",
            "船舶",
            "靠港"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《关于规范我省港口岸电使用价格收费及有关事项的通.txt",
          "title": "《关于规范我省港口岸电使用价格收费及有关事项的通",
          "year": null,
          "char_count": 564,
          "score": 84,
          "match_keywords": [
            "岸电",
            "港口",
            "船舶"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《关于加快推广港口岸电系统意见的通知》.txt",
          "title": "《关于加快推广港口岸电系统意见的通知》",
          "year": null,
          "char_count": 336,
          "score": 84,
          "match_keywords": [
            "岸电",
            "岸电系统",
            "港口",
            "船舶",
            "靠港"
          ]
        }
      ]
    },
    {
      "theme_key": "clean_heating",
      "theme_name_zh": "清洁取暖",
      "candidate_count": 68,
      "sampled_count": 8,
      "sampled_docs": [
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《2024-2025年咸阳市采暖季清洁取暖运行.txt",
          "title": "《2024-2025年咸阳市采暖季清洁取暖运行",
          "year": 2025,
          "char_count": 503,
          "score": 59,
          "match_keywords": [
            "清洁取暖",
            "煤改气",
            "煤改电",
            "采暖季"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《滨州市2019年清洁取暖建设推进实施方案》.txt",
          "title": "《滨州市2019年清洁取暖建设推进实施方案》",
          "year": 2019,
          "char_count": 787,
          "score": 53,
          "match_keywords": [
            "清洁供暖",
            "清洁取暖",
            "煤改气",
            "煤改电",
            "采暖季"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《运城市2022-2023年煤改电煤改气运行补贴办法》.txt",
          "title": "《运城市2022-2023年煤改电煤改气运行补贴办法》",
          "year": 2023,
          "char_count": 303,
          "score": 53,
          "match_keywords": [
            "清洁取暖",
            "煤改气",
            "煤改电",
            "采暖季"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《夏县2023-2024年度冬季清洁取暖“煤改电”“煤改气”运行补贴实施办法》.txt",
          "title": "《夏县2023-2024年度冬季清洁取暖“煤改电”“煤改气”运行补贴实施办法》",
          "year": 2024,
          "char_count": 154,
          "score": 49,
          "match_keywords": [
            "清洁取暖",
            "煤改气",
            "煤改电",
            "采暖季"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《怀柔区2022年农村地区“减煤换煤”工程实方案》.txt",
          "title": "《怀柔区2022年农村地区“减煤换煤”工程实方案》",
          "year": 2022,
          "char_count": 1520,
          "score": 31,
          "match_keywords": [
            "清洁取暖",
            "煤改电",
            "采暖季"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《关于印发北方地区冬季清洁取暖规划（2017-2021年）的通知》.txt",
          "title": "《关于印发北方地区冬季清洁取暖规划（2017-2021年）的通知》",
          "year": 2021,
          "char_count": 372,
          "score": 31,
          "match_keywords": [
            "清洁供暖",
            "清洁取暖",
            "煤改气"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/《忻州市2023年冬季清洁取暖工作实施方案》.txt",
          "title": "《忻州市2023年冬季清洁取暖工作实施方案》",
          "year": 2023,
          "char_count": 392,
          "score": 49,
          "match_keywords": [
            "清洁取暖",
            "煤改气",
            "煤改电",
            "采暖季"
          ]
        },
        {
          "source_path": "02_电能替代与清洁取暖/01_政策文本/关于印发河津市2024年冬季清洁取暖工作实施方案的通知.txt",
          "title": "关于印发河津市2024年冬季清洁取暖工作实施方案的通知",
          "year": 2024,
          "char_count": 408,
          "score": 41,
          "match_keywords": [
            "清洁取暖",
            "煤改电"
          ]
        }
      ]
    }
  ],
  "annotation_pool_union": {
    "doc_count": 38,
    "docs": [
      {
        "source_path": "01_电价政策/02_阶梯与差别电价/2012年6月15日 海南省物价局关于试行居民阶梯电价的通知.txt",
        "title": "2012年6月15日 海南省物价局关于试行居民阶梯电价的通知",
        "year": 2012,
        "char_count": 376,
        "themes": [
          "differential_pricing",
          "tiered_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/02_阶梯与差别电价/2013年6月17日 青海省发展和改革委员会关于试行居民阶梯电价的通知.txt",
        "title": "2013年6月17日 青海省发展和改革委员会关于试行居民阶梯电价的通知",
        "year": 2013,
        "char_count": 254,
        "themes": [
          "differential_pricing",
          "tiered_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/02_阶梯与差别电价/2016年10月11日 广西壮族自治区物价局关于调整居民生活用电阶梯电价政策有关.txt",
        "title": "2016年10月11日 广西壮族自治区物价局关于调整居民生活用电阶梯电价政策有关",
        "year": 2016,
        "char_count": 352,
        "themes": [
          "differential_pricing",
          "tiered_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/02_阶梯与差别电价/2018年12月29日 山东省发展改革委关于炼化和焦化企业生产用电实行阶梯电价政.txt",
        "title": "2018年12月29日 山东省发展改革委关于炼化和焦化企业生产用电实行阶梯电价政",
        "year": 2018,
        "char_count": 257,
        "themes": [
          "differential_pricing",
          "tiered_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/02_阶梯与差别电价/2019年12月19日 黑龙江省关于出台“多人口”居民用电优惠新政的通知.txt",
        "title": "2019年12月19日 黑龙江省关于出台“多人口”居民用电优惠新政的通知",
        "year": 2019,
        "char_count": 265,
        "themes": [
          "differential_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/02_阶梯与差别电价/2019年7月9日 山东省发展和改革委员会关于居民阶梯电价制度有关事项的通知.txt",
        "title": "2019年7月9日 山东省发展和改革委员会关于居民阶梯电价制度有关事项的通知",
        "year": 2019,
        "char_count": 241,
        "themes": [
          "tiered_pricing"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《滨州市2019年清洁取暖建设推进实施方案》.txt",
        "title": "《滨州市2019年清洁取暖建设推进实施方案》",
        "year": 2019,
        "char_count": 787,
        "themes": [
          "clean_heating",
          "subsidy"
        ]
      },
      {
        "source_path": "01_电价政策/02_阶梯与差别电价/2020年10月 福建省发展和改革委员会关于完善钢铁、水泥和电解铝行业差别（阶梯.txt",
        "title": "2020年10月 福建省发展和改革委员会关于完善钢铁、水泥和电解铝行业差别（阶梯",
        "year": 2020,
        "char_count": 231,
        "themes": [
          "differential_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/01_分时电价/2021年11月23日 广西壮族自治区发展和改革委员会关于完善我区峰谷分时电价机.txt",
        "title": "2021年11月23日 广西壮族自治区发展和改革委员会关于完善我区峰谷分时电价机",
        "year": 2021,
        "char_count": 337,
        "themes": [
          "tou_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/01_分时电价/2021年12月14日 山西省发展和改革委员会关于完善分时电价机制有关事项的通知.txt",
        "title": "2021年12月14日 山西省发展和改革委员会关于完善分时电价机制有关事项的通知",
        "year": 2021,
        "char_count": 341,
        "themes": [
          "tou_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/01_分时电价/2021年12月24日 天津市发展改革委关于峰谷分时电价政策有关事项的通知.txt",
        "title": "2021年12月24日 天津市发展改革委关于峰谷分时电价政策有关事项的通知",
        "year": 2021,
        "char_count": 331,
        "themes": [
          "tou_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/02_阶梯与差别电价/2021年10月27日 广西壮族自治区发展和改革委员会关于我区高耗能企业执行差别.txt",
        "title": "2021年10月27日 广西壮族自治区发展和改革委员会关于我区高耗能企业执行差别",
        "year": 2021,
        "char_count": 287,
        "themes": [
          "differential_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/02_阶梯与差别电价/2021年4月29日 广东省发展改革委关于居民阶梯电价“一户多人口”政策有关事项.txt",
        "title": "2021年4月29日 广东省发展改革委关于居民阶梯电价“一户多人口”政策有关事项",
        "year": 2021,
        "char_count": 258,
        "themes": [
          "tiered_pricing"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《关于印发北方地区冬季清洁取暖规划（2017-2021年）的通知》.txt",
        "title": "《关于印发北方地区冬季清洁取暖规划（2017-2021年）的通知》",
        "year": 2021,
        "char_count": 372,
        "themes": [
          "clean_heating"
        ]
      },
      {
        "source_path": "01_电价政策/01_分时电价/2022年12月6日 河北发改委印发《关于明确居民峰谷分时电价政策的通知》.txt",
        "title": "2022年12月6日 河北发改委印发《关于明确居民峰谷分时电价政策的通知》",
        "year": 2022,
        "char_count": 465,
        "themes": [
          "tou_pricing"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《怀柔区2022年农村地区“减煤换煤”工程实方案》.txt",
        "title": "《怀柔区2022年农村地区“减煤换煤”工程实方案》",
        "year": 2022,
        "char_count": 1520,
        "themes": [
          "clean_heating",
          "subsidy"
        ]
      },
      {
        "source_path": "01_电价政策/01_分时电价/2023年7月31日 广西壮族自治区发展和改革委员会关于优化峰谷分时电价机制的通.txt",
        "title": "2023年7月31日 广西壮族自治区发展和改革委员会关于优化峰谷分时电价机制的通",
        "year": 2023,
        "char_count": 295,
        "themes": [
          "tou_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/02_阶梯与差别电价/2023年12月27日 安徽省发展改革委关于居民阶梯电价“一户多人口”政策有关事.txt",
        "title": "2023年12月27日 安徽省发展改革委关于居民阶梯电价“一户多人口”政策有关事",
        "year": 2023,
        "char_count": 220,
        "themes": [
          "tiered_pricing"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《忻州市2023年冬季清洁取暖工作实施方案》.txt",
        "title": "《忻州市2023年冬季清洁取暖工作实施方案》",
        "year": 2023,
        "char_count": 392,
        "themes": [
          "clean_heating"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《运城市2022-2023年煤改电煤改气运行补贴办法》.txt",
        "title": "《运城市2022-2023年煤改电煤改气运行补贴办法》",
        "year": 2023,
        "char_count": 303,
        "themes": [
          "clean_heating",
          "subsidy"
        ]
      },
      {
        "source_path": "01_电价政策/01_分时电价/2024年7月29日 黑龙江省发展和改革委员会关于进一步完善峰谷分时电价政策措施.txt",
        "title": "2024年7月29日 黑龙江省发展和改革委员会关于进一步完善峰谷分时电价政策措施",
        "year": 2024,
        "char_count": 343,
        "themes": [
          "tou_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/01_分时电价/2024年7月5日 甘肃省发展和改革委员会关于优化调整工商业等用户峰谷分时电价政.txt",
        "title": "2024年7月5日 甘肃省发展和改革委员会关于优化调整工商业等用户峰谷分时电价政",
        "year": 2024,
        "char_count": 400,
        "themes": [
          "tou_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/01_分时电价/2024年8月27日 海南省发展和改革委员会关于调整电动汽车峰谷分时电价政策有关.txt",
        "title": "2024年8月27日 海南省发展和改革委员会关于调整电动汽车峰谷分时电价政策有关",
        "year": 2024,
        "char_count": 357,
        "themes": [
          "tou_pricing"
        ]
      },
      {
        "source_path": "01_电价政策/02_阶梯与差别电价/2024年1月8日 湖南省发展改革委员会关于进一步完善居民阶梯电价制度的通知.txt",
        "title": "2024年1月8日 湖南省发展改革委员会关于进一步完善居民阶梯电价制度的通知",
        "year": 2024,
        "char_count": 354,
        "themes": [
          "differential_pricing",
          "tiered_pricing"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《夏县2023-2024年度冬季清洁取暖“煤改电”“煤改气”运行补贴实施办法》.txt",
        "title": "《夏县2023-2024年度冬季清洁取暖“煤改电”“煤改气”运行补贴实施办法》",
        "year": 2024,
        "char_count": 154,
        "themes": [
          "clean_heating",
          "subsidy"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/关于印发河津市2024年冬季清洁取暖工作实施方案的通知.txt",
        "title": "关于印发河津市2024年冬季清洁取暖工作实施方案的通知",
        "year": 2024,
        "char_count": 408,
        "themes": [
          "clean_heating"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《2024-2025年咸阳市采暖季清洁取暖运行.txt",
        "title": "《2024-2025年咸阳市采暖季清洁取暖运行",
        "year": 2025,
        "char_count": 503,
        "themes": [
          "clean_heating",
          "subsidy"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《交通运输部办公厅关于加快长江干线推进靠港船舶使用岸电和推广液化天然气船舶应用的指导意见》.txt",
        "title": "《交通运输部办公厅关于加快长江干线推进靠港船舶使用岸电和推广液化天然气船舶应用的指导意见》",
        "year": null,
        "char_count": 359,
        "themes": [
          "shore_power"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《关中地区铁腕治霾专项行动奖补办法》.txt",
        "title": "《关中地区铁腕治霾专项行动奖补办法》",
        "year": null,
        "char_count": 828,
        "themes": [
          "subsidy"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《关于加快推广港口岸电系统意见的通知》.txt",
        "title": "《关于加快推广港口岸电系统意见的通知》",
        "year": null,
        "char_count": 336,
        "themes": [
          "shore_power"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《关于示范推进国际航线集装箱船舶和邮轮靠港使用岸电.txt",
        "title": "《关于示范推进国际航线集装箱船舶和邮轮靠港使用岸电",
        "year": null,
        "char_count": 430,
        "themes": [
          "shore_power"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《关于规范我省港口岸电使用价格收费及有关事项的通.txt",
        "title": "《关于规范我省港口岸电使用价格收费及有关事项的通",
        "year": null,
        "char_count": 564,
        "themes": [
          "shore_power"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《关于进一步共同推进船舶靠港使用岸电工作的通知》.txt",
        "title": "《关于进一步共同推进船舶靠港使用岸电工作的通知》",
        "year": null,
        "char_count": 919,
        "themes": [
          "shore_power"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/《关于进一步推进长江经济带船舶靠港使用岸电的通知》.txt",
        "title": "《关于进一步推进长江经济带船舶靠港使用岸电的通知》",
        "year": null,
        "char_count": 686,
        "themes": [
          "shore_power"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/交通运输部 国家发展改革委 国家能源局 国家电网有限公司关于进一步推进长江经济带船舶靠港使用岸电的通知.txt",
        "title": "交通运输部 国家发展改革委 国家能源局 国家电网有限公司关于进一步推进长江经济带船舶靠港使用岸电的通知",
        "year": null,
        "char_count": 853,
        "themes": [
          "shore_power"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/关于完善新能源汽车推广应用财政补贴政策的通知.txt",
        "title": "关于完善新能源汽车推广应用财政补贴政策的通知",
        "year": null,
        "char_count": 1157,
        "themes": [
          "subsidy"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/北京市农村地区清洁取暖设备更新工作指导意见.txt",
        "title": "北京市农村地区清洁取暖设备更新工作指导意见",
        "year": null,
        "char_count": 841,
        "themes": [
          "subsidy"
        ]
      },
      {
        "source_path": "02_电能替代与清洁取暖/01_政策文本/洋浦港鼓励靠泊船舶使用岸电扶持暂行办法.txt",
        "title": "洋浦港鼓励靠泊船舶使用岸电扶持暂行办法",
        "year": null,
        "char_count": 739,
        "themes": [
          "shore_power"
        ]
      }
    ]
  },
  "all_doc_theme_match_count": 147
}
```

## Step3：预处理、切分与审计链
### 创新方法
- 构建 raw/clean 双向 offset 映射（含 roundtrip 校验），确保任何抽取结果可回指原文证据位置。
- 对汇总拼接文本先按 `<h2>file:` 切成政策单元，再做条款切分，避免跨文档污染。
- 条款切分采用“编号规则 + 语义标点 + 超长再切 + 表格兜底”多级策略，提高结构化稳定性。

### 全指标
#### Step3 预处理 QC 指标
来源：`00_整理记录/step3_qc_report.json`

```json
{
  "generated_at": "2026-02-09 19:06:28",
  "preprocess_version": "step3_preprocess_v1.0",
  "git_commit": "5c7c40a6b036ddb63edece4e1f97bc539a5c41d8",
  "pipeline_params_hash": "cd182077a4ddf8c8941b9edfe2f484adead9ae497bcddf77b927566f669616b0",
  "source_file_count": 151,
  "unit_document_count": 317,
  "compiled_source_file_count": 4,
  "compiled_chunk_count": 170,
  "encoding_used_count": {
    "utf-8": 151,
    "gb18030": 0
  },
  "raw_char_total": 128968,
  "clean_char_total": 127771,
  "preprocess_change_counts": {
    "removed_bom_count": 0,
    "collapsed_crlf_count": 1197,
    "converted_cr_count": 0,
    "removed_control_count": 0
  },
  "offset_mapping_qc": {
    "docs_with_mismatch": 0,
    "mismatch_char_total": 0,
    "mismatch_ratio": 0.0
  },
  "clause_qc": {
    "clause_total": 2022,
    "docs_without_clause": 0,
    "docs_with_table_clause": 130,
    "avg_clause_per_doc": 6.3785,
    "length_summary": {
      "count": 2022,
      "min": 20,
      "max": 400,
      "avg": 71.44,
      "p90": 134
    },
    "clause_type_distribution": {
      "time_rule": 527,
      "pricing_rule": 207,
      "scope_rule": 77,
      "other": 527,
      "execution_rule": 113,
      "subsidy_rule": 361,
      "task_assessment": 80,
      "table_row_clause": 130
    },
    "clause_span_invalid_count": 0,
    "clause_non_empty_rate": 1.0
  },
  "quality_gates": {
    "all_doc_have_ids": true,
    "all_clause_span_valid": true,
    "no_offset_mismatch": true,
    "clause_non_empty_rate_ge_99": true,
    "clause_max_len_le_400": true,
    "overall_pass": true
  },
  "artifacts": {
    "manifest": "00_整理记录/step3_input_manifest.json",
    "document_corpus": "00_整理记录/step3_document_corpus.jsonl",
    "clause_corpus": "00_整理记录/step3_clause_corpus.jsonl",
    "offset_map": "00_整理记录/step3_offset_map.jsonl"
  }
}
```

## Step4：UIE 抽取与入图可用性优化
### 创新方法
- 两阶段 UIE（doc + clause）与规则后填充耦合，不只追求命中率，而是面向“可入图”优化。
- 引入机制证据双通道（span/规则证据）与参数绑定字段（`param_bind_mechanism`、`bind_reason`），降低孤立参数。
- 用可导入性评分（structure/evidence/doc/clause）驱动迭代，形成可复现实验闭环。

### 全指标
#### Step4 迭代评分总表
来源：`00_整理记录/step4_iteration_scores.json`

```json
[
  {
    "iteration": "iter0_baseline",
    "total_score": 39.482,
    "structure_score": 20.0,
    "evidence_score": 10.0,
    "doc_score": 8.418,
    "clause_score": 1.064,
    "mechanism_non_empty_rate": 0.0,
    "clause_type_non_empty_rate": 0.0,
    "raw_non_empty_rate": 0.043521,
    "strict_triplet_ready_rate": 0.0,
    "param_bind_rate": 0.0,
    "task_ready_rate": 0.1182,
    "doc_min_ready_rate": 0.73817,
    "doc_rich_ready_rate": 0.148265,
    "is_good": false
  },
  {
    "iteration": "iter1_v1",
    "total_score": 56.896,
    "structure_score": 20.0,
    "evidence_score": 10.0,
    "doc_score": 10.959,
    "clause_score": 15.937,
    "mechanism_non_empty_rate": 0.650346,
    "clause_type_non_empty_rate": 1.0,
    "raw_non_empty_rate": 0.043521,
    "strict_triplet_ready_rate": 0.001484,
    "param_bind_rate": 0.5,
    "task_ready_rate": 0.1182,
    "doc_min_ready_rate": 0.842271,
    "doc_rich_ready_rate": 0.470032,
    "is_good": false
  },
  {
    "iteration": "iter2_v2",
    "total_score": 72.817,
    "structure_score": 20.0,
    "evidence_score": 20.0,
    "doc_score": 10.959,
    "clause_score": 21.858,
    "mechanism_non_empty_rate": 0.650346,
    "clause_type_non_empty_rate": 1.0,
    "raw_non_empty_rate": 0.290307,
    "strict_triplet_ready_rate": 0.200297,
    "param_bind_rate": 0.698467,
    "task_ready_rate": 0.279426,
    "doc_min_ready_rate": 0.842271,
    "doc_rich_ready_rate": 0.470032,
    "is_good": false
  },
  {
    "iteration": "iter3_v2plus",
    "total_score": 76.332,
    "structure_score": 20.0,
    "evidence_score": 20.0,
    "doc_score": 10.959,
    "clause_score": 25.373,
    "mechanism_non_empty_rate": 0.781405,
    "clause_type_non_empty_rate": 1.0,
    "raw_non_empty_rate": 0.290307,
    "strict_triplet_ready_rate": 0.251731,
    "param_bind_rate": 0.88075,
    "task_ready_rate": 0.279426,
    "doc_min_ready_rate": 0.842271,
    "doc_rich_ready_rate": 0.470032,
    "is_good": true
  }
]
```

#### Step4 最终轮（iter3_v2plus）指标
来源：`00_整理记录/step4_iter3_v2plus_kb_score.json`

```json
{
  "metrics": {
    "doc_total": 317,
    "clause_total": 2022,
    "parse_ok_rate": 1.0,
    "schema_key_complete_rate": 1.0,
    "raw_value_span_valid_rate": 1.0,
    "mechanism_evidence_rate": 1.0,
    "doc_min_ready_rate": 0.842271,
    "doc_rich_ready_rate": 0.470032,
    "mechanism_non_empty_rate": 0.781405,
    "clause_type_non_empty_rate": 1.0,
    "raw_non_empty_rate": 0.290307,
    "raw_numeric_rate_among_raw": 0.972743,
    "task_ready_rate": 0.279426,
    "param_bind_rate": 0.88075,
    "strict_triplet_ready_rate": 0.251731,
    "counts": {
      "mechanism_non_empty": 1580,
      "clause_type_non_empty": 2022,
      "raw_non_empty": 587,
      "raw_numeric_clause": 571,
      "task_ready": 565,
      "param_bind_true": 517,
      "param_bind_total_raw_clause": 587,
      "strict_triplet_ready": 509,
      "raw_item_total": 1180,
      "raw_item_span_ok": 1180,
      "mechanism_item_total": 1580,
      "mechanism_item_evidence_ok": 1580
    }
  },
  "scores": {
    "structure_score": 20.0,
    "evidence_score": 20.0,
    "doc_score": 10.959,
    "clause_score": 25.373,
    "total_score": 76.332
  },
  "good_threshold": 75.0,
  "is_good": true
}
```

## Step5：归一化、重绑定与严格门禁
### 创新方法
- 固化三套分母（`all_clause`、`valid_all`、`valid_numeric`），规避跨轮对比时分母漂移。
- 机制绑定采用 clause 候选打分 + mention 级重绑定两阶段，配合负域守卫减少错绑。
- 严格区分 `strict_all` 与 `strict_high` 两轨，兼顾召回池与高置信入图主集。

### 全指标
#### Step5 最终轮（rebind14_fixabcd_plus2）验证指标
来源：`00_整理记录/step5_seq_step2_v2_rebind14_fixabcd_plus2_validation_report.json`

```json
{
  "input": {
    "clause_pred_file": "00_整理记录/step4_seq_step2_clause_predictions.jsonl",
    "clause_source_file": "00_整理记录/step3_clause_corpus.jsonl",
    "clause_total": 2022,
    "known_mechanisms": [
      "tou_pricing",
      "tiered_pricing",
      "differential_penalty_pricing",
      "general_price_adjustment",
      "subsidy",
      "task_assessment",
      "technology_route"
    ],
    "strict_high_threshold": 0.6,
    "bind_min_score": 1.0
  },
  "frozen_denominators": {
    "all_clause": 2022,
    "valid_all": 1141,
    "valid_numeric": 1079,
    "mention_total": 1141
  },
  "counts": {
    "mention_total": 1141,
    "definition_total": 339,
    "triple_total": 3176,
    "parse_error_count": 0,
    "span_valid_count": 1141,
    "normalization_attempted_count": 1141,
    "normalization_matched_count": 1079,
    "canonical_key_count": 1079,
    "mechanism_bound_count": 1140,
    "ready_with_mechanism_count": 1079,
    "strict_all_count": 1079,
    "strict_high_count": 916,
    "mechanism_bound_valid_all_count": 1140,
    "mechanism_bound_valid_numeric_count": 1079,
    "local_supported_count": 966,
    "pricing_negative_conflict_count": 0,
    "unit_conflict_group_count": 11,
    "clause_candidate_non_empty_count": 1701,
    "clause_negative_count": 56,
    "raw_value_filtered_non_value_count": 69,
    "raw_value_filtered_by_rule_count": 147,
    "unit_pairing_dropped_count": 98,
    "unit_alias_applied_count": 0,
    "full_clause_retry_success_count": 0,
    "post_guard_adjusted_count": 5,
    "low_confidence_cap_count": 23,
    "time_window_tou_override_count": 0,
    "strict_high_compat_block_count": 11,
    "strict_high_weak_constraint_block_count": 5
  },
  "rates": {
    "span_valid_rate": 1.0,
    "normalization_matched_rate": 0.945662,
    "canonical_key_rate": 0.945662,
    "mechanism_bound_rate": 0.999124,
    "ready_with_mechanism_rate": 0.945662,
    "mechanism_bound_rate_valid_all": 0.999124,
    "mechanism_bound_rate_valid_numeric": 1.0,
    "strict_all_rate_valid_numeric": 1.0,
    "strict_high_rate_valid_numeric": 0.848934,
    "local_supported_rate_valid_numeric": 0.895273,
    "pricing_negative_conflict_rate_valid_numeric": 0.0,
    "clause_candidate_non_empty_rate": 0.841246,
    "clause_negative_rate": 0.027695
  },
  "metrics_with_denominator": {
    "normalization_matched_on_mentions": {
      "num": 1079,
      "den": 1141,
      "rate": 0.945662
    },
    "mechanism_bound_on_valid_all": {
      "num": 1140,
      "den": 1141,
      "rate": 0.999124
    },
    "mechanism_bound_on_valid_numeric": {
      "num": 1079,
      "den": 1079,
      "rate": 1.0
    },
    "strict_all_on_valid_numeric": {
      "num": 1079,
      "den": 1079,
      "rate": 1.0
    },
    "strict_high_on_valid_numeric": {
      "num": 916,
      "den": 1079,
      "rate": 0.848934
    }
  },
  "targets": {
    "normalization_matched_rate": 0.9,
    "mechanism_bound_rate_valid_numeric": 0.85,
    "strict_high_rate_valid_numeric": 0.65,
    "local_supported_rate_valid_numeric": 0.85
  },
  "target_pass": {
    "normalization_matched_rate": true,
    "mechanism_bound_rate_valid_numeric": true,
    "strict_high_rate_valid_numeric": true,
    "local_supported_rate_valid_numeric": true
  },
  "all_targets_passed": true,
  "distribution": {
    "param_type_top20": {
      "ratio_target": 275,
      "subsidy_amount": 246,
      "time_window": 128,
      "price_delta_pct": 127,
      "consumption_threshold_kwh": 122,
      "price_value": 94,
      "target_household_count": 27,
      "area_subsidy_amount": 24,
      "duration_threshold_hour": 14,
      "funding_share_ratio": 9,
      "duration_threshold_month": 5,
      "other": 4,
      "duration_threshold_year": 2,
      "tonnage_threshold": 2
    },
    "norm_unit_top20": {
      "percent": 397,
      "yuan": 191,
      "kwh": 122,
      "time_window": 118,
      "ten_thousand_yuan": 92,
      "yuan_per_kwh": 51,
      "household": 27,
      "yuan_per_sqm": 24,
      "hour": 14,
      "none": 14,
      "time_point": 10,
      "month": 5,
      "kw": 4,
      "yuan_per_ton": 3,
      "yuan_per_watt": 3,
      "year": 2,
      "ton": 2
    },
    "rule_top20": {
      "percent_numeric": 397,
      "yuan_generic": 188,
      "time_window": 118,
      "kwh_threshold": 111,
      "ten_thousand_yuan_generic": 65,
      "no_match": 62,
      "yuan_per_kwh": 32,
      "household_count": 27,
      "ten_thousand_yuan_per_village": 27,
      "yuan_per_sqm": 24,
      "yuan_per_degree_to_yuan_per_kwh": 17,
      "duration_hour": 14,
      "ratio_sequence": 14,
      "kwh_threshold_range": 11,
      "time_point": 10,
      "duration_month_context": 7,
      "capacity_value": 4,
      "yuan_per_ton": 3,
      "yuan_per_watt": 3,
      "price_value_retyped_to_subsidy_amount_context": 3
    },
    "filtered_rule_counts": {},
    "bind_reason_top20": {
      "keyword_plus_prior": 674,
      "keyword_hit": 194,
      "param_type_map": 147,
      "candidate_score": 91,
      "step4_inherit": 22,
      "step4_fallback": 12,
      "no_candidate": 1
    },
    "bind_transition_top20": {
      "subsidy->subsidy": 364,
      "tou_pricing->tou_pricing": 247,
      "tiered_pricing->tiered_pricing": 148,
      "tou_pricing->task_assessment": 102,
      "task_assessment->technology_route": 48,
      "technology_route->tou_pricing": 42,
      "tou_pricing->subsidy": 29,
      "technology_route->technology_route": 27,
      "general_price_adjustment->general_price_adjustment": 26,
      "task_assessment->task_assessment": 21,
      "tou_pricing->general_price_adjustment": 16,
      "general_price_adjustment->tiered_pricing": 12,
      "subsidy->tiered_pricing": 11,
      "tou_pricing->tiered_pricing": 10,
      "None->task_assessment": 10,
      "subsidy->technology_route": 10,
      "general_price_adjustment->tou_pricing": 7,
      "task_assessment->tou_pricing": 3,
      "task_assessment->subsidy": 2,
      "general_price_adjustment->subsidy": 1
    },
    "skip_reason_top20": {
      "time_meta_filtered": 117,
      "label_only_filtered": 17,
      "pollutant_unit_filtered": 13
    },
    "post_guard_top20": {
      "price_value_retyped_to_subsidy_amount": 3,
      "subsidy_amount_retyped_to_price_value": 2
    }
  },
  "unit_conflicts_top20": [
    {
      "doc_instance_id": "10695560c26cc67b7a3e26b8dbcd7b856b0b17ef49c31ba529efd3caf059a1de",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "17b169c01d0fd11691f3014066bc982e9d5aae3ef301b3d897d2a4b986dac45b",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "3c1392fd897f1d095efaa1ae2a1eaa5c0c3df313cd5a9a185aacffe05575b886",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "41eed2fc03a95dc30af898124e00962d37f00dd998abb5da87c6e10e209db169",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "6618b31ad2d2553801e75f1d42256338782cda332eb141a7fea6466fee1dccfd",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "6ca5d9d44b93a3440cc8f24b4feda441563e6841021017b2c5db628a6976c9f5",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "a63aaa1b99aae78cd58b5beb8c271e538c4b10b43ff4aff7312d6e081dd79eed",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "c32ed07b1f8848d45dcf196616c7064ebdf5a10f0ce328b277c662ee5197f29b",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan_per_ton"
      ]
    },
    {
      "doc_instance_id": "cd86e3487ec66701c2d41c1399f9a453338981c169b847ab9321c78351d62988",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "yuan",
        "yuan_per_watt"
      ]
    },
    {
      "doc_instance_id": "f6f8d5f9847c1fe31624cb64353d12b61bebca40113c37e445b63a2d226db18d",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "yuan",
        "yuan_per_watt"
      ]
    }
  ]
}
```

## Step6：多人双盲 Gold/IAA 评测
### 创新方法
- 多标注者双盲两轮（Pass-A/Pass-B）+ 仲裁流程，显式约束分歧处理规则。
- 分层抽样覆盖机制类型、参数类型、hard case 与 strict 高风险样本，避免评测盲区。
- 将高危错误簇（时间窗误判、价格数量级错误等）纳入门禁，而非只看均值指标。

### 全指标
#### Step6 最终轮（iter4_fixabcd_plus）IAA 与精度指标
来源：`00_整理记录/step6_iter4_fixabcd_plus_iaa_report.json`

```json
{
  "config": {
    "mentions": "00_整理记录/step5_seq_step2_v2_rebind13_fixabcd_plus_parameter_mentions.jsonl",
    "clause_corpus": "00_整理记录/step3_clause_corpus.jsonl",
    "sample_size": 300,
    "strict_min": 140,
    "hard_min": 80,
    "seed": 20260211
  },
  "sampling": {
    "target_total": 300,
    "actual_total": 300,
    "strict_high_count": 214,
    "hard_case_count": 157,
    "mechanism_distribution": {
      "tou_pricing": 55,
      "subsidy": 48,
      "task_assessment": 73,
      "tiered_pricing": 42,
      "technology_route": 46,
      "general_price_adjustment": 34,
      "differential_penalty_pricing": 1,
      "None": 1
    },
    "param_type_distribution": {
      "price_delta_pct": 40,
      "subsidy_amount": 19,
      "time_window": 28,
      "ratio_target": 101,
      "price_value": 25,
      "area_subsidy_amount": 5,
      "target_household_count": 15,
      "None": 22,
      "consumption_threshold_kwh": 28,
      "tonnage_threshold": 2,
      "funding_share_ratio": 3,
      "duration_threshold_hour": 5,
      "other": 3,
      "duration_threshold_month": 2,
      "duration_threshold_year": 2
    },
    "bind_group_distribution": {
      "high_conf": 243,
      "fallback": 23,
      "candidate_score": 33,
      "other": 1
    },
    "hard_tag_distribution": {
      "time_token": 28,
      "negative_domain": 43,
      "task_clause": 44,
      "candidate_score": 33,
      "threshold_price_same_clause": 24
    }
  },
  "iaa": {
    "kappa_mechanism": 0.987997,
    "kappa_param_type": 1.0,
    "exact_match_norm_unit": 1.0,
    "agreement_strict_high_eligible": 1.0
  },
  "quality": {
    "denominators": {
      "all_clause": 2022,
      "sample_total": 300,
      "valid_all": 300,
      "valid_numeric": 278
    },
    "mechanism_precision_on_valid_numeric": {
      "num": 261,
      "den": 274,
      "rate": 0.952555
    },
    "normalization_precision_on_valid_numeric": {
      "num": 277,
      "den": 278,
      "rate": 0.996403
    },
    "strict_high_precision": {
      "num": 213,
      "den": 214,
      "rate": 0.995327
    }
  },
  "error_clusters": {
    "time_raw_not_time_window": 0,
    "price_value_large_raw_small_norm": 0,
    "candidate_score_strict_high": 0
  },
  "target_pass": {
    "kappa_mechanism_ge_0_80": true,
    "kappa_param_type_ge_0_80": true,
    "exact_match_norm_unit_ge_0_90": true,
    "agreement_strict_high_eligible_ge_0_90": true,
    "mechanism_precision_ge_0_90": true,
    "normalization_precision_ge_0_90": true,
    "strict_high_precision_ge_0_92": true,
    "time_raw_not_time_window_eq_0": true,
    "price_value_large_raw_small_norm_eq_0": true,
    "candidate_score_strict_high_eq_0": true,
    "sample_size_ge_240": true,
    "sample_strict_ge_120": true,
    "sample_hard_ge_60": true
  },
  "all_targets_passed": true
}
```

## Step7：小样本增量优化与联合门禁复测
### 创新方法
- 在不改 Step4 主模型的前提下，做单位错配局部修复与时间参数语义对齐，提升稳定性。
- Step5 归一化指标与 Step6 Gold/IAA 指标联合门禁，确保“提召回不降精度”。
- 固化 gate 报告，统一放行判断，避免人工口径偏差。

### 全指标
#### Step7 Step5侧验证指标
来源：`00_整理记录/step7_iter3_unitfix_timeunit_thr060_validation_report.json`

```json
{
  "input": {
    "clause_pred_file": "00_整理记录/step4_seq_step2_clause_predictions.jsonl",
    "clause_source_file": "00_整理记录/step3_clause_corpus.jsonl",
    "clause_total": 2022,
    "known_mechanisms": [
      "tou_pricing",
      "tiered_pricing",
      "differential_penalty_pricing",
      "general_price_adjustment",
      "subsidy",
      "task_assessment",
      "technology_route"
    ],
    "strict_high_threshold": 0.6,
    "bind_min_score": 1.0
  },
  "frozen_denominators": {
    "all_clause": 2022,
    "valid_all": 1141,
    "valid_numeric": 1119,
    "mention_total": 1141
  },
  "counts": {
    "mention_total": 1141,
    "definition_total": 354,
    "triple_total": 3296,
    "parse_error_count": 0,
    "span_valid_count": 1141,
    "normalization_attempted_count": 1141,
    "normalization_matched_count": 1119,
    "canonical_key_count": 1119,
    "mechanism_bound_count": 1140,
    "ready_with_mechanism_count": 1119,
    "strict_all_count": 1119,
    "strict_high_count": 952,
    "mechanism_bound_valid_all_count": 1140,
    "mechanism_bound_valid_numeric_count": 1119,
    "local_supported_count": 1006,
    "pricing_negative_conflict_count": 0,
    "unit_conflict_group_count": 11,
    "clause_candidate_non_empty_count": 1701,
    "clause_negative_count": 56,
    "raw_value_filtered_non_value_count": 69,
    "raw_value_filtered_by_rule_count": 147,
    "unit_pairing_dropped_count": 98,
    "unit_alias_applied_count": 0,
    "full_clause_retry_success_count": 0,
    "post_guard_adjusted_count": 7,
    "low_confidence_cap_count": 21,
    "time_window_tou_override_count": 0,
    "strict_high_compat_block_count": 14,
    "strict_high_weak_constraint_block_count": 5
  },
  "rates": {
    "span_valid_rate": 1.0,
    "normalization_matched_rate": 0.980719,
    "canonical_key_rate": 0.980719,
    "mechanism_bound_rate": 0.999124,
    "ready_with_mechanism_rate": 0.980719,
    "mechanism_bound_rate_valid_all": 0.999124,
    "mechanism_bound_rate_valid_numeric": 1.0,
    "strict_all_rate_valid_numeric": 1.0,
    "strict_high_rate_valid_numeric": 0.85076,
    "local_supported_rate_valid_numeric": 0.899017,
    "pricing_negative_conflict_rate_valid_numeric": 0.0,
    "clause_candidate_non_empty_rate": 0.841246,
    "clause_negative_rate": 0.027695
  },
  "metrics_with_denominator": {
    "normalization_matched_on_mentions": {
      "num": 1119,
      "den": 1141,
      "rate": 0.980719
    },
    "mechanism_bound_on_valid_all": {
      "num": 1140,
      "den": 1141,
      "rate": 0.999124
    },
    "mechanism_bound_on_valid_numeric": {
      "num": 1119,
      "den": 1119,
      "rate": 1.0
    },
    "strict_all_on_valid_numeric": {
      "num": 1119,
      "den": 1119,
      "rate": 1.0
    },
    "strict_high_on_valid_numeric": {
      "num": 952,
      "den": 1119,
      "rate": 0.85076
    }
  },
  "targets": {
    "normalization_matched_rate": 0.9,
    "mechanism_bound_rate_valid_numeric": 0.85,
    "strict_high_rate_valid_numeric": 0.65,
    "local_supported_rate_valid_numeric": 0.85
  },
  "target_pass": {
    "normalization_matched_rate": true,
    "mechanism_bound_rate_valid_numeric": true,
    "strict_high_rate_valid_numeric": true,
    "local_supported_rate_valid_numeric": true
  },
  "all_targets_passed": true,
  "distribution": {
    "param_type_top20": {
      "ratio_target": 275,
      "subsidy_amount": 247,
      "consumption_threshold_kwh": 134,
      "time_window": 128,
      "price_delta_pct": 127,
      "price_value": 119,
      "target_household_count": 29,
      "area_subsidy_amount": 24,
      "duration_threshold_hour": 14,
      "funding_share_ratio": 9,
      "duration_threshold_month": 5,
      "other": 4,
      "duration_threshold_year": 2,
      "tonnage_threshold": 2
    },
    "norm_unit_top20": {
      "percent": 397,
      "yuan": 195,
      "kwh": 134,
      "time_window": 128,
      "ten_thousand_yuan": 92,
      "yuan_per_kwh": 73,
      "household": 29,
      "yuan_per_sqm": 24,
      "hour": 14,
      "none": 14,
      "month": 5,
      "kw": 4,
      "yuan_per_ton": 3,
      "yuan_per_watt": 3,
      "year": 2,
      "ton": 2
    },
    "rule_top20": {
      "percent_numeric": 397,
      "yuan_generic": 192,
      "kwh_threshold": 121,
      "time_window": 118,
      "ten_thousand_yuan_generic": 65,
      "yuan_per_kwh": 43,
      "household_count": 29,
      "yuan_per_degree_to_yuan_per_kwh": 28,
      "ten_thousand_yuan_per_village": 27,
      "yuan_per_sqm": 24,
      "no_match": 22,
      "duration_hour": 14,
      "ratio_sequence": 14,
      "kwh_threshold_range": 11,
      "time_point": 10,
      "duration_month_context": 7,
      "capacity_value": 4,
      "yuan_per_ton": 3,
      "yuan_per_watt": 3,
      "price_value_retyped_to_subsidy_amount_context": 3
    },
    "filtered_rule_counts": {},
    "bind_reason_top20": {
      "keyword_plus_prior": 702,
      "keyword_hit": 166,
      "param_type_map": 152,
      "candidate_score": 90,
      "step4_inherit": 18,
      "step4_fallback": 12,
      "no_candidate": 1
    },
    "bind_transition_top20": {
      "subsidy->subsidy": 364,
      "tou_pricing->tou_pricing": 245,
      "tiered_pricing->tiered_pricing": 148,
      "tou_pricing->task_assessment": 102,
      "task_assessment->technology_route": 48,
      "technology_route->tou_pricing": 42,
      "tou_pricing->subsidy": 29,
      "general_price_adjustment->general_price_adjustment": 27,
      "technology_route->technology_route": 27,
      "task_assessment->task_assessment": 21,
      "tou_pricing->general_price_adjustment": 16,
      "tou_pricing->tiered_pricing": 12,
      "general_price_adjustment->tiered_pricing": 11,
      "subsidy->tiered_pricing": 11,
      "None->task_assessment": 10,
      "subsidy->technology_route": 10,
      "general_price_adjustment->tou_pricing": 7,
      "task_assessment->tou_pricing": 3,
      "task_assessment->subsidy": 2,
      "general_price_adjustment->subsidy": 1
    },
    "skip_reason_top20": {
      "time_meta_filtered": 117,
      "label_only_filtered": 17,
      "pollutant_unit_filtered": 13
    },
    "post_guard_top20": {
      "price_value_retyped_to_subsidy_amount": 3,
      "subsidy_amount_retyped_to_price_value": 2,
      "price_conflict_retyped_to_kwh": 2
    }
  },
  "unit_conflicts_top20": [
    {
      "doc_instance_id": "10695560c26cc67b7a3e26b8dbcd7b856b0b17ef49c31ba529efd3caf059a1de",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "17b169c01d0fd11691f3014066bc982e9d5aae3ef301b3d897d2a4b986dac45b",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "3c1392fd897f1d095efaa1ae2a1eaa5c0c3df313cd5a9a185aacffe05575b886",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "41eed2fc03a95dc30af898124e00962d37f00dd998abb5da87c6e10e209db169",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "6618b31ad2d2553801e75f1d42256338782cda332eb141a7fea6466fee1dccfd",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "6ca5d9d44b93a3440cc8f24b4feda441563e6841021017b2c5db628a6976c9f5",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "a63aaa1b99aae78cd58b5beb8c271e538c4b10b43ff4aff7312d6e081dd79eed",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan"
      ]
    },
    {
      "doc_instance_id": "c32ed07b1f8848d45dcf196616c7064ebdf5a10f0ce328b277c662ee5197f29b",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "ten_thousand_yuan",
        "yuan_per_ton"
      ]
    },
    {
      "doc_instance_id": "cd86e3487ec66701c2d41c1399f9a453338981c169b847ab9321c78351d62988",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "yuan",
        "yuan_per_watt"
      ]
    },
    {
      "doc_instance_id": "f6f8d5f9847c1fe31624cb64353d12b61bebca40113c37e445b63a2d226db18d",
      "mechanism_type": "subsidy",
      "param_type": "subsidy_amount",
      "norm_units": [
        "yuan",
        "yuan_per_watt"
      ]
    }
  ]
}
```

#### Step7 Step6侧IAA指标
来源：`00_整理记录/step7_iter3b_unitfix_timeunit_thr060_iaa_report.json`

```json
{
  "config": {
    "mentions": "00_整理记录/step7_iter3_unitfix_timeunit_thr060_parameter_mentions.jsonl",
    "clause_corpus": "00_整理记录/step3_clause_corpus.jsonl",
    "sample_size": 300,
    "strict_min": 140,
    "hard_min": 80,
    "seed": 20260211
  },
  "sampling": {
    "target_total": 300,
    "actual_total": 300,
    "strict_high_count": 221,
    "hard_case_count": 153,
    "mechanism_distribution": {
      "task_assessment": 74,
      "subsidy": 52,
      "tou_pricing": 53,
      "technology_route": 45,
      "tiered_pricing": 42,
      "general_price_adjustment": 32,
      "differential_penalty_pricing": 1,
      "None": 1
    },
    "param_type_distribution": {
      "duration_threshold_month": 3,
      "subsidy_amount": 20,
      "ratio_target": 102,
      "price_delta_pct": 42,
      "price_value": 28,
      "None": 13,
      "area_subsidy_amount": 4,
      "consumption_threshold_kwh": 31,
      "target_household_count": 12,
      "time_window": 28,
      "duration_threshold_hour": 6,
      "funding_share_ratio": 4,
      "tonnage_threshold": 2,
      "other": 3,
      "duration_threshold_year": 2
    },
    "bind_group_distribution": {
      "high_conf": 246,
      "fallback": 21,
      "candidate_score": 32,
      "other": 1
    },
    "hard_tag_distribution": {
      "negative_domain": 43,
      "task_clause": 44,
      "candidate_score": 32,
      "time_token": 28,
      "threshold_price_same_clause": 21
    }
  },
  "iaa": {
    "kappa_mechanism": 0.991969,
    "kappa_param_type": 1.0,
    "exact_match_norm_unit": 1.0,
    "agreement_strict_high_eligible": 1.0
  },
  "quality": {
    "denominators": {
      "all_clause": 2022,
      "sample_total": 300,
      "valid_all": 300,
      "valid_numeric": 287
    },
    "mechanism_precision_on_valid_numeric": {
      "num": 271,
      "den": 283,
      "rate": 0.957597
    },
    "normalization_precision_on_valid_numeric": {
      "num": 287,
      "den": 287,
      "rate": 1.0
    },
    "strict_high_precision": {
      "num": 220,
      "den": 221,
      "rate": 0.995475
    }
  },
  "error_clusters": {
    "time_raw_not_time_window": 0,
    "price_value_large_raw_small_norm": 0,
    "candidate_score_strict_high": 0
  },
  "target_pass": {
    "kappa_mechanism_ge_0_80": true,
    "kappa_param_type_ge_0_80": true,
    "exact_match_norm_unit_ge_0_90": true,
    "agreement_strict_high_eligible_ge_0_90": true,
    "mechanism_precision_ge_0_90": true,
    "normalization_precision_ge_0_90": true,
    "strict_high_precision_ge_0_92": true,
    "time_raw_not_time_window_eq_0": true,
    "price_value_large_raw_small_norm_eq_0": true,
    "candidate_score_strict_high_eq_0": true,
    "sample_size_ge_240": true,
    "sample_strict_ge_120": true,
    "sample_hard_ge_60": true
  },
  "all_targets_passed": true
}
```

#### Step7 联合门禁指标
来源：`00_整理记录/step7_gate_iter3_final.json`

```json
{
  "input": {
    "step5_report": "00_整理记录/step7_iter3_unitfix_timeunit_thr060_validation_report.json",
    "step6_report": "00_整理记录/step7_iter3b_unitfix_timeunit_thr060_iaa_report.json"
  },
  "step5_snapshot": {
    "normalization_matched_on_mentions": {
      "num": 1119,
      "den": 1141,
      "rate": 0.980719
    },
    "strict_high_on_valid_numeric": {
      "num": 952,
      "den": 1119,
      "rate": 0.85076
    },
    "mechanism_bound_on_valid_numeric": {
      "num": 1119,
      "den": 1119,
      "rate": 1.0
    },
    "local_supported_rate_valid_numeric": 0.899017
  },
  "step6_snapshot": {
    "iaa": {
      "kappa_mechanism": 0.991969,
      "kappa_param_type": 1.0,
      "exact_match_norm_unit": 1.0,
      "agreement_strict_high_eligible": 1.0
    },
    "quality_denominators": {
      "all_clause": 2022,
      "sample_total": 300,
      "valid_all": 300,
      "valid_numeric": 287
    },
    "mechanism_precision_on_valid_numeric": {
      "num": 271,
      "den": 283,
      "rate": 0.957597
    },
    "normalization_precision_on_valid_numeric": {
      "num": 287,
      "den": 287,
      "rate": 1.0
    },
    "strict_high_precision": {
      "num": 220,
      "den": 221,
      "rate": 0.995475
    },
    "target_pass": {
      "kappa_mechanism_ge_0_80": true,
      "kappa_param_type_ge_0_80": true,
      "exact_match_norm_unit_ge_0_90": true,
      "agreement_strict_high_eligible_ge_0_90": true,
      "mechanism_precision_ge_0_90": true,
      "normalization_precision_ge_0_90": true,
      "strict_high_precision_ge_0_92": true,
      "time_raw_not_time_window_eq_0": true,
      "price_value_large_raw_small_norm_eq_0": true,
      "candidate_score_strict_high_eq_0": true,
      "sample_size_ge_240": true,
      "sample_strict_ge_120": true,
      "sample_hard_ge_60": true
    }
  },
  "target_pass": {
    "step5_normalization_matched_rate_ge_0_95": true,
    "step5_strict_high_rate_valid_numeric_ge_0_85": true,
    "step5_mechanism_bound_rate_valid_numeric_eq_1_0": true,
    "step5_local_supported_rate_valid_numeric_ge_0_85": true,
    "step6_kappa_mechanism_ge_0_90": true,
    "step6_kappa_param_type_ge_0_95": true,
    "step6_mechanism_precision_ge_0_95": true,
    "step6_normalization_precision_ge_0_995": true,
    "step6_strict_high_precision_ge_0_992": true,
    "step6_hard_error_time_raw_not_time_window_eq_0": true,
    "step6_hard_error_price_value_large_raw_small_norm_eq_0": true,
    "step6_hard_error_candidate_score_strict_high_eq_0": true
  },
  "all_targets_passed": true
}
```

## Step8：双轨图包导出与工程验收（含 Step8.2）
### 创新方法
- 双轨图包：`strict_high`（高置信主图）+ `strict_all`（扩展召回图）并行导出，服务不同应用层。
- 通过 manifest/hash/replay 做确定性复现，保证论文与工程可复跑。
- Step8.2 将冲突日志信号化并固化查询模板，直接形成可评测的推演入口。

### 全指标
#### Step8 图包验收指标
来源：`结果文件夹/step8_iter1/validation_report.json`

```json
{
  "all_targets_passed": true,
  "checks": {
    "conflict_explainability": true,
    "deterministic_replay_match": true,
    "manifest_file_integrity": true,
    "strict_all:dry_run_simulated": true,
    "strict_all:edge_unit_legal_strict_high": true,
    "strict_all:evidence_traceability_strict_high": true,
    "strict_all:fk_integrity": true,
    "strict_all:node_unit_legal_strict_high": true,
    "strict_all:pk_edges_unique": true,
    "strict_all:pk_nodes_unique": true,
    "strict_all:schema_integrity": true,
    "strict_high:dry_run_simulated": true,
    "strict_high:edge_unit_legal_strict_high": true,
    "strict_high:evidence_traceability_strict_high": true,
    "strict_high:fk_integrity": true,
    "strict_high:node_unit_legal_strict_high": true,
    "strict_high:pk_edges_unique": true,
    "strict_high:pk_nodes_unique": true,
    "strict_high:schema_integrity": true
  },
  "config": {
    "canonical_units": [
      "hour",
      "household",
      "kva",
      "kw",
      "kwh",
      "month",
      "mw",
      "none",
      "percent",
      "ten_thousand_yuan",
      "time_window",
      "ton",
      "year",
      "yuan",
      "yuan_per_kwh",
      "yuan_per_sqm",
      "yuan_per_ton",
      "yuan_per_watt"
    ],
    "edge_schema": {
      "clause_has_parameter_mention": [
        "Clause",
        "ParameterMention"
      ],
      "clause_supports_mechanism": [
        "Clause",
        "Mechanism"
      ],
      "contains_clause": [
        "PolicyDocument",
        "Clause"
      ],
      "contains_mechanism": [
        "PolicyDocument",
        "Mechanism"
      ],
      "mechanism_anchor_clause": [
        "Mechanism",
        "Clause"
      ],
      "mechanism_has_parameter_definition": [
        "Mechanism",
        "ParameterDefinition"
      ],
      "parameter_mention_refers_to_definition": [
        "ParameterMention",
        "ParameterDefinition"
      ]
    },
    "extraction_version": "step7b_iterB_rulefix",
    "git_commit": "78de16a3ec07cce26cb43d0ab6a1f554cb9f0ad9",
    "input": {
      "clause_corpus": "00_整理记录\\step3_clause_corpus.jsonl",
      "definitions": "00_整理记录\\step7b_iterB_rulefix_parameter_definitions.jsonl",
      "mentions": "00_整理记录\\step7b_iterB_rulefix_parameter_mentions.jsonl"
    },
    "known_mechanisms": [
      "differential_penalty_pricing",
      "general_price_adjustment",
      "subsidy",
      "task_assessment",
      "technology_route",
      "tiered_pricing",
      "tou_pricing"
    ],
    "run_id": "step8_iter1",
    "schema_version": "schema_v1.4",
    "strict_all_topk": 5,
    "timestamp_utc": "2026-02-11T09:41:30.185315+00:00",
    "tracks": [
      "strict_high",
      "strict_all"
    ]
  },
  "conflict_count": 3929,
  "conflict_explainability_ok": true,
  "deterministic_check": {
    "enabled": true,
    "mismatches": [],
    "passed": true
  },
  "extraction_version": "step7b_iterB_rulefix",
  "file_integrity_checks": [
    {
      "actual_sha256": "caf4f99f7b6cb72c9bf6f9f218fba907b5baeced0b35e2ea3024d996a7c729f9",
      "exists": true,
      "hash_match": true,
      "manifest_row_count": null,
      "manifest_sha256": "caf4f99f7b6cb72c9bf6f9f218fba907b5baeced0b35e2ea3024d996a7c729f9",
      "path": "config.json"
    },
    {
      "actual_sha256": "2beefeabb0043d0864a403e5a9b1104e5cfb3d2f9e4004d05ac2d2a902c6fa97",
      "exists": true,
      "hash_match": true,
      "manifest_row_count": 3929,
      "manifest_sha256": "2beefeabb0043d0864a403e5a9b1104e5cfb3d2f9e4004d05ac2d2a902c6fa97",
      "path": "conflicts.jsonl"
    },
    {
      "actual_sha256": "4505e23e7c914c256bc6bb0850f4f0cf03dff9fd7076446d92b4d441259e91ab",
      "exists": true,
      "hash_match": true,
      "manifest_row_count": 205,
      "manifest_sha256": "4505e23e7c914c256bc6bb0850f4f0cf03dff9fd7076446d92b4d441259e91ab",
      "path": "rejects.jsonl"
    },
    {
      "actual_sha256": "472d8ccacee43d928337323d418a157f5da8d994c173c1a837395cb41f061a5e",
      "exists": true,
      "hash_match": true,
      "manifest_row_count": null,
      "manifest_sha256": "472d8ccacee43d928337323d418a157f5da8d994c173c1a837395cb41f061a5e",
      "path": "stats.json"
    },
    {
      "actual_sha256": "4ab46c2be99049db7e27c2b97578a807d57effb5383a24c04da1939abbc1d7cf",
      "exists": true,
      "hash_match": true,
      "manifest_row_count": 5742,
      "manifest_sha256": "4ab46c2be99049db7e27c2b97578a807d57effb5383a24c04da1939abbc1d7cf",
      "path": "strict_all/edges.csv"
    },
    {
      "actual_sha256": "8fb514afd73da28f3dcaec42b6af7a872c2189726a92f636745fe3bf6240dcd8",
      "exists": true,
      "hash_match": true,
      "manifest_row_count": 2892,
      "manifest_sha256": "8fb514afd73da28f3dcaec42b6af7a872c2189726a92f636745fe3bf6240dcd8",
      "path": "strict_all/nodes.csv"
    },
    {
      "actual_sha256": "b48280cfd599d2b6b037da3c7299b49f3035fea1b198c2a511c410600e8d1200",
      "exists": true,
      "hash_match": true,
      "manifest_row_count": 5742,
      "manifest_sha256": "b48280cfd599d2b6b037da3c7299b49f3035fea1b198c2a511c410600e8d1200",
      "path": "strict_all/triples_spo.jsonl"
    },
    {
      "actual_sha256": "270c1caf24682a54625a7292d28304a58409aa32b8e6980e3cbbafa41a808681",
      "exists": true,
      "hash_match": true,
      "manifest_row_count": 4868,
      "manifest_sha256": "270c1caf24682a54625a7292d28304a58409aa32b8e6980e3cbbafa41a808681",
      "path": "strict_high/edges.csv"
    },
    {
      "actual_sha256": "957191766f42190e0991a03af88b4d8e3f34bbd405215875d9d1db4850a78577",
      "exists": true,
      "hash_match": true,
      "manifest_row_count": 2494,
      "manifest_sha256": "957191766f42190e0991a03af88b4d8e3f34bbd405215875d9d1db4850a78577",
      "path": "strict_high/nodes.csv"
    },
    {
      "actual_sha256": "34fc7712c2fc265213b551cdb910efe915c96a80569df36003bb4f62a4eca0c0",
      "exists": true,
      "hash_match": true,
      "manifest_row_count": 4868,
      "manifest_sha256": "34fc7712c2fc265213b551cdb910efe915c96a80569df36003bb4f62a4eca0c0",
      "path": "strict_high/triples_spo.jsonl"
    }
  ],
  "package_dir": "00_整理记录\\graph_pkg\\step8_iter1",
  "run_id": "step8_iter1",
  "schema_version": "schema_v1.4",
  "stats_snapshot": {
    "strict_all": {
      "edge_count": 5742,
      "label_distribution": {
        "Clause": 599,
        "Mechanism": 613,
        "ParameterDefinition": 356,
        "ParameterMention": 1122,
        "PolicyDocument": 202
      },
      "mention_accepted": 1122,
      "mention_total_input": 1141,
      "node_count": 2892,
      "predicate_distribution": {
        "clause_has_parameter_mention": 1122,
        "clause_supports_mechanism": 613,
        "contains_clause": 599,
        "contains_mechanism": 613,
        "mechanism_anchor_clause": 613,
        "mechanism_has_parameter_definition": 1060,
        "parameter_mention_refers_to_definition": 1122
      },
      "reject_count": 19,
      "reject_reason_distribution": {
        "E_FK_MISSING": 19
      },
      "track": "strict_all",
      "triple_count": 5742
    },
    "strict_high": {
      "edge_count": 4868,
      "label_distribution": {
        "Clause": 509,
        "Mechanism": 513,
        "ParameterDefinition": 330,
        "ParameterMention": 955,
        "PolicyDocument": 187
      },
      "mention_accepted": 955,
      "mention_total_input": 1141,
      "node_count": 2494,
      "predicate_distribution": {
        "clause_has_parameter_mention": 955,
        "clause_supports_mechanism": 513,
        "contains_clause": 509,
        "contains_mechanism": 513,
        "mechanism_anchor_clause": 513,
        "mechanism_has_parameter_definition": 910,
        "parameter_mention_refers_to_definition": 955
      },
      "reject_count": 186,
      "reject_reason_distribution": {
        "E_FK_MISSING": 19,
        "E_STRICT_FILTER": 167
      },
      "track": "strict_high",
      "triple_count": 4868
    }
  },
  "track_reports": {
    "strict_all": {
      "all_checks_passed": true,
      "checks": {
        "dry_run_simulated": true,
        "edge_unit_legal_strict_high": true,
        "evidence_traceability_strict_high": true,
        "fk_integrity": true,
        "node_unit_legal_strict_high": true,
        "pk_edges_unique": true,
        "pk_nodes_unique": true,
        "schema_integrity": true
      },
      "counts": {
        "edges": 5742,
        "nodes": 2892,
        "predicates": {
          "clause_has_parameter_mention": 1122,
          "clause_supports_mechanism": 613,
          "contains_clause": 599,
          "contains_mechanism": 613,
          "mechanism_anchor_clause": 613,
          "mechanism_has_parameter_definition": 1060,
          "parameter_mention_refers_to_definition": 1122
        }
      },
      "errors": {
        "evidence_bad": 0,
        "fk_missing": 0,
        "node_def_unit_bad": 0,
        "schema_violations": 0,
        "unit_bad": 0,
        "unit_missing": 0
      }
    },
    "strict_high": {
      "all_checks_passed": true,
      "checks": {
        "dry_run_simulated": true,
        "edge_unit_legal_strict_high": true,
        "evidence_traceability_strict_high": true,
        "fk_integrity": true,
        "node_unit_legal_strict_high": true,
        "pk_edges_unique": true,
        "pk_nodes_unique": true,
        "schema_integrity": true
      },
      "counts": {
        "edges": 4868,
        "nodes": 2494,
        "predicates": {
          "clause_has_parameter_mention": 955,
          "clause_supports_mechanism": 513,
          "contains_clause": 509,
          "contains_mechanism": 513,
          "mechanism_anchor_clause": 513,
          "mechanism_has_parameter_definition": 910,
          "parameter_mention_refers_to_definition": 955
        }
      },
      "errors": {
        "evidence_bad": 0,
        "fk_missing": 0,
        "node_def_unit_bad": 0,
        "schema_violations": 0,
        "unit_bad": 0,
        "unit_missing": 0
      }
    }
  },
  "warnings": []
}
```

#### Step8 图规模与拒收统计
来源：`结果文件夹/step8_iter1/stats.json`

```json
{
  "strict_all": {
    "edge_count": 5742,
    "label_distribution": {
      "Clause": 599,
      "Mechanism": 613,
      "ParameterDefinition": 356,
      "ParameterMention": 1122,
      "PolicyDocument": 202
    },
    "mention_accepted": 1122,
    "mention_total_input": 1141,
    "node_count": 2892,
    "predicate_distribution": {
      "clause_has_parameter_mention": 1122,
      "clause_supports_mechanism": 613,
      "contains_clause": 599,
      "contains_mechanism": 613,
      "mechanism_anchor_clause": 613,
      "mechanism_has_parameter_definition": 1060,
      "parameter_mention_refers_to_definition": 1122
    },
    "reject_count": 19,
    "reject_reason_distribution": {
      "E_FK_MISSING": 19
    },
    "track": "strict_all",
    "triple_count": 5742
  },
  "strict_high": {
    "edge_count": 4868,
    "label_distribution": {
      "Clause": 509,
      "Mechanism": 513,
      "ParameterDefinition": 330,
      "ParameterMention": 955,
      "PolicyDocument": 187
    },
    "mention_accepted": 955,
    "mention_total_input": 1141,
    "node_count": 2494,
    "predicate_distribution": {
      "clause_has_parameter_mention": 955,
      "clause_supports_mechanism": 513,
      "contains_clause": 509,
      "contains_mechanism": 513,
      "mechanism_anchor_clause": 513,
      "mechanism_has_parameter_definition": 910,
      "parameter_mention_refers_to_definition": 955
    },
    "reject_count": 186,
    "reject_reason_distribution": {
      "E_FK_MISSING": 19,
      "E_STRICT_FILTER": 167
    },
    "track": "strict_high",
    "triple_count": 4868
  }
}
```

#### Step8.2 查询与信号评测指标
来源：`结果文件夹/step8_2_iter1/step8_2_eval_report.json`

```json
{
  "all_targets_passed": true,
  "checks": {
    "conflict_type_classification_coverage_ge_95": true,
    "core_path_coverage_100": true,
    "deterministic_pack_rebuild_match_100": true,
    "edge_signal_coverage_on_strict_high_100": true,
    "parameterized_example_coverage_100": true,
    "query_execution_success_rate_100": true,
    "query_template_count_10_20": true
  },
  "conflict_signal_summary": {
    "conflict_classified": 3929,
    "conflict_total": 3929,
    "conflict_type_classification_coverage": 1.0,
    "conflict_type_distribution": {
      "dedup_aggregation": 3875,
      "semantic_collision": 54
    }
  },
  "input": {
    "conflicts": 3929,
    "step8_dir": "00_整理记录\\graph_pkg\\step8_iter1",
    "step8_manifest_run_id": "step8_iter1",
    "strict_all_edges": 5742,
    "strict_high_edges": 4868,
    "strict_high_nodes": 2494
  },
  "metrics": {
    "conflict_type_classification_coverage": 1.0,
    "core_path_coverage": 1.0,
    "deterministic_pack_rebuild_match": true,
    "edge_signal_coverage_on_strict_high": 1.0,
    "parameterized_example_coverage": 1.0,
    "query_execution_success_rate": 1.0,
    "query_template_count": 12
  },
  "query_eval": [
    {
      "error": "",
      "executed_successfully": true,
      "path_tag": "forward_main",
      "query_id": "Q01",
      "result_count": 1,
      "title": "policy_to_mechanism_path"
    },
    {
      "error": "",
      "executed_successfully": true,
      "path_tag": "reverse_main",
      "query_id": "Q02",
      "result_count": 1,
      "title": "mechanism_reverse_to_policy"
    },
    {
      "error": "",
      "executed_successfully": true,
      "path_tag": "forward_main",
      "query_id": "Q03",
      "result_count": 1,
      "title": "mechanism_to_definitions"
    },
    {
      "error": "",
      "executed_successfully": true,
      "path_tag": "reverse_main",
      "query_id": "Q04",
      "result_count": 9,
      "title": "definition_reverse_to_policy"
    },
    {
      "error": "",
      "executed_successfully": true,
      "path_tag": "forward_main",
      "query_id": "Q05",
      "result_count": 7,
      "title": "time_window_mechanisms_by_policy"
    },
    {
      "error": "",
      "executed_successfully": true,
      "path_tag": "forward_main",
      "query_id": "Q06",
      "result_count": 10,
      "title": "threshold_filter_by_param_type"
    },
    {
      "error": "",
      "executed_successfully": true,
      "path_tag": "forward_main",
      "query_id": "Q07",
      "result_count": 3,
      "title": "region_proxy_filter"
    },
    {
      "error": "",
      "executed_successfully": true,
      "path_tag": "forward_main",
      "query_id": "Q08",
      "result_count": 10,
      "title": "target_group_proxy_filter"
    },
    {
      "error": "",
      "executed_successfully": true,
      "path_tag": "risk_signal",
      "query_id": "Q09",
      "result_count": 10,
      "title": "mechanism_conflict_rank"
    },
    {
      "error": "",
      "executed_successfully": true,
      "path_tag": "risk_signal",
      "query_id": "Q10",
      "result_count": 10,
      "title": "high_risk_facts"
    },
    {
      "error": "",
      "executed_successfully": true,
      "path_tag": "risk_signal",
      "query_id": "Q11",
      "result_count": 1,
      "title": "cross_clause_conflict_by_mechanism_type"
    },
    {
      "error": "",
      "executed_successfully": true,
      "path_tag": "risk_signal",
      "query_id": "Q12",
      "result_count": 10,
      "title": "strict_all_backfill_candidates"
    }
  ]
}
```

#### Step8.2 冲突信号覆盖指标
来源：`结果文件夹/step8_2_iter1/conflict_signal_report.json`

```json
{
  "conflict_classified": 3929,
  "conflict_total": 3929,
  "conflict_type_classification_coverage": 1.0,
  "conflict_type_distribution": {
    "dedup_aggregation": 3875,
    "semantic_collision": 54
  }
}
```

## Step9：Neo4j 落地、查询评测与推演闭环
### 创新方法
- 把 Step8 图包在 Neo4j 做可复跑导入，串联“导入 -> 查询 -> 推演 -> 总门禁”的端到端闭环。
- 将风险信号挂载到边并参与重排，验证风险感知策略在不退化前提下可运行。
- 输出脚本化评测报告，支持论文复现实验与工程审计。

### 全指标
#### Step9 Neo4j 导入验收指标
来源：`00_整理记录/step9_iter1/step9_neo4j_import_report.json`

```json
{
  "actual": {
    "constraint_total": 5,
    "edge_signal_attached_total": 4868,
    "edge_total": 10610,
    "index_total": 11,
    "node_label_distribution": [
      {
        "cnt": 599,
        "label": "Clause"
      },
      {
        "cnt": 613,
        "label": "Mechanism"
      },
      {
        "cnt": 356,
        "label": "ParameterDefinition"
      },
      {
        "cnt": 1122,
        "label": "ParameterMention"
      },
      {
        "cnt": 202,
        "label": "PolicyDocument"
      }
    ],
    "node_total": 2892,
    "predicate_track_distribution": [
      {
        "count": 1122,
        "predicate": "clause_has_parameter_mention",
        "track": "strict_all"
      },
      {
        "count": 955,
        "predicate": "clause_has_parameter_mention",
        "track": "strict_high"
      },
      {
        "count": 613,
        "predicate": "clause_supports_mechanism",
        "track": "strict_all"
      },
      {
        "count": 513,
        "predicate": "clause_supports_mechanism",
        "track": "strict_high"
      },
      {
        "count": 599,
        "predicate": "contains_clause",
        "track": "strict_all"
      },
      {
        "count": 509,
        "predicate": "contains_clause",
        "track": "strict_high"
      },
      {
        "count": 613,
        "predicate": "contains_mechanism",
        "track": "strict_all"
      },
      {
        "count": 513,
        "predicate": "contains_mechanism",
        "track": "strict_high"
      },
      {
        "count": 613,
        "predicate": "mechanism_anchor_clause",
        "track": "strict_all"
      },
      {
        "count": 513,
        "predicate": "mechanism_anchor_clause",
        "track": "strict_high"
      },
      {
        "count": 1060,
        "predicate": "mechanism_has_parameter_definition",
        "track": "strict_all"
      },
      {
        "count": 910,
        "predicate": "mechanism_has_parameter_definition",
        "track": "strict_high"
      },
      {
        "count": 1122,
        "predicate": "parameter_mention_refers_to_definition",
        "track": "strict_all"
      },
      {
        "count": 955,
        "predicate": "parameter_mention_refers_to_definition",
        "track": "strict_high"
      }
    ],
    "trace_total": 10610,
    "traceability_rate": 1.0,
    "traceable": 10610
  },
  "all_targets_passed": true,
  "checks": {
    "constraints_created_ge_5": true,
    "edge_total_match_expected": true,
    "indexes_created_ge_4": true,
    "node_total_match_expected": true,
    "predicate_track_count_match": true,
    "risk_signal_attached_on_strict_high_edges": true,
    "traceability_rate_100": true
  },
  "expected": {
    "edge_signal_total": 4868,
    "edge_total": 10610,
    "node_total": 2892,
    "predicate_track_distribution": {
      "clause_has_parameter_mention|strict_all": 1122,
      "clause_has_parameter_mention|strict_high": 955,
      "clause_supports_mechanism|strict_all": 613,
      "clause_supports_mechanism|strict_high": 513,
      "contains_clause|strict_all": 599,
      "contains_clause|strict_high": 509,
      "contains_mechanism|strict_all": 613,
      "contains_mechanism|strict_high": 513,
      "mechanism_anchor_clause|strict_all": 613,
      "mechanism_anchor_clause|strict_high": 513,
      "mechanism_has_parameter_definition|strict_all": 1060,
      "mechanism_has_parameter_definition|strict_high": 910,
      "parameter_mention_refers_to_definition|strict_all": 1122,
      "parameter_mention_refers_to_definition|strict_high": 955
    }
  },
  "input": {
    "edge_signals_csv": "结果文件夹/step8_2_iter1/edge_signals.csv",
    "step8_2_dir": "结果文件夹/step8_2_iter1",
    "step8_dir": "结果文件夹/step8_iter1",
    "strict_all_edges_csv": "结果文件夹/step8_iter1/strict_all/edges.csv",
    "strict_all_nodes_csv": "结果文件夹/step8_iter1/strict_all/nodes.csv",
    "strict_high_edges_csv": "结果文件夹/step8_iter1/strict_high/edges.csv"
  },
  "neo4j": {
    "bolt_port": 17687,
    "container_name": "policy-kg-step9-neo4j",
    "docker": {
      "created": false,
      "status_after": "running",
      "status_before": "running"
    },
    "http_port": 17474,
    "image": "neo4j:5.26.0-community",
    "url": "http://127.0.0.1:17474"
  },
  "staged_files": [
    {
      "dest": "/var/lib/neo4j/import/step9/nodes_strict_all.csv",
      "source": "结果文件夹/step8_iter1/strict_all/nodes.csv"
    },
    {
      "dest": "/var/lib/neo4j/import/step9/edges_strict_high.csv",
      "source": "结果文件夹/step8_iter1/strict_high/edges.csv"
    },
    {
      "dest": "/var/lib/neo4j/import/step9/edges_strict_all.csv",
      "source": "结果文件夹/step8_iter1/strict_all/edges.csv"
    },
    {
      "dest": "/var/lib/neo4j/import/step9/edge_signals.csv",
      "source": "结果文件夹/step8_2_iter1/edge_signals.csv"
    }
  ]
}
```

#### Step9 查询执行评测指标
来源：`00_整理记录/step9_iter1/step9_query_exec_report.json`

```json
{
  "all_targets_passed": true,
  "checks": {
    "core_path_coverage_100": true,
    "non_empty_query_rate_ge_95": true,
    "parameterized_example_coverage_100": true,
    "query_execution_success_rate_100": true,
    "query_template_count_10_20": true,
    "risk_signal_query_coverage_ge_95": true
  },
  "input": {
    "query_examples": "结果文件夹/step8_2_iter1/query_examples.json",
    "query_pack": "结果文件夹/step8_2_iter1/query_pack.cql",
    "step8_2_eval_report": "结果文件夹/step8_2_iter1/step8_2_eval_report.json"
  },
  "metrics": {
    "core_path_coverage": 1.0,
    "non_empty_query_rate": 1.0,
    "parameterized_example_coverage": 1.0,
    "query_execution_success_rate": 1.0,
    "query_template_count": 12,
    "risk_signal_query_coverage": 1.0
  },
  "neo4j": {
    "url": "http://127.0.0.1:17474"
  },
  "query_eval": [
    {
      "error": "",
      "executed_successfully": true,
      "params": {
        "limit": 10,
        "policy_id": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec"
      },
      "path_tag": "forward_main",
      "query_id": "Q01",
      "result_count": 8,
      "result_preview": [
        {
          "c.id": "Clause:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0000",
          "m.id": "Mechanism:mechanism_04962c40a9d41dc13aea",
          "m.mechanism_type": "task_assessment",
          "p.id": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec"
        },
        {
          "c.id": "Clause:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0000",
          "m.id": "Mechanism:mechanism_04962c40a9d41dc13aea",
          "m.mechanism_type": "task_assessment",
          "p.id": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec"
        },
        {
          "c.id": "Clause:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0001",
          "m.id": "Mechanism:mechanism_4f0f2ebab9dc78254ad0",
          "m.mechanism_type": "task_assessment",
          "p.id": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec"
        }
      ],
      "title": "policy_to_mechanism_path"
    },
    {
      "error": "",
      "executed_successfully": true,
      "params": {
        "limit": 10,
        "mechanism_id": "Mechanism:mechanism_001af6c12cbeeea0013f"
      },
      "path_tag": "reverse_main",
      "query_id": "Q02",
      "result_count": 4,
      "result_preview": [
        {
          "c.id": "Clause:15d322df36604ef5082b3cbb152c1ae45bda6ad3f5d941b024f5371b4210c4d8#clause_0005",
          "m.id": "Mechanism:mechanism_001af6c12cbeeea0013f",
          "p.id": "PolicyDocument:15d322df36604ef5082b3cbb152c1ae45bda6ad3f5d941b024f5371b4210c4d8"
        },
        {
          "c.id": "Clause:15d322df36604ef5082b3cbb152c1ae45bda6ad3f5d941b024f5371b4210c4d8#clause_0005",
          "m.id": "Mechanism:mechanism_001af6c12cbeeea0013f",
          "p.id": "PolicyDocument:15d322df36604ef5082b3cbb152c1ae45bda6ad3f5d941b024f5371b4210c4d8"
        },
        {
          "c.id": "Clause:15d322df36604ef5082b3cbb152c1ae45bda6ad3f5d941b024f5371b4210c4d8#clause_0005",
          "m.id": "Mechanism:mechanism_001af6c12cbeeea0013f",
          "p.id": "PolicyDocument:15d322df36604ef5082b3cbb152c1ae45bda6ad3f5d941b024f5371b4210c4d8"
        }
      ],
      "title": "mechanism_reverse_to_policy"
    },
    {
      "error": "",
      "executed_successfully": true,
      "params": {
        "limit": 10,
        "mechanism_id": "Mechanism:mechanism_001af6c12cbeeea0013f"
      },
      "path_tag": "forward_main",
      "query_id": "Q03",
      "result_count": 2,
      "result_preview": [
        {
          "d.id": "ParameterDefinition:pd_8ac00f0dcf4e20b172df",
          "d.norm_unit": "percent",
          "d.norm_value": "20.0",
          "d.param_type": "price_delta_pct",
          "m.id": "Mechanism:mechanism_001af6c12cbeeea0013f"
        },
        {
          "d.id": "ParameterDefinition:pd_8ac00f0dcf4e20b172df",
          "d.norm_unit": "percent",
          "d.norm_value": "20.0",
          "d.param_type": "price_delta_pct",
          "m.id": "Mechanism:mechanism_001af6c12cbeeea0013f"
        }
      ],
      "title": "mechanism_to_definitions"
    },
    {
      "error": "",
      "executed_successfully": true,
      "params": {
        "definition_id": "ParameterDefinition:pd_001ecda849d68a57ab32",
        "limit": 10
      },
      "path_tag": "reverse_main",
      "query_id": "Q04",
      "result_count": 10,
      "result_preview": [
        {
          "c.id": "Clause:6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a#clause_0009",
          "d.id": "ParameterDefinition:pd_001ecda849d68a57ab32",
          "p.id": "PolicyDocument:6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a",
          "pm.id": "ParameterMention:pm_ecc769d5802c9f838983"
        },
        {
          "c.id": "Clause:6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a#clause_0009",
          "d.id": "ParameterDefinition:pd_001ecda849d68a57ab32",
          "p.id": "PolicyDocument:6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a",
          "pm.id": "ParameterMention:pm_ecc769d5802c9f838983"
        },
        {
          "c.id": "Clause:6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a#clause_0009",
          "d.id": "ParameterDefinition:pd_001ecda849d68a57ab32",
          "p.id": "PolicyDocument:6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a",
          "pm.id": "ParameterMention:pm_ecc769d5802c9f838983"
        }
      ],
      "title": "definition_reverse_to_policy"
    },
    {
      "error": "",
      "executed_successfully": true,
      "params": {
        "limit": 10,
        "policy_id": "PolicyDocument:15d322df36604ef5082b3cbb152c1ae45bda6ad3f5d941b024f5371b4210c4d8"
      },
      "path_tag": "forward_main",
      "query_id": "Q05",
      "result_count": 7,
      "result_preview": [
        {
          "d.id": "ParameterDefinition:pd_fa9d1c22b4a56bb008b3",
          "m.id": "Mechanism:mechanism_ba113fab235698330be1",
          "p.id": "PolicyDocument:15d322df36604ef5082b3cbb152c1ae45bda6ad3f5d941b024f5371b4210c4d8"
        },
        {
          "d.id": "ParameterDefinition:pd_33d729b051e248048b95",
          "m.id": "Mechanism:mechanism_ba113fab235698330be1",
          "p.id": "PolicyDocument:15d322df36604ef5082b3cbb152c1ae45bda6ad3f5d941b024f5371b4210c4d8"
        },
        {
          "d.id": "ParameterDefinition:pd_b9cd2caf8b914338fb85",
          "m.id": "Mechanism:mechanism_e17accc3e828aad00c7c",
          "p.id": "PolicyDocument:15d322df36604ef5082b3cbb152c1ae45bda6ad3f5d941b024f5371b4210c4d8"
        }
      ],
      "title": "time_window_mechanisms_by_policy"
    },
    {
      "error": "",
      "executed_successfully": true,
      "params": {
        "limit": 10,
        "min_value": 0,
        "param_type": "area_subsidy_amount"
      },
      "path_tag": "forward_main",
      "query_id": "Q06",
      "result_count": 10,
      "result_preview": [
        {
          "d.id": "ParameterDefinition:pd_149e98b2a5b780b26003",
          "m.id": "Mechanism:mechanism_bb423bb678ae0743a3f8",
          "p.id": "PolicyDocument:41eed2fc03a95dc30af898124e00962d37f00dd998abb5da87c6e10e209db169"
        },
        {
          "d.id": "ParameterDefinition:pd_149e98b2a5b780b26003",
          "m.id": "Mechanism:mechanism_b2f264ae7bed8d36d571",
          "p.id": "PolicyDocument:3c1392fd897f1d095efaa1ae2a1eaa5c0c3df313cd5a9a185aacffe05575b886"
        },
        {
          "d.id": "ParameterDefinition:pd_149e98b2a5b780b26003",
          "m.id": "Mechanism:mechanism_2faa916caf15250492b6",
          "p.id": "PolicyDocument:a63aaa1b99aae78cd58b5beb8c271e538c4b10b43ff4aff7312d6e081dd79eed"
        }
      ],
      "title": "threshold_filter_by_param_type"
    },
    {
      "error": "",
      "executed_successfully": true,
      "params": {
        "limit": 10,
        "region_keyword": "上海"
      },
      "path_tag": "forward_main",
      "query_id": "Q07",
      "result_count": 10,
      "result_preview": [
        {
          "clause_count": 4,
          "m.id": "Mechanism:mechanism_9cd9ab8742ecdffff267",
          "p.id": "PolicyDocument:cc7addf8ff4efe3409afac8915cc6b8df3283617d08af2da6658e58933736301"
        },
        {
          "clause_count": 4,
          "m.id": "Mechanism:mechanism_f142d4328f8ce0de1045",
          "p.id": "PolicyDocument:cc7addf8ff4efe3409afac8915cc6b8df3283617d08af2da6658e58933736301"
        },
        {
          "clause_count": 4,
          "m.id": "Mechanism:mechanism_1cbaef9a4c85f0cae388",
          "p.id": "PolicyDocument:cc7addf8ff4efe3409afac8915cc6b8df3283617d08af2da6658e58933736301"
        }
      ],
      "title": "region_proxy_filter"
    },
    {
      "error": "",
      "executed_successfully": true,
      "params": {
        "limit": 10,
        "param_type": "area_subsidy_amount"
      },
      "path_tag": "forward_main",
      "query_id": "Q08",
      "result_count": 10,
      "result_preview": [
        {
          "d.id": "ParameterDefinition:pd_149e98b2a5b780b26003",
          "d.norm_unit": "yuan_per_sqm",
          "d.norm_value": "0.0",
          "m.id": "Mechanism:mechanism_bb423bb678ae0743a3f8"
        },
        {
          "d.id": "ParameterDefinition:pd_149e98b2a5b780b26003",
          "d.norm_unit": "yuan_per_sqm",
          "d.norm_value": "0.0",
          "m.id": "Mechanism:mechanism_b2f264ae7bed8d36d571"
        },
        {
          "d.id": "ParameterDefinition:pd_149e98b2a5b780b26003",
          "d.norm_unit": "yuan_per_sqm",
          "d.norm_value": "0.0",
          "m.id": "Mechanism:mechanism_2faa916caf15250492b6"
        }
      ],
      "title": "target_group_proxy_filter"
    },
    {
      "error": "",
      "executed_successfully": true,
      "params": {
        "limit": 10
      },
      "path_tag": "risk_signal",
      "query_id": "Q09",
      "result_count": 10,
      "result_preview": [
        {
          "m.id": "Mechanism:mechanism_610817c963c7fad38960",
          "total_conflict": 2
        },
        {
          "m.id": "Mechanism:mechanism_1e6ce495b7147017cf8b",
          "total_conflict": 2
        },
        {
          "m.id": "Mechanism:mechanism_ea7ac7fff0dc22d4630d",
          "total_conflict": 2
        }
      ],
      "title": "mechanism_conflict_rank"
    },
    {
      "error": "",
      "executed_successfully": true,
      "params": {
        "limit": 10
      },
      "path_tag": "risk_signal",
      "query_id": "Q10",
      "result_count": 10,
      "result_preview": [
        {
          "r.alt_candidates_count": 1,
          "r.conflict_count": 0,
          "r.edge_id": "edge_a737cf194a9f613f4104ba3c",
          "r.predicate": "contains_mechanism",
          "r.source": "PolicyDocument:10695560c26cc67b7a3e26b8dbcd7b856b0b17ef49c31ba529efd3caf059a1de",
          "r.target": "Mechanism:mechanism_d83fd96b9b6e54c2e6d8"
        },
        {
          "r.alt_candidates_count": 1,
          "r.conflict_count": 0,
          "r.edge_id": "edge_881dc1d5baa3dfc2c7f48e38",
          "r.predicate": "contains_mechanism",
          "r.source": "PolicyDocument:693f3a55fe86330e400962dd0b43476d41023ad39e89f0254b4f9e2651efaca2",
          "r.target": "Mechanism:mechanism_3f524bc2b4e81cae9234"
        },
        {
          "r.alt_candidates_count": 1,
          "r.conflict_count": 0,
          "r.edge_id": "edge_2669e613bb8a50a463da1031",
          "r.predicate": "contains_mechanism",
          "r.source": "PolicyDocument:693f3a55fe86330e400962dd0b43476d41023ad39e89f0254b4f9e2651efaca2",
          "r.target": "Mechanism:mechanism_9c7e0f03846f9d46fa6f"
        }
      ],
      "title": "high_risk_facts"
    },
    {
      "error": "",
      "executed_successfully": true,
      "params": {
        "limit": 10,
        "mechanism_type": "differential_penalty_pricing"
      },
      "path_tag": "risk_signal",
      "query_id": "Q11",
      "result_count": 2,
      "result_preview": [
        {
          "d.id": "ParameterDefinition:pd_f71e04834c4336b777e3",
          "m.id": "Mechanism:mechanism_6c3977c1687f0f3b09cd",
          "r.clause_id": "ead750f28a3326778e25ebd3928e8e4ad3b65d0bfdec89dc61d743d7585fbf58#clause_0002",
          "r.conflict_type": null,
          "r.risk_level": null
        },
        {
          "d.id": "ParameterDefinition:pd_f71e04834c4336b777e3",
          "m.id": "Mechanism:mechanism_6c3977c1687f0f3b09cd",
          "r.clause_id": "ead750f28a3326778e25ebd3928e8e4ad3b65d0bfdec89dc61d743d7585fbf58#clause_0002",
          "r.conflict_type": "none",
          "r.risk_level": "low"
        }
      ],
      "title": "cross_clause_conflict_by_mechanism_type"
    },
    {
      "error": "",
      "executed_successfully": true,
      "params": {
        "limit": 10
      },
      "path_tag": "risk_signal",
      "query_id": "Q12",
      "result_count": 10,
      "result_preview": [
        {
          "ra.clause_id": "00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0001",
          "ra.predicate": "contains_clause",
          "ra.source": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec",
          "ra.target": "Clause:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0001"
        },
        {
          "ra.clause_id": "00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0002",
          "ra.predicate": "contains_clause",
          "ra.source": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec",
          "ra.target": "Clause:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0002"
        },
        {
          "ra.clause_id": "00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0003",
          "ra.predicate": "contains_clause",
          "ra.source": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec",
          "ra.target": "Clause:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0003"
        }
      ],
      "title": "strict_all_backfill_candidates"
    }
  ]
}
```

#### Step9 推演案例集指标
来源：`00_整理记录/step9_iter1/step9_simulation_casebook.json`

```json
{
  "hotspot_analysis": {
    "high_risk_facts": [
      {
        "alt_candidates_count": 1,
        "clause_id": "f8c4fb0263c1210088bbd510f8af1d01facfaac347c1633daea0ff54339aae1d#clause_0003",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "f8c4fb0263c1210088bbd510f8af1d01facfaac347c1633daea0ff54339aae1d",
        "edge_id": "edge_07ae61fa1ec565d70d0f41f6",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_d623da637647de6e2a79",
        "target": "ParameterDefinition:pd_cd23806167ebcbb203e7"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "3c1392fd897f1d095efaa1ae2a1eaa5c0c3df313cd5a9a185aacffe05575b886#clause_0012",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "3c1392fd897f1d095efaa1ae2a1eaa5c0c3df313cd5a9a185aacffe05575b886",
        "edge_id": "edge_307bdc8cb6ee83dcb03dbf6d",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_b2f264ae7bed8d36d571",
        "target": "ParameterDefinition:pd_d450b467d74fdd325fec"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "41eed2fc03a95dc30af898124e00962d37f00dd998abb5da87c6e10e209db169#clause_0012",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "41eed2fc03a95dc30af898124e00962d37f00dd998abb5da87c6e10e209db169",
        "edge_id": "edge_30f9ebd3436108dd16e945e2",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_bb423bb678ae0743a3f8",
        "target": "ParameterDefinition:pd_d450b467d74fdd325fec"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "a90ad1a3b708e8808bab56f3ff9155d788b100ae8fd28a759d636304a9fb6b03#clause_0001",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "a90ad1a3b708e8808bab56f3ff9155d788b100ae8fd28a759d636304a9fb6b03",
        "edge_id": "edge_3641646c6190a34741a9b7ad",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:a90ad1a3b708e8808bab56f3ff9155d788b100ae8fd28a759d636304a9fb6b03",
        "target": "Mechanism:mechanism_c7fe316e00abd82c368d"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "a7f3f83cc719dbd58fa3cba1078d11a8511ace91597d326e11375e817e2d73f6#clause_0004",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "a7f3f83cc719dbd58fa3cba1078d11a8511ace91597d326e11375e817e2d73f6",
        "edge_id": "edge_394ee5b75c8cfd6d9faf2d2d",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_ea4ac3bff3dee387e95f",
        "target": "ParameterDefinition:pd_3c768eea1a4710ef1740"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "83348a380b3b3d6a053a6b89707affb993adc6db4dd70aed9d2fc76779e202b5#clause_0002",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "83348a380b3b3d6a053a6b89707affb993adc6db4dd70aed9d2fc76779e202b5",
        "edge_id": "edge_399ac6d58a034acfa88ccdbb",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_b65181ad984a4e5dfdf3",
        "target": "ParameterDefinition:pd_a6d0c9eec886340cb4ef"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "438c0392b9db32d7f7e7063819ff233da3aefc768abccbae0d8cebcf58748a29#clause_0002",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "438c0392b9db32d7f7e7063819ff233da3aefc768abccbae0d8cebcf58748a29",
        "edge_id": "edge_3aba53dfe0ea60422d1d3f16",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_31e4048a8768776a0bfb",
        "target": "ParameterDefinition:pd_a6d0c9eec886340cb4ef"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "62f668d2db29a9b35b4e6b01f6064c10ad77ad238436d5b7314a37cbf4824821#clause_0002",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "62f668d2db29a9b35b4e6b01f6064c10ad77ad238436d5b7314a37cbf4824821",
        "edge_id": "edge_42f2e6db2dc979899c22dfb8",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_350301622fb30b399168",
        "target": "ParameterDefinition:pd_a6d0c9eec886340cb4ef"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "99dce90179e84c5da237d3a228a84ba994f4c04a9a167533654c0cfcdc8d9686#clause_0004",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "99dce90179e84c5da237d3a228a84ba994f4c04a9a167533654c0cfcdc8d9686",
        "edge_id": "edge_62622300281b7b44f26ffa44",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:99dce90179e84c5da237d3a228a84ba994f4c04a9a167533654c0cfcdc8d9686",
        "target": "Mechanism:mechanism_45bce995974f7f10830e"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "ee74d273b781a2f2d3b7cdfadfe4c9a63e6e423f10874fba1e3c84a0a1f35295#clause_0001",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "ee74d273b781a2f2d3b7cdfadfe4c9a63e6e423f10874fba1e3c84a0a1f35295",
        "edge_id": "edge_6836f400b0fed4b37f26a63b",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_adf8e329fb2f48f92898",
        "target": "ParameterDefinition:pd_fb32e004e64575e6325a"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "9842b76e12450c90ad9c0680b04217082b8a8fafe2cef53d19367fc9dd8179c2#clause_0004",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "9842b76e12450c90ad9c0680b04217082b8a8fafe2cef53d19367fc9dd8179c2",
        "edge_id": "edge_769ef4fe6ecda372fddc27cf",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:9842b76e12450c90ad9c0680b04217082b8a8fafe2cef53d19367fc9dd8179c2",
        "target": "Mechanism:mechanism_96075df1132f7a533e6d"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "a63aaa1b99aae78cd58b5beb8c271e538c4b10b43ff4aff7312d6e081dd79eed#clause_0010",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "a63aaa1b99aae78cd58b5beb8c271e538c4b10b43ff4aff7312d6e081dd79eed",
        "edge_id": "edge_89f6b7e89fc71a1c5a79e303",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_2faa916caf15250492b6",
        "target": "ParameterDefinition:pd_d450b467d74fdd325fec"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "ee74d273b781a2f2d3b7cdfadfe4c9a63e6e423f10874fba1e3c84a0a1f35295#clause_0000",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "ee74d273b781a2f2d3b7cdfadfe4c9a63e6e423f10874fba1e3c84a0a1f35295",
        "edge_id": "edge_9e15b30a2ef793e73dcd114e",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_c494352133f4b2a710bb",
        "target": "ParameterDefinition:pd_17f49ddfae7c641704ef"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "6ca5d9d44b93a3440cc8f24b4feda441563e6841021017b2c5db628a6976c9f5#clause_0012",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "6ca5d9d44b93a3440cc8f24b4feda441563e6841021017b2c5db628a6976c9f5",
        "edge_id": "edge_ab7f7c174f508ee54c8be71f",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_fc9efe19aa7d7379423d",
        "target": "ParameterDefinition:pd_d450b467d74fdd325fec"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "9842b76e12450c90ad9c0680b04217082b8a8fafe2cef53d19367fc9dd8179c2#clause_0004",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "9842b76e12450c90ad9c0680b04217082b8a8fafe2cef53d19367fc9dd8179c2",
        "edge_id": "edge_ae6ab601a8357b543219ac87",
        "predicate": "clause_supports_mechanism",
        "source": "Clause:9842b76e12450c90ad9c0680b04217082b8a8fafe2cef53d19367fc9dd8179c2#clause_0004",
        "target": "Mechanism:mechanism_96075df1132f7a533e6d"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "53fc822864624a590cef5b5fa21ff00698716adde9cef0962459c0216e2b8855#clause_0020",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "53fc822864624a590cef5b5fa21ff00698716adde9cef0962459c0216e2b8855",
        "edge_id": "edge_caa91a950b5e8f29abe316d9",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_df529820b4a7e9f7c7e5",
        "target": "ParameterDefinition:pd_2e90a7f9f35c1dfe95b3"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a#clause_0012",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a",
        "edge_id": "edge_dad68d84cce986aca5b5bcec",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_6afb27fdb231ebd6e518",
        "target": "ParameterDefinition:pd_d450b467d74fdd325fec"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "99dce90179e84c5da237d3a228a84ba994f4c04a9a167533654c0cfcdc8d9686#clause_0004",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "99dce90179e84c5da237d3a228a84ba994f4c04a9a167533654c0cfcdc8d9686",
        "edge_id": "edge_e37bf52ed70eef608619fdcd",
        "predicate": "clause_supports_mechanism",
        "source": "Clause:99dce90179e84c5da237d3a228a84ba994f4c04a9a167533654c0cfcdc8d9686#clause_0004",
        "target": "Mechanism:mechanism_45bce995974f7f10830e"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "c87c6c303d4ebe0bce627bed2792bac1dd9e89ad192d23b7144aa9570705b240#clause_0002",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "c87c6c303d4ebe0bce627bed2792bac1dd9e89ad192d23b7144aa9570705b240",
        "edge_id": "edge_e800f8eb7270f16c0c5c82bb",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_35e61ca458ea66ceba0d",
        "target": "ParameterDefinition:pd_a6d0c9eec886340cb4ef"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "a90ad1a3b708e8808bab56f3ff9155d788b100ae8fd28a759d636304a9fb6b03#clause_0001",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "a90ad1a3b708e8808bab56f3ff9155d788b100ae8fd28a759d636304a9fb6b03",
        "edge_id": "edge_f3e65004b40f57efb7ba5708",
        "predicate": "clause_supports_mechanism",
        "source": "Clause:a90ad1a3b708e8808bab56f3ff9155d788b100ae8fd28a759d636304a9fb6b03#clause_0001",
        "target": "Mechanism:mechanism_c7fe316e00abd82c368d"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "2c6f8bdce8c0c7967763bb1bf530c46fe6bbfac7bab4a3c48d3256ace950b987#clause_0000",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "2c6f8bdce8c0c7967763bb1bf530c46fe6bbfac7bab4a3c48d3256ace950b987",
        "edge_id": "edge_f478b6b85554fea083d0d249",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_582ecd80347043d92cb5",
        "target": "ParameterDefinition:pd_12edcd4a409324f6bec0"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "bd9a5debe3e285290408196ff9a61cc7d1acd325eab100746bcd7562b196b7dd#clause_0002",
        "conflict_count": 1,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "bd9a5debe3e285290408196ff9a61cc7d1acd325eab100746bcd7562b196b7dd",
        "edge_id": "edge_ffd9b7c635057b3ea5ef4111",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_a65ebf625b34d8993a85",
        "target": "ParameterDefinition:pd_a6d0c9eec886340cb4ef"
      },
      {
        "alt_candidates_count": 2,
        "clause_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba#clause_0001",
        "conflict_count": 0,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba",
        "edge_id": "edge_00664f7fc3f2575327ed9a2c",
        "predicate": "clause_has_parameter_mention",
        "source": "Clause:22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba#clause_0001",
        "target": "ParameterMention:pm_0315761daf6f233f4c1f"
      },
      {
        "alt_candidates_count": 2,
        "clause_id": "0de53d8f7a3a1c2de8a8ce98c12216d63084f7e235dd8ddcc02f07760d36a17a#clause_0026",
        "conflict_count": 0,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "0de53d8f7a3a1c2de8a8ce98c12216d63084f7e235dd8ddcc02f07760d36a17a",
        "edge_id": "edge_00c5ecd5ed82ff403ddc5442",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_6dc8302dcb64a0639fec",
        "target": "ParameterDefinition:pd_69697f57149656ea0675"
      },
      {
        "alt_candidates_count": 2,
        "clause_id": "dc812e8b13d03ff73b79b4b814a56ec987458e2b4ac3147020283904460efdc9#clause_0003",
        "conflict_count": 0,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "dc812e8b13d03ff73b79b4b814a56ec987458e2b4ac3147020283904460efdc9",
        "edge_id": "edge_0149a5e3a02f5f16b743b637",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_94a39e061f9d692f7fe1",
        "target": "ParameterDefinition:pd_dd6d2ad3219f5053e698"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "60a8d6c66d757ef90db55edf809fb9816c710a1021f9df39aba80b9949b9a6f7#clause_0002",
        "conflict_count": 0,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "60a8d6c66d757ef90db55edf809fb9816c710a1021f9df39aba80b9949b9a6f7",
        "edge_id": "edge_01e723296af50045d920c24f",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_c1af81c8290dc353e2ab",
        "target": "ParameterDefinition:pd_2e90a7f9f35c1dfe95b3"
      },
      {
        "alt_candidates_count": 2,
        "clause_id": "e15bd62111869ef28d319c4782660d56e7d6f9284bf4198ae86a54d79d2940fe#clause_0001",
        "conflict_count": 0,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "e15bd62111869ef28d319c4782660d56e7d6f9284bf4198ae86a54d79d2940fe",
        "edge_id": "edge_023bfbf578a00aab70e41cc6",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_fcc16d42aa6946a12da4",
        "target": "ParameterDefinition:pd_36fd38a8d61bb10b6678"
      },
      {
        "alt_candidates_count": 1,
        "clause_id": "dc812e8b13d03ff73b79b4b814a56ec987458e2b4ac3147020283904460efdc9#clause_0001",
        "conflict_count": 0,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "dc812e8b13d03ff73b79b4b814a56ec987458e2b4ac3147020283904460efdc9",
        "edge_id": "edge_02551b6f50c6ce177ed8ae7a",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_09b7d28037f2cd80c617",
        "target": "ParameterDefinition:pd_f20d2c19e6c6335b388c"
      },
      {
        "alt_candidates_count": 2,
        "clause_id": "cc7addf8ff4efe3409afac8915cc6b8df3283617d08af2da6658e58933736301#clause_0003",
        "conflict_count": 0,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "cc7addf8ff4efe3409afac8915cc6b8df3283617d08af2da6658e58933736301",
        "edge_id": "edge_02824120d1e2f8997568ac78",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_1cbaef9a4c85f0cae388",
        "target": "ParameterDefinition:pd_f22ac6dcf9e5399410f2"
      },
      {
        "alt_candidates_count": 2,
        "clause_id": "231f1eeb573e2b351f92117ef696b8d2077cec456aacd516232f031d673da137#clause_0001",
        "conflict_count": 0,
        "conflict_type": "semantic_collision",
        "doc_instance_id": "231f1eeb573e2b351f92117ef696b8d2077cec456aacd516232f031d673da137",
        "edge_id": "edge_02a80906bce8229938886d1f",
        "predicate": "mechanism_has_parameter_definition",
        "source": "Mechanism:mechanism_b0521b5a46cdb8cf2611",
        "target": "ParameterDefinition:pd_d6d3b01a6f2108d1889d"
      }
    ],
    "strict_all_backfill_candidates_preview": [
      {
        "clause_id": "00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0001",
        "predicate": "contains_clause",
        "source": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec",
        "target": "Clause:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0001",
        "unit": null
      },
      {
        "clause_id": "00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec",
        "target": "Clause:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0002",
        "unit": null
      },
      {
        "clause_id": "00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec",
        "target": "Clause:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0003",
        "unit": null
      },
      {
        "clause_id": "00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec",
        "target": "Clause:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0004",
        "unit": null
      },
      {
        "clause_id": "010dd88159617e9e9382aae1b693db97e9b9aa123fefe31ae3a1ceeca57bb8d5#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:010dd88159617e9e9382aae1b693db97e9b9aa123fefe31ae3a1ceeca57bb8d5",
        "target": "Clause:010dd88159617e9e9382aae1b693db97e9b9aa123fefe31ae3a1ceeca57bb8d5#clause_0004",
        "unit": null
      },
      {
        "clause_id": "0d4df7638a86e161686866b0b8ac4efc520827097e76902f88d922c41e699999#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:0d4df7638a86e161686866b0b8ac4efc520827097e76902f88d922c41e699999",
        "target": "Clause:0d4df7638a86e161686866b0b8ac4efc520827097e76902f88d922c41e699999#clause_0003",
        "unit": null
      },
      {
        "clause_id": "0de53d8f7a3a1c2de8a8ce98c12216d63084f7e235dd8ddcc02f07760d36a17a#clause_0000",
        "predicate": "contains_clause",
        "source": "PolicyDocument:0de53d8f7a3a1c2de8a8ce98c12216d63084f7e235dd8ddcc02f07760d36a17a",
        "target": "Clause:0de53d8f7a3a1c2de8a8ce98c12216d63084f7e235dd8ddcc02f07760d36a17a#clause_0000",
        "unit": null
      },
      {
        "clause_id": "0ef7089f429ca4377a5b92c9f7a419ffcb4a3102d8d0ac5666c9f1bfef4ba625#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:0ef7089f429ca4377a5b92c9f7a419ffcb4a3102d8d0ac5666c9f1bfef4ba625",
        "target": "Clause:0ef7089f429ca4377a5b92c9f7a419ffcb4a3102d8d0ac5666c9f1bfef4ba625#clause_0002",
        "unit": null
      },
      {
        "clause_id": "0f3400361f4f38388365c57c706fc464f0fa6aee962bdb434173380878f8c94b#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:0f3400361f4f38388365c57c706fc464f0fa6aee962bdb434173380878f8c94b",
        "target": "Clause:0f3400361f4f38388365c57c706fc464f0fa6aee962bdb434173380878f8c94b#clause_0002",
        "unit": null
      },
      {
        "clause_id": "10695560c26cc67b7a3e26b8dbcd7b856b0b17ef49c31ba529efd3caf059a1de#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:10695560c26cc67b7a3e26b8dbcd7b856b0b17ef49c31ba529efd3caf059a1de",
        "target": "Clause:10695560c26cc67b7a3e26b8dbcd7b856b0b17ef49c31ba529efd3caf059a1de#clause_0002",
        "unit": null
      },
      {
        "clause_id": "13677b49d0d053be96bfcd32cd36eeba7c68f125c6f32cc220322ba98c178bf4#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:13677b49d0d053be96bfcd32cd36eeba7c68f125c6f32cc220322ba98c178bf4",
        "target": "Clause:13677b49d0d053be96bfcd32cd36eeba7c68f125c6f32cc220322ba98c178bf4#clause_0003",
        "unit": null
      },
      {
        "clause_id": "13677b49d0d053be96bfcd32cd36eeba7c68f125c6f32cc220322ba98c178bf4#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:13677b49d0d053be96bfcd32cd36eeba7c68f125c6f32cc220322ba98c178bf4",
        "target": "Clause:13677b49d0d053be96bfcd32cd36eeba7c68f125c6f32cc220322ba98c178bf4#clause_0004",
        "unit": null
      },
      {
        "clause_id": "13677b49d0d053be96bfcd32cd36eeba7c68f125c6f32cc220322ba98c178bf4#clause_0005",
        "predicate": "contains_clause",
        "source": "PolicyDocument:13677b49d0d053be96bfcd32cd36eeba7c68f125c6f32cc220322ba98c178bf4",
        "target": "Clause:13677b49d0d053be96bfcd32cd36eeba7c68f125c6f32cc220322ba98c178bf4#clause_0005",
        "unit": null
      },
      {
        "clause_id": "13677b49d0d053be96bfcd32cd36eeba7c68f125c6f32cc220322ba98c178bf4#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:13677b49d0d053be96bfcd32cd36eeba7c68f125c6f32cc220322ba98c178bf4",
        "target": "Clause:13677b49d0d053be96bfcd32cd36eeba7c68f125c6f32cc220322ba98c178bf4#clause_0006",
        "unit": null
      },
      {
        "clause_id": "1be33bff3ea2876b31bbd3f23c81aa44573ad1f2de6cfb2cd7d649a3ebd1028d#clause_0008",
        "predicate": "contains_clause",
        "source": "PolicyDocument:1be33bff3ea2876b31bbd3f23c81aa44573ad1f2de6cfb2cd7d649a3ebd1028d",
        "target": "Clause:1be33bff3ea2876b31bbd3f23c81aa44573ad1f2de6cfb2cd7d649a3ebd1028d#clause_0008",
        "unit": null
      },
      {
        "clause_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba",
        "target": "Clause:22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba#clause_0003",
        "unit": null
      },
      {
        "clause_id": "264f74e1e9077c0e94590da482db92ebc125f4c14559852d89ad14b209d7e41f#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:264f74e1e9077c0e94590da482db92ebc125f4c14559852d89ad14b209d7e41f",
        "target": "Clause:264f74e1e9077c0e94590da482db92ebc125f4c14559852d89ad14b209d7e41f#clause_0006",
        "unit": null
      },
      {
        "clause_id": "2a1a7ca09fde9e1e09c537a13a8c19be802c349c78fec60b60b126242522ccdc#clause_0000",
        "predicate": "contains_clause",
        "source": "PolicyDocument:2a1a7ca09fde9e1e09c537a13a8c19be802c349c78fec60b60b126242522ccdc",
        "target": "Clause:2a1a7ca09fde9e1e09c537a13a8c19be802c349c78fec60b60b126242522ccdc#clause_0000",
        "unit": null
      },
      {
        "clause_id": "2f9184a72b1488e94b2de32d7d9489e5d523b09268cd7142f059723054a93828#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:2f9184a72b1488e94b2de32d7d9489e5d523b09268cd7142f059723054a93828",
        "target": "Clause:2f9184a72b1488e94b2de32d7d9489e5d523b09268cd7142f059723054a93828#clause_0003",
        "unit": null
      },
      {
        "clause_id": "34de2093bea75d704c113e23bf49b9018637efa1841e90bf224a6566684fd8df#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:34de2093bea75d704c113e23bf49b9018637efa1841e90bf224a6566684fd8df",
        "target": "Clause:34de2093bea75d704c113e23bf49b9018637efa1841e90bf224a6566684fd8df#clause_0003",
        "unit": null
      },
      {
        "clause_id": "3991fbb237169347871b06ab54a5fa6484949f06838d537bedebcccd7d1380b8#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:3991fbb237169347871b06ab54a5fa6484949f06838d537bedebcccd7d1380b8",
        "target": "Clause:3991fbb237169347871b06ab54a5fa6484949f06838d537bedebcccd7d1380b8#clause_0004",
        "unit": null
      },
      {
        "clause_id": "3d453b46781e992f20c2a7120846ab15062f4e272266f310b85e96ae17b26383#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:3d453b46781e992f20c2a7120846ab15062f4e272266f310b85e96ae17b26383",
        "target": "Clause:3d453b46781e992f20c2a7120846ab15062f4e272266f310b85e96ae17b26383#clause_0006",
        "unit": null
      },
      {
        "clause_id": "3fd79998d4631ca6e3407dfaacd9b7e9186fa2e143618d0740ab46f0a9063745#clause_0000",
        "predicate": "contains_clause",
        "source": "PolicyDocument:3fd79998d4631ca6e3407dfaacd9b7e9186fa2e143618d0740ab46f0a9063745",
        "target": "Clause:3fd79998d4631ca6e3407dfaacd9b7e9186fa2e143618d0740ab46f0a9063745#clause_0000",
        "unit": null
      },
      {
        "clause_id": "40eaa271256c3f5b89ddb8760613b6fabdcf0efb295059429c972a9d9abc394a#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:40eaa271256c3f5b89ddb8760613b6fabdcf0efb295059429c972a9d9abc394a",
        "target": "Clause:40eaa271256c3f5b89ddb8760613b6fabdcf0efb295059429c972a9d9abc394a#clause_0002",
        "unit": null
      },
      {
        "clause_id": "432528cbb25bdbdce8825781b81c73beb96a63f824057f93f5800fc0a512a713#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:432528cbb25bdbdce8825781b81c73beb96a63f824057f93f5800fc0a512a713",
        "target": "Clause:432528cbb25bdbdce8825781b81c73beb96a63f824057f93f5800fc0a512a713#clause_0002",
        "unit": null
      },
      {
        "clause_id": "438c0392b9db32d7f7e7063819ff233da3aefc768abccbae0d8cebcf58748a29#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:438c0392b9db32d7f7e7063819ff233da3aefc768abccbae0d8cebcf58748a29",
        "target": "Clause:438c0392b9db32d7f7e7063819ff233da3aefc768abccbae0d8cebcf58748a29#clause_0006",
        "unit": null
      },
      {
        "clause_id": "4978300e5965b0d812a67eb9a07c584011b661c940c300faf4990fb8586e3a13#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:4978300e5965b0d812a67eb9a07c584011b661c940c300faf4990fb8586e3a13",
        "target": "Clause:4978300e5965b0d812a67eb9a07c584011b661c940c300faf4990fb8586e3a13#clause_0002",
        "unit": null
      },
      {
        "clause_id": "4978300e5965b0d812a67eb9a07c584011b661c940c300faf4990fb8586e3a13#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:4978300e5965b0d812a67eb9a07c584011b661c940c300faf4990fb8586e3a13",
        "target": "Clause:4978300e5965b0d812a67eb9a07c584011b661c940c300faf4990fb8586e3a13#clause_0003",
        "unit": null
      },
      {
        "clause_id": "4978300e5965b0d812a67eb9a07c584011b661c940c300faf4990fb8586e3a13#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:4978300e5965b0d812a67eb9a07c584011b661c940c300faf4990fb8586e3a13",
        "target": "Clause:4978300e5965b0d812a67eb9a07c584011b661c940c300faf4990fb8586e3a13#clause_0004",
        "unit": null
      },
      {
        "clause_id": "4978300e5965b0d812a67eb9a07c584011b661c940c300faf4990fb8586e3a13#clause_0005",
        "predicate": "contains_clause",
        "source": "PolicyDocument:4978300e5965b0d812a67eb9a07c584011b661c940c300faf4990fb8586e3a13",
        "target": "Clause:4978300e5965b0d812a67eb9a07c584011b661c940c300faf4990fb8586e3a13#clause_0005",
        "unit": null
      },
      {
        "clause_id": "509a0ad904c063d5cf05fca6cbf14e771fafd94288045c9c2d767dc19ec43ab5#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:509a0ad904c063d5cf05fca6cbf14e771fafd94288045c9c2d767dc19ec43ab5",
        "target": "Clause:509a0ad904c063d5cf05fca6cbf14e771fafd94288045c9c2d767dc19ec43ab5#clause_0002",
        "unit": null
      },
      {
        "clause_id": "53fc822864624a590cef5b5fa21ff00698716adde9cef0962459c0216e2b8855#clause_0009",
        "predicate": "contains_clause",
        "source": "PolicyDocument:53fc822864624a590cef5b5fa21ff00698716adde9cef0962459c0216e2b8855",
        "target": "Clause:53fc822864624a590cef5b5fa21ff00698716adde9cef0962459c0216e2b8855#clause_0009",
        "unit": null
      },
      {
        "clause_id": "53fc822864624a590cef5b5fa21ff00698716adde9cef0962459c0216e2b8855#clause_0013",
        "predicate": "contains_clause",
        "source": "PolicyDocument:53fc822864624a590cef5b5fa21ff00698716adde9cef0962459c0216e2b8855",
        "target": "Clause:53fc822864624a590cef5b5fa21ff00698716adde9cef0962459c0216e2b8855#clause_0013",
        "unit": null
      },
      {
        "clause_id": "53fc822864624a590cef5b5fa21ff00698716adde9cef0962459c0216e2b8855#clause_0016",
        "predicate": "contains_clause",
        "source": "PolicyDocument:53fc822864624a590cef5b5fa21ff00698716adde9cef0962459c0216e2b8855",
        "target": "Clause:53fc822864624a590cef5b5fa21ff00698716adde9cef0962459c0216e2b8855#clause_0016",
        "unit": null
      },
      {
        "clause_id": "55486d5eaf1202de357651355eea469df92d887e1b388dd7c1a3fcd9b75286cb#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:55486d5eaf1202de357651355eea469df92d887e1b388dd7c1a3fcd9b75286cb",
        "target": "Clause:55486d5eaf1202de357651355eea469df92d887e1b388dd7c1a3fcd9b75286cb#clause_0002",
        "unit": null
      },
      {
        "clause_id": "55486d5eaf1202de357651355eea469df92d887e1b388dd7c1a3fcd9b75286cb#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:55486d5eaf1202de357651355eea469df92d887e1b388dd7c1a3fcd9b75286cb",
        "target": "Clause:55486d5eaf1202de357651355eea469df92d887e1b388dd7c1a3fcd9b75286cb#clause_0003",
        "unit": null
      },
      {
        "clause_id": "55486d5eaf1202de357651355eea469df92d887e1b388dd7c1a3fcd9b75286cb#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:55486d5eaf1202de357651355eea469df92d887e1b388dd7c1a3fcd9b75286cb",
        "target": "Clause:55486d5eaf1202de357651355eea469df92d887e1b388dd7c1a3fcd9b75286cb#clause_0004",
        "unit": null
      },
      {
        "clause_id": "55486d5eaf1202de357651355eea469df92d887e1b388dd7c1a3fcd9b75286cb#clause_0005",
        "predicate": "contains_clause",
        "source": "PolicyDocument:55486d5eaf1202de357651355eea469df92d887e1b388dd7c1a3fcd9b75286cb",
        "target": "Clause:55486d5eaf1202de357651355eea469df92d887e1b388dd7c1a3fcd9b75286cb#clause_0005",
        "unit": null
      },
      {
        "clause_id": "56a73d05dcfd76555b7fe12d90d1696b709acf1556a8913f3314c3c6c644cfb5#clause_0000",
        "predicate": "contains_clause",
        "source": "PolicyDocument:56a73d05dcfd76555b7fe12d90d1696b709acf1556a8913f3314c3c6c644cfb5",
        "target": "Clause:56a73d05dcfd76555b7fe12d90d1696b709acf1556a8913f3314c3c6c644cfb5#clause_0000",
        "unit": null
      },
      {
        "clause_id": "59fb420eead4837faf2f90b58927c9c874cd61e9cfbcb91d127cfeeb50f5be76#clause_0001",
        "predicate": "contains_clause",
        "source": "PolicyDocument:59fb420eead4837faf2f90b58927c9c874cd61e9cfbcb91d127cfeeb50f5be76",
        "target": "Clause:59fb420eead4837faf2f90b58927c9c874cd61e9cfbcb91d127cfeeb50f5be76#clause_0001",
        "unit": null
      },
      {
        "clause_id": "59fb420eead4837faf2f90b58927c9c874cd61e9cfbcb91d127cfeeb50f5be76#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:59fb420eead4837faf2f90b58927c9c874cd61e9cfbcb91d127cfeeb50f5be76",
        "target": "Clause:59fb420eead4837faf2f90b58927c9c874cd61e9cfbcb91d127cfeeb50f5be76#clause_0002",
        "unit": null
      },
      {
        "clause_id": "59fb420eead4837faf2f90b58927c9c874cd61e9cfbcb91d127cfeeb50f5be76#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:59fb420eead4837faf2f90b58927c9c874cd61e9cfbcb91d127cfeeb50f5be76",
        "target": "Clause:59fb420eead4837faf2f90b58927c9c874cd61e9cfbcb91d127cfeeb50f5be76#clause_0003",
        "unit": null
      },
      {
        "clause_id": "59fb420eead4837faf2f90b58927c9c874cd61e9cfbcb91d127cfeeb50f5be76#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:59fb420eead4837faf2f90b58927c9c874cd61e9cfbcb91d127cfeeb50f5be76",
        "target": "Clause:59fb420eead4837faf2f90b58927c9c874cd61e9cfbcb91d127cfeeb50f5be76#clause_0004",
        "unit": null
      },
      {
        "clause_id": "62f668d2db29a9b35b4e6b01f6064c10ad77ad238436d5b7314a37cbf4824821#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:62f668d2db29a9b35b4e6b01f6064c10ad77ad238436d5b7314a37cbf4824821",
        "target": "Clause:62f668d2db29a9b35b4e6b01f6064c10ad77ad238436d5b7314a37cbf4824821#clause_0006",
        "unit": null
      },
      {
        "clause_id": "632c503920a67e010e21ba8cc1bfddfd101d9f4a5981b038ab8e365c65c57b08#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:632c503920a67e010e21ba8cc1bfddfd101d9f4a5981b038ab8e365c65c57b08",
        "target": "Clause:632c503920a67e010e21ba8cc1bfddfd101d9f4a5981b038ab8e365c65c57b08#clause_0004",
        "unit": null
      },
      {
        "clause_id": "635192af8baf11262c4e886f015d6f452a5241a0a6d153db4c730e4108cbf7f3#clause_0000",
        "predicate": "contains_clause",
        "source": "PolicyDocument:635192af8baf11262c4e886f015d6f452a5241a0a6d153db4c730e4108cbf7f3",
        "target": "Clause:635192af8baf11262c4e886f015d6f452a5241a0a6d153db4c730e4108cbf7f3#clause_0000",
        "unit": null
      },
      {
        "clause_id": "68cf8b47055553fd101877102c4de7301c148b4dfe2101a20a960809ffb02d3e#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:68cf8b47055553fd101877102c4de7301c148b4dfe2101a20a960809ffb02d3e",
        "target": "Clause:68cf8b47055553fd101877102c4de7301c148b4dfe2101a20a960809ffb02d3e#clause_0006",
        "unit": null
      },
      {
        "clause_id": "7b751605b49132dd141591500721a0a0aeef9413b412efd887a6985a4ada323a#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:7b751605b49132dd141591500721a0a0aeef9413b412efd887a6985a4ada323a",
        "target": "Clause:7b751605b49132dd141591500721a0a0aeef9413b412efd887a6985a4ada323a#clause_0003",
        "unit": null
      },
      {
        "clause_id": "7e1dff3ee78977bc7e5f87b686fc7b8ccf4f78bd15144d2fd3f7c60c48ec3209#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:7e1dff3ee78977bc7e5f87b686fc7b8ccf4f78bd15144d2fd3f7c60c48ec3209",
        "target": "Clause:7e1dff3ee78977bc7e5f87b686fc7b8ccf4f78bd15144d2fd3f7c60c48ec3209#clause_0006",
        "unit": null
      },
      {
        "clause_id": "7f64d12d77538daeb634de40f7634de40d034d5512fa29948f5af09d83039026#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:7f64d12d77538daeb634de40f7634de40d034d5512fa29948f5af09d83039026",
        "target": "Clause:7f64d12d77538daeb634de40f7634de40d034d5512fa29948f5af09d83039026#clause_0002",
        "unit": null
      },
      {
        "clause_id": "819c31e2886f7e8adcaade88373bb32f7768902a56246226666f0aeddd11bb1b#clause_0001",
        "predicate": "contains_clause",
        "source": "PolicyDocument:819c31e2886f7e8adcaade88373bb32f7768902a56246226666f0aeddd11bb1b",
        "target": "Clause:819c31e2886f7e8adcaade88373bb32f7768902a56246226666f0aeddd11bb1b#clause_0001",
        "unit": null
      },
      {
        "clause_id": "83348a380b3b3d6a053a6b89707affb993adc6db4dd70aed9d2fc76779e202b5#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:83348a380b3b3d6a053a6b89707affb993adc6db4dd70aed9d2fc76779e202b5",
        "target": "Clause:83348a380b3b3d6a053a6b89707affb993adc6db4dd70aed9d2fc76779e202b5#clause_0006",
        "unit": null
      },
      {
        "clause_id": "85f4b58cc76ff64db857d8c4b587b2d911ae13a29f7c836d636ef07c2efd6e24#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:85f4b58cc76ff64db857d8c4b587b2d911ae13a29f7c836d636ef07c2efd6e24",
        "target": "Clause:85f4b58cc76ff64db857d8c4b587b2d911ae13a29f7c836d636ef07c2efd6e24#clause_0004",
        "unit": null
      },
      {
        "clause_id": "881491ec6e32e0e2abc98ea7df793609e0167cc5202791da22a326af5e787a2c#clause_0005",
        "predicate": "contains_clause",
        "source": "PolicyDocument:881491ec6e32e0e2abc98ea7df793609e0167cc5202791da22a326af5e787a2c",
        "target": "Clause:881491ec6e32e0e2abc98ea7df793609e0167cc5202791da22a326af5e787a2c#clause_0005",
        "unit": null
      },
      {
        "clause_id": "88741f01ecfe3abf37bb1d0d44c17bad4304be617de9deefdeb893a60fd9290e#clause_0012",
        "predicate": "contains_clause",
        "source": "PolicyDocument:88741f01ecfe3abf37bb1d0d44c17bad4304be617de9deefdeb893a60fd9290e",
        "target": "Clause:88741f01ecfe3abf37bb1d0d44c17bad4304be617de9deefdeb893a60fd9290e#clause_0012",
        "unit": null
      },
      {
        "clause_id": "9634a7cefdb8a7018741e8ef683bb7b815f1dbc1d60d42350574f3dd240e55b7#clause_0001",
        "predicate": "contains_clause",
        "source": "PolicyDocument:9634a7cefdb8a7018741e8ef683bb7b815f1dbc1d60d42350574f3dd240e55b7",
        "target": "Clause:9634a7cefdb8a7018741e8ef683bb7b815f1dbc1d60d42350574f3dd240e55b7#clause_0001",
        "unit": null
      },
      {
        "clause_id": "9634a7cefdb8a7018741e8ef683bb7b815f1dbc1d60d42350574f3dd240e55b7#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:9634a7cefdb8a7018741e8ef683bb7b815f1dbc1d60d42350574f3dd240e55b7",
        "target": "Clause:9634a7cefdb8a7018741e8ef683bb7b815f1dbc1d60d42350574f3dd240e55b7#clause_0002",
        "unit": null
      },
      {
        "clause_id": "9634a7cefdb8a7018741e8ef683bb7b815f1dbc1d60d42350574f3dd240e55b7#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:9634a7cefdb8a7018741e8ef683bb7b815f1dbc1d60d42350574f3dd240e55b7",
        "target": "Clause:9634a7cefdb8a7018741e8ef683bb7b815f1dbc1d60d42350574f3dd240e55b7#clause_0003",
        "unit": null
      },
      {
        "clause_id": "9634a7cefdb8a7018741e8ef683bb7b815f1dbc1d60d42350574f3dd240e55b7#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:9634a7cefdb8a7018741e8ef683bb7b815f1dbc1d60d42350574f3dd240e55b7",
        "target": "Clause:9634a7cefdb8a7018741e8ef683bb7b815f1dbc1d60d42350574f3dd240e55b7#clause_0004",
        "unit": null
      },
      {
        "clause_id": "9842b76e12450c90ad9c0680b04217082b8a8fafe2cef53d19367fc9dd8179c2#clause_0001",
        "predicate": "contains_clause",
        "source": "PolicyDocument:9842b76e12450c90ad9c0680b04217082b8a8fafe2cef53d19367fc9dd8179c2",
        "target": "Clause:9842b76e12450c90ad9c0680b04217082b8a8fafe2cef53d19367fc9dd8179c2#clause_0001",
        "unit": null
      },
      {
        "clause_id": "99dce90179e84c5da237d3a228a84ba994f4c04a9a167533654c0cfcdc8d9686#clause_0001",
        "predicate": "contains_clause",
        "source": "PolicyDocument:99dce90179e84c5da237d3a228a84ba994f4c04a9a167533654c0cfcdc8d9686",
        "target": "Clause:99dce90179e84c5da237d3a228a84ba994f4c04a9a167533654c0cfcdc8d9686#clause_0001",
        "unit": null
      },
      {
        "clause_id": "9c3afee7cca39cb92c7272cf554cc02fdb162ec89bc92c98f6324cf2bb423c92#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:9c3afee7cca39cb92c7272cf554cc02fdb162ec89bc92c98f6324cf2bb423c92",
        "target": "Clause:9c3afee7cca39cb92c7272cf554cc02fdb162ec89bc92c98f6324cf2bb423c92#clause_0002",
        "unit": null
      },
      {
        "clause_id": "a841fd40884f65693f42fff950340f5c6e1dbdd734f6cb20bc5e15c9bbf474ec#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:a841fd40884f65693f42fff950340f5c6e1dbdd734f6cb20bc5e15c9bbf474ec",
        "target": "Clause:a841fd40884f65693f42fff950340f5c6e1dbdd734f6cb20bc5e15c9bbf474ec#clause_0003",
        "unit": null
      },
      {
        "clause_id": "ad67c3fdaa5a26925e5e3474443bab3a8b1737e94937ccbe115cabd74e2fc9a0#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:ad67c3fdaa5a26925e5e3474443bab3a8b1737e94937ccbe115cabd74e2fc9a0",
        "target": "Clause:ad67c3fdaa5a26925e5e3474443bab3a8b1737e94937ccbe115cabd74e2fc9a0#clause_0004",
        "unit": null
      },
      {
        "clause_id": "b271f30c7c5bbb7895cc6deb831772df2106e756fd6d2f0fa32695d59dba3cda#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:b271f30c7c5bbb7895cc6deb831772df2106e756fd6d2f0fa32695d59dba3cda",
        "target": "Clause:b271f30c7c5bbb7895cc6deb831772df2106e756fd6d2f0fa32695d59dba3cda#clause_0003",
        "unit": null
      },
      {
        "clause_id": "bd73b5413d3142d68aeb1a0da4a43352c8e1b26d5db0852155778c681c7a2aa4#clause_0009",
        "predicate": "contains_clause",
        "source": "PolicyDocument:bd73b5413d3142d68aeb1a0da4a43352c8e1b26d5db0852155778c681c7a2aa4",
        "target": "Clause:bd73b5413d3142d68aeb1a0da4a43352c8e1b26d5db0852155778c681c7a2aa4#clause_0009",
        "unit": null
      },
      {
        "clause_id": "bd9a5debe3e285290408196ff9a61cc7d1acd325eab100746bcd7562b196b7dd#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:bd9a5debe3e285290408196ff9a61cc7d1acd325eab100746bcd7562b196b7dd",
        "target": "Clause:bd9a5debe3e285290408196ff9a61cc7d1acd325eab100746bcd7562b196b7dd#clause_0006",
        "unit": null
      },
      {
        "clause_id": "c87c6c303d4ebe0bce627bed2792bac1dd9e89ad192d23b7144aa9570705b240#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:c87c6c303d4ebe0bce627bed2792bac1dd9e89ad192d23b7144aa9570705b240",
        "target": "Clause:c87c6c303d4ebe0bce627bed2792bac1dd9e89ad192d23b7144aa9570705b240#clause_0006",
        "unit": null
      },
      {
        "clause_id": "ca0ecafa5d9b0881a307250ed1dfb3f239da064ec327235d5f6bf4b0afde27d8#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:ca0ecafa5d9b0881a307250ed1dfb3f239da064ec327235d5f6bf4b0afde27d8",
        "target": "Clause:ca0ecafa5d9b0881a307250ed1dfb3f239da064ec327235d5f6bf4b0afde27d8#clause_0003",
        "unit": null
      },
      {
        "clause_id": "cabe05c4dbda50ec49c95f7660116adc6893472b4c0d161d06711a5647f6c00f#clause_0000",
        "predicate": "contains_clause",
        "source": "PolicyDocument:cabe05c4dbda50ec49c95f7660116adc6893472b4c0d161d06711a5647f6c00f",
        "target": "Clause:cabe05c4dbda50ec49c95f7660116adc6893472b4c0d161d06711a5647f6c00f#clause_0000",
        "unit": null
      },
      {
        "clause_id": "cfc5659b83ee4ad1d1f2661e5333bd1e0c3dd1876428b74b183b3a6d310c4184#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:cfc5659b83ee4ad1d1f2661e5333bd1e0c3dd1876428b74b183b3a6d310c4184",
        "target": "Clause:cfc5659b83ee4ad1d1f2661e5333bd1e0c3dd1876428b74b183b3a6d310c4184#clause_0006",
        "unit": null
      },
      {
        "clause_id": "d093bca3315576388f93648eb80178c1d6231b42de0de86db5ead37b5950bf2c#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:d093bca3315576388f93648eb80178c1d6231b42de0de86db5ead37b5950bf2c",
        "target": "Clause:d093bca3315576388f93648eb80178c1d6231b42de0de86db5ead37b5950bf2c#clause_0006",
        "unit": null
      },
      {
        "clause_id": "d30af01520d50ba7d996b79b99121ed0cc0e9b34bb66761144c9c1d2f0cd1ba5#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:d30af01520d50ba7d996b79b99121ed0cc0e9b34bb66761144c9c1d2f0cd1ba5",
        "target": "Clause:d30af01520d50ba7d996b79b99121ed0cc0e9b34bb66761144c9c1d2f0cd1ba5#clause_0006",
        "unit": null
      },
      {
        "clause_id": "d6295fc6d120b2f270803869f63327efa8f7e3ea98515eb80da25abd977ff9f6#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:d6295fc6d120b2f270803869f63327efa8f7e3ea98515eb80da25abd977ff9f6",
        "target": "Clause:d6295fc6d120b2f270803869f63327efa8f7e3ea98515eb80da25abd977ff9f6#clause_0002",
        "unit": null
      },
      {
        "clause_id": "d6295fc6d120b2f270803869f63327efa8f7e3ea98515eb80da25abd977ff9f6#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:d6295fc6d120b2f270803869f63327efa8f7e3ea98515eb80da25abd977ff9f6",
        "target": "Clause:d6295fc6d120b2f270803869f63327efa8f7e3ea98515eb80da25abd977ff9f6#clause_0003",
        "unit": null
      },
      {
        "clause_id": "d6295fc6d120b2f270803869f63327efa8f7e3ea98515eb80da25abd977ff9f6#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:d6295fc6d120b2f270803869f63327efa8f7e3ea98515eb80da25abd977ff9f6",
        "target": "Clause:d6295fc6d120b2f270803869f63327efa8f7e3ea98515eb80da25abd977ff9f6#clause_0004",
        "unit": null
      },
      {
        "clause_id": "d6295fc6d120b2f270803869f63327efa8f7e3ea98515eb80da25abd977ff9f6#clause_0005",
        "predicate": "contains_clause",
        "source": "PolicyDocument:d6295fc6d120b2f270803869f63327efa8f7e3ea98515eb80da25abd977ff9f6",
        "target": "Clause:d6295fc6d120b2f270803869f63327efa8f7e3ea98515eb80da25abd977ff9f6#clause_0005",
        "unit": null
      },
      {
        "clause_id": "eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3",
        "target": "Clause:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0002",
        "unit": null
      },
      {
        "clause_id": "eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3",
        "target": "Clause:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0003",
        "unit": null
      },
      {
        "clause_id": "eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3",
        "target": "Clause:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0004",
        "unit": null
      },
      {
        "clause_id": "eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0006",
        "predicate": "contains_clause",
        "source": "PolicyDocument:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3",
        "target": "Clause:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0006",
        "unit": null
      },
      {
        "clause_id": "eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0007",
        "predicate": "contains_clause",
        "source": "PolicyDocument:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3",
        "target": "Clause:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0007",
        "unit": null
      },
      {
        "clause_id": "eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0008",
        "predicate": "contains_clause",
        "source": "PolicyDocument:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3",
        "target": "Clause:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0008",
        "unit": null
      },
      {
        "clause_id": "eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0009",
        "predicate": "contains_clause",
        "source": "PolicyDocument:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3",
        "target": "Clause:eb659fbcd99dcc85f2745f39faae903578c8a5403a504ed63c81c4ca3987afc3#clause_0009",
        "unit": null
      },
      {
        "clause_id": "ebba22b0a7b7a9a06ccf6dfbe862a330eb615359451c4ccb8bff79fd2d9bd1ad#clause_0002",
        "predicate": "contains_clause",
        "source": "PolicyDocument:ebba22b0a7b7a9a06ccf6dfbe862a330eb615359451c4ccb8bff79fd2d9bd1ad",
        "target": "Clause:ebba22b0a7b7a9a06ccf6dfbe862a330eb615359451c4ccb8bff79fd2d9bd1ad#clause_0002",
        "unit": null
      },
      {
        "clause_id": "ebba22b0a7b7a9a06ccf6dfbe862a330eb615359451c4ccb8bff79fd2d9bd1ad#clause_0003",
        "predicate": "contains_clause",
        "source": "PolicyDocument:ebba22b0a7b7a9a06ccf6dfbe862a330eb615359451c4ccb8bff79fd2d9bd1ad",
        "target": "Clause:ebba22b0a7b7a9a06ccf6dfbe862a330eb615359451c4ccb8bff79fd2d9bd1ad#clause_0003",
        "unit": null
      },
      {
        "clause_id": "ebba22b0a7b7a9a06ccf6dfbe862a330eb615359451c4ccb8bff79fd2d9bd1ad#clause_0004",
        "predicate": "contains_clause",
        "source": "PolicyDocument:ebba22b0a7b7a9a06ccf6dfbe862a330eb615359451c4ccb8bff79fd2d9bd1ad",
        "target": "Clause:ebba22b0a7b7a9a06ccf6dfbe862a330eb615359451c4ccb8bff79fd2d9bd1ad#clause_0004",
        "unit": null
      },
      {
        "clause_id": "ebba22b0a7b7a9a06ccf6dfbe862a330eb615359451c4ccb8bff79fd2d9bd1ad#clause_0005",
        "predicate": "contains_clause",
        "source": "PolicyDocument:ebba22b0a7b7a9a06ccf6dfbe862a330eb615359451c4ccb8bff79fd2d9bd1ad",
        "target": "Clause:ebba22b0a7b7a9a06ccf6dfbe862a330eb615359451c4ccb8bff79fd2d9bd1ad#clause_0005",
        "unit": null
      },
      {
        "clause_id": "f0504aae844e886a34041b00b27979b42a08612c461a8d553797330210658574#clause_0000",
        "predicate": "contains_clause",
        "source": "PolicyDocument:f0504aae844e886a34041b00b27979b42a08612c461a8d553797330210658574",
        "target": "Clause:f0504aae844e886a34041b00b27979b42a08612c461a8d553797330210658574#clause_0000",
        "unit": null
      },
      {
        "clause_id": "f855ce5878be9d1e5976fcdb738fa1f41755c19766cf04453045b0e0c69af4ab#clause_0000",
        "predicate": "contains_clause",
        "source": "PolicyDocument:f855ce5878be9d1e5976fcdb738fa1f41755c19766cf04453045b0e0c69af4ab",
        "target": "Clause:f855ce5878be9d1e5976fcdb738fa1f41755c19766cf04453045b0e0c69af4ab#clause_0000",
        "unit": null
      },
      {
        "clause_id": "00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0003",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec",
        "target": "Mechanism:mechanism_0cc398635fa689bfbe94",
        "unit": null
      },
      {
        "clause_id": "00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0001",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec",
        "target": "Mechanism:mechanism_4f0f2ebab9dc78254ad0",
        "unit": null
      },
      {
        "clause_id": "00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0004",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec",
        "target": "Mechanism:mechanism_af91596153d51bc45ad8",
        "unit": null
      },
      {
        "clause_id": "00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec#clause_0002",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:00a12958eaee9a105dcc89c19bd002fa5ac8761a4154324faee32237e8364fec",
        "target": "Mechanism:mechanism_f46b3be7be9c6a035808",
        "unit": null
      },
      {
        "clause_id": "010dd88159617e9e9382aae1b693db97e9b9aa123fefe31ae3a1ceeca57bb8d5#clause_0004",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:010dd88159617e9e9382aae1b693db97e9b9aa123fefe31ae3a1ceeca57bb8d5",
        "target": "Mechanism:mechanism_6314286ed3519af75449",
        "unit": null
      },
      {
        "clause_id": "0d4df7638a86e161686866b0b8ac4efc520827097e76902f88d922c41e699999#clause_0003",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:0d4df7638a86e161686866b0b8ac4efc520827097e76902f88d922c41e699999",
        "target": "Mechanism:mechanism_15e87fbb776d2e4c6bf4",
        "unit": null
      },
      {
        "clause_id": "0de53d8f7a3a1c2de8a8ce98c12216d63084f7e235dd8ddcc02f07760d36a17a#clause_0000",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:0de53d8f7a3a1c2de8a8ce98c12216d63084f7e235dd8ddcc02f07760d36a17a",
        "target": "Mechanism:mechanism_48141ab6a3842b21a876",
        "unit": null
      },
      {
        "clause_id": "0ef7089f429ca4377a5b92c9f7a419ffcb4a3102d8d0ac5666c9f1bfef4ba625#clause_0002",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:0ef7089f429ca4377a5b92c9f7a419ffcb4a3102d8d0ac5666c9f1bfef4ba625",
        "target": "Mechanism:mechanism_42c66c13b657f20c42c2",
        "unit": null
      },
      {
        "clause_id": "0f3400361f4f38388365c57c706fc464f0fa6aee962bdb434173380878f8c94b#clause_0002",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:0f3400361f4f38388365c57c706fc464f0fa6aee962bdb434173380878f8c94b",
        "target": "Mechanism:mechanism_b00cdd1efa1f7c980608",
        "unit": null
      },
      {
        "clause_id": "10695560c26cc67b7a3e26b8dbcd7b856b0b17ef49c31ba529efd3caf059a1de#clause_0005",
        "predicate": "contains_mechanism",
        "source": "PolicyDocument:10695560c26cc67b7a3e26b8dbcd7b856b0b17ef49c31ba529efd3caf059a1de",
        "target": "Mechanism:mechanism_d0d5304bb9d580767832",
        "unit": null
      }
    ],
    "top_mechanism_conflict": [
      {
        "mechanism_id": "Mechanism:mechanism_1a9d1c42a89af57c2d16",
        "mechanism_type": "tou_pricing",
        "total_conflict": 2
      },
      {
        "mechanism_id": "Mechanism:mechanism_1e6ce495b7147017cf8b",
        "mechanism_type": "tou_pricing",
        "total_conflict": 2
      },
      {
        "mechanism_id": "Mechanism:mechanism_4f2ff40ccae1fbaf8e90",
        "mechanism_type": "subsidy",
        "total_conflict": 2
      },
      {
        "mechanism_id": "Mechanism:mechanism_610817c963c7fad38960",
        "mechanism_type": "subsidy",
        "total_conflict": 2
      },
      {
        "mechanism_id": "Mechanism:mechanism_bc950338f4e8aaa22d6a",
        "mechanism_type": "subsidy",
        "total_conflict": 2
      },
      {
        "mechanism_id": "Mechanism:mechanism_c07ec90abc95b5e3d032",
        "mechanism_type": "subsidy",
        "total_conflict": 2
      },
      {
        "mechanism_id": "Mechanism:mechanism_ea7ac7fff0dc22d4630d",
        "mechanism_type": "subsidy",
        "total_conflict": 2
      },
      {
        "mechanism_id": "Mechanism:mechanism_0da0afe6ab689a9d353e",
        "mechanism_type": "subsidy",
        "total_conflict": 1
      },
      {
        "mechanism_id": "Mechanism:mechanism_0eef3b51103e8f296933",
        "mechanism_type": "subsidy",
        "total_conflict": 1
      },
      {
        "mechanism_id": "Mechanism:mechanism_114d6aca12e9856f6655",
        "mechanism_type": "tou_pricing",
        "total_conflict": 1
      },
      {
        "mechanism_id": "Mechanism:mechanism_117e0a55f3972668a06d",
        "mechanism_type": "tiered_pricing",
        "total_conflict": 1
      },
      {
        "mechanism_id": "Mechanism:mechanism_2d8bd71ab3d7d228954e",
        "mechanism_type": "tou_pricing",
        "total_conflict": 1
      },
      {
        "mechanism_id": "Mechanism:mechanism_2faa916caf15250492b6",
        "mechanism_type": "subsidy",
        "total_conflict": 1
      },
      {
        "mechanism_id": "Mechanism:mechanism_31e4048a8768776a0bfb",
        "mechanism_type": "subsidy",
        "total_conflict": 1
      },
      {
        "mechanism_id": "Mechanism:mechanism_350301622fb30b399168",
        "mechanism_type": "subsidy",
        "total_conflict": 1
      },
      {
        "mechanism_id": "Mechanism:mechanism_35e61ca458ea66ceba0d",
        "mechanism_type": "subsidy",
        "total_conflict": 1
      },
      {
        "mechanism_id": "Mechanism:mechanism_582ecd80347043d92cb5",
        "mechanism_type": "tiered_pricing",
        "total_conflict": 1
      },
      {
        "mechanism_id": "Mechanism:mechanism_62f3a7f7a29668e4c28d",
        "mechanism_type": "tou_pricing",
        "total_conflict": 1
      },
      {
        "mechanism_id": "Mechanism:mechanism_6afb27fdb231ebd6e518",
        "mechanism_type": "subsidy",
        "total_conflict": 1
      },
      {
        "mechanism_id": "Mechanism:mechanism_795dc9d8c70080171c4c",
        "mechanism_type": "general_price_adjustment",
        "total_conflict": 1
      }
    ]
  },
  "neo4j": {
    "url": "http://127.0.0.1:17474"
  },
  "risk_aware_rerank": {
    "added_low_risk_preview": [],
    "baseline_top_preview": [
      {
        "alt_candidates_count": 0,
        "clause_id": "6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a#clause_0019",
        "confidence": 1.0,
        "conflict_count": 0,
        "doc_instance_id": "6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a",
        "edge_id": "edge_9d11aa8e2ac9830250143cbb",
        "risk_adjusted_score": 1.0,
        "risk_level": "low",
        "source": "Mechanism:mechanism_d799f1a0f9b26b3791d8",
        "target": "ParameterDefinition:pd_e6d1601074f70f806eeb",
        "unit": "ten_thousand_yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "6ca5d9d44b93a3440cc8f24b4feda441563e6841021017b2c5db628a6976c9f5#clause_0019",
        "confidence": 1.0,
        "conflict_count": 0,
        "doc_instance_id": "6ca5d9d44b93a3440cc8f24b4feda441563e6841021017b2c5db628a6976c9f5",
        "edge_id": "edge_a05fcac7edd9abce4dd16478",
        "risk_adjusted_score": 1.0,
        "risk_level": "low",
        "source": "Mechanism:mechanism_13f5a0b5a8d3b8453d2e",
        "target": "ParameterDefinition:pd_e6d1601074f70f806eeb",
        "unit": "ten_thousand_yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "3c1392fd897f1d095efaa1ae2a1eaa5c0c3df313cd5a9a185aacffe05575b886#clause_0019",
        "confidence": 1.0,
        "conflict_count": 0,
        "doc_instance_id": "3c1392fd897f1d095efaa1ae2a1eaa5c0c3df313cd5a9a185aacffe05575b886",
        "edge_id": "edge_ad0527626acdd17bed0e2989",
        "risk_adjusted_score": 1.0,
        "risk_level": "low",
        "source": "Mechanism:mechanism_1f990b6b177c30850a23",
        "target": "ParameterDefinition:pd_e6d1601074f70f806eeb",
        "unit": "ten_thousand_yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "41eed2fc03a95dc30af898124e00962d37f00dd998abb5da87c6e10e209db169#clause_0019",
        "confidence": 1.0,
        "conflict_count": 0,
        "doc_instance_id": "41eed2fc03a95dc30af898124e00962d37f00dd998abb5da87c6e10e209db169",
        "edge_id": "edge_fdfa0f6ee32ad9499da1c8bc",
        "risk_adjusted_score": 1.0,
        "risk_level": "low",
        "source": "Mechanism:mechanism_06d738e2a5a3340b96b2",
        "target": "ParameterDefinition:pd_e6d1601074f70f806eeb",
        "unit": "ten_thousand_yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "ee74d273b781a2f2d3b7cdfadfe4c9a63e6e423f10874fba1e3c84a0a1f35295#clause_0000",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "ee74d273b781a2f2d3b7cdfadfe4c9a63e6e423f10874fba1e3c84a0a1f35295",
        "edge_id": "edge_09574c8686d757855992e72d",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_c494352133f4b2a710bb",
        "target": "ParameterDefinition:pd_cd23d356da4710fd302b",
        "unit": "kwh"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "f5bc3bee6322d7a50db50b302cf7684c06fe73a55292d8b2fce0e09d9ce0dea5#clause_0000",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "f5bc3bee6322d7a50db50b302cf7684c06fe73a55292d8b2fce0e09d9ce0dea5",
        "edge_id": "edge_1026f9324298b7522267cffb",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_578c78091cb55ca4b045",
        "target": "ParameterDefinition:pd_d4b5b08ef15226b14a44",
        "unit": "time_window"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba",
        "edge_id": "edge_17cbd2dc98f140603ea1f4d8",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_f692896ac3d42b576dbc",
        "target": "ParameterDefinition:pd_91a1c9cf9e03d2e7dd9c",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "f6f8d5f9847c1fe31624cb64353d12b61bebca40113c37e445b63a2d226db18d#clause_0004",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "f6f8d5f9847c1fe31624cb64353d12b61bebca40113c37e445b63a2d226db18d",
        "edge_id": "edge_22b3224d9715304dafc8b2a9",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_3f804a359e629da6180f",
        "target": "ParameterDefinition:pd_ad6264527f1bb4813b4b",
        "unit": "yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "f6f8d5f9847c1fe31624cb64353d12b61bebca40113c37e445b63a2d226db18d#clause_0004",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "f6f8d5f9847c1fe31624cb64353d12b61bebca40113c37e445b63a2d226db18d",
        "edge_id": "edge_359a75e0ace9f00b9dc3c6e9",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_3f804a359e629da6180f",
        "target": "ParameterDefinition:pd_98041f81920656b8b65a",
        "unit": "yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "f5bc3bee6322d7a50db50b302cf7684c06fe73a55292d8b2fce0e09d9ce0dea5#clause_0000",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "f5bc3bee6322d7a50db50b302cf7684c06fe73a55292d8b2fce0e09d9ce0dea5",
        "edge_id": "edge_3aac9ea9f4c0d38d52a15da1",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_578c78091cb55ca4b045",
        "target": "ParameterDefinition:pd_36bd5ecfd8c4b21dbb62",
        "unit": "time_window"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "ee74d273b781a2f2d3b7cdfadfe4c9a63e6e423f10874fba1e3c84a0a1f35295#clause_0000",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "ee74d273b781a2f2d3b7cdfadfe4c9a63e6e423f10874fba1e3c84a0a1f35295",
        "edge_id": "edge_54bdb3dfa432458df265a9aa",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_c494352133f4b2a710bb",
        "target": "ParameterDefinition:pd_17f49ddfae7c641704ef",
        "unit": "kwh"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "ca0ecafa5d9b0881a307250ed1dfb3f239da064ec327235d5f6bf4b0afde27d8#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "ca0ecafa5d9b0881a307250ed1dfb3f239da064ec327235d5f6bf4b0afde27d8",
        "edge_id": "edge_724577a3ad7b59215fbbb0b3",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_c75d27f3a6422d368132",
        "target": "ParameterDefinition:pd_33df67b4485ac531912b",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "34de2093bea75d704c113e23bf49b9018637efa1841e90bf224a6566684fd8df#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "34de2093bea75d704c113e23bf49b9018637efa1841e90bf224a6566684fd8df",
        "edge_id": "edge_7da3665c792f882a7556ee14",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_68b54d92a1f0539c4203",
        "target": "ParameterDefinition:pd_91a1c9cf9e03d2e7dd9c",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "cd86e3487ec66701c2d41c1399f9a453338981c169b847ab9321c78351d62988#clause_0004",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "cd86e3487ec66701c2d41c1399f9a453338981c169b847ab9321c78351d62988",
        "edge_id": "edge_859ae90c6745cf22eaad25e3",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_20a047fd2ea4eb2d6197",
        "target": "ParameterDefinition:pd_ad6264527f1bb4813b4b",
        "unit": "yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "f5bc3bee6322d7a50db50b302cf7684c06fe73a55292d8b2fce0e09d9ce0dea5#clause_0000",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "f5bc3bee6322d7a50db50b302cf7684c06fe73a55292d8b2fce0e09d9ce0dea5",
        "edge_id": "edge_86e6c875c9bd36849ec34d6a",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_578c78091cb55ca4b045",
        "target": "ParameterDefinition:pd_2fece49c772b4079c2cd",
        "unit": "time_window"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba",
        "edge_id": "edge_a4b422944c297e183d53706a",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_f692896ac3d42b576dbc",
        "target": "ParameterDefinition:pd_72a503c7e684700fadb8",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba",
        "edge_id": "edge_b1cad80b938f557cb124a7de",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_f692896ac3d42b576dbc",
        "target": "ParameterDefinition:pd_33df67b4485ac531912b",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "7b751605b49132dd141591500721a0a0aeef9413b412efd887a6985a4ada323a#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "7b751605b49132dd141591500721a0a0aeef9413b412efd887a6985a4ada323a",
        "edge_id": "edge_b65491f0b69dd4ca63b4e64b",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_af82b4583eb2a08b7990",
        "target": "ParameterDefinition:pd_72a503c7e684700fadb8",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "7b751605b49132dd141591500721a0a0aeef9413b412efd887a6985a4ada323a#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "7b751605b49132dd141591500721a0a0aeef9413b412efd887a6985a4ada323a",
        "edge_id": "edge_b912a9b8018475a74bb73942",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_af82b4583eb2a08b7990",
        "target": "ParameterDefinition:pd_91a1c9cf9e03d2e7dd9c",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "34de2093bea75d704c113e23bf49b9018637efa1841e90bf224a6566684fd8df#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "34de2093bea75d704c113e23bf49b9018637efa1841e90bf224a6566684fd8df",
        "edge_id": "edge_ce28d4989105bb104b2388c8",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_68b54d92a1f0539c4203",
        "target": "ParameterDefinition:pd_72a503c7e684700fadb8",
        "unit": "percent"
      }
    ],
    "removed_high_risk_preview": [],
    "risk_adjusted_top_preview": [
      {
        "alt_candidates_count": 0,
        "clause_id": "6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a#clause_0019",
        "confidence": 1.0,
        "conflict_count": 0,
        "doc_instance_id": "6970500b879273b0b83bb7a489716ace3a254448e313c9392b1c8d699aa8443a",
        "edge_id": "edge_9d11aa8e2ac9830250143cbb",
        "risk_adjusted_score": 1.0,
        "risk_level": "low",
        "source": "Mechanism:mechanism_d799f1a0f9b26b3791d8",
        "target": "ParameterDefinition:pd_e6d1601074f70f806eeb",
        "unit": "ten_thousand_yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "6ca5d9d44b93a3440cc8f24b4feda441563e6841021017b2c5db628a6976c9f5#clause_0019",
        "confidence": 1.0,
        "conflict_count": 0,
        "doc_instance_id": "6ca5d9d44b93a3440cc8f24b4feda441563e6841021017b2c5db628a6976c9f5",
        "edge_id": "edge_a05fcac7edd9abce4dd16478",
        "risk_adjusted_score": 1.0,
        "risk_level": "low",
        "source": "Mechanism:mechanism_13f5a0b5a8d3b8453d2e",
        "target": "ParameterDefinition:pd_e6d1601074f70f806eeb",
        "unit": "ten_thousand_yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "3c1392fd897f1d095efaa1ae2a1eaa5c0c3df313cd5a9a185aacffe05575b886#clause_0019",
        "confidence": 1.0,
        "conflict_count": 0,
        "doc_instance_id": "3c1392fd897f1d095efaa1ae2a1eaa5c0c3df313cd5a9a185aacffe05575b886",
        "edge_id": "edge_ad0527626acdd17bed0e2989",
        "risk_adjusted_score": 1.0,
        "risk_level": "low",
        "source": "Mechanism:mechanism_1f990b6b177c30850a23",
        "target": "ParameterDefinition:pd_e6d1601074f70f806eeb",
        "unit": "ten_thousand_yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "41eed2fc03a95dc30af898124e00962d37f00dd998abb5da87c6e10e209db169#clause_0019",
        "confidence": 1.0,
        "conflict_count": 0,
        "doc_instance_id": "41eed2fc03a95dc30af898124e00962d37f00dd998abb5da87c6e10e209db169",
        "edge_id": "edge_fdfa0f6ee32ad9499da1c8bc",
        "risk_adjusted_score": 1.0,
        "risk_level": "low",
        "source": "Mechanism:mechanism_06d738e2a5a3340b96b2",
        "target": "ParameterDefinition:pd_e6d1601074f70f806eeb",
        "unit": "ten_thousand_yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "ee74d273b781a2f2d3b7cdfadfe4c9a63e6e423f10874fba1e3c84a0a1f35295#clause_0000",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "ee74d273b781a2f2d3b7cdfadfe4c9a63e6e423f10874fba1e3c84a0a1f35295",
        "edge_id": "edge_09574c8686d757855992e72d",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_c494352133f4b2a710bb",
        "target": "ParameterDefinition:pd_cd23d356da4710fd302b",
        "unit": "kwh"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "f5bc3bee6322d7a50db50b302cf7684c06fe73a55292d8b2fce0e09d9ce0dea5#clause_0000",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "f5bc3bee6322d7a50db50b302cf7684c06fe73a55292d8b2fce0e09d9ce0dea5",
        "edge_id": "edge_1026f9324298b7522267cffb",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_578c78091cb55ca4b045",
        "target": "ParameterDefinition:pd_d4b5b08ef15226b14a44",
        "unit": "time_window"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba",
        "edge_id": "edge_17cbd2dc98f140603ea1f4d8",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_f692896ac3d42b576dbc",
        "target": "ParameterDefinition:pd_91a1c9cf9e03d2e7dd9c",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "f6f8d5f9847c1fe31624cb64353d12b61bebca40113c37e445b63a2d226db18d#clause_0004",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "f6f8d5f9847c1fe31624cb64353d12b61bebca40113c37e445b63a2d226db18d",
        "edge_id": "edge_22b3224d9715304dafc8b2a9",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_3f804a359e629da6180f",
        "target": "ParameterDefinition:pd_ad6264527f1bb4813b4b",
        "unit": "yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "f6f8d5f9847c1fe31624cb64353d12b61bebca40113c37e445b63a2d226db18d#clause_0004",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "f6f8d5f9847c1fe31624cb64353d12b61bebca40113c37e445b63a2d226db18d",
        "edge_id": "edge_359a75e0ace9f00b9dc3c6e9",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_3f804a359e629da6180f",
        "target": "ParameterDefinition:pd_98041f81920656b8b65a",
        "unit": "yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "f5bc3bee6322d7a50db50b302cf7684c06fe73a55292d8b2fce0e09d9ce0dea5#clause_0000",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "f5bc3bee6322d7a50db50b302cf7684c06fe73a55292d8b2fce0e09d9ce0dea5",
        "edge_id": "edge_3aac9ea9f4c0d38d52a15da1",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_578c78091cb55ca4b045",
        "target": "ParameterDefinition:pd_36bd5ecfd8c4b21dbb62",
        "unit": "time_window"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "ee74d273b781a2f2d3b7cdfadfe4c9a63e6e423f10874fba1e3c84a0a1f35295#clause_0000",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "ee74d273b781a2f2d3b7cdfadfe4c9a63e6e423f10874fba1e3c84a0a1f35295",
        "edge_id": "edge_54bdb3dfa432458df265a9aa",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_c494352133f4b2a710bb",
        "target": "ParameterDefinition:pd_17f49ddfae7c641704ef",
        "unit": "kwh"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "ca0ecafa5d9b0881a307250ed1dfb3f239da064ec327235d5f6bf4b0afde27d8#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "ca0ecafa5d9b0881a307250ed1dfb3f239da064ec327235d5f6bf4b0afde27d8",
        "edge_id": "edge_724577a3ad7b59215fbbb0b3",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_c75d27f3a6422d368132",
        "target": "ParameterDefinition:pd_33df67b4485ac531912b",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "34de2093bea75d704c113e23bf49b9018637efa1841e90bf224a6566684fd8df#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "34de2093bea75d704c113e23bf49b9018637efa1841e90bf224a6566684fd8df",
        "edge_id": "edge_7da3665c792f882a7556ee14",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_68b54d92a1f0539c4203",
        "target": "ParameterDefinition:pd_91a1c9cf9e03d2e7dd9c",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "cd86e3487ec66701c2d41c1399f9a453338981c169b847ab9321c78351d62988#clause_0004",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "cd86e3487ec66701c2d41c1399f9a453338981c169b847ab9321c78351d62988",
        "edge_id": "edge_859ae90c6745cf22eaad25e3",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_20a047fd2ea4eb2d6197",
        "target": "ParameterDefinition:pd_ad6264527f1bb4813b4b",
        "unit": "yuan"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "f5bc3bee6322d7a50db50b302cf7684c06fe73a55292d8b2fce0e09d9ce0dea5#clause_0000",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "f5bc3bee6322d7a50db50b302cf7684c06fe73a55292d8b2fce0e09d9ce0dea5",
        "edge_id": "edge_86e6c875c9bd36849ec34d6a",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_578c78091cb55ca4b045",
        "target": "ParameterDefinition:pd_2fece49c772b4079c2cd",
        "unit": "time_window"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba",
        "edge_id": "edge_a4b422944c297e183d53706a",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_f692896ac3d42b576dbc",
        "target": "ParameterDefinition:pd_72a503c7e684700fadb8",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "22683cdc818adbda88476b2ce5ef07bfd17154e8f751efbcf70c4b68e9dd70ba",
        "edge_id": "edge_b1cad80b938f557cb124a7de",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_f692896ac3d42b576dbc",
        "target": "ParameterDefinition:pd_33df67b4485ac531912b",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "7b751605b49132dd141591500721a0a0aeef9413b412efd887a6985a4ada323a#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "7b751605b49132dd141591500721a0a0aeef9413b412efd887a6985a4ada323a",
        "edge_id": "edge_b65491f0b69dd4ca63b4e64b",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_af82b4583eb2a08b7990",
        "target": "ParameterDefinition:pd_72a503c7e684700fadb8",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "7b751605b49132dd141591500721a0a0aeef9413b412efd887a6985a4ada323a#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "7b751605b49132dd141591500721a0a0aeef9413b412efd887a6985a4ada323a",
        "edge_id": "edge_b912a9b8018475a74bb73942",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_af82b4583eb2a08b7990",
        "target": "ParameterDefinition:pd_91a1c9cf9e03d2e7dd9c",
        "unit": "percent"
      },
      {
        "alt_candidates_count": 0,
        "clause_id": "34de2093bea75d704c113e23bf49b9018637efa1841e90bf224a6566684fd8df#clause_0001",
        "confidence": 0.999999,
        "conflict_count": 0,
        "doc_instance_id": "34de2093bea75d704c113e23bf49b9018637efa1841e90bf224a6566684fd8df",
        "edge_id": "edge_ce28d4989105bb104b2388c8",
        "risk_adjusted_score": 0.999999,
        "risk_level": "low",
        "source": "Mechanism:mechanism_68b54d92a1f0539c4203",
        "target": "ParameterDefinition:pd_72a503c7e684700fadb8",
        "unit": "percent"
      }
    ],
    "summary": {
      "adjusted_top_avg_conflict": 0.0,
      "adjusted_top_high_risk_count": 0,
      "adjusted_top_high_risk_ratio": 0.0,
      "baseline_top_avg_conflict": 0.0,
      "baseline_top_high_risk_count": 0,
      "baseline_top_high_risk_ratio": 0.0,
      "candidate_pool_size": 1060,
      "high_risk_ratio_reduction": 0.0,
      "high_risk_reduction": 0,
      "risk_aware_improved": false,
      "risk_aware_non_regression": true,
      "topn": 100
    }
  }
}
```

#### Step9 总门禁指标
来源：`00_整理记录/step9_iter1/step9_gate_report.json`

```json
{
  "all_targets_passed": true,
  "checks": {
    "core_path_coverage_100": true,
    "neo4j_traceability_rate_100": true,
    "query_execution_success_rate_100": true,
    "risk_aware_rerank_non_regression": true,
    "simulation_backfill_candidates_non_empty": true,
    "simulation_high_risk_cases_non_empty": true,
    "step9_import_gate_passed": true,
    "step9_query_gate_passed": true
  },
  "input": {
    "import_report": "00_整理记录/step9_iter1/step9_neo4j_import_report.json",
    "query_report": "00_整理记录/step9_iter1/step9_query_exec_report.json",
    "simulation_casebook": "00_整理记录/step9_iter1/step9_simulation_casebook.json",
    "step9_dir": "00_整理记录/step9_iter1"
  },
  "snapshot": {
    "import": {
      "edge_total": 10610,
      "node_total": 2892,
      "traceability_rate": 1.0
    },
    "query": {
      "core_path_coverage": 1.0,
      "query_execution_success_rate": 1.0,
      "query_template_count": 12
    },
    "simulation": {
      "adjusted_top_avg_conflict": 0.0,
      "adjusted_top_high_risk_count": 0,
      "adjusted_top_high_risk_ratio": 0.0,
      "baseline_top_avg_conflict": 0.0,
      "baseline_top_high_risk_count": 0,
      "baseline_top_high_risk_ratio": 0.0,
      "candidate_pool_size": 1060,
      "high_risk_ratio_reduction": 0.0,
      "high_risk_reduction": 0,
      "risk_aware_improved": false,
      "risk_aware_non_regression": true,
      "topn": 100
    }
  }
}
```

## 结论（可直接用于论文“实验结果概述”）
- Step1-Step9 已形成完整可复跑流水线：Schema -> 抽样标注 -> 预处理 -> 抽取优化 -> 归一化 -> Gold/IAA -> 门禁复测 -> 图包导出 -> Neo4j 闭环评测。
- 从门禁报告看，核心链路在当前版本达到 `all_targets_passed=true`。
- 文档内已完整转录各步指标报告，可直接作为论文附录或审计附件。
