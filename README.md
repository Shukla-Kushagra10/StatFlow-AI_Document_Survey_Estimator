# StatFlow AI

### AI-Enhanced Application for Automated Data Preparation, Estimation, and Report Writing

> **StatFlow AI** is an end-to-end, low-code statistical processing and automated reporting engine designed to simplify complex survey-data workflows through automated data preparation, validation, weighting, estimation, analytical insights, and standardized report generation.

---

## 📌 Executive Summary

Official statistical agencies such as **MoSPI** routinely handle complex, multi-strata survey microdata that require substantial manual preparation, cleaning, domain-rule validation, survey weighting, estimation, and reporting before dissemination.

Traditional manual workflows are:

* Time-consuming
* Vulnerable to human error
* Difficult to reproduce
* Dependent on manual statistical processing
* Prone to inconsistencies in data-quality checks
* Difficult to audit

**StatFlow AI** addresses these challenges by providing an end-to-end statistical processing pipeline.

The platform automates:

1. Data ingestion and profiling
2. Data-quality assessment
3. Non-destructive data cleaning
4. Statistical and ML-based imputation
5. Domain-rule validation
6. Outlier detection and treatment
7. Survey-weight calibration
8. Statistical estimation
9. Uncertainty and Margin of Error calculations
10. Deterministic analytical insights
11. PDF and HTML report generation
12. Immutable audit logging

The system is designed around the principles of **transparency, reproducibility, explainability, and statistical reliability**.

---

# 🏛️ High-Level System Architecture

```text
+---------------------------------------------------------------------------------------+
|                                     CLIENT LAYER                                      |
|                                                                                       |
|   +-------------------------------------------------------------------------------+   |
|   |                       React 18 Single-Page Application                        |   |
|   |                  (Tailwind CSS, Lucide Icons, Axios Client)                   |   |
|   +---------------------------------------+---------------------------------------+   |
+-------------------------------------------|-------------------------------------------+
                                            |
                              REST API / JSON / Multipart HTTP
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                                    API GATEWAY LAYER                                  |
|                                                                                       |
|   +-------------------------------------------------------------------------------+   |
|   |                     FastAPI Asynchronous Backend Engine                       |   |
|   |                  (CORS, Pydantic Schema Validation, Router)                   |   |
|   +---------------------------------------+---------------------------------------+   |
+-------------------------------------------|-------------------------------------------+
                                            |
         +--------------------+-------------+------------+--------------------+
         |                    |                          |                    |
         v                    v                          v                    v
+-----------------+  +-----------------+        +-----------------+  +-----------------+
|  DATA ENGINE    |  | CLEANING ENGINE |        |  WEIGHT ENGINE  |  |  STATS ENGINE   |
| (Pandas/NumPy)  |  | (KNN/MICE/Mode) |        | (Raking/PostSt) |  |  (Taylor/MoE)   |
|                 |  |                 |        |                 |  |                 |
| - CSV/XLSX IO   |  | - Deduplication |        | - Strata Mapping|  | - Point Est.    |
| - Profiling     |  | - Whitespace Cln|        | - IPF Raking    |  | - Std Errors    |
| - Quality Score |  | - Winsorization |        | - Kish Eff Size |  | - Conf. Interval|
+--------+--------+  +--------+--------+        +--------+--------+  +--------+--------+
         |                    |                          |                    |
         +--------------------+-------------+------------+--------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                             REPORTING & AI INSIGHT ENGINE                             |
|                                                                                       |
|   +-------------------------------------------------------------------------------+   |
|   |  - ReportLab (PDF Engine)              - Jinja2 (HTML Template Compiler)      |   |
|   |  - Deterministic AI Narrative Module   - Summary Analytics Compiler           |   |
|   +---------------------------------------+---------------------------------------+   |
+-------------------------------------------|-------------------------------------------+
                                            |
                                            v
+---------------------------------------------------------------------------------------+
|                              PERSISTENCE & STORAGE LAYER                              |
|                                                                                       |
|   +--------------------------+   +--------------------------+   +-----------------+   |
|   |     SQLite Database      |   |       File Storage       |   |   Audit Logs    |   |
|   |   (SQLAlchemy Models)    |   | (Raw / Processed Files)  |   | (Immutable Log) |   |
|   +--------------------------+   +--------------------------+   +-----------------+   |
+---------------------------------------------------------------------------------------+
```

