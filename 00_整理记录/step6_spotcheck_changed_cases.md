# Step6 Spotcheck (Changed Cases)

Updated: 2026-02-11

## Overview
- sample_total: `300`
- changed_cases (Step5 vs adjudicated Gold): `32`
- mechanism change reason distribution:
  - `agree`: 32
- param-type change reason distribution:
  - `agree`: 17
  - `keep_step5_param`: 15

## 20 Example Changed Mentions
- `pm_045806889ecbbfd5b120`: mechanism `technology_route -> subsidy`, param `subsidy_amount -> subsidy_amount`, unit `yuan -> yuan`
- `pm_0750569cc63ec6887c3b`: mechanism `subsidy -> None`, param `None -> None`, unit `None -> None`
- `pm_296552a3297b9f0030f2`: mechanism `technology_route -> subsidy`, param `subsidy_amount -> subsidy_amount`, unit `yuan -> yuan`
- `pm_36e6f52042fa93a84f9d`: mechanism `tou_pricing -> tou_pricing`, param `None -> price_value`, unit `None -> yuan_per_kwh`
- `pm_3c302bd527b0d6f56199`: mechanism `general_price_adjustment -> tou_pricing`, param `price_delta_pct -> price_delta_pct`, unit `percent -> percent`
- `pm_3d0d00a77a3a9be117e4`: mechanism `tou_pricing -> None`, param `None -> None`, unit `None -> None`
- `pm_3dbe4a76b7bc91acac6b`: mechanism `tou_pricing -> tou_pricing`, param `None -> price_value`, unit `None -> yuan_per_kwh`
- `pm_4acf027ab61142d3d163`: mechanism `tiered_pricing -> tiered_pricing`, param `None -> price_value`, unit `None -> yuan_per_kwh`
- `pm_4bb6cdc6a2d5846b9d82`: mechanism `general_price_adjustment -> tou_pricing`, param `price_delta_pct -> price_delta_pct`, unit `percent -> percent`
- `pm_4d42b2cfaf4a5abd3e88`: mechanism `general_price_adjustment -> None`, param `None -> price_value`, unit `None -> yuan_per_kwh`
- `pm_516f745345da576a4545`: mechanism `tiered_pricing -> general_price_adjustment`, param `price_value -> price_value`, unit `yuan -> yuan`
- `pm_533f35fb8f55c9c31545`: mechanism `tiered_pricing -> tiered_pricing`, param `None -> price_value`, unit `None -> yuan_per_kwh`
- `pm_563c875773b4949abd64`: mechanism `tiered_pricing -> tiered_pricing`, param `None -> consumption_threshold_kwh`, unit `None -> kwh`
- `pm_5e2ee04e41a3ae2df676`: mechanism `general_price_adjustment -> None`, param `None -> price_value`, unit `None -> yuan_per_kwh`
- `pm_62eae82132606befc2a8`: mechanism `tiered_pricing -> general_price_adjustment`, param `price_value -> price_value`, unit `yuan_per_kwh -> yuan_per_kwh`
- `pm_67e2a66db0e3ef84a2cb`: mechanism `subsidy -> None`, param `other -> other`, unit `kw -> kw`
- `pm_68af1cbb598ab260dd5d`: mechanism `technology_route -> task_assessment`, param `ratio_target -> ratio_target`, unit `percent -> percent`
- `pm_68e59f24452a15c7d021`: mechanism `subsidy -> subsidy`, param `None -> price_value`, unit `None -> yuan_per_kwh`
- `pm_79c4f08366ce4ffc3290`: mechanism `subsidy -> subsidy`, param `None -> price_value`, unit `None -> yuan_per_kwh`
- `pm_7fb3d4411ceb94898930`: mechanism `tou_pricing -> tou_pricing`, param `time_window -> time_point`, unit `time_point -> time_window`
