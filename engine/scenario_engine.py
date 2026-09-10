"""
ScoreSentinel Scenario Coordinator & Engine (v2.0)
Part of the ScoreSentinel Enterprise AML Rules Engine
Authored by Atul Krishnan, CAMS
"""

import os
import json
import copy
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from .scenarios import (
    BaseScenario,
    StructuringScenario,
    RapidMovementScenario,
    CorridorScenario
)

class ScenarioEngine:
    """
    Enterprise AML Scenario Coordinator.
    Loads and executes configurable detection scenarios (SCEN-STRUC-01, SCEN-VEL-01, SCEN-CORR-01),
    supports dynamic parameter overrides for 2LoD threshold tuning, and produces
    deterministic, audit-ready alert packages.
    """

    SCENARIO_CLASS_MAP = {
        "SCEN-STRUC-01": StructuringScenario,
        "SCEN-VEL-01": RapidMovementScenario,
        "SCEN-CORR-01": CorridorScenario
    }

    def __init__(self, catalog_path: Optional[str] = None):
        self.catalog_path = catalog_path or self._resolve_default_catalog_path()
        self.catalog_metadata: Dict[str, Any] = {}
        self.scenarios: Dict[str, BaseScenario] = {}
        self.load_catalog()

    def _resolve_default_catalog_path(self) -> str:
        """Locates the default rules/scenario_catalog.json file."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "rules", "scenario_catalog.json")

    def load_catalog(self, catalog_path: Optional[str] = None) -> None:
        """Loads or reloads scenario catalog from JSON file."""
        target_path = catalog_path or self.catalog_path
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Scenario catalog file not found at: {target_path}")

        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.catalog_metadata = {
            "catalog_version": data.get("catalog_version", "2.0.0"),
            "framework": data.get("framework", "ScoreSentinel AML / SR 11-7"),
            "effective_date": data.get("effective_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        }

        self.scenarios = {}
        for scenario_cfg in data.get("scenarios", []):
            scen_id = scenario_cfg.get("scenario_id")
            cls = self.SCENARIO_CLASS_MAP.get(scen_id, BaseScenario)
            self.scenarios[scen_id] = cls(scenario_cfg)

    def get_catalog(self) -> Dict[str, Any]:
        """Returns the current catalog overview with active parameters and metadata."""
        scenario_list = []
        for scen_id, inst in self.scenarios.items():
            scenario_list.append({
                "scenario_id": inst.scenario_id,
                "name": inst.name,
                "typology": inst.typology,
                "enabled": inst.enabled,
                "severity": inst.severity,
                "recommended_action": inst.recommended_action,
                "regulatory_citation": inst.regulatory_citation,
                "description": inst.description,
                "parameters": copy.deepcopy(inst.parameters),
                "default_parameters": copy.deepcopy(inst.default_parameters),
                "parameter_definitions": copy.deepcopy(inst.parameter_definitions)
            })

        return {
            "metadata": copy.deepcopy(self.catalog_metadata),
            "scenario_count": len(scenario_list),
            "scenarios": scenario_list
        }

    def get_scenario(self, scenario_id: str) -> Optional[BaseScenario]:
        """Retrieves a specific scenario instance by ID."""
        return self.scenarios.get(scenario_id)

    def update_parameters(self, scenario_id: str, parameters: Dict[str, Any]) -> bool:
        """Dynamically tunes parameters for a specific scenario."""
        if scenario_id in self.scenarios:
            self.scenarios[scenario_id].set_parameters(parameters)
            return True
        return False

    def reset_parameters(self, scenario_id: Optional[str] = None) -> None:
        """Resets a specific scenario or all scenarios to default baseline."""
        if scenario_id:
            if scenario_id in self.scenarios:
                self.scenarios[scenario_id].reset_parameters()
        else:
            for inst in self.scenarios.values():
                inst.reset_parameters()

    def evaluate_transaction(
        self,
        transaction: Dict[str, Any],
        history: Optional[List[Dict[str, Any]]] = None,
        customer_profile: Optional[Dict[str, Any]] = None,
        parameter_overrides: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a transaction and customer history against all enabled scenarios.
        Accepts transient parameter_overrides for on-the-fly 2LoD simulation.
        """
        history = history or []
        customer_profile = customer_profile or {}
        parameter_overrides = parameter_overrides or {}

        # Backup current parameters if transient overrides are passed
        original_params = {}
        for scen_id, overrides in parameter_overrides.items():
            if scen_id in self.scenarios:
                original_params[scen_id] = copy.deepcopy(self.scenarios[scen_id].parameters)
                self.scenarios[scen_id].set_parameters(overrides)

        try:
            alerts = []
            scenario_results = []
            severity_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
            max_severity = "NONE"
            max_severity_rank = 0

            for scen_id, scenario in self.scenarios.items():
                if not scenario.enabled:
                    continue

                res = scenario.evaluate(transaction, history=history, customer_profile=customer_profile)
                scenario_results.append(res)

                if res.get("triggered"):
                    alerts.append(res)
                    sev = res.get("severity", "LOW")
                    rank = severity_order.get(sev, 0)
                    if rank > max_severity_rank:
                        max_severity_rank = rank
                        max_severity = sev

            has_breach = len(alerts) > 0
            tx_id = transaction.get("id", transaction.get("transaction_id", "tx_eval"))

            return {
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "transaction_id": tx_id,
                "has_breach": has_breach,
                "alert_count": len(alerts),
                "max_severity": max_severity,
                "alerts": alerts,
                "all_results": scenario_results
            }

        finally:
            # Restore parameters after simulation run
            for scen_id, orig in original_params.items():
                if scen_id in self.scenarios:
                    self.scenarios[scen_id].parameters = orig

    def evaluate_batch(
        self,
        transactions: List[Dict[str, Any]],
        history: Optional[List[Dict[str, Any]]] = None,
        customer_profile: Optional[Dict[str, Any]] = None,
        parameter_overrides: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Batch evaluation runner. Progressively appends transactions to rolling history,
        measuring alert counts, breach distributions, and scenario trigger rates.
        """
        rolling_history = list(history or [])
        results = []
        total_alerts = 0
        scenario_trigger_counts: Dict[str, int] = {scen_id: 0 for scen_id in self.scenarios}

        for tx in transactions:
            eval_res = self.evaluate_transaction(
                tx,
                history=rolling_history,
                customer_profile=customer_profile,
                parameter_overrides=parameter_overrides
            )
            results.append(eval_res)
            if eval_res["has_breach"]:
                total_alerts += eval_res["alert_count"]
                for alert in eval_res["alerts"]:
                    scen_id = alert["scenario_id"]
                    scenario_trigger_counts[scen_id] = scenario_trigger_counts.get(scen_id, 0) + 1

            # Append evaluated tx to rolling history
            rolling_history.append(tx)

        total_tx = len(transactions)
        alert_rate = (total_alerts / total_tx) if total_tx > 0 else 0.0

        return {
            "total_transactions_evaluated": total_tx,
            "total_alerts_generated": total_alerts,
            "overall_alert_rate": round(alert_rate, 4),
            "scenario_trigger_distribution": scenario_trigger_counts,
            "evaluations": results
        }