---

# 🔄 End-to-End Data Flow

```text
[Raw Survey Microdata] (CSV / XLSX / XLS)
           │
           ▼
┌──────────────────┐
│ 1. Ingestion &   │
│    Profiling     │
└─────────┬────────┘
          │
          ├──► Compute memory footprint
          ├──► Detect variable types
          ├──► Calculate null rates
          └──► Calculate Data Quality Index (0–100)
          │
          ▼
┌──────────────────┐
│ 2. Non-Destruct.  │
│    Cleaning       │
└─────────┬────────┘
          │
          ├──► Remove exact duplicate rows
          ├──► Normalize whitespace
          └──► Apply configurable imputation
          │
          ▼
┌──────────────────┐
│ 3. Consistency & │
│    Rule Checks   │
└─────────┬────────┘
          │
          ├──► Range validation
          ├──► Domain validation
          └──► Cross-column consistency checks
          │
          ▼
┌──────────────────┐
│ 4. Outlier Scan  │
│    & Treatment   │
└─────────┬────────┘
          │
          ├──► IQR detection
          ├──► Z-score detection
          └──► Configurable treatment
          │
          ▼
┌──────────────────┐
│ 5. Survey Weight │
│    Calibration   │
└─────────┬────────┘
          │
          ├──► Design-weight calibration
          ├──► Post-stratification
          ├──► Raking / IPF
          └──► Kish effective sample size
          │
          ▼
┌──────────────────┐
│ 6. Estimation &  │
│    Uncertainty   │
└─────────┬────────┘
          │
          ├──► Weighted estimates
          ├──► Unweighted estimates
          ├──► Standard errors
          ├──► Margin of Error
          └──► Confidence intervals
          │
          ▼
┌──────────────────┐
│ 7. AI Analytical │
│    Insights      │
└─────────┬────────┘
          │
          ├──► Deterministic synthesis
          ├──► Quality observations
          └──► Methodology observations
          │
          ▼
┌──────────────────┐
│ 8. Official      │
│    Reporting     │
└─────────┬────────┘
          │
          ├──► PDF report
          └──► Interactive HTML report
          │
          ▼
┌──────────────────────────────────────────────────────────┐
│                       9. AUDIT TRAIL                      │
│                                                          │
│ Timestamped and immutable logging of pipeline actions   │
└──────────────────────────────────────────────────────────┘
```

---

# 🚀 Key Functional Modules

## 1. Data Ingestion & Automated Profiling

StatFlow AI supports common official survey data formats:

* `.csv`
* `.xlsx`
* `.xls`

The profiling engine automatically calculates:

* Number of rows
* Number of columns
* Variable names
* Variable data types
* Non-null counts
* Missing-value percentages
* Unique values
* Numeric distributions
* Minimum and maximum values
* Mean
* Median
* Standard deviation
* Quartiles
* Memory footprint
* Duplicate-row density

### Data Quality Score

A transparent **0–100 Data Quality Score** is generated using measurable indicators such as:

* Missingness
* Duplicate density
* Invalid values
* Extreme distributions
* Structural inconsistencies

The score allows users to quickly understand the overall health of the dataset before processing.

---

# 2. Intelligent Data Cleaning & Imputation

StatFlow AI uses a **non-destructive cleaning workflow**.

Before modifications are permanently applied, users can preview the expected impact of each operation.

### Supported Operations

#### Deduplication

Exact duplicate records can be identified and removed.

#### Whitespace Normalization

Unnecessary leading and trailing whitespace can be removed from textual fields.

#### Missing-Value Imputation

The platform supports:

* Mean imputation
* Median imputation
* Mode imputation
* K-Nearest Neighbors (KNN)
* Linear Regression imputation

### Example

