"""
=============================================================
  AI-Based Customer Lifetime Value (CLV) Prediction System
  File: model/train_model.py
  Purpose: Generate synthetic data, train ML model, save artifacts
=============================================================
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import pickle
import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent   # project root
DATA_DIR   = BASE_DIR / "data"
MODEL_DIR  = Path(__file__).parent          # model/

DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

# ── 1. Generate Synthetic Dataset ──────────────────────────
print("=" * 55)
print("  CLV Prediction System - Model Training")
print("=" * 55)

np.random.seed(42)
N = 600  # number of synthetic customers

customer_ids      = [f"CUST{str(i).zfill(4)}" for i in range(1, N + 1)]
age               = np.random.randint(18, 72, N)
purchase_freq     = np.random.randint(1, 31, N)       # purchases per year
avg_order_value   = np.round(np.random.uniform(20, 500, N), 2)   # USD
recency           = np.random.randint(1, 366, N)      # days since last purchase
tenure            = np.random.randint(1, 121, N)      # months as customer

# ── CLV Formula ────────────────────────────────────────────
# CLV = monthly_revenue × tenure_months × margin × retention_factor
monthly_revenue  = (avg_order_value * purchase_freq) / 12.0
retention_factor = np.exp(-recency / 250.0)   # decays with inactivity
age_factor       = 0.85 + (age / 200.0)       # slight boost for mature customers
clv              = monthly_revenue * tenure * 0.3 * retention_factor * age_factor

# Add realistic Gaussian noise (~12 %)
clv += np.random.normal(0, clv * 0.12)
clv  = np.clip(clv, 50.0, 12000.0).round(2)

df = pd.DataFrame({
    "CustomerID"       : customer_ids,
    "Age"              : age,
    "PurchaseFrequency": purchase_freq,
    "AvgOrderValue"    : avg_order_value,
    "Recency"          : recency,
    "Tenure"           : tenure,
    "CLV"              : clv,
})

csv_path = DATA_DIR / "customers.csv"
df.to_csv(csv_path, index=False)
print(f"\n[OK] Dataset saved -> {csv_path}")
print(f"   Rows        : {len(df)}")
print(f"   CLV range   : ${df['CLV'].min():,.2f} - ${df['CLV'].max():,.2f}")
print(f"   CLV mean    : ${df['CLV'].mean():,.2f}")

# ── 2. Feature Selection ───────────────────────────────────
FEATURES = ["Age", "PurchaseFrequency", "AvgOrderValue", "Recency", "Tenure"]
X = df[FEATURES]
y = df["CLV"]

# ── 3. Train / Test Split ──────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

# ── 4. Feature Scaling ─────────────────────────────────────
scaler          = StandardScaler()
X_train_scaled  = scaler.fit_transform(X_train)
X_test_scaled   = scaler.transform(X_test)

# ── 5. Model Training ──────────────────────────────────────
print("\n  Training Random Forest Regressor ...")
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=12,
    min_samples_split=4,
    random_state=42,
    n_jobs=-1,
)
model.fit(X_train_scaled, y_train)
print("[OK] Training complete.")

# ── 6. Evaluation ──────────────────────────────────────────
y_pred = model.predict(X_test_scaled)
r2     = r2_score(y_test, y_pred)
mae    = mean_absolute_error(y_test, y_pred)
rmse   = np.sqrt(mean_squared_error(y_test, y_pred))

print("\n--- Model Evaluation (Test Set) ---")
print(f"   R2 Score  :  {r2:.4f}")
print(f"   MAE       :  ${mae:,.2f}")
print(f"   RMSE      :  ${rmse:,.2f}")

# Feature importance
importances = model.feature_importances_
print("\n--- Feature Importances ---")
for feat, imp in sorted(zip(FEATURES, importances), key=lambda x: -x[1]):
    bar = "#" * int(imp * 40)
    print(f"   {feat:<20} {bar}  {imp:.3f}")

# ── 7. Save Artifacts ──────────────────────────────────────
model_path  = MODEL_DIR / "clv_model.pkl"
scaler_path = MODEL_DIR / "scaler.pkl"

with open(model_path, "wb") as f:
    pickle.dump(model, f)
with open(scaler_path, "wb") as f:
    pickle.dump(scaler, f)

print(f"\n[OK] Model saved  -> {model_path}")
print(f"[OK] Scaler saved -> {scaler_path}")
print("\n  All done! Run the backend with:")
print("  uvicorn backend.app:app --reload\n")
