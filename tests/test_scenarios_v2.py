"""
ScoreSentinel Enterprise Scenario Engine Test Suite (v2.0)
Validates SCEN-STRUC-01, SCEN-VEL-01, SCEN-CORR-01, Parameter Overrides, and API Endpoints.
Authored by Atul Krishnan, CAMS
"""

import os
import sys
import unittest
from datetime import datetime, timedelta

# Ensure workspace root is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.scenario_engine import ScenarioEngine
from api.app import app, DEMO_API_KEY, READ_API_KEY

class TestEnterpriseScenarios(unittest.TestCase):

    def setUp(self):
        self.engine = ScenarioEngine()
        self.engine.reset_parameters()
        self.base_time = datetime(2026, 6, 1, 10, 0, 0)
        self.client = app.test_client()

    def tearDown(self):
        self.engine.reset_parameters()

    # -------------------------------------------------------------
    # 1. CATALOG INTEGRITY TESTS
    # -------------------------------------------------------------
    def test_catalog_integrity(self):
        catalog = self.engine.get_catalog()
        self.assertGreaterEqual(catalog["scenario_count"], 3)
        
        scenario_ids = [s["scenario_id"] for s in catalog["scenarios"]]
        self.assertIn("SCEN-STRUC-01", scenario_ids)
        self.assertIn("SCEN-VEL-01", scenario_ids)
        self.assertIn("SCEN-CORR-01", scenario_ids)

        for s in catalog["scenarios"]:
            self.assertTrue(s["regulatory_citation"], f"Missing citation for {s['scenario_id']}")
            self.assertTrue(s["description"], f"Missing description for {s['scenario_id']}")
            self.assertIn("parameters", s)
            self.assertIn("default_parameters", s)

    # -------------------------------------------------------------
    # 2. SCEN-STRUC-01: STRUCTURING / SMURFING
    # -------------------------------------------------------------
    def test_structuring_scenario_default_trigger(self):
        # 3 transactions between $9,000 and $9,999 in 3 days
        history = [
            {"id": "TX-S1", "amount": 9200.0, "date": self.base_time - timedelta(days=2)},
            {"id": "TX-S2", "amount": 9500.0, "date": self.base_time - timedelta(days=1)}
        ]
        curr = {"id": "TX-S3", "amount": 9800.0, "date": self.base_time}

        result = self.engine.evaluate_transaction(curr, history=history)
        self.assertTrue(result["has_breach"])
        
        struc_alert = next((a for a in result["alerts"] if a["scenario_id"] == "SCEN-STRUC-01"), None)
        self.assertIsNotNone(struc_alert)
        self.assertEqual(struc_alert["severity"], "CRITICAL") # 9200 + 9500 + 9800 = 28,500 >= 25k aggregate
        self.assertEqual(struc_alert["triggering_transaction_count"], 3)
        self.assertIn("BSA 31 U.S.C. § 5324", struc_alert["regulatory_citation"])

    def test_structuring_scenario_clean_transactions(self):
        # Transactions well below structuring band ($2,000)
        history = [
            {"id": "TX-C1", "amount": 2000.0, "date": self.base_time - timedelta(days=2)},
            {"id": "TX-C2", "amount": 2500.0, "date": self.base_time - timedelta(days=1)}
        ]
        curr = {"id": "TX-C3", "amount": 2100.0, "date": self.base_time}

        result = self.engine.evaluate_transaction(curr, history=history)
        struc_alert = next((a for a in result["alerts"] if a["scenario_id"] == "SCEN-STRUC-01"), None)
        self.assertIsNone(struc_alert)

    def test_structuring_dynamic_threshold_override(self):
        # Transactions at $8,500 (does not trigger default $9,000 lower bound)
        history = [
            {"id": "TX-O1", "amount": 8500.0, "date": self.base_time - timedelta(days=2)},
            {"id": "TX-O2", "amount": 8600.0, "date": self.base_time - timedelta(days=1)}
        ]
        curr = {"id": "TX-O3", "amount": 8700.0, "date": self.base_time}

        # Default run: should NOT trigger
        res_default = self.engine.evaluate_transaction(curr, history=history)
        self.assertFalse(any(a["scenario_id"] == "SCEN-STRUC-01" for a in res_default["alerts"]))

        # Override lower_bound to 8000: SHOULD trigger!
        res_override = self.engine.evaluate_transaction(
            curr,
            history=history,
            parameter_overrides={"SCEN-STRUC-01": {"lower_bound": 8000.0}}
        )
        self.assertTrue(any(a["scenario_id"] == "SCEN-STRUC-01" for a in res_override["alerts"]))

    # -------------------------------------------------------------
    # 3. SCEN-VEL-01: RAPID MOVEMENT / PASS-THROUGH
    # -------------------------------------------------------------
    def test_rapid_movement_scenario_trigger(self):
        # Inflow of $20,000 followed by outflow of $19,000 within 2 hours (95% dissipation)
        history = [
            {
                "id": "TX-IN-1",
                "amount": 20000.0,
                "type": "CREDIT",
                "date": self.base_time - timedelta(hours=2)
            }
        ]
        curr = {
            "id": "TX-OUT-1",
            "amount": 19000.0,
            "type": "DEBIT",
            "date": self.base_time
        }

        result = self.engine.evaluate_transaction(curr, history=history)
        self.assertTrue(result["has_breach"])
        
        vel_alert = next((a for a in result["alerts"] if a["scenario_id"] == "SCEN-VEL-01"), None)
        self.assertIsNotNone(vel_alert)
        self.assertGreaterEqual(vel_alert["metrics"]["dissipation_ratio"], 0.85)
        self.assertIn("FATF", vel_alert["regulatory_citation"])

    def test_rapid_movement_scenario_normal_retention(self):
        # Inflow of $20,000, but only $2,000 outflow (10% dissipation -> not a pass-through)
        history = [
            {
                "id": "TX-IN-2",
                "amount": 20000.0,
                "type": "CREDIT",
                "date": self.base_time - timedelta(hours=2)
            }
        ]
        curr = {
            "id": "TX-OUT-2",
            "amount": 2000.0,
            "type": "DEBIT",
            "date": self.base_time
        }

        result = self.engine.evaluate_transaction(curr, history=history)
        vel_alert = next((a for a in result["alerts"] if a["scenario_id"] == "SCEN-VEL-01"), None)
        self.assertIsNone(vel_alert)

    # -------------------------------------------------------------
    # 4. SCEN-CORR-01: HIGH-RISK CORRIDOR SPIKE
    # -------------------------------------------------------------
    def test_corridor_scenario_spike_trigger(self):
        # Customer baseline: 5 domestic transactions of ~$500
        history = [
            {"id": f"TX-B{i}", "amount": 500.0, "sender_country": "United Kingdom", "receiver_country": "United Kingdom", "date": self.base_time - timedelta(days=i*3)}
            for i in range(1, 6)
        ]
        # Sudden $40,000 transfer to Cayman Islands (Offshore Secrecy + CPI score 55)
        curr = {
            "id": "TX-CORR-1",
            "amount": 40000.0,
            "sender_country": "United Kingdom",
            "receiver_country": "Cayman Islands",
            "date": self.base_time
        }

        result = self.engine.evaluate_transaction(curr, history=history)
        self.assertTrue(result["has_breach"])
        
        corr_alert = next((a for a in result["alerts"] if a["scenario_id"] == "SCEN-CORR-01"), None)
        self.assertIsNotNone(corr_alert)
        self.assertGreaterEqual(corr_alert["metrics"]["corridor_risk_score"], 40.0)
        self.assertGreaterEqual(corr_alert["metrics"]["observed_multiplier"], 3.0)

    def test_corridor_scenario_clean_domestic(self):
        # Low risk UK -> UK transfer
        curr = {
            "id": "TX-DOM-1",
            "amount": 1000.0,
            "sender_country": "United Kingdom",
            "receiver_country": "United Kingdom",
            "date": self.base_time
        }
        result = self.engine.evaluate_transaction(curr, history=[])
        corr_alert = next((a for a in result["alerts"] if a["scenario_id"] == "SCEN-CORR-01"), None)
        self.assertIsNone(corr_alert)

    # -------------------------------------------------------------
    # 5. BATCH EVALUATION
    # -------------------------------------------------------------
    def test_batch_evaluation_flow(self):
        tx_stream = [
            {"id": "BATCH-1", "amount": 1000.0, "date": self.base_time - timedelta(days=5)},
            {"id": "BATCH-2", "amount": 9300.0, "date": self.base_time - timedelta(days=2)},
            {"id": "BATCH-3", "amount": 9400.0, "date": self.base_time - timedelta(days=1)},
            {"id": "BATCH-4", "amount": 9500.0, "date": self.base_time}, # 3rd structuring tx
        ]
        batch_summary = self.engine.evaluate_batch(tx_stream)
        self.assertEqual(batch_summary["total_transactions_evaluated"], 4)
        self.assertGreaterEqual(batch_summary["total_alerts_generated"], 1)
        self.assertIn("SCEN-STRUC-01", batch_summary["scenario_trigger_distribution"])

    # -------------------------------------------------------------
    # 6. REST API V2 ENDPOINT TESTS
    # -------------------------------------------------------------
    def test_api_v2_catalog_unauthorized(self):
        res = self.client.get("/api/v2/scenarios")
        self.assertEqual(res.status_code, 401)

    def test_api_v2_catalog_success(self):
        headers = {"X-READ-API-KEY": READ_API_KEY}
        res = self.client.get("/api/v2/scenarios", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("scenarios", data)
        self.assertGreaterEqual(data["scenario_count"], 3)

    def test_api_v2_evaluate_endpoint(self):
        headers = {
            "Content-Type": "application/json",
            "X-DEMO-API-KEY": DEMO_API_KEY
        }
        payload = {
            "transaction": {
                "id": "API-TX-1",
                "amount": 9600.0,
                "date": self.base_time.isoformat()
            },
            "history": [
                {"id": "API-TX-H1", "amount": 9200.0, "date": (self.base_time - timedelta(days=1)).isoformat()},
                {"id": "API-TX-H2", "amount": 9500.0, "date": (self.base_time - timedelta(days=2)).isoformat()}
            ]
        }
        res = self.client.post("/api/v2/scenarios/evaluate", headers=headers, json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["has_breach"])
        self.assertEqual(data["alerts"][0]["scenario_id"], "SCEN-STRUC-01")

    def test_api_v2_update_and_reset_parameters(self):
        headers = {
            "Content-Type": "application/json",
            "X-DEMO-API-KEY": DEMO_API_KEY
        }
        # Update lower_bound to 8500
        update_payload = {"parameters": {"lower_bound": 8500.0}}
        res = self.client.put("/api/v2/scenarios/SCEN-STRUC-01/parameters", headers=headers, json=update_payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["active_parameters"]["lower_bound"], 8500.0)

        # Reset back
        res_reset = self.client.post("/api/v2/scenarios/reset", headers=headers, json={})
        self.assertEqual(res_reset.status_code, 200)

        # Verify reset in catalog
        scen = self.engine.get_scenario("SCEN-STRUC-01")
        self.assertEqual(scen.parameters["lower_bound"], 9000.0)

if __name__ == "__main__":
    unittest.main()
