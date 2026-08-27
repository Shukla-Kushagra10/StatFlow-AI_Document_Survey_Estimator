from typing import Dict, Any, List
import pandas as pd
import numpy as np

class InsightService:
    @staticmethod
    def generate_rule_based_insights(profile: Dict[str, Any], estimation_sample: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generates deterministic, non-hallucinatory narrative summaries based
        strictly on calculated distributions, quality metrics, and sample estimates.
        """
        total_rows = profile.get("total_rows", 0)
        total_cols = profile.get("total_columns", 0)
        q_score = profile.get("quality_score", {}).get("overall_score", 0.0)
        
        # 1. Executive Summary
        exec_summary = (
            f"The dataset comprises {total_rows:,} survey records spanning {total_cols} attributes. "
            f"Overall structural quality scored at {q_score}/100. "
        )
        if q_score >= 85:
            exec_summary += "The survey input demonstrates high data integrity with minimal preprocessing needed."
        elif q_score >= 65:
            exec_summary += "Moderate data anomalies detected; imputation and outlier cap operations are advised."
        else:
            exec_summary += "Significant data quality concerns identified across missingness and duplicate profiles."

        # 2. Key Data Quality Findings
        findings = []
        col_profiles = profile.get("columns", {})
        for col_name, col_data in col_profiles.items():
            m_pct = col_data.get("missing_percentage", 0.0)
            if m_pct > 0.0:
                findings.append(f"Attribute '{col_name}' exhibits {m_pct}% missingness ({col_data.get('missing_count')} records).")
            
            if col_data.get("type") == "numeric":
                mean_val = col_data.get("mean")
                med_val = col_data.get("median")
                if mean_val is not None and med_val is not None and abs(mean_val - med_val) > (0.5 * (med_val or 1)):
                    findings.append(f"Attribute '{col_name}' displays substantial skewness (Mean: {mean_val}, Median: {med_val}).")

        # 3. Statistical Findings (if estimation provided)
        stat_insights = []
        if estimation_sample and "unweighted" in estimation_sample and "weighted" in estimation_sample:
            target = estimation_sample.get("target_variable")
            unw = estimation_sample.get("unweighted", {})
            w = estimation_sample.get("weighted", {})
            if unw and w:
                diff = w["point_estimate"] - unw["point_estimate"]
                pct_diff = (diff / unw["point_estimate"] * 100) if unw["point_estimate"] != 0 else 0
                stat_insights.append(
                    f"Applying survey weights altered the point estimate for '{target}' from "
                    f"{unw['point_estimate']:,} to {w['point_estimate']:,} (a {pct_diff:+.2f}% adjustment)."
                )
                stat_insights.append(
                    f"Weighted 95% Confidence Interval is [{w['confidence_interval'][0]:,}, {w['confidence_interval'][1]:,}], "
                    f"with a Margin of Error of ±{w['margin_of_error']}."
                )

        return {
            "executive_summary": exec_summary,
            "data_quality_findings": findings,
            "statistical_observations": stat_insights,
            "recommendations": [
                "Verify survey sampling weights against external census totals where available.",
                "Review multi-variable outliers before final statistical publishing.",
                "Standardize categorical codes for consistent administrative aggregation."
            ]
        }