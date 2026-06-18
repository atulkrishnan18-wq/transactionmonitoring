-- ScoreSentinel 2.0 | Day 02: Link Analysis Design
-- Draft Schema for customer_links table
-- Objective: Detect how accounts are connected beyond just transactions.

CREATE TABLE customer_links (
    link_id             SERIAL PRIMARY KEY,
    customer_id_1       VARCHAR(50) NOT NULL REFERENCES customers(customer_id),
    customer_id_2       VARCHAR(50) NOT NULL REFERENCES customers(customer_id),
    link_type           VARCHAR(30) NOT NULL, -- 'SHARED_IP', 'SHARED_DEVICE', 'SHARED_ADDRESS'
    link_value          TEXT NOT NULL,        -- The actual IP, Device ID, or Address
    first_seen          TIMESTAMP DEFAULT NOW(),
    last_seen           TIMESTAMP DEFAULT NOW(),
    link_strength       DECIMAL(5,2) DEFAULT 1.00,
    is_active           BOOLEAN DEFAULT TRUE,
    metadata            JSONB,                -- Store context like 'count', 'frequency', or 'source'
    created_at          TIMESTAMP DEFAULT NOW(),
    
    -- Prevent duplicate links (bi-directional check)
    -- We enforce customer_id_1 < customer_id_2 to ensure only one record exists for any pair
    CONSTRAINT unique_customer_link UNIQUE (customer_id_1, customer_id_2, link_type, link_value),
    CONSTRAINT check_customer_order CHECK (customer_id_1 < customer_id_2)
);

-- Performance Indexes for Link Analysis
CREATE INDEX idx_customer_links_c1 ON customer_links(customer_id_1);
CREATE INDEX idx_customer_links_c2 ON customer_links(customer_id_2);
CREATE INDEX idx_customer_links_type ON customer_links(link_type);
CREATE INDEX idx_customer_links_value ON customer_links(link_value);

-- Potential addition to customers table to support link counts
-- ALTER TABLE customers ADD COLUMN device_nexus_count INTEGER DEFAULT 0; -- ALREADY PRESENT IN DB
-- ALTER TABLE customers ADD COLUMN ip_nexus_count INTEGER DEFAULT 0;
-- ALTER TABLE customers ADD COLUMN address_nexus_count INTEGER DEFAULT 0;
