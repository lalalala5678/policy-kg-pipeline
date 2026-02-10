# Step4 Iteration Scores

| iteration | total | structure | evidence | doc | clause | mechanism_rate | clause_type_rate | raw_rate | strict_triplet_rate | bind_rate | task_rate | is_good |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| iter0_baseline | 39.482 | 20.000 | 10.000 | 8.418 | 1.064 | 0.0000 | 0.0000 | 0.0435 | 0.0000 | 0.0000 | 0.1182 | False |
| iter1_v1 | 56.896 | 20.000 | 10.000 | 10.959 | 15.937 | 0.6503 | 1.0000 | 0.0435 | 0.0015 | 0.5000 | 0.1182 | False |
| iter2_v2 | 72.817 | 20.000 | 20.000 | 10.959 | 21.858 | 0.6503 | 1.0000 | 0.2903 | 0.2003 | 0.6985 | 0.2794 | False |
| iter3_v2plus | 76.332 | 20.000 | 20.000 | 10.959 | 25.373 | 0.7814 | 1.0000 | 0.2903 | 0.2517 | 0.8808 | 0.2794 | True |

## Notes
- score excludes runtime performance; it only targets KB import usability.
- strict_triplet_ready_rate uses: mechanism_type + clause_type + numeric raw_value.
