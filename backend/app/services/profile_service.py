import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List

class ProfileService:
    @staticmethod
    def load_dataset(file_path: Path) -> pd.DataFrame:
        """Loads dataset from CSV or Excel formats safely."""
        suffix = file_path.suffix.lower()
        if suffix == ".csv":
            try:
                return pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                return pd.read_csv(file_path, encoding="latin1")
        elif suffix in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}. Expected CSV or Excel.")

    @staticmethod
    def calculate_quality_score(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates an application-defined transparent Data Quality Score (0 to 100).
        Penalties:
          - Missingness: up to 35 points deduction
          - Duplicates: up to 25 points deduction
          - Statistical outliers (numeric): up to 20 points deduction
        """
        total_cells = df.size
        total_rows = len(df)
        
        if total_cells == 0 or total_rows == 0:
            return {
                "overall_score": 0.0,
                "missing_penalty": 0.0,
                "duplicate_penalty": 0.0,
                "outlier_penalty": 0.0,
                "validation_penalty": 0.0,
                "explanation": "Empty dataset."
            }

        # 1. Missingness penalty
        missing_count = int(df.isna().sum().sum())
        missing_ratio = missing_count / total_cells
        missing_penalty = round(min(35.0, missing_ratio * 100 * 1.5), 2)

        # 2. Duplicate penalty
        dup_count = int(df.duplicated().sum())
        dup_ratio = dup_count / total_rows
        duplicate_penalty = round(min(25.0, dup_ratio * 100 * 2.0), 2)

        # 3. Outlier estimation penalty (IQR based across numeric columns)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_count = 0
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) > 4:
                q25, q75 = np.percentile(series, 25), np.percentile(series, 75)
                iqr = q75 - q25
                if iqr > 0:
                    outliers = series[(series < (q25 - 1.5 * iqr)) | (series > (q75 + 1.5 * iqr))]
                    outlier_count += len(outliers)

        outlier_ratio = outlier_count / total_cells if total_cells > 0 else 0
        outlier_penalty = round(min(20.0, outlier_ratio * 100 * 2.0), 2)

        # Base quality deduction
        overall_score = max(0.0, round(100.0 - (missing_penalty + duplicate_penalty + outlier_penalty), 2))

        explanation = (
            f"Quality Score computed at {overall_score}/100. "
            f"Deductions: Missing values (-{missing_penalty} pts), "
            f"Duplicate records (-{duplicate_penalty} pts), "
            f"Detected outliers (-{outlier_penalty} pts)."
        )

        return {
            "overall_score": overall_score,
            "missing_penalty": missing_penalty,
            "duplicate_penalty": duplicate_penalty,
            "outlier_penalty": outlier_penalty,
            "validation_penalty": 0.0,
            "explanation": explanation
        }

    @classmethod
    def generate_full_profile(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Generates comprehensive dataset profiling statistics."""
        total_rows, total_cols = df.shape
        num_duplicates = int(df.duplicated().sum())
        memory_usage_bytes = int(df.memory_usage(deep=True).sum())

        column_profiles = {}
        numeric_columns = []
        categorical_columns = []
        date_columns = []

        for col in df.columns:
            series = df[col]
            missing_count = int(series.isna().sum())
            missing_pct = round((missing_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
            unique_count = int(series.nunique(dropna=True))

            col_info: Dict[str, Any] = {
                "name": col,
                "dtype": str(series.dtype),
                "missing_count": missing_count,
                "missing_percentage": missing_pct,
                "unique_count": unique_count,
                "sample_values": series.dropna().head(5).tolist()
            }

            if pd.api.types.is_numeric_dtype(series):
                numeric_columns.append(col)
                clean_series = series.dropna()
                if len(clean_series) > 0:
                    col_info.update({
                        "type": "numeric",
                        "min": float(clean_series.min()),
                        "max": float(clean_series.max()),
                        "mean": round(float(clean_series.mean()), 4),
                        "median": round(float(clean_series.median()), 4),
                        "std": round(float(clean_series.std()), 4) if len(clean_series) > 1 else 0.0,
                        "q25": round(float(clean_series.quantile(0.25)), 4),
                        "q75": round(float(clean_series.quantile(0.75)), 4)
                    })
                else:
                    col_info.update({"type": "numeric", "min": None, "max": None, "mean": None, "median": None, "std": None})

            elif pd.api.types.is_datetime64_any_dtype(series):
                date_columns.append(col)
                col_info["type"] = "datetime"
            else:
                sample = series.dropna().astype(str).head(10)
                is_date = False
                if len(sample) > 0:
                    try:
                        pd.to_datetime(sample)
                        is_date = True
                    except Exception:
                        is_date = False
                
                if is_date:
                    date_columns.append(col)
                    col_info["type"] = "datetime"
                else:
                    categorical_columns.append(col)
                    val_counts = series.value_counts(dropna=True).head(10).to_dict()
                    col_info.update({
                        "type": "categorical",
                        "top_categories": {str(k): int(v) for k, v in val_counts.items()}
                    })

            column_profiles[col] = col_info

        quality_report = cls.calculate_quality_score(df)

        return {
            "total_rows": total_rows,
            "total_columns": total_cols,
            "duplicate_rows": num_duplicates,
            "memory_usage_bytes": memory_usage_bytes,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "date_columns": date_columns,
            "quality_score": quality_report,
            "columns": column_profiles
        }