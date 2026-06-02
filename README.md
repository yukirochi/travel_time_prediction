# Travel Time Prediction System

A comprehensive data pipeline and machine learning system that predicts travel times using real-world routing data. The system employs a modern, cloud-native architecture with serverless data collection, cloud-based transformation, and predictive analytics.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRAVEL TIME PREDICTION                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐      ┌──────────────┐    ┌────────────┐  │
│  │  TomTom API      │  ──→ │   Azure      │ ──→│ Snowflake  │  │
│  │  (Real-time)     │      │  Functions   │    │ Data       │  │
│  │                  │      │  (Scraper)   │    │ Warehouse  │  │
│  └──────────────────┘      └──────────────┘    └────┬───────┘  │
│                                                      │           │
│                                                      ↓           │
│  ┌──────────────────┐      ┌──────────────┐    ┌────────────┐  │
│  │  Local Machine   │  ←── │     dbt      │ ←── │Snowflake   │  │
│  │                  │      │ (Transform)  │     │(Raw Data)  │  │
│  │  ┌────────────┐  │      └──────────────┘    └────────────┘  │
│  │  │Orchestrator│  │                                          │
│  │  │ + Model    │  │                                          │
│  │  └────────────┘  │                                          │
│  └──────────────────┘                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tools & Technologies Used

### Data Collection & Integration

| Tool                | Purpose               | Role                                                           |
| ------------------- | --------------------- | -------------------------------------------------------------- |
| **Azure Functions** | Serverless compute    | Runs the scraper on a scheduled timer to fetch data hourly     |
| **TomTom API**      | Routing & travel data | Provides real-time travel times, distances, and traffic delays |
| **Python**          | Runtime               | Implements the scraper logic for Azure Functions               |

### Data Warehousing & Storage

| Tool          | Purpose              | Role                                                 |
| ------------- | -------------------- | ---------------------------------------------------- |
| **Snowflake** | Cloud data warehouse | Stores raw API data and transformed analytics tables |
| **pandas**    | Data manipulation    | Processes and reads data from Snowflake              |

### Data Transformation

| Tool                      | Purpose                   | Role                                                                         |
| ------------------------- | ------------------------- | ---------------------------------------------------------------------------- |
| **dbt (data build tool)** | ELT/analytics engineering | Transforms raw travel data into dimensional tables (staging and mart layers) |
| **SQL**                   | Data modeling             | dbt uses SQL to define transformations and tests data quality                |

### Machine Learning & Analytics

| Tool             | Purpose                  | Role                                                             |
| ---------------- | ------------------------ | ---------------------------------------------------------------- |
| **scikit-learn** | Machine learning library | Trains decision tree regression model for travel time prediction |
| **pandas**       | Data analysis            | Handles feature engineering and dataset preparation              |
| **matplotlib**   | Visualization            | Generates model performance visualizations                       |

### Orchestration & Automation

| Tool           | Purpose           | Role                                             |
| -------------- | ----------------- | ------------------------------------------------ |
| **Python**     | Scripting         | Custom orchestration logic                       |
| **subprocess** | Process execution | Runs dbt commands and Python scripts in sequence |

### Development & Configuration

| Tool            | Purpose                  | Role                                           |
| --------------- | ------------------------ | ---------------------------------------------- |
| **Python venv** | Virtual environment      | Isolates project dependencies                  |
| **pip**         | Package management       | Manages Python dependencies (requirements.txt) |
| **dotenv**      | Configuration management | Loads environment variables for credentials    |

---

## System Workflow

### 1. Data Collection (Azure Functions - Cloud)

**File:** `scraper/function_app.py`

- **Trigger:** Timer-based (runs every hour at minute 0)
- **Input:** TomTom Routing API
- **Output:** Raw travel data inserted into Snowflake
- **Flow:**
  1. Fetch travel time data from TomTom API
  2. Extract key metrics (travel time, traffic delay, route length, timestamps)
  3. Connect to Snowflake (credentials from environment variables)
  4. Create `raw_table` if it doesn't exist
  5. Insert extracted data as new rows
  6. Log success/error to Azure Functions monitoring