```text
Original:

Age     Income     Employment
25      25000      Employed
31      NULL       Employed
42      50000      Self-Employed

After Median Imputation:

Age     Income     Employment
25      25000      Employed
31      37500      Employed
42      50000      Self-Employed
```

All transformations are recorded in the audit trail.

---

# 3. Outlier Detection & Treatment

StatFlow AI provides multiple statistical and machine-learning methods for detecting anomalous observations.

### Statistical Methods

#### IQR Method

The Interquartile Range method identifies observations outside:

```text
Lower Bound = Q1 - 1.5 × IQR

Upper Bound = Q3 + 1.5 × IQR
```

where:

```text
IQR = Q3 - Q1
```

#### Z-Score

Observations can also be identified based on configurable Z-score thresholds.

#### Isolation Forest

For multi-dimensional anomaly detection, the system supports the **Isolation Forest** machine-learning algorithm.

### Treatment Options

Detected outliers can be:

* Flagged for review
* Retained but marked
* Removed
* Winsorized

### Winsorization

The system supports configurable percentile-based Winsorization, including:

```text
5th percentile  → Lower bound
95th percentile → Upper bound
```

---

# 4. Rule Validation Engine

The rule engine performs domain-specific consistency and validation checks.

### Range Checks

Examples:

```text
Age >= 0
Age <= 120

Income >= 0
```

### Cross-Column Validation

The engine can evaluate relationships between multiple variables.

Example:

```text
IF Age < 18
AND Employment_Status = "Retired"

THEN
Flag Record
```

### Validation Results

Each rule produces:

* Rule ID
* Rule description
* Number of violations
* Percentage of affected records
* Affected columns
* Sample violating records
* Severity level

This makes the validation process transparent and reviewable.

---

# 5. Survey Weighting & Calibration

Survey datasets often require weighting to correctly represent the target population.

StatFlow AI supports multiple weighting techniques.

## Design Weights

Initial survey weights can be supplied or calculated from the sampling design.

---

## Post-Stratification

Weights can be recalibrated against known population totals.

Example:

```text
Sample Population

Male   = 4,000
Female = 6,000

Target Population

Male   = 45,000
Female = 55,000
```

The system adjusts weights so that weighted sample totals align with the known population distribution.

---

## Raking / Iterative Proportional Fitting

The system supports **Iterative Proportional Fitting (IPF)** for multi-dimensional calibration.

Example dimensions:

```text
Gender
   +
Age Group
   +
Region
```

The algorithm iteratively adjusts weights until the weighted marginal distributions converge toward the target population margins.

---

# 6. Weight Diagnostics

StatFlow AI calculates important weight diagnostics.

### Weight Variance

Measures the dispersion of survey weights.

### Coefficient of Variation

```text
CV = Standard Deviation of Weights
     --------------------------------
          Mean Weight
```

### Kish Effective Sample Size

The effective sample size can be approximated using:

```text
n_eff = (Σw)²
       ---------
        Σw²
```

where `w` represents the survey weights.

A smaller effective sample size indicates that unequal weighting has reduced statistical efficiency.

---

# 7. Statistical Estimation & Uncertainty

StatFlow AI provides both weighted and unweighted estimates.

### Supported Point Estimates

* Population mean
* Population total
* Ratios
* Weighted mean
* Unweighted mean

---

## Weighted Mean

The weighted mean is calculated as:

```text
x̄w = Σ(wx)
     ------
      Σw
```

where:

* `x` = observed value
* `w` = survey weight

---

# 8. Variance & Standard Error

For complex survey estimation, the platform supports analytical variance estimation using **Taylor Series Linearization**.

The estimation engine calculates:

* Variance
* Standard Error
* Margin of Error
* Confidence Intervals

---

# 9. Margin of Error

For a confidence level using a suitable critical value `z`, the Margin of Error is calculated as:

```text
MoE = z × SE
```

For a 95% confidence interval:

```text
MoE ≈ 1.96 × SE
```

The confidence interval is:

```text
Lower Bound = Estimate - MoE

Upper Bound = Estimate + MoE
```

---

## Supported Confidence Levels

