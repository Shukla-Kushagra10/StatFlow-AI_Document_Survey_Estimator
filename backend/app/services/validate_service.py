import pandas as pd
from typing import Dict, Any, List

class ValidateService:
    @staticmethod
    def evaluate_rules(df: pd.DataFrame, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluates domain and cross-column logic:
        Rule schema:
          {
             "name": "Age check",
             "rule_type": "range",
             "column": "age",
             "min_val": 0,
             "max_val": 120
          }
          or
          {
             "name": "Employment Skip Pattern",
             "rule_type": "cross_column",
             "condition": "age < 18 and employment_status == 'Retired'"
          }
        """
        violations = []

        for rule in rules:
            r_name = rule.get("name", "Unnamed Rule")
            r_type = rule.get("rule_type")

            if r_type == "range":
                col = rule["column"]
                if col in df.columns:
                    min_v = rule.get("min_val", -float("inf"))
                    max_v = rule.get("max_val", float("inf"))
                    invalid = df[(df[col] < min_v) | (df[col] > max_v)]
                    for idx in invalid.index:
                        violations.append({
                            "rule_name": r_name,
                            "row_index": int(idx),
                            "column": col,
                            "value": str(df.at[idx, col]),
                            "message": f"Value out of permissible bounds [{min_v}, {max_v}]."
                        })

            elif r_type == "cross_column":
                query_str = rule.get("condition", "")
                try:
                    invalid = df.query(query_str)
                    for idx in invalid.index:
                        violations.append({
                            "rule_name": r_name,
                            "row_index": int(idx),
                            "column": "Multiple",
                            "value": "Logic mismatch",
                            "message": f"Violated consistency rule: {query_str}"
                        })
                except Exception as e:
                    violations.append({
                        "rule_name": r_name,
                        "row_index": -1,
                        "column": "N/A",
                        "value": "Error",
                        "message": f"Malformed rule query expression: {str(e)}"
                    })

        return violations

    @classmethod
    def get_standard_mospi_rules(cls) -> List[Dict[str, Any]]:
        """Provides default domain integrity checks for standard demographic surveys."""
        return [
            {
                "name": "Age Bound Validation",
                "rule_type": "range",
                "column": "age",
                "min_val": 0,
                "max_val": 120
            },
            {
                "name": "Income Non-Negative",
                "rule_type": "range",
                "column": "income",
                "min_val": 0,
                "max_val": 100000000
            },
            {
                "name": "Household Size Validation",
                "rule_type": "range",
                "column": "household_size",
                "min_val": 1,
                "max_val": 30
            },
            {
                "name": "Minor Retirement Conflict",
                "rule_type": "cross_column",
                "condition": "age < 18 and employment_status == 'Retired'"
            }
        ]