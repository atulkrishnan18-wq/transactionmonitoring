"""
ScoreSentinel — FIU-IND Suspicious Transaction Report (STR) Generator
Aligned to FIU-IND submission standards under PMLA 2002 (Section 12 & Rule 3).
"""

import os
from datetime import datetime
from psycopg2.extras import RealDictCursor


def _row_to_dict(cur, row):
    """Convert a database row (dict or tuple) into a standard dictionary."""
    if row is None:
        return None
    if isinstance(row, dict):
        return dict(row)
    if hasattr(cur, "description") and cur.description:
        return {col.name: val for col, val in zip(cur.description, row)}
    return {}


def generate_str(alert_id, db_connection):
    """
    Fetches alert, linked transaction, and customer record from database,
    maps all available data to FIU-IND STR fields, and returns a structured
    STR dictionary.
    """
    try:
        cur = db_connection.cursor(cursor_factory=RealDictCursor)
    except TypeError:
        cur = db_connection.cursor()

    try:
        # 1. Fetch alert record
        cur.execute("SELECT * FROM alerts WHERE alert_id = %s", (alert_id,))
        alert = _row_to_dict(cur, cur.fetchone())
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        # 2. Fetch linked transaction record
        tx_id = alert.get("transaction_id")
        tx = {}
        if tx_id:
            cur.execute("SELECT * FROM transactions WHERE transaction_id = %s", (tx_id,))
            tx = _row_to_dict(cur, cur.fetchone()) or {}

        # 3. Fetch customer record
        cust_id = alert.get("customer_id") or tx.get("customer_id")
        customer = {}
        if cust_id:
            cur.execute("SELECT * FROM customers WHERE customer_id = %s", (cust_id,))
            customer = _row_to_dict(cur, cur.fetchone()) or {}
    finally:
        cur.close()

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    date_compact = now.strftime("%Y%m%d")

    # Format timestamps safely
    tx_timestamp = tx.get("timestamp_processed") or alert.get("created_at")
    if hasattr(tx_timestamp, "isoformat"):
        tx_timestamp_str = tx_timestamp.isoformat()
    else:
        tx_timestamp_str = str(tx_timestamp) if tx_timestamp else today_str

    # Format rules_fired
    raw_rules = tx.get("rules_fired") or []
    if isinstance(raw_rules, (list, tuple)):
        rules_list = [str(r) for r in raw_rules]
        rules_fired_str = ", ".join(rules_list)
    else:
        rules_fired_str = str(raw_rules) if raw_rules else ""
        rules_list = [r.strip() for r in rules_fired_str.split(",") if r.strip()]

    rules_upper = rules_fired_str.upper()
    alert_type_str = str(alert.get("alert_type") or "")
    uapa_matched = str(alert.get("uapa_list_matched") or "")

    # Build Grounds for Suspicion (Narrative)
    narrative_parts = []

    if (
        "STRUCTURING" in rules_upper
        or "SCN-001" in rules_upper
        or "SMURFING" in rules_upper
    ):
        narrative_parts.append(
            "Multiple transactions detected below reporting threshold indicating deliberate structuring."
        )

    if (
        "HIGH_RISK_CORRIDOR" in rules_upper
        or "SCN-003" in rules_upper
        or "GEO-AUTO" in rules_upper
    ):
        narrative_parts.append(
            "Transaction involves high-risk jurisdiction flagged under FATF grey/black list."
        )

    if (
        "FAN_IN" in rules_upper
        or "FAN-IN" in rules_upper
        or "SCN-004" in rules_upper
        or "VEL-028" in rules_upper
    ):
        narrative_parts.append(
            "Account receiving funds from unusual number of distinct sources indicating mule activity."
        )

    if "UAPA" in alert_type_str.upper() or "UAPA" in uapa_matched.upper() or "SCHEDULE" in alert_type_str.upper():
        narrative_parts.append(
            "Customer name matches designated terrorist list under Section 51A of UAPA 1967. Mandatory reporting required."
        )

    if "OFAC" in alert_type_str.upper() or "OFAC" in uapa_matched.upper():
        narrative_parts.append(
            "Customer name matches OFAC SDN sanctions list."
        )

    reviewer_rationale = (alert.get("reviewer_rationale") or "").strip()
    if reviewer_rationale:
        narrative_parts.append(f"Reviewer Rationale: {reviewer_rationale}")
    else:
        narrative_parts.append("Reviewer Rationale: N/A")

    grounds_for_suspicion = " ".join(narrative_parts)

    # STR Reference: "STR-{YYYYMMDD}-{alert_id last 6 chars}"
    alert_suffix = str(alert_id)[-6:] if alert_id else "000000"
    str_reference = alert.get("str_reference") or f"STR-{date_compact}-{alert_suffix}"

    # PART A — Reporting Entity Details
    part_a = {
        "report_type": "STR",
        "reporting_entity_name": os.environ.get("REPORTING_ENTITY_NAME") or "ScoreSentinel Financial Services Pvt Ltd",
        "reporting_entity_type": os.environ.get("REPORTING_ENTITY_TYPE") or "NBFC",
        "principal_officer_name": os.environ.get("PRINCIPAL_OFFICER_NAME") or "Atul Krishnan, CAMS",
        "principal_officer_designation": os.environ.get("PRINCIPAL_OFFICER_DESIGNATION") or "Principal Officer & Head of AML Compliance",
        "reporting_entity_address": os.environ.get("REPORTING_ENTITY_ADDRESS") or "Mumbai, Maharashtra, India",
        "reporting_entity_fiu_reg_no": os.environ.get("REPORTING_ENTITY_FIU_REG_NO") or "FIUIND-NBFC-2026-001",
        "report_date": today_str,
        "period_of_transaction": tx_timestamp_str,
    }

    # PART B — Suspicious Transaction Details
    crs_val = tx.get("crs")
    part_b = {
        "transaction_id": tx.get("transaction_id") or alert.get("transaction_id") or "N/A",
        "transaction_date": tx_timestamp_str,
        "transaction_amount": float(tx.get("transaction_amount")) if tx.get("transaction_amount") is not None else 0.0,
        "transaction_currency": tx.get("transaction_currency") or "INR",
        "transaction_type": tx.get("transaction_type") or "N/A",
        "sender_account": cust_id or "N/A",
        "sender_bank": "As per records",
        "receiver_account": tx.get("receiver_account_id") or "Not Available",
        "mode_of_transaction": tx.get("transaction_type") or "N/A",
        "crs_score": float(crs_val) if crs_val is not None else "AUTO_ALERT",
        "rules_fired": rules_fired_str if rules_fired_str else "None",
        "risk_band": tx.get("risk_band") or customer.get("risk_band") or "HIGH_RISK",
    }

    # PART C — Suspect Details
    pep_tier = customer.get("pep_tier")
    cust_type_val = customer.get("customer_type") or tx.get("customer_type") or "INDIVIDUAL"
    if pep_tier:
        pep_status_val = f"PEP Tier {pep_tier}"
    elif "PEP" in str(cust_type_val).upper():
        pep_status_val = "PEP"
    else:
        pep_status_val = "Non-PEP"

    tx_band = tx.get("risk_band")
    cust_band = customer.get("risk_band")
    risk_class = tx_band if (tx_band and cust_band in (None, "LOW")) else (cust_band or tx_band or "HIGH_RISK")

    part_c = {
        "suspect_name": customer.get("full_name") or f"Customer {cust_id}",
        "suspect_account": cust_id or "N/A",
        "customer_type": cust_type_val,
        "pep_status": pep_status_val,
        "country_of_domicile": customer.get("country_of_domicile") or tx.get("sender_country") or "IN",
        "risk_classification": risk_class,
    }

    # PART D — Grounds for Suspicion (Narrative)
    part_d = {
        "narrative": grounds_for_suspicion,
        "alert_type": alert_type_str,
        "disposition": alert.get("disposition") or "PENDING",
        "reviewer_rationale": reviewer_rationale,
    }

    # PART E — STR Metadata
    part_e = {
        "str_reference": str_reference,
        "alert_id": alert_id,
        "generated_at": now.isoformat(),
        "generated_by": alert.get("reviewer_id") or "ANALYST_01",
        "three_point_met": bool(alert.get("three_point_met")),
        "point_1_identifier": alert.get("point_1_identifier") or "N/A",
        "point_1_source": alert.get("point_1_source") or "N/A",
        "point_2_identifier": alert.get("point_2_identifier") or "N/A",
        "point_2_source": alert.get("point_2_source") or "N/A",
        "point_3_identifier": alert.get("point_3_identifier") or "N/A",
        "point_3_source": alert.get("point_3_source") or "N/A",
        "status": "DRAFT — Pending Principal Officer Review",
    }

    return {
        "str_reference": str_reference,
        "alert_id": alert_id,
        "part_a_reporting_entity": part_a,
        "part_b_transaction_details": part_b,
        "part_c_suspect_details": part_c,
        "part_d_grounds_for_suspicion": part_d,
        "part_e_metadata": part_e,
    }
