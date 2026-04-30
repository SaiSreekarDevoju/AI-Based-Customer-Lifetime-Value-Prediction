# 🧠 AI-Based Customer Lifetime Value (CLV) Prediction System

> A complete end-to-end full-stack machine learning project that predicts how valuable a customer will be over their lifetime — and segments them into Low / Medium / High Value tiers.

---

## 📌 Project Explanation (Simple Words)

**Customer Lifetime Value (CLV)** is the total revenue a business can expect from a single customer over the entire relationship. Instead of guessing, this system uses **machine learning** to predict CLV based on a customer's behaviour:

- How often they buy
- How much they spend per order
- How recently they last purchased
- How long they've been a customer

The result helps businesses focus marketing budgets on the right customers.

---

## 🔄 Working Flow

```
 User fills form
      │
      ▼
 Frontend (HTML/CSS/JS)
      │  HTTP POST /predict
      ▼
 FastAPI Backend (Python)
      │  loads model + scaler
      ▼
 Random Forest ML Model
      │  returns predicted CLV ($)
      ▼
 Backend sends JSON response
      │
      ▼
 Dashboard shows:
   ├── CLV amount (animated)
   ├── Segment badge (Low / Medium / High)
   ├── Monthly & Annual value
   └── Recommended strategy
```

---

## 🗂️ Project Structure

```
AI-Based Customer Lifetime Value Prediction/
├── data/
│   └── customers.csv            ← auto-generated synthetic dataset (600 rows)
│
├── model/
│   ├── train_model.py           ← ML training script
│   ├── clv_model.pkl            ← saved trained model (auto-generated)
│   └── scaler.pkl               ← saved feature scaler (auto-generated)
│
├── backend/
│   ├── app.py                   ← FastAPI REST API
│   └── requirements.txt         ← Python dependencies
│
├── frontend/
│   ├── index.html               ← Dashboard UI
│   ├── style.css                ← Dark glassmorphism styling
│   └── app.js                   ← Fetch API + Chart.js logic
│
└── README.md
```

---

## ⚙️ Setup & Run Instructions

### Prerequisites
- Python 3.9 or higher
- pip

---

### Step 1 — Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

### Step 2 — Train the ML Model

Run this from the **project root**:

```bash
python model/train_model.py
```

**Expected output:**
```
=======================================================
  CLV Prediction System — Model Training
=======================================================

✔  Dataset saved  →  data/customers.csv
   Rows        : 600
   CLV range   : $50.00  –  $12,000.00
   CLV mean    : ~$1,800

  Training Random Forest Regressor …
✔  Training complete.

── Model Evaluation (Test Set) ──────────────────────
   R² Score  :  0.97xx
   MAE       :  $xx.xx
   RMSE      :  $xx.xx

✔  Model saved   →  model/clv_model.pkl
✔  Scaler saved  →  model/scaler.pkl
```

---

### Step 3 — Start the Backend

From the **project root**:

```bash
uvicorn backend.app:app --reload
```

The API will be live at: **http://localhost:8000**
Interactive API docs: **http://localhost:8000/docs**

---

### Step 4 — Open the Dashboard

Open `frontend/index.html` directly in your browser.

> **Note:** If your browser blocks CORS from `file://`, serve the frontend with Python:
> ```bash
> cd frontend
> python -m http.server 5500
> ```
> Then open **http://localhost:5500**

---

## 🔌 API Reference

### `GET /` — Health Check
```json
{ "status": "running", "app": "CLV Prediction API", "version": "1.0.0" }
```

---

### `GET /stats` — Dashboard Statistics
```json
{
  "total_customers": 600,
  "avg_clv": 1842.50,
  "max_clv": 11980.20,
  "min_clv": 52.30,
  "high_value_pct": 18.5,
  "segment_distribution": {
    "Low Value": 210,
    "Medium Value": 280,
    "High Value": 110
  },
  "avg_by_segment": {
    "Low Value": 620.10,
    "Medium Value": 2840.75,
    "High Value": 8120.50
  }
}
```

---

### `GET /customers?limit=50` — Sample Dataset
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
      "AvgOrderValue": 145.50,
      "Recency": 22,
      "Tenure": 36,
      "CLV": 2874.30
    }
  ]
}
```

---

### `POST /predict` — Predict CLV

**Request:**
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

**Response:**
```json
{
  "predicted_clv": 4215.82,
  "segment": "Medium Value",
  "segment_color": "#f59e0b",
  "segment_emoji": "📊",
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

---

## 🤖 ML Model Details

| Property | Value |
|---|---|
| **Algorithm** | Random Forest Regressor |
| **Features** | Age, PurchaseFrequency, AvgOrderValue, Recency, Tenure |
| **Target** | CLV (USD) |
| **Train/Test Split** | 80% / 20% |
| **Preprocessing** | StandardScaler |
| **Estimators** | 200 trees, max_depth=12 |
| **Typical R²** | ~0.97 |

---

## 🏷️ Customer Segmentation

| Segment | CLV Range | Strategy |
|---|---|---|
| 📉 **Low Value** | < $1,500 | Re-engage with discount offers |
| 📊 **Medium Value** | $1,500 – $6,000 | Nurture, upsell, loyalty programs |
| 🏆 **High Value** | > $6,000 | Retain with VIP perks & rewards |

---

## ✅ Key Benefits

1. **Data-Driven Marketing** — Stop guessing; invest budget in high-value customers
2. **Early Churn Detection** — High recency + low frequency = at-risk customer
3. **Personalised Strategy** — Each segment gets a tailored approach
4. **Real-Time Predictions** — Instant API response via REST endpoint
5. **Explainable** — Feature importance from Random Forest shows what drives CLV

---

## 🔮 Future Improvements

- [ ] **Real Database** — Replace CSV with PostgreSQL or MongoDB
- [ ] **Authentication** — Add API key or OAuth2 for secure access
- [ ] **SHAP Explainability** — Per-prediction feature explanations
- [ ] **Time-Series CLV** — BG/NBD + Gamma-Gamma statistical model
- [ ] **CI/CD Pipeline** — Auto-retrain model when new data arrives
- [ ] **Deploy to Cloud** — Docker + AWS/GCP/Azure deployment
- [ ] **A/B Testing Module** — Test different retention strategies
- [ ] **Email Alerts** — Notify when a customer drops a segment

---

## 📜 License

MIT — Free to use and modify for educational and commercial purposes.