**Key Data Points Captured:**

- `timestamp` - UTC timestamp of data collection
- `length_in_meters` - Route distance
- `travel_time_in_seconds` - Total travel duration
- `traffic_delay_in_seconds` - Traffic-induced delay
- `traffic_length_in_meters` - Distance affected by traffic
- `departure_time` - Scheduled departure time
- `arrival_time` - Scheduled arrival time

---

### 2. Data Transformation (dbt - Local/Cloud)

**Folder:** `travel_time_prediction/`

**Transformation Layers:**

#### Staging Layer (`models/staging/stg_data.sql`)

- Cleans and standardizes raw data from Snowflake
- Renames columns to business terminology
- Converts timestamps and numeric formats
- Filters invalid or null records

**Output Table:** `stg_data`

#### Mart Layer (`models/mart/mart_data.sql`)

- Aggregates staging data into analytical tables
- Calculates derived metrics (e.g., average travel time by day/hour)
- Creates slowly changing dimensions
- Optimizes for reporting and ML model training

**Output Table:** `mart_data` (in `training_data.staging_mart` schema)

**Execution:**

```bash
cd travel_time_prediction
dbt run      # Runs all transformations
dbt test     # Validates data quality
```

---

### 3. Model Training & Prediction (Python - Local)

**Files:**

- `model/predictor.py` - Model training and inference
- `model/snowflake_info.py` - Database connection

**Workflow:**

1. **Data Fetch:**
   - Connect to Snowflake using credentials
   - Query `training_data.staging_mart.mart_data`

2. **Feature Selection:**
   - `DAY_OF_WEEK` - Day of the week (0-6)
   - `DEPARTURE_TIME` - Time of departure (normalized)

3. **Target Variable:**
   - `TRAVEL_TIME_IN_MINUTES` - Ground truth travel time

4. **Model Training:**
   - Split data: 80% train, 20% test
   - Algorithm: Decision Tree Regressor (max_depth=4)
   - Evaluation Metric: Mean Absolute Error (MAE)

5. **Prediction:**
   - Make sample predictions for a Monday departure at 2:51

**Output:**

```
Mean Absolute Error: [X.XX] minutes
Predicted Travel Time: [X.XX] minutes
```

---

### 4. Orchestration (Python - Local)

**File:** `orchestrator/orchestrator.py`

**Purpose:** Automate the end-to-end pipeline

**Workflow:**

1. Run dbt transformations
2. If dbt succeeds → Run predictor model training
3. If dbt fails → Log error and skip predictor
4. All steps logged to `orchestrator/orch_runs.log`

**Execution:**

```bash
cd orchestrator
python orchestrator.py
```

**Log Format:**

```
2026-06-02 14:30:15,123 - INFO - Starting DBT Models...
2026-06-02 14:32:45,567 - INFO - DBT Models completed successfully.
2026-06-02 14:32:46,789 - INFO - Starting Predictor Script...
2026-06-02 14:32:55,234 - INFO - Predictor Script completed successfully.
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ HOUR 0                                                      │
├─────────────────────────────────────────────────────────────┤
│  TomTom API → Azure Function (Scraper)                     │
│               └─→ Snowflake (raw_table)                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ ON DEMAND (e.g., Daily)                                    │
├─────────────────────────────────────────────────────────────┤
│  dbt run (Transform raw_table → stg_data → mart_data)     │
│            └─→ Snowflake (mart_data)                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ ON DEMAND (Model Training)                                 │
├─────────────────────────────────────────────────────────────┤
│  predictor.py (Query mart_data → Train Model)             │
│                └─→ Decision Tree Model                     │
│                └─→ Predictions & MAE                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Setup & Execution

### Prerequisites

- Python 3.8+
- Snowflake account with credentials
- TomTom API key
- Azure account (for Function App deployment)
- dbt CLI installed

### Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

**1. Environment Variables** (`scraper/.env` or Azure App Settings)

```
API=<TomTom_API_URL>
SF_USER=<snowflake_user>
SF_PASSWORD=<snowflake_password>
SF_ACCOUNT=<snowflake_account>
SF_WAREHOUSE=<snowflake_warehouse>
SF_DATABASE=<snowflake_database>
SF_SCHEMA=<snowflake_schema>
```

**2. dbt Configuration** (`travel_time_prediction/profiles.yml`)

```yaml
travel_time_prediction:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: [account_id]
      user: [username]
      password: [password]
      database: training_data
      schema: staging_mart
      warehouse: prediction_wh
