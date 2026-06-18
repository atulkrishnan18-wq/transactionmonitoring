-- database/queries/link_graph_traversal.sql
-- Recursive CTE for 2-hop Link Analysis Graph Traversal
-- Handles bidirectional links with customer_id_1 < customer_id_2 constraint

WITH RECURSIVE link_network AS (
    -- Anchor member: Find direct links (Depth 1)
    SELECT 
        CASE 
            WHEN customer_id_1 = %s THEN customer_id_2 
            ELSE customer_id_1 
        END AS linked_id,
        link_type,
        1 AS depth,
        ARRAY[%s] AS path
    FROM customer_links
    WHERE (customer_id_1 = %s OR customer_id_2 = %s)
      AND is_active = TRUE

    UNION ALL

    -- Recursive member: Find links-of-links (Depth 2)
    SELECT 
        CASE 
            WHEN cl.customer_id_1 = ln.linked_id THEN cl.customer_id_2 
            ELSE cl.customer_id_1 
        END AS linked_id,
        cl.link_type,
        ln.depth + 1 AS depth,
        ln.path || ln.linked_id AS path
    FROM customer_links cl
    JOIN link_network ln ON (cl.customer_id_1 = ln.linked_id OR cl.customer_id_2 = ln.linked_id)
    WHERE ln.depth < 2
      AND cl.is_active = TRUE
      -- Prevent cycles and don't link back to the starting customer
      AND (
          CASE 
              WHEN cl.customer_id_1 = ln.linked_id THEN cl.customer_id_2 
              ELSE cl.customer_id_1 
          END != ALL(ln.path)
      )
      AND (
          CASE 
              WHEN cl.customer_id_1 = ln.linked_id THEN cl.customer_id_2 
              ELSE cl.customer_id_1 
          END != %s
      )
)
SELECT 
    linked_id,
    MIN(depth) as depth,
    link_type,
    COUNT(*) as link_count,
    path
FROM link_network
GROUP BY linked_id, depth, link_type, path
ORDER BY depth, link_count DESC;
