import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from sklearn.impute import KNNImputer
from sklearn.linear_model import LinearRegression

class CleanService:
    @staticmethod
    def handle_duplicates(df: pd.DataFrame, action: str = "remove") -> pd.DataFrame:
        """Removes or flags duplicate records in the dataset."""
        df_cleaned = df.copy()
        if action == "remove":
            df_cleaned = df_cleaned.drop_duplicates().reset_index(drop=True)
        return df_cleaned

    @staticmethod
    def impute_column(df: pd.DataFrame, column: str, method: str, **kwargs) -> pd.DataFrame:
        """
        Imputes missing values using statistical and ML strategies:
        - 'mean', 'median', 'mode'
        - 'constant' (requires 'fill_value')
        - 'knn' (KNN-based imputation using numeric context)
        - 'regression' (predictive regression using complete numeric features)
        - 'drop' (removes rows where target column is missing)
        """
        df_cleaned = df.copy()
        if column not in df_cleaned.columns:
            raise ValueError(f"Column '{column}' does not exist in the dataset.")

        if not df_cleaned[column].isna().any():
            return df_cleaned

        if method == "mean":
            if not pd.api.types.is_numeric_dtype(df_cleaned[column]):
                raise ValueError(f"Mean imputation is only valid for numeric columns: {column}")
            fill_val = df_cleaned[column].mean()
            df_cleaned[column] = df_cleaned[column].fillna(fill_val)

        elif method == "median":
            if not pd.api.types.is_numeric_dtype(df_cleaned[column]):
                raise ValueError(f"Median imputation is only valid for numeric columns: {column}")
            fill_val = df_cleaned[column].median()
            df_cleaned[column] = df_cleaned[column].fillna(fill_val)

        elif method == "mode":
            mode_val = df_cleaned[column].mode()
            if not mode_val.empty:
                df_cleaned[column] = df_cleaned[column].fillna(mode_val[0])

        elif method == "constant":
            fill_val = kwargs.get("fill_value", "Missing")
            df_cleaned[column] = df_cleaned[column].fillna(fill_val)

        elif method == "drop":
            df_cleaned = df_cleaned.dropna(subset=[column]).reset_index(drop=True)

        elif method == "knn":
            n_neighbors = kwargs.get("n_neighbors", 5)
            numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
            if column not in numeric_cols:
                raise ValueError(f"KNN imputation is currently restricted to numeric columns: {column}")
            
            # Check if there are sufficient numeric columns to infer from
            imputer = KNNImputer(n_neighbors=min(n_neighbors, max(1, len(df_cleaned) - 1)))
            df_cleaned[numeric_cols] = imputer.fit_transform(df_cleaned[numeric_cols])

        elif method == "regression":
            numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
            feature_cols = [c for c in numeric_cols if c != column]
            
            if not feature_cols:
                raise ValueError(f"Regression imputation requires at least one other numeric feature column.")
            
            # Temporary median fill for feature columns to train regressor
            features_clean = df_cleaned[feature_cols].apply(lambda x: x.fillna(x.median()))
            
            train_mask = df_cleaned[column].notna()
            test_mask = df_cleaned[column].isna()

            if train_mask.sum() < 3:
                raise ValueError(f"Insufficient non-missing data points to train regression on {column}.")

            reg = LinearRegression()
            reg.fit(features_clean[train_mask], df_cleaned.loc[train_mask, column])
            predicted = reg.predict(features_clean[test_mask])
            df_cleaned.loc[test_mask, column] = predicted

        else:
            raise ValueError(f"Unsupported imputation method: {method}")

        return df_cleaned

    @classmethod
    def apply_batch_cleaning(cls, df: pd.DataFrame, operations: List[Dict[str, Any]]) -> pd.DataFrame:
        """Applies a sequence of approved cleaning operations."""
        df_result = df.copy()
        for op in operations:
            op_type = op.get("type")
            if op_type == "deduplicate":
                df_result = cls.handle_duplicates(df_result, action=op.get("action", "remove"))
            elif op_type == "impute":
                df_result = cls.impute_column(
                    df_result,
                    column=op["column"],
                    method=op["method"],
                    fill_value=op.get("fill_value"),
                    n_neighbors=op.get("n_neighbors", 5)
                )
            elif op_type == "strip_whitespace":
                str_cols = df_result.select_dtypes(include=["object", "string"]).columns
                for col in str_cols:
                    df_result[col] = df_result[col].astype(str).str.strip()
        return df_result