StatFlow AI supports:

* 90%
* 95%
* 99%

---

# 10. Weighted vs Unweighted Analysis

The system provides side-by-side comparisons between:

```text
Unweighted Estimate
        vs.
Weighted Estimate
```

This helps analysts understand the effect of survey weighting on the final statistical results.

Example:

| Metric                | Unweighted | Weighted |
| --------------------- | ---------: | -------: |
| Mean Income           |     38,500 |   41,200 |
| Sample Size           |     10,000 |   10,000 |
| Effective Sample Size |          — |    7,850 |
| Standard Error        |        520 |      610 |
| Margin of Error       |      1,019 |    1,196 |

---

# 11. AI Analytical Insights

StatFlow AI uses a **deterministic analytical narrative engine** rather than relying entirely on unrestricted generative AI.

The objective is to ensure that generated insights are:

* Evidence-backed
* Reproducible
* Transparent
* Traceable
* Based on computed statistics
* Resistant to hallucination

### Example Insight

```text
The dataset contains 25,000 records across 18 variables.

Overall data quality is 87/100.

Missing values are concentrated primarily in the Income
and Employment_Status variables.

Survey weighting increased the estimated mean income from
₹38,500 to ₹41,200, representing an increase of approximately
7.0%.

The effective sample size is lower than the nominal sample
size due to unequal survey weights.
```

Every numerical statement should be derived directly from the analytical results.

---

# 12. Automated Report Generation

StatFlow AI generates standardized statistical release reports.

## PDF Reports

PDF reports are generated using:

**ReportLab**

Reports can contain:

* Executive summary
* Dataset information
* Data-quality statistics
* Cleaning summary
* Validation results
* Outlier analysis
* Weight diagnostics
* Statistical estimates
* Confidence intervals
* Analytical insights
* Methodology
* Audit information

---

## HTML Reports

Interactive HTML reports are generated using:

**Jinja2**

HTML reports can provide:

* Interactive tables
* Statistical summaries
* Data-quality dashboards
* Weight diagnostics
* Estimation results
* Analytical observations

---

# 13. Reproducibility & Audit Trail

Every major operation is logged.

Examples include:

```text
DATASET_UPLOADED
PROFILE_GENERATED
DUPLICATES_REMOVED
MISSING_VALUES_IMPUTED
OUTLIERS_DETECTED
OUTLIERS_TREATED
RULES_EXECUTED
WEIGHTS_CALIBRATED
ESTIMATION_COMPLETED
REPORT_GENERATED
```

Each audit event contains information such as:

* Timestamp
* Operation
* Dataset
* Parameters
* Result
* User/action identifier
* Status

The objective is to make the complete statistical processing pipeline reproducible and auditable.

---

# 🛠️ Technology Stack

| Layer                | Technology   |
| -------------------- | ------------ |
| Frontend UI          | React 18     |
| Build Tool           | Vite         |
| Styling              | Tailwind CSS |
| Icons                | Lucide React |
| HTTP Client          | Axios        |
| Backend API          | FastAPI      |
| Server               | Uvicorn      |
| Validation           | Pydantic     |
| Language             | Python 3.11+ |
| Data Processing      | Pandas       |
| Numerical Computing  | NumPy        |
| Machine Learning     | Scikit-learn |
| Scientific Computing | SciPy        |
| Excel Processing     | OpenPyXL     |
| PDF Generation       | ReportLab    |
| HTML Templates       | Jinja2       |
| Database             | SQLite3      |
| ORM                  | SQLAlchemy   |

---

# 📁 Project Structure

