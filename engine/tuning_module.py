"""
ScoreSentinel Threshold Tuning & ATL/BTL Optimization Module (v2.0)
Part of the ScoreSentinel Enterprise AML Rules Engine
Authored by Atul Krishnan, CAMS
"""

import copy
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple

from .scenario_engine import ScenarioEngine

class ThresholdTuningEngine:
    """
    Enterprise 2LoD Model Risk Optimization Engine (SR 11-7 / OCC 2011-12).
    Simulates threshold sensitivity sweeps, computes Above-The-Line (ATL) alert volumes,
    Below-The-Line (BTL) false-negative sampling populations, and alert deflation metrics.
    """

    def __init__(self, scenario_engine: Optional[ScenarioEngine] = None):
        self.scenario_engine = scenario_engine or ScenarioEngine()
        self._benchmark_population: Optional[List[Dict[str, Any]]] = None

    def get_benchmark_population(self, count: int = 250, seed: int = 42) -> List[Dict[str, Any]]:
        """
        Generates or retrieves a deterministic, statistically representative population
        of banking transactions mirroring retail and commercial cash flows.
        """
        if self._benchmark_population is not None and len(self._benchmark_population) == count:
            return copy.deepcopy(self._benchmark_population)

        random.seed(seed)
        base_time = datetime(2026, 6, 1, 9, 0, 0, tzinfo=timezone.utc)
        population = []

        countries = [
            ("United Kingdom", 0.50),
            ("United States", 0.20),
            ("Cayman Islands", 0.08),
            ("Nigeria", 0.07),
            ("British Virgin Islands", 0.05),
            ("United Arab Emirates", 0.05),
            ("Pakistan", 0.05)
        ]

        def pick_country():
            r = random.random()
            cum = 0.0
            for c, w in countries:
                cum += w
                if r <= cum:
                    return c
            return "United Kingdom"

        for i in range(count):
            tx_id = f"BENCH-{i+1:04d}"
            tx_time = base_time + timedelta(hours=i * 2.5 + random.randint(0, 45))
            
            # Create a distribution across low, borderline (BTL), and high-risk structuring
            tier = random.random()
            if tier < 0.55:
                # Normal low-risk retail/commercial ($150 - $6,500)
                amount = round(random.uniform(150.0, 6500.0), 2)
                tx_type = random.choice(["CREDIT", "DEBIT", "WIRE", "PAYMENT"])
                sender = "United Kingdom"
                receiver = "United Kingdom"
            elif tier < 0.75:
                # Borderline BTL candidates ($7,500 - $8,999)
                amount = round(random.uniform(7500.0, 8999.0), 2)
                tx_type = random.choice(["CREDIT", "DEBIT"])
                sender = "United Kingdom"
                receiver = pick_country()
            elif tier < 0.90:
                # High structuring zone ($9,000 - $9,950)
                amount = round(random.choice([9100.0, 9250.0, 9400.0, 9500.0, 9700.0, 9850.0, 9900.0]), 2)
                tx_type = "CREDIT"
                sender = "United Kingdom"
                receiver = pick_country()
            else:
                # Large corporate / high-risk corridor ($15,000 - $85,000)
                amount = round(random.uniform(15000.0, 85000.0), 2)
                tx_type = "WIRE"
                sender = pick_country()
                receiver = pick_country()

            population.append({
                "id": tx_id,
                "customer_id": f"CUST-{random.randint(100, 140)}",
                "amount": amount,
                "transaction_amount": amount,
                "type": tx_type,
                "sender_country": sender,
                "receiver_country": receiver,
                "date": tx_time.isoformat()
            })

        self._benchmark_population = population
        return copy.deepcopy(population)

    def simulate_threshold_sweep(
        self,
        scenario_id: str,
        parameter_name: str,
        min_val: float,
        max_val: float,
        step: float,
        btl_margin_pct: float = 0.15,
        transactions: Optional[List[Dict[str, Any]]] = None,
        investigation_hours_per_alert: float = 0.75
    ) -> Dict[str, Any]:
        """
        Executes an empirical parameter sensitivity sweep.
        Calculates ATL alert curves, BTL sampling populations, and analyst workload impact.
        """
        scenario = self.scenario_engine.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found in catalog.")

        if parameter_name not in scenario.parameters:
            raise ValueError(f"Parameter '{parameter_name}' not defined for scenario {scenario_id}.")

        population = transactions if (transactions and len(transactions) > 0) else self.get_benchmark_population()
        total_tx = len(population)

        # Baseline metrics with active production threshold
        baseline_threshold = float(scenario.parameters[parameter_name])
        baseline_eval = self.scenario_engine.evaluate_batch(
            transactions=population,
            parameter_overrides={scenario_id: {parameter_name: baseline_threshold}}
        )
        baseline_alert_count = baseline_eval["total_alerts_generated"]

        # Generate sweep values
        sweep_values = []
        curr = min_val
        while curr <= max_val + 1e-6:
            sweep_values.append(round(curr, 4))
            curr += step

        sensitivity_curve = []
        for val in sweep_values:
            # Simulate ATL under tested threshold
            eval_res = self.scenario_engine.evaluate_batch(
                transactions=population,
                parameter_overrides={scenario_id: {parameter_name: val}}
            )
            atl_alert_count = eval_res["total_alerts_generated"]
            atl_rate = round((atl_alert_count / total_tx) * 100, 2) if total_tx > 0 else 0.0

            # Calculate deflation percentage relative to baseline
            if baseline_alert_count > 0:
                deflation_pct = round(((baseline_alert_count - atl_alert_count) / baseline_alert_count) * 100, 2)
            else:
                deflation_pct = 0.0

            # Calculate BTL population:
            # For lower bound / min thresholds: values between val * (1 - btl_margin) and val
            # Evaluate with lowered threshold to count false-negative candidates
            btl_threshold = round(val * (1.0 - btl_margin_pct), 4)
            btl_eval = self.scenario_engine.evaluate_batch(
                transactions=population,
                parameter_overrides={scenario_id: {parameter_name: btl_threshold}}
            )
            broadened_alerts = btl_eval["total_alerts_generated"]
            btl_count = max(0, broadened_alerts - atl_alert_count)
            btl_rate = round((btl_count / total_tx) * 100, 2) if total_tx > 0 else 0.0

            # Analyst workload hours estimated
            analyst_hours = round(atl_alert_count * investigation_hours_per_alert, 1)
            hours_saved = round((baseline_alert_count - atl_alert_count) * investigation_hours_per_alert, 1)

            sensitivity_curve.append({
                "threshold_value": val,
                "atl_alert_count": atl_alert_count,
                "atl_alert_rate_pct": atl_rate,
                "deflation_pct": deflation_pct,
                "btl_count": btl_count,
                "btl_rate_pct": btl_rate,
                "analyst_hours": analyst_hours,
                "hours_saved_vs_baseline": hours_saved,
                "is_current_baseline": (abs(val - baseline_threshold) < 1e-4)
            })

        # Extract representative BTL sample for model audit review
        btl_sample = self.get_btl_sample(
            scenario_id=scenario_id,
            parameter_name=parameter_name,
            current_threshold=baseline_threshold,
            btl_margin_pct=btl_margin_pct,
            sample_size=10,
            transactions=population
        )

        return {
            "scenario_id": scenario_id,
            "scenario_name": scenario.name,
            "parameter_name": parameter_name,
            "baseline_threshold": baseline_threshold,
            "total_evaluated_transactions": total_tx,
            "baseline_alert_count": baseline_alert_count,
            "baseline_alert_rate_pct": round((baseline_alert_count / total_tx) * 100, 2) if total_tx > 0 else 0.0,
            "btl_margin_pct": btl_margin_pct,
            "sensitivity_curve": sensitivity_curve,
            "btl_sample": btl_sample,
            "model_governance_note": (
                "Simulated in accordance with OCC 2011-12 / Federal Reserve SR 11-7 standards. "
                "Below-The-Line (BTL) testing validates model boundaries against false negatives."
            )
        }

    def get_btl_sample(
        self,
        scenario_id: str,
        parameter_name: str,
        current_threshold: float,
        btl_margin_pct: float = 0.15,
        sample_size: int = 10,
        transactions: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Samples specific transactions that fall in the Below-The-Line (BTL) window
        for supervisory testing and false-negative validation.
        """
        population = transactions if (transactions and len(transactions) > 0) else self.get_benchmark_population()
        lower_limit = current_threshold * (1.0 - btl_margin_pct)

        btl_candidates = []
        for tx in population:
            amt = float(tx.get("amount", tx.get("transaction_amount", 0.0)))
            if lower_limit <= amt < current_threshold:
                btl_candidates.append({
                    "transaction_id": tx.get("id"),
                    "customer_id": tx.get("customer_id", "N/A"),
                    "amount": amt,
                    "date": tx.get("date"),
                    "sender_country": tx.get("sender_country"),
                    "receiver_country": tx.get("receiver_country"),
                    "variance_from_threshold": round(current_threshold - amt, 2),
                    "variance_pct": round(((current_threshold - amt) / current_threshold) * 100, 1),
                    "btl_zone": f"{btl_margin_pct*100:.0f}% Margin Below Threshold"
                })

        return btl_candidates[:sample_size]
