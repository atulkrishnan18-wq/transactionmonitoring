"""
ScoreSentinel Link Analysis Module (v2.0)
Part of the ScoreSentinel 2.0 Graph Intelligence Suite
Authored by Gemini CLI | Day 03 of 30
"""

import os

class LinkAnalysisModule:
    def __init__(self):
        # Module Maximum for normalization as defined in COMPOSITE_LOGIC.md
        self.module_maximum = 100
        self.alert_threshold = 50
        
        # Load the SQL query
        query_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'queries', 'link_graph_traversal.sql')
        with open(query_path, 'r') as f:
            self.traversal_query = f.read()

    def get_network(self, customer_id, db_connection):
        """
        Executes the recursive CTE to find the 2-hop network.
        Returns list of dicts: {linked_id, depth, link_type, link_count, path}
        """
        from psycopg2.extras import RealDictCursor
        cur = db_connection.cursor(cursor_factory=RealDictCursor)
        try:
            # The query has 5 placeholders in order:
            # 1. CASE WHEN customer_id_1 = %s THEN customer_id_2 ...
            # 2. ARRAY[%s]
            # 3. WHERE (customer_id_1 = %s OR customer_id_2 = %s)
            # 4. AND (CASE ... != %s)
            cur.execute(self.traversal_query, (customer_id, customer_id, customer_id, customer_id, customer_id))
            return cur.fetchall()
        finally:
            cur.close()

    def calculate_link_risk_score(self, customer_id, network_result):
        """
        Scores the network based on topology and link types.
        """
        raw_score = 0
        rules_fired = []
        
        # network_result format: {'linked_id': '...', 'depth': 1, 'link_type': '...', 'link_count': 5, 'path': [...]}
        
        direct_links = [r for r in network_result if r['depth'] == 1]
        second_hop_links = [r for r in network_result if r['depth'] == 2]
        
        # Rule LNK-001: Single direct device link
        device_links_d1 = [r for r in direct_links if r['link_type'] == 'SHARED_DEVICE']
        if len(device_links_d1) == 1:
            raw_score += 25
            rules_fired.append("LNK-001")
            
        # Rule LNK-002: Multiple direct device links
        if len(device_links_d1) > 1:
            raw_score += 50
            rules_fired.append("LNK-002")
            
        # Rule LNK-003: Second-hop device connection
        device_links_d2 = [r for r in second_hop_links if r['link_type'] == 'SHARED_DEVICE']
        if len(device_links_d2) > 0:
            raw_score += 15
            rules_fired.append("LNK-003")
            
        # Rule LNK-004: High link_count on a single connection (Frequent shared access)
        high_frequency_links = [r for r in network_result if r['link_count'] >= 10]
        if len(high_frequency_links) > 0:
            raw_score += 20
            rules_fired.append("LNK-004")
            
        # Rule LNK-005: Fully connected cluster (3+ customers all linked to each other)
        # We look for "triangles" involving the start customer.
        # If customer_id is linked to B and C, and B is linked to C.
        linked_ids_d1 = set(r['linked_id'] for r in direct_links)
        triangles = 0
        for r2 in second_hop_links:
            # r2['linked_id'] is C, r2['path'] is [customer_id, B]
            # If C is also in linked_ids_d1, then customer_id -> B, B -> C, and customer_id -> C.
            if r2['linked_id'] in linked_ids_d1:
                triangles += 1
                
        if triangles > 0:
            raw_score += 40
            rules_fired.append("LNK-005")

        # Cap at module maximum
        raw_score = min(raw_score, self.module_maximum)
        
        risk_band = "LOW"
        if raw_score >= 80: risk_band = "CRITICAL"
        elif raw_score >= 50: risk_band = "HIGH"
        elif raw_score >= 25: risk_band = "MEDIUM"
        
        # Build node/edge lists for visualization
        nodes = [{"id": customer_id, "depth": 0}]
        edges = []
        seen_nodes = {customer_id}
        
        for r in network_result:
            if r['linked_id'] not in seen_nodes:
                nodes.append({"id": r['linked_id'], "depth": r['depth']})
                seen_nodes.add(r['linked_id'])
            
            # Edge from path[-1] to linked_id
            source = r['path'][-1]
            edges.append({
                "source": source,
                "target": r['linked_id'],
                "type": r['link_type'],
                "count": r['link_count']
            })
            
            # If depth 1, also connect start to direct
            if r['depth'] == 1:
                # This is already covered by source=path[-1] where path=[customer_id]
                pass
        
        return {
            "network_nodes": nodes,
            "network_edges": edges,
            "link_risk_score": raw_score,
            "risk_band": risk_band,
            "triggered_rules": sorted(list(set(rules_fired)))
        }
