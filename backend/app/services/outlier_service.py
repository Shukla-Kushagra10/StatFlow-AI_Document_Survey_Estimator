import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.ensemble import IsolationForest

class OutlierService:
    @staticmethod
    def detect_iqr(series: pd.Series, multiplier: float = 1.5) -> pd.Series:
        """Flags boolean mask for outliers using Interquartile Range."""
        clean_s = series.dropna()
        if len(clean_s) < 4:
            return pd.Series(False, index=series.index)
        q25 = np.percentile(clean_s, 25)
        q75 = np.percentile(clean_s, 75)
        iqr = q75 - q25
        lower_bound = q25 - (multiplier * iqr)
        upper_bound = q75 + (multiplier * iqr)
        return (series < lower_bound) | (series > upper_bound)

    @staticmethod
    def detect_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
        """Flags boolean mask for outliers using Z-score threshold."""
        clean_s = series.dropna()
        if len(clean_s) < 4 or clean_s.std() == 0:
            return pd.Series(False, index=series.index)
        z_scores = np.abs((series - clean_s.mean()) / clean_s.std())
        return z_scores > threshold

    @staticmethod
    def detect_isolation_forest(df: pd.DataFrame, columns: List[str], contamination: float = 0.05) -> pd.Series:
        """Multi-attribute anomaly detection using Isolation Forest."""
        sub_df = df[columns].copy()
        for c in columns:
            sub_df[c] = sub_df[c].fillna(sub_df[c].median())
        
        iso = IsolationForest(contamination=contamination, random_state=42)
        preds = iso.fit_predict(sub_df)
        return pd.Series(preds == -1, index=df.index)

    @classmethod
    def scan_dataset(cls, df: pd.DataFrame, method: str = "iqr") -> List[Dict[str, Any]]:
        """Scans all numeric columns and returns itemized anomaly records."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        anomalies = []

        for col in numeric_cols:
            if method == "iqr":
                mask = cls.detect_iqr(df[col])
            elif method == "zscore":
                mask = cls.detect_zscore(df[col])
            else:
                continue

            for idx in df[mask].index:
                val = df.at[idx, col]
                anomalies.append({
                    "row_index": int(idx),
                    "column": col,
                    "value": float(val) if pd.notna(val) else None,
                    "method": method.upper(),
                    "recommended_action": "Winsorize or Review"
                })

        return anomalies

    @classmethod
    def apply_treatment(cls, df: pd.DataFrame, treatments: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Applies non-destructive or user-selected outlier treatments:
        - 'winsorize': caps values to 5th/95th percentiles
        - 'remove_row': drops the outlier record
        """
        df_mod = df.copy()
        for t in treatments:
            col = t.get("column")
            action = t.get("action")
            if action == "winsorize" and col in df_mod.columns:
                p_low = df_mod[col].quantile(0.05)
                p_high = df_mod[col].quantile(0.95)
                df_mod[col] = df_mod[col].clip(lower=p_low, upper=p_high)
            elif action == "remove_row" and "row_index" in t:
                idx = t["row_index"]
                if idx in df_mod.index:
                    df_mod = df_mod.drop(index=idx)
        return df_mod.reset_index(drop=True)