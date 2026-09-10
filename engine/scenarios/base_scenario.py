"""
ScoreSentinel Base Scenario Interface (v2.0)
Part of the ScoreSentinel Enterprise AML Rules Engine
Authored by Atul Krishnan, CAMS
"""

import copy
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional

class BaseScenario:
    """
    Abstract base class for all enterprise AML detection scenarios.
    Provides parameter management, threshold override support, and
    standardized alert generation conforming to regulatory audit standards.
    """

    def __init__(self, config: Dict[str, Any]):
        self.scenario_id: str = config.get("scenario_id", "SCEN-GENERIC")
        self.name: str = config.get("name", "Generic Scenario")
        self.typology: str = config.get("typology", "AML Typology")
        self.enabled: bool = config.get("enabled", True)
        self.severity: str = config.get("severity", "MEDIUM")
        self.recommended_action: str = config.get("recommended_action", "INVESTIGATE")
        self.regulatory_citation: str = config.get("regulatory_citation", "BSA / FATF")
        self.description: str = config.get("description", "")
        
        # Store default parameters immutably, and maintain active runtime copy
        self.default_parameters: Dict[str, Any] = copy.deepcopy(config.get("parameters", {}))
        self.parameters: Dict[str, Any] = copy.deepcopy(self.default_parameters)
        self.parameter_definitions: Dict[str, str] = copy.deepcopy(config.get("parameter_definitions", {}))

    def set_parameters(self, overrides: Dict[str, Any]) -> None:
        """Dynamically updates active scenario parameters (used in threshold tuning)."""
        if not overrides:
            return
        for k, v in overrides.items():
            if k in self.parameters:
                # Type coercion based on default parameter type
                expected_type = type(self.default_parameters[k])
                try:
                    if expected_type in (int, float) and isinstance(v, (int, float, str)):
                        self.parameters[k] = expected_type(v)
                    elif expected_type is bool and isinstance(v, (bool, str)):
                        self.parameters[k] = (str(v).lower() in ("true", "1"))
                    else:
                        self.parameters[k] = v
                except (ValueError, TypeError):
                    self.parameters[k] = v

    def reset_parameters(self) -> None:
        """Restores scenario parameters back to baseline default values."""
        self.parameters = copy.deepcopy(self.default_parameters)

    @staticmethod
    def parse_datetime(dt_val: Any) -> datetime:
        """Normalizes string or date objects into datetime instances."""
        if isinstance(dt_val, datetime):
            return dt_val
        if isinstance(dt_val, date):
            return datetime.combine(dt_val, datetime.min.time())
        if isinstance(dt_val, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(dt_val.replace("Z", "+00:00"))
            except ValueError:
                # Fallback common formats
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
                    try:
                        return datetime.strptime(dt_val, fmt)
                    except ValueError:
                        pass
        return datetime.now(timezone.utc)

    def build_result(
        self,
        triggered: bool,
        breach_summary: str,
        metrics: Dict[str, Any],
        triggering_transactions: List[Dict[str, Any]],
        custom_severity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Formats a standardized, deterministic alert output compliant with
        institutional audit requirements and SR 11-7 model transparency.
        """
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.name,
            "typology": self.typology,
            "triggered": triggered,
            "severity": (custom_severity or self.severity) if triggered else "NONE",
            "recommended_action": self.recommended_action if triggered else "NO_ACTION",
            "regulatory_citation": self.regulatory_citation,
            "breach_summary": breach_summary if triggered else "Threshold parameters not breached.",
            "evaluated_parameters": copy.deepcopy(self.parameters),
            "metrics": metrics,
            "triggering_transaction_count": len(triggering_transactions) if triggered else 0,
            "triggering_transactions": triggering_transactions if triggered else [],
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }

    def evaluate(
        self,
        current_tx: Dict[str, Any],
        history: Optional[List[Dict[str, Any]]] = None,
        customer_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Abstract evaluation entry point to be implemented by concrete scenarios."""
        raise NotImplementedError("Subclasses must implement evaluate()")
