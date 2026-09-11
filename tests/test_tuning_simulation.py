"""
ScoreSentinel Threshold Tuning & ATL/BTL Test Suite (v2.0)
Validates Sensitivity Sweeps, Deflation Curves, BTL False-Negative Sampling, and API Endpoints.
Authored by Atul Krishnan, CAMS
"""

import os
import sys
import unittest

# Ensure workspace root is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.tuning_module import ThresholdTuningEngine
from api.app import app, DEMO_API_KEY, READ_API_KEY

class TestTuningSimulation(unittest.TestCase):

    def setUp(self):
        self.tuning_engine = ThresholdTuningEngine()
        self.client = app.test_client()

    def test_benchmark_population_generation(self):
        population = self.tuning_engine.get_benchmark_population(count=150)
        self.assertEqual(len(population), 150)
        first = population[0]
        self.assertIn("amount", first)
        self.assertIn("sender_country", first)
        self.assertIn("receiver_country", first)
        self.assertIn("date", first)

    def test_simulate_threshold_sweep_structuring(self):
        result = self.tuning_engine.simulate_threshold_sweep(
            scenario_id="SCEN-STRUC-01",
            parameter_name="lower_bound",
            min_val=8000.0,
            max_val=9800.0,
            step=450.0,
            btl_margin_pct=0.15
        )

        self.assertEqual(result["scenario_id"], "SCEN-STRUC-01")
        self.assertEqual(result["parameter_name"], "lower_bound")
        self.assertGreater(result["total_evaluated_transactions"], 0)
        
        curve = result["sensitivity_curve"]
        self.assertGreaterEqual(len(curve), 4)

        # Verify monotonicity of alert count (higher lower_bound -> less or equal alerts)
        for i in range(len(curve) - 1):
            self.assertGreaterEqual(
                curve[i]["atl_alert_count"],
                curve[i+1]["atl_alert_count"],
                f"Alert counts should be non-increasing as threshold increases: {curve[i]} vs {curve[i+1]}"
            )

        # Deflation percentage at lowest threshold vs highest threshold
        self.assertLess(curve[0]["deflation_pct"], curve[-1]["deflation_pct"])

        # Check BTL sample structure
        self.assertIn("btl_sample", result)
        self.assertIsInstance(result["btl_sample"], list)

    def test_btl_sampling_margin_bounds(self):
        threshold = 9500.0
        margin = 0.15 # 15% margin -> 8075 to 9499.99
        btl_samples = self.tuning_engine.get_btl_sample(
            scenario_id="SCEN-STRUC-01",
            parameter_name="lower_bound",
            current_threshold=threshold,
            btl_margin_pct=margin,
            sample_size=10
        )

        self.assertGreater(len(btl_samples), 0)
        for s in btl_samples:
            amt = s["amount"]
            self.assertGreaterEqual(amt, threshold * (1.0 - margin))
            self.assertLess(amt, threshold)
            self.assertIn("variance_from_threshold", s)

    def test_api_v2_tuning_simulate_authorized(self):
        headers = {
            "Content-Type": "application/json",
            "X-DEMO-API-KEY": DEMO_API_KEY
        }
        payload = {
            "scenario_id": "SCEN-STRUC-01",
            "parameter_name": "lower_bound",
            "min_val": 8500.0,
            "max_val": 9500.0,
            "step": 500.0,
            "btl_margin_pct": 0.15
        }
        res = self.client.post("/api/v2/tuning/simulate", headers=headers, json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("sensitivity_curve", data)
        self.assertIn("btl_sample", data)
        self.assertEqual(data["scenario_id"], "SCEN-STRUC-01")

    def test_api_v2_tuning_simulate_unauthorized(self):
        res = self.client.post("/api/v2/tuning/simulate", json={})
        self.assertEqual(res.status_code, 401)

    def test_api_v2_tuning_benchmark_authorized(self):
        headers = {"X-READ-API-KEY": READ_API_KEY}
        res = self.client.get("/api/v2/tuning/benchmark", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_transactions", data)
        self.assertGreater(data["total_transactions"], 0)

if __name__ == "__main__":
    unittest.main()
