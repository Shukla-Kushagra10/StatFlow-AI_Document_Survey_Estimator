import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

class WeightingService:
    @staticmethod
    def post_stratify(
        df: pd.DataFrame,
        strata_col: str,
        pop_distribution: Dict[str, float],
        base_weight_col: Optional[str] = None
    ) -> pd.Series:
        """
        Adjusts weights so that the weighted sample proportion in each stratum
        matches the known population stratum totals/proportions.
        """
        df_work = df.copy()
        if base_weight_col and base_weight_col in df_work.columns:
            base_w = df_work[base_weight_col].fillna(1.0).astype(float)
        else:
            base_w = pd.Series(1.0, index=df_work.index)

        df_work["_base_w"] = base_w
        adjusted_weights = df_work["_base_w"].copy()

        # Compute current weighted sum per stratum
        stratum_sample_totals = df_work.groupby(strata_col)["_base_w"].sum()
        total_pop_target = sum(pop_distribution.values())

        for stratum_val, target_n in pop_distribution.items():
            mask = df_work[strata_col] == stratum_val
            sample_w_sum = stratum_sample_totals.get(stratum_val, 0)
            
            if sample_w_sum > 0:
                # Calibration adjustment factor
                factor = (target_n / total_pop_target) * (df_work["_base_w"].sum() / sample_w_sum)
                adjusted_weights.loc[mask] = df_work.loc[mask, "_base_w"] * factor

        return adjusted_weights

    @staticmethod
    def rake(
        df: pd.DataFrame,
        margins: Dict[str, Dict[str, float]],
        base_weight_col: Optional[str] = None,
        max_iter: int = 50,
        tol: float = 1e-4
    ) -> pd.Series:
        """
        Iterative Proportional Fitting (Raking) across multiple marginal distributions.
        margins: e.g. {'gender': {'Male': 0.51, 'Female': 0.49}, 'education': {...}}
        """
        df_work = df.copy()
        if base_weight_col and base_weight_col in df_work.columns:
            weights = df_work[base_weight_col].fillna(1.0).astype(float).values
        else:
            weights = np.ones(len(df_work), dtype=float)

        for _ in range(max_iter):
            max_diff = 0.0
            for col, target_props in margins.items():
                if col not in df_work.columns:
                    continue
                
                total_current_w = np.sum(weights)
                if total_current_w == 0:
                    continue
                    
                for cat, target_p in target_props.items():
                    mask = (df_work[col] == cat).values
                    cat_w_sum = np.sum(weights[mask])
                    
                    if cat_w_sum > 0:
                        current_p = cat_w_sum / total_current_w
                        diff = abs(current_p - target_p)
                        if diff > max_diff:
                            max_diff = diff
                        
                        adjustment = (target_p * total_current_w) / cat_w_sum
                        weights[mask] *= adjustment

            if max_diff < tol:
                break

        return pd.Series(weights, index=df.index)

    @staticmethod
    def calculate_weight_diagnostics(weights: pd.Series) -> Dict[str, Any]:
        """Calculates diagnostics including Kish's Effective Sample Size."""
        w = weights.dropna().values
        n = len(w)
        if n == 0 or np.sum(w) == 0:
            return {"mean": 0, "min": 0, "max": 0, "cv": 0, "eff_sample_size": 0}

        sum_w = np.sum(w)
        sum_w_sq = np.sum(w ** 2)
        # Kish's formula for design effect approximation
        deff = (n * sum_w_sq) / (sum_w ** 2) if sum_w ** 2 > 0 else 1.0
        eff_n = n / deff if deff > 0 else n

        return {
            "count": int(n),
            "mean": round(float(np.mean(w)), 4),
            "min": round(float(np.min(w)), 4),
            "max": round(float(np.max(w)), 4),
            "std": round(float(np.std(w)), 4),
            "cv": round(float(np.std(w) / np.mean(w)), 4) if np.mean(w) > 0 else 0,
            "design_effect_approx": round(float(deff), 4),
            "effective_sample_size": round(float(eff_n), 2)
        }