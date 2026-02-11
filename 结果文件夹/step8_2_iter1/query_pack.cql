// Step8.2 query pack

// Q01 policy_to_mechanism_path
// 主链路：政策到机制
MATCH (p:PolicyDocument {id:$policy_id})-[:contains_clause]->(c:Clause)-[:clause_supports_mechanism]->(m:Mechanism) RETURN p.id,c.id,m.id,m.mechanism_type LIMIT $limit;

// Q02 mechanism_reverse_to_policy
// 反查链路：机制回到政策
MATCH (m:Mechanism {id:$mechanism_id})<-[:clause_supports_mechanism]-(c:Clause)<-[:contains_clause]-(p:PolicyDocument) RETURN m.id,c.id,p.id LIMIT $limit;

// Q03 mechanism_to_definitions
// 机制参数定义明细
MATCH (m:Mechanism {id:$mechanism_id})-[:mechanism_has_parameter_definition]->(d:ParameterDefinition) RETURN m.id,d.id,d.param_type,d.norm_value,d.norm_unit LIMIT $limit;

// Q04 definition_reverse_to_policy
// 定义反查到政策
MATCH (d:ParameterDefinition {id:$definition_id})<-[:parameter_mention_refers_to_definition]-(pm:ParameterMention)<-[:clause_has_parameter_mention]-(c:Clause)<-[:contains_clause]-(p:PolicyDocument) RETURN d.id,pm.id,c.id,p.id LIMIT $limit;

// Q05 time_window_mechanisms_by_policy
// 按时段筛选机制
MATCH (p:PolicyDocument {id:$policy_id})-[:contains_clause]->(c:Clause)-[:clause_supports_mechanism]->(m:Mechanism)-[:mechanism_has_parameter_definition]->(d:ParameterDefinition {norm_unit:'time_window'}) RETURN DISTINCT p.id,m.id,d.id LIMIT $limit;

// Q06 threshold_filter_by_param_type
// 按阈值类参数过滤
MATCH (d:ParameterDefinition {param_type:$param_type}) WHERE toFloat(d.norm_value) >= $min_value MATCH (m:Mechanism)-[:mechanism_has_parameter_definition]->(d) MATCH (p:PolicyDocument)-[:contains_clause]->(:Clause)-[:clause_supports_mechanism]->(m) RETURN DISTINCT p.id,m.id,d.id LIMIT $limit;

// Q07 region_proxy_filter
// 按地区关键词（source_path代理）过滤
MATCH (p:PolicyDocument) WHERE p.source_path CONTAINS $region_keyword MATCH (p)-[:contains_clause]->(c:Clause)-[:clause_supports_mechanism]->(m:Mechanism) RETURN p.id,m.id,count(c) AS clause_count LIMIT $limit;

// Q08 target_group_proxy_filter
// 按目标对象代理参数过滤
MATCH (d:ParameterDefinition {param_type:$param_type}) MATCH (m:Mechanism)-[:mechanism_has_parameter_definition]->(d) RETURN m.id,d.id,d.norm_value,d.norm_unit LIMIT $limit;

// Q09 mechanism_conflict_rank
// 按机制聚合冲突强度
MATCH (m:Mechanism)-[r:mechanism_has_parameter_definition]->(d:ParameterDefinition) RETURN m.id,sum(r.conflict_count) AS total_conflict ORDER BY total_conflict DESC LIMIT $limit;

// Q10 high_risk_facts
// 高风险事实定位
MATCH ()-[r]->() WHERE r.risk_level='high' RETURN r.edge_id,r.predicate,r.source,r.target,r.conflict_count,r.alt_candidates_count LIMIT $limit;

// Q11 cross_clause_conflict_by_mechanism_type
// 同机制跨条款冲突定位
MATCH (m:Mechanism {mechanism_type:$mechanism_type})-[r:mechanism_has_parameter_definition]->(d:ParameterDefinition) RETURN m.id,d.id,r.clause_id,r.conflict_type,r.risk_level LIMIT $limit;

// Q12 strict_all_backfill_candidates
// strict_all 对 strict_high 的候选补充
MATCH ()-[ra]->() WHERE ra.track='strict_all' AND NOT EXISTS { MATCH ()-[rh]->() WHERE rh.track='strict_high' AND rh.source=ra.source AND rh.predicate=ra.predicate AND rh.target=ra.target AND rh.clause_id=ra.clause_id } RETURN ra.source,ra.predicate,ra.target,ra.clause_id LIMIT $limit;