```text
statathon-ps4/
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   │
│   │   ├── models/
│   │   │   └── schema_models.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── api_schemas.py
│   │   │   └── clean_schema.py
│   │   │
│   │   ├── routes/
│   │   │   ├── upload.py
│   │   │   ├── profile.py
│   │   │   ├── clean.py
│   │   │   ├── outliers.py
│   │   │   ├── validate.py
│   │   │   ├── weighting.py
│   │   │   ├── estimation.py
│   │   │   ├── insights.py
│   │   │   ├── audit.py
│   │   │   └── reports.py
│   │   │
│   │   ├── services/
│   │   │   ├── profile_service.py
│   │   │   ├── clean_service.py
│   │   │   ├── outlier_service.py
│   │   │   ├── validate_service.py
│   │   │   ├── weighting_service.py
│   │   │   ├── estimation_service.py
│   │   │   ├── insight_service.py
│   │   │   └── report_service.py
│   │   │
│   │   └── utils/
│   │       └── synthetic_generator.py
│   │
│   ├── tests/
│   │   └── test_pipeline.py
│   │
│   ├── generate_test_excel.py
│   ├── requirements.txt
│   └── setup.py
│
├── frontend/
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   └── Sidebar.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── data/
│   ├── uploads/
│   └── processed/
│
├── reports/
│
└── README.md
```

---

# ⚙️ Installation & Setup

## Prerequisites

Make sure the following are installed:

* Python 3.11+
* Node.js 18+
* npm
* Git

Verify the installations:

```bash
python --version
node --version
npm --version
git --version
```

---

# 🔧 Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The backend API will typically be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🎨 Frontend Setup

Open another terminal and navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will typically be available at:

```text
http://localhost:5173
```

---

# 🔌 API Architecture

The backend exposes REST APIs for each stage of the statistical pipeline.

| Endpoint      | Purpose                        |
| ------------- | ------------------------------ |
| `/upload`     | Upload dataset                 |
| `/profile`    | Generate dataset profile       |
| `/clean`      | Execute cleaning               |
| `/outliers`   | Detect/treat outliers          |
| `/validate`   | Execute domain rules           |
| `/weighting`  | Calibrate survey weights       |
| `/estimation` | Generate statistical estimates |
| `/insights`   | Generate analytical insights   |
| `/audit`      | Retrieve audit history         |
| `/reports`    | Generate PDF/HTML reports      |

---

# 🔄 Processing Pipeline

The complete pipeline can be represented as:

```text
Upload
  ↓
Profile
  ↓
Clean
  ↓
Validate
  ↓
Detect Outliers
  ↓
Treat Outliers
  ↓
Calibrate Weights
  ↓
Estimate Statistics
  ↓
Calculate Uncertainty
  ↓
Generate Insights
  ↓
Generate Reports
  ↓
Audit
```

---

# 🧪 Testing

Automated tests are located in:

```text
backend/tests/test_pipeline.py
```

Run the test suite using:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

---

# 📊 Synthetic Test Data

StatFlow AI includes a synthetic survey-data generator:

```text
backend/app/utils/synthetic_generator.py
```

A test Excel generation script is also provided:

```text
backend/generate_test_excel.py
```

This allows the complete pipeline to be tested without exposing sensitive official survey microdata.

---

# 🔐 Data Privacy & Security Considerations

StatFlow AI is designed to support sensitive statistical datasets.

Recommended deployment practices include:

* Do not commit raw survey datasets to Git.
* Keep uploaded datasets outside the source repository.
* Use `.gitignore` for raw and processed data.
* Restrict access to generated reports.
* Avoid logging personally identifiable information.
* Use synthetic data during development.
* Maintain immutable audit records.
* Apply role-based access control in production deployments.
* Encrypt sensitive data at rest and in transit.

Example `.gitignore` entries:

```gitignore
venv/
__pycache__/
*.pyc

data/uploads/*
data/processed/*

reports/*

*.db
*.sqlite
*.sqlite3

.env
```

---

# 📈 Example Workflow

A typical user workflow is:

### Step 1 — Upload

The analyst uploads:

```text
survey_data.xlsx
```

### Step 2 — Profile

StatFlow AI generates:

```text
Rows:             50,000
Columns:          24
Missing Values:   3.8%
Duplicates:       0.7%
Quality Score:    91/100
```

### Step 3 — Clean

The analyst previews:

```text
Duplicates to remove:       350
Missing Income values:      1,245
Whitespace corrections:     732
```

The analyst approves the selected operations.

### Step 4 — Validate

The rule engine detects:

