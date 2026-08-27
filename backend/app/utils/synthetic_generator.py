import numpy as np
import pandas as pd
from pathlib import Path

def generate_synthetic_survey(num_records: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic MoSPI-style household & employment survey.
    Contains intentional edge cases: missing fields, outliers, and logical inconsistencies.
    """
    np.random.seed(seed)
    
    states = ["Maharashtra", "Uttar Pradesh", "Tamil Nadu", "West Bengal", "Gujarat", "Karnataka", "Bihar"]
    genders = ["Male", "Female", "Other"]
    education_levels = ["Primary", "Secondary", "Higher Secondary", "Graduate", "Postgraduate", "None"]
    employment_statuses = ["Employed", "Unemployed", "Self-Employed", "Student", "Retired"]

    respondent_ids = [f"RSP-2025-{i:05d}" for i in range(1, num_records + 1)]
    ages = np.random.randint(15, 85, size=num_records)
    gender_choices = np.random.choice(genders, size=num_records, p=[0.50, 0.48, 0.02])
    state_choices = np.random.choice(states, size=num_records)
    edu_choices = np.random.choice(education_levels, size=num_records)
    emp_choices = np.random.choice(employment_statuses, size=num_records, p=[0.45, 0.15, 0.20, 0.10, 0.10])
    
    # Base Income with lognormal distribution
    income = np.random.lognormal(mean=10.2, sigma=0.65, size=num_records).round(2)
    # Adjust income according to employment
    for i in range(num_records):
        if emp_choices[i] in ["Student", "Unemployed"]:
            income[i] = 0.0 if np.random.rand() > 0.1 else income[i] * 0.1

    household_size = np.random.poisson(lam=4.2, size=num_records)
    household_size = np.clip(household_size, 1, 15)

    # Base design weights (Sampling probability inversely proportional)
    survey_weight = np.random.uniform(10.5, 125.0, size=num_records).round(4)
    satisfaction_score = np.random.randint(1, 11, size=num_records).astype(float)
    
    dates = pd.date_range(start="2024-01-01", periods=180).to_series()
    survey_dates = np.random.choice(dates.dt.strftime("%Y-%m-%d"), size=num_records)

    df = pd.DataFrame({
        "respondent_id": respondent_ids,
        "age": ages,
        "gender": gender_choices,
        "state": state_choices,
        "education": edu_choices,
        "employment_status": emp_choices,
        "income": income,
        "household_size": household_size,
        "survey_weight": survey_weight,
        "satisfaction_score": satisfaction_score,
        "survey_date": survey_dates
    })

    # INTENTIONAL DATA QUALITY FLAWS FOR DEMONSTRATION & BENCHMARKING:
    # 1. Missing values (~5% in income, 3% in satisfaction_score, 2% in education)
    df.loc[np.random.choice(df.index, size=int(0.05 * num_records), replace=False), "income"] = np.nan
    df.loc[np.random.choice(df.index, size=int(0.03 * num_records), replace=False), "satisfaction_score"] = np.nan
    df.loc[np.random.choice(df.index, size=int(0.02 * num_records), replace=False), "education"] = None

    # 2. Extreme Outliers (5 extreme income values)
    outlier_idx = np.random.choice(df.index, size=5, replace=False)
    df.loc[outlier_idx, "income"] = df["income"].max() * np.random.uniform(8.0, 15.0, size=5)

    # 3. Rule Inconsistencies (e.g., Age < 18 but status is Retired; or Age > 75 but status is Student)
    df.loc[0, "age"] = 16
    df.loc[0, "employment_status"] = "Retired"
    df.loc[1, "age"] = 82
    df.loc[1, "employment_status"] = "Student"

    # 4. Duplicate rows (inject 3 duplicate entries)
    duplicates = df.iloc[10:13].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    return df

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "uploads"
    out_dir.mkdir(parents=True, exist_ok=True)
    synthetic_df = generate_synthetic_survey(1000)
    synthetic_df.to_csv(out_dir / "synthetic_survey_sample.csv", index=False)
    print(f"Synthetic dataset created successfully with {len(synthetic_df)} records.")