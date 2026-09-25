# 🧠 AI-Based Customer Lifetime Value (CLV) Prediction System

> An end-to-end machine-learning project that predicts customer lifetime value and groups customers into Low, Medium, or High Value segments.

## Overview

Customer Lifetime Value (CLV) estimates the revenue a business can expect from a customer over the full relationship. This project uses customer behaviour features to produce a CLV prediction and a simple segment recommendation.

The current model uses these inputs:

- Purchase frequency
- Average order value
- Recency of the last purchase
- Customer tenure
- Customer age

The result is returned through a FastAPI backend and displayed in a lightweight browser dashboard.

## How the system works

```text
User submits customer features
        ↓
Frontend (HTML / CSS / JavaScript)
        ↓  POST /predict
FastAPI backend
        ↓
Feature scaling + Random Forest model
        ↓
Predicted CLV and customer segment
        ↓
Dashboard displays the result
```

## Project structure

```text
AI-Based-Customer-Lifetime-Value-Prediction/
├── data/
│   └── customers.csv            # Generated training dataset
├── model/
│   ├── train_model.py           # Model-training script
│   ├── clv_model.pkl            # Generated trained model
│   └── scaler.pkl               # Generated feature scaler
├── backend/
│   ├── app.py                   # FastAPI application
│   └── requirements.txt         # Backend dependencies
├── frontend/
│   ├── index.html               # Dashboard markup
│   ├── style.css                # Dashboard styles
│   └── app.js                   # API calls and chart logic
└── README.md
```

## Requirements

- Python 3.9 or newer
- `pip`
- A modern browser

## Setup and run

### 1. Install backend dependencies

From the repository root:

```bash
pip install -r backend/requirements.txt
```

### 2. Generate the model artifacts

Run the training script from the repository root:

```bash
python model/train_model.py
```

This creates or refreshes the generated files under `data/` and `model/`.

The API expects all three generated artifacts to exist before startup:

- `data/customers.csv`
- `model/clv_model.pkl`
- `model/scaler.pkl`

If any artifact is missing, the API reports the missing file during startup and prediction/data endpoints remain unavailable until the artifacts are generated.

### 3. Start the API

From the repository root:

```bash
uvicorn backend.app:app --reload
```

The API will be available at `http://localhost:8000`.

Interactive API documentation is available at `http://localhost:8000/docs`.

If you prefer to run the application from inside `backend/`, use:

```bash
cd backend
uvicorn app:app --reload
```

### 4. Open the dashboard

Open `frontend/index.html` in a browser. If the browser blocks API requests from a `file://` URL, serve the frontend directory with a local HTTP server:

```bash
python -m http.server 5500 --directory frontend
```

Then open `http://localhost:5500`.

> Start the API before using the dashboard so the frontend can reach the prediction endpoints.

## API reference

All API endpoints use JSON responses. FastAPI's interactive documentation at `/docs` can also be used to inspect the request schema and try endpoints locally.

### `GET /` — Health check

Returns a small payload confirming that the API is running.

```json
{
  "status": "running",
  "app": "CLV Prediction API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### `GET /stats` — Dataset summary

Returns dataset-level statistics used by the dashboard overview.

The response includes:

- Total customer count
- Average, minimum, and maximum CLV
- Percentage of High Value customers
- Counts for Low, Medium, and High Value segments
- Average CLV for each segment
- Average customer age
- Average order value
- Average customer tenure in months

### `GET /customers?limit=50&offset=0` — Sample customer records

Returns a paginated slice of the training dataset.

- `limit` controls the number of rows returned.
- `offset` controls the starting row.
- The response's `total` field reports the complete dataset size.

Example response shape:

```json
{
  "total": 600,
  "limit": 50,
  "offset": 0,
  "customers": [
    {
      "CustomerID": "CUST0001",
      "Age": 34,
      "PurchaseFrequency": 12,
      "AvgOrderValue": 145.5,
      "Recency": 22,
      "Tenure": 36,
      "CLV": 2874.3
    }
  ]
}
```

### `POST /predict` — Predict CLV

Request body:

```json
{
  "age": 35,
  "purchase_frequency": 15,
  "avg_order_value": 180.0,
  "recency": 20,
  "tenure": 48
}
```

The backend validates the numeric ranges before making a prediction:

| Field | Allowed range |
|---|---|
| `age` | 18–100 years |
| `purchase_frequency` | 1–365 purchases |
| `avg_order_value` | At least 1 USD |
| `recency` | 0–730 days |
| `tenure` | 1–360 months |

If the model or scaler has not loaded, the endpoint returns HTTP 503 instead of attempting a prediction.

Response shape:

```json
{
  "predicted_clv": 4215.82,
  "segment": "Medium Value",
  "segment_color": "#f59e0b",
  "segment_emoji": "Mid",
  "monthly_value": 87.83,
  "annual_value": 1053.96,
  "input_summary": {
    "age": 35,
    "purchase_frequency": 15,
    "avg_order_value": 180.0,
    "recency": 20,
    "tenure": 48
  }
}
```

Example `curl` request:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "purchase_frequency": 15,
    "avg_order_value": 180.00,
    "recency": 20,
    "tenure": 48
  }'
```

## Model details

| Property | Value |
|---|---|
| Algorithm | Random Forest Regressor |
| Features | Age, PurchaseFrequency, AvgOrderValue, Recency, Tenure |
| Target | CLV (USD) |
| Train/test split | 80% / 20% |
| Preprocessing | StandardScaler |
| Estimators | 200 trees |
| Maximum depth | 12 |
| Typical R² | Approximately 0.97 on the generated dataset |

Model metrics depend on the generated data and the local training run. Treat the example values above as indicative rather than guaranteed.

## Customer segmentation

| Segment | CLV range | Example strategy |
|---|---:|---|
| Low Value | `< $1,500` | Re-engagement and introductory offers |
| Medium Value | `$1,500 – $6,000` | Nurture, upsell, and loyalty programs |
| High Value | `> $6,000` | Retention, VIP support, and rewards |

The thresholds are defined in `backend/app.py` and are used by the API response and dataset statistics.

## Generated artifacts

The training script writes the dataset and serialized model files used by the backend. Regenerate them whenever the training logic or source data changes.

Do not edit generated `.csv` or `.pkl` files by hand.

## Limitations

- The sample dataset is synthetic and is intended for demonstration.
- The model is not a substitute for a production CLV pipeline or financial analysis.
- The backend currently loads the model, scaler, and dataset during application startup.
- The example CORS configuration is permissive for local development.
- The `/customers` endpoint exposes the generated sample dataset and should not be treated as a production customer-data API.
- The serialized model and scaler are generated locally rather than versioned as a reproducible model artifact pipeline.

## Future improvements

- [ ] Replace the CSV workflow with a production database
- [ ] Add authentication and API-key protection
- [ ] Add per-prediction SHAP explanations
- [ ] Evaluate statistical CLV approaches such as BG/NBD and Gamma-Gamma
- [ ] Add automated tests and CI checks
- [ ] Add Docker-based deployment documentation
- [ ] Add monitoring and model-drift checks

## License

MIT — Free to use and modify for educational and commercial purposes.