```

### Running the Pipeline

```bash
# 1. Run the full orchestration
cd orchestrator
python orchestrator.py

# 2. Or run components individually:

# Run dbt only
cd travel_time_prediction
dbt run

# Run model training only
cd model
python predictor.py
```

---

## Project Structure

```
travel_time_prediction/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── test_data.csv               # Test dataset
├── training_data.csv           # Training dataset
│
├── scraper/                    # Azure Functions (Cloud)
│   ├── function_app.py         # Timer-triggered scraper
│   ├── host.json               # Azure Functions config
│   └── local.settings.json     # Local development settings
│
├── model/                      # ML Model
│   ├── predictor.py            # Model training & prediction
│   └── snowflake_info.py       # Snowflake connection
│
├── orchestrator/               # Orchestration
│   ├── orchestrator.py         # Main orchestration script
│   └── orch_runs.log           # Execution logs
│
└── travel_time_prediction/     # dbt Project
    ├── dbt_project.yml         # dbt configuration
    ├── models/
    │   ├── staging/            # Raw data layer
    │   │   ├── stg_data.sql
    │   │   └── src_sources.yml
    │   └── mart/               # Analytics layer
    │       ├── mart_data.sql
    │       └── src_sources.yml
    ├── tests/                  # dbt data quality tests
    ├── macros/                 # dbt macros
    └── target/                 # dbt build artifacts
```

---

## Key Design Decisions

| Decision                        | Rationale                                                                             |
| ------------------------------- | ------------------------------------------------------------------------------------- |
| **Azure Functions for Scraper** | Serverless, cost-effective, no infrastructure management, scheduled execution         |
| **Snowflake as DW**             | Scalable, fast analytics queries, cloud-native, integrates well with dbt              |
| **dbt for Transformation**      | Version control, testing, documentation, separates analytics logic                    |
| **Decision Tree Model**         | Interpretable, fast inference, good for travel time prediction with temporal features |
| **Local Orchestration**         | Flexible scheduling, easy debugging, can be moved to cloud scheduler later            |

---

## Monitoring & Logging

- **Scraper Logs:** Azure Functions → Application Insights
- **dbt Logs:** `travel_time_prediction/target/run_results.json`
- **Orchestrator Logs:** `orchestrator/orch_runs.log`
- **Model Output:** Console output + can be logged to file

---

## Future Enhancements

- [ ] Deploy orchestrator to Azure Data Factory or Synapse
- [ ] Implement more advanced ML models (XGBoost, Neural Networks)
- [ ] Add real-time prediction API
- [ ] Implement A/B testing framework
- [ ] Add data quality monitoring and alerting
- [ ] Create BI dashboards in Power BI/Tableau
- [ ] Containerize with Docker for consistency

---

## Troubleshooting

**Issue:** Scraper fails to insert data  
**Solution:** Check environment variables, verify Snowflake credentials and connectivity

**Issue:** dbt run fails with SQL errors  
**Solution:** Verify Snowflake schema/table names, check data types in staging layer

**Issue:** Model training fails with "No data"  
**Solution:** Ensure mart_data table exists and has records, check Snowflake query

**Issue:** Orchestrator can't find directories  
**Solution:** Run from project root, ensure directory structure matches (fixed in v1.1)

---

## Contact & Support

For questions or issues, refer to individual component documentation or contact the engineering team.

---

**Last Updated:** June 2, 2026  
**Version:** 1.1