```text
Age > 120:                         4 records
Income < 0:                       12 records
Age < 18 & Retired:                7 records
```

### Step 5 — Outlier Detection

The system identifies potential anomalies using:

```text
IQR
Z-Score
Isolation Forest
```

### Step 6 — Weight Calibration

The analyst selects:

```text
Post-Stratification
```

or:

```text
Raking / IPF
```

### Step 7 — Estimation

The system calculates:

```text
Weighted Mean
Unweighted Mean
Standard Error
Margin of Error
95% Confidence Interval
```

### Step 8 — Insights

The deterministic insight engine converts the statistical outputs into evidence-backed observations.

### Step 9 — Reporting

The analyst exports:

```text
StatFlow_Report.pdf
StatFlow_Report.html
```

### Step 10 — Audit

All operations remain available in the audit trail.

---

# 🎯 Project Objectives

StatFlow AI aims to achieve the following:

* Reduce manual statistical processing time
* Improve data-quality assurance
* Reduce processing errors
* Provide transparent statistical transformations
* Support reproducible workflows
* Automate survey-weight calibration
* Provide reliable uncertainty measures
* Generate standardized statistical reports
* Improve auditability
* Enable low-code statistical processing

---

# ⭐ Key Advantages

## 1. End-to-End Automation

The complete workflow is integrated into a single platform.

## 2. Non-Destructive Processing

Raw data remains untouched while processed datasets are generated separately.

## 3. Explainable Analytics

Statistical calculations and transformation steps are visible to the analyst.

## 4. Deterministic AI Insights

Narratives are generated from verified statistical outputs instead of unconstrained AI-generated claims.

## 5. Reproducibility

Every important transformation is recorded.

## 6. Survey-Aware Processing

The platform supports weighting, calibration, effective sample size, and uncertainty analysis.

## 7. Automated Reporting

Publication-ready PDF and HTML reports can be generated directly from the processed results.

---

# 🏛️ Intended Use Cases

StatFlow AI can be adapted for:

* Government statistical agencies
* Official survey processing
* Socio-economic surveys
* Population surveys
* Labour surveys
* Household surveys
* Agricultural surveys
* Education surveys
* Health surveys
* Market research
* Academic research
* Large-scale survey analytics

---

# 🔮 Future Enhancements

Potential future improvements include:

* Role-based authentication
* PostgreSQL support
* Redis-based task queues
* Background processing with Celery
* Cloud storage integration
* Advanced survey-design variance estimation
* Replicate weights
* Bootstrap variance estimation
* Jackknife variance estimation
* BRR variance estimation
* Interactive visualization dashboards
* Data lineage visualization
* Advanced ML imputation
* Automated schema detection
* Natural-language rule creation
* Multi-user collaboration
* Versioned datasets
* Containerized deployment with Docker
* Kubernetes deployment
* Production-grade observability
* Digital signatures for official reports

---

# 🧭 Design Principles

StatFlow AI follows these core principles:

```text
Transparency
     ↓
Reproducibility
     ↓
Non-Destructive Processing
     ↓
Statistical Validity
     ↓
Auditability
     ↓
Explainability
     ↓
Reliable Reporting
```

---

# 📜 License

This project is intended for academic, research, and prototype purposes unless a separate license is provided by the project owners.

---

# 👥 Project

**Project Name:** StatFlow AI

**Problem Statement:** AI-Enhanced Application for Automated Data Preparation, Estimation, and Report Writing

**Primary Focus:**

```text
Data Preparation
+
Statistical Validation
+
Survey Weighting
+
Statistical Estimation
+
AI-Assisted Analytical Reporting
```

---

# 🚀 Quick Start

```bash
# Clone / enter the project
cd statathon-ps4

# Backend
cd backend

# Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload
```

Open another terminal:

```bash
cd statathon-ps4/frontend

# Install frontend dependencies
npm install

# Start frontend
npm run dev
```

Then open the frontend development URL displayed by Vite.

---

## 💡 StatFlow AI

> **From raw survey microdata to validated statistics and publication-ready reports — automatically, transparently, and reproducibly.**
