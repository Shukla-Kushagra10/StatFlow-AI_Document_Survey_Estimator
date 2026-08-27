import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List, Optional

class EstimationService:
    @staticmethod
    def estimate_parameter(
        df: pd.DataFrame,
        target_col: str,
        weight_col: Optional[str] = None,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Calculates descriptive and survey-weighted parameter estimates with
        analytical standard errors and Margins of Error (MoE).
        """
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not present in dataframe.")

        # Filter complete pairs
        cols_to_use = [target_col] + ([weight_col] if weight_col and weight_col in df.columns else [])
        valid_df = df[cols_to_use].dropna().copy()
        
        y = valid_df[target_col].values
        n = len(y)
        if n < 2:
            raise ValueError(f"Insufficient observations in column '{target_col}'.")

        # Determine if continuous or binary/categorical
        is_numeric = pd.api.types.is_numeric_dtype(df[target_col])
        z_crit = stats.norm.ppf((1 + confidence_level) / 2)

        # 1. Unweighted Calculations
        unw_mean = np.mean(y) if is_numeric else 0.0
        unw_var = np.var(y, ddof=1) if is_numeric else 0.0
        unw_se = np.sqrt(unw_var / n) if is_numeric else 0.0
        unw_moe = z_crit * unw_se
        unw_ci = [float(unw_mean - unw_moe), float(unw_mean + unw_moe)] if is_numeric else [0, 0]

        result = {
            "target_variable": target_col,
            "sample_size": int(n),
            "confidence_level": confidence_level,
            "unweighted": {
                "point_estimate": round(float(unw_mean), 4) if is_numeric else None,
                "variance": round(float(unw_var), 4) if is_numeric else None,
                "standard_error": round(float(unw_se), 4) if is_numeric else None,
                "margin_of_error": round(float(unw_moe), 4) if is_numeric else None,
                "confidence_interval": [round(c, 4) for c in unw_ci]
            }
        }

        # 2. Weighted Calculations
        if weight_col and weight_col in valid_df.columns:
            w = valid_df[weight_col].values
            sum_w = np.sum(w)

            if sum_w > 0 and is_numeric:
                w_mean = np.sum(w * y) / sum_w
                # Taylor Linearization variance estimation for survey weighted mean
                residuals = y - w_mean
                # Variance of weighted mean formula: (n / (n-1)) * (sum(w^2 * (y - w_mean)^2)) / (sum(w)^2)
                taylor_var = (n / (n - 1)) * (np.sum((w ** 2) * (residuals ** 2))) / (sum_w ** 2)
                w_se = np.sqrt(taylor_var)
                w_moe = z_crit * w_se
                w_ci = [float(w_mean - w_moe), float(w_mean + w_moe)]

                result["weighted"] = {
                    "weight_variable_used": weight_col,
                    "point_estimate": round(float(w_mean), 4),
                    "variance": round(float(taylor_var), 6),
                    "standard_error": round(float(w_se), 4),
                    "margin_of_error": round(float(w_moe), 4),
                    "confidence_interval": [round(c, 4) for c in w_ci],
                    "total_weighted_population": round(float(sum_w), 2)
                }
            else:
                result["weighted"] = None
        else:
            result["weighted"] = None

        return result