-- ScoreSentinel Database Schema
-- Version: 1.0 | Day: 26 of 60
-- Purpose: Implementation of AML Audit Requirements & Operational Dashboarding
-- Compatible with: PostgreSQL

-- IMMUTABILITY RULE: The transactions table 
-- is INSERT-ONLY. No UPDATE or DELETE 
-- operations are permitted after a transaction 
-- is scored. Corrections must be made via new 
-- entries only. Enforced at application layer.

-- TABLE 1: transactions
-- Stores full history of scored transactions, raw module scores, and audit trails.
CREATE TABLE transactions (
    transaction_id      VARCHAR(50) PRIMARY KEY,
    customer_id         VARCHAR(50) NOT NULL,
    timestamp_processed TIMESTAMP NOT NULL DEFAULT NOW(),
    engine_version      VARCHAR(20) DEFAULT '1.0',
    
    -- Input fields
    transaction_amount  DECIMAL(15,2) NOT NULL,
    transaction_currency VARCHAR(3) NOT NULL,
    transaction_type    VARCHAR(50) NOT NULL,
    sender_country      VARCHAR(100) NOT NULL,
    receiver_country    VARCHAR(100) NOT NULL,
    customer_type       VARCHAR(50),
    
    -- Module raw scores
    customer_risk_raw   INTEGER DEFAULT 0,
    structuring_raw     INTEGER DEFAULT 0,
    geography_raw       INTEGER DEFAULT 0,
    transaction_type_raw INTEGER DEFAULT 0,
    
    -- Module normalised scores
    customer_normalised  DECIMAL(5,2) DEFAULT 0,
    structuring_normalised DECIMAL(5,2) DEFAULT 0,
    geography_normalised DECIMAL(5,2) DEFAULT 0,
    transaction_normalised DECIMAL(5,2) DEFAULT 0,
    
    -- Composite score
    crs                 DECIMAL(5,2),
    risk_band           VARCHAR(20),
    
    -- Rules and alerts
    rules_fired         TEXT[],
    alert_generated     BOOLEAN DEFAULT FALSE,
    alert_type          VARCHAR(50),
    auto_alert_trigger  VARCHAR(100),
    
    -- Disposition
    disposition_status  VARCHAR(20) DEFAULT 'PENDING',
    reviewer_id         VARCHAR(50),
    review_timestamp    TIMESTAMP,
    reviewer_rationale  TEXT,
    second_reviewer_id  VARCHAR(50),
    second_review_timestamp TIMESTAMP,
    next_review_date    DATE
);

-- TABLE 2: customers
-- Stores master customer records, risk bands, and beneficial ownership data.
CREATE TABLE customers (
    customer_id         VARCHAR(50) PRIMARY KEY,
    full_name           VARCHAR(200) NOT NULL,
    customer_type       VARCHAR(50) NOT NULL,
    ccrs                INTEGER DEFAULT 0,
    risk_band           VARCHAR(20) DEFAULT 'LOW',
    pep_tier            VARCHAR(10),
    beneficial_owner    VARCHAR(200),
    bo_ownership_pct    DECIMAL(5,2),
    country_of_domicile VARCHAR(100),
    onboarding_date     DATE,
    last_reviewed       TIMESTAMP,
    next_review_date    DATE,
    created_at          TIMESTAMP DEFAULT NOW()
);

-- TABLE 3: alerts
-- Case management for AML alerts, implementing the 3-point identifier audit standard.
CREATE TABLE alerts (
    alert_id            VARCHAR(50) PRIMARY KEY,
    transaction_id      VARCHAR(50) REFERENCES transactions(transaction_id),
    customer_id         VARCHAR(50) REFERENCES customers(customer_id),
    alert_type          VARCHAR(50) NOT NULL,
    
    -- Case management fields from HRDT operational experience
    stage               VARCHAR(30) DEFAULT 'PENDING_ASSESSMENT',
    client_rp           VARCHAR(100),
    worldcheck_id       VARCHAR(100),
    internal_summary    TEXT,
    sent_to             VARCHAR(50),
    waiting_for         TEXT,
    
    -- Three-point standard from AUDIT_REQUIREMENTS.md
    point_1_identifier  TEXT,
    point_1_source      TEXT,
    point_2_identifier  TEXT,
    point_2_source      TEXT,
    point_3_identifier  TEXT,
    point_3_source      TEXT,
    three_point_met     BOOLEAN DEFAULT FALSE,
    
    -- Disposition
    status              VARCHAR(20) DEFAULT 'PENDING',
    disposition         VARCHAR(30),
    reviewer_id         VARCHAR(50),
    review_timestamp    TIMESTAMP,
    reviewer_rationale  TEXT,
    second_reviewer_id  VARCHAR(50),
    second_review_timestamp TIMESTAMP,
    residual_risk       TEXT,
    enhanced_rescreening VARCHAR(20),
    
    -- Metadata
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

-- ALERTS TABLE CONSTRAINTS
ALTER TABLE alerts 
ADD CONSTRAINT valid_stage 
CHECK (stage IN (
    'PENDING_ASSESSMENT',
    'PENDING_ACTION', 
    'SENT_FOR_REVIEW',
    'RESOLVED'
));

-- INDEXES FOR PERFORMANCE
-- Optimized for dashboard queries and historical lookups.
CREATE INDEX idx_transactions_customer 
    ON transactions(customer_id);
CREATE INDEX idx_transactions_alert 
    ON transactions(alert_generated);
CREATE INDEX idx_transactions_timestamp 
    ON transactions(timestamp_processed);
CREATE INDEX idx_alerts_stage 
    ON alerts(stage);
CREATE INDEX idx_alerts_status 
    ON alerts(status);
CREATE INDEX idx_alerts_type 
    ON alerts(alert_type);
