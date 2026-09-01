# RazorShield AI — AI-Powered Chargeback Risk & Evidence Intelligence Engine

> **Razorpay AI Buildathon 2026** — Track 02: AI Risk Manager  
> **Problem Focus**: Chargeback Risk Mitigation + Evidence Intelligence

---

## 1. Project Overview

**RazorShield AI** is an enterprise-grade merchant defense and decision-support system designed to reduce chargeback fraud losses, streamline dispute evidence collection, and eliminate unwarranted payment rejections.

Combining real-time machine learning risk scoring, TF-IDF Retrieval-Augmented Generation (RAG) policy intelligence, and a human-in-the-loop audit workflow, RazorShield AI empowers merchant risk analysts to make grounded, evidence-backed financial decisions.

---

## 2. Problem Statement

Merchants face severe financial losses and reputational damage due to payment chargebacks:
- **Financial Drag**: Merchants lose both order revenue and penalty fees ($15–$100 per chargeback).
- **False Positive Friction**: Overly aggressive fraud blocking alienates legitimate buyers and cuts revenue.
- **Evidence Gap**: Dispute defense requires synthesizing transaction telemetry, customer order history, 3DS authentication logs, and card brand dispute policies under tight strict deadlines.

RazorShield AI solves this by delivering automated risk scoring, dynamic evidence extraction, and policy-grounded analyst reasoning while keeping human analysts in total control of final financial actions.

---

## 3. System Architecture

```
                                  +---------------------------------------+
                                  |         React + Vite Dashboard        |
                                  |  (Risk Cards, Analyst AI, Audit UI)   |
                                  +-------------------+-------------------+
                                                      | HTTP / REST
                                                      v
                                  +---------------------------------------+
                                  |           FastAPI REST Server          |
                                  |            (backend/main.py)          |
                                  +---------+-------------------+---------+
                                            |                   |
                     +----------------------+                   +----------------------+
                     v                                                                         v
+---------------------------------------+                                   +---------------------------------------+
|          Machine Learning ML          |                                   |        RAG Policy Intelligence        |
|  - Preprocessing Pipeline             |                                   |  - TF-IDF Vectorizer                  |
|  - Random Forest / Logistic Reg.      |                                   |  - Chargeback Policy Knowledge Base   |
|  - Feature Engineering                |                                   |  - Grounded Analyst Reasoning         |
+---------------------------------------+                                   +---------------------------------------+
                                                    |
                                                    v
                                  +---------------------------------------+
                                  |        SQLite Audit Database          |
                                  |        (razorshield_audit.db)         |
                                  +---------------------------------------+
```

---

## 4. Machine Learning Approach

- **Model Architectures**: Trained and evaluated **Logistic Regression**, **Random Forest**, and **XGBoost** classifiers on engineered customer telemetry.
- **Feature Engineering**:
  - `amount_to_avg_order_ratio`: Ratio of current transaction amount to customer average order value.
  - `customer_chargeback_rate` & `customer_refund_rate`: Historical dispute frequency ratios.
  - `customer_success_rate`: Ratio of successful transactions to total transaction history.
  - `is_new_customer`: Indicator for account age under 30 days.
  - `has_previous_chargeback`: Binary marker for prior dispute records.
- **Preprocessing Pipeline**: Standard scaling for numerical features and One-Hot Encoding for categorical features (`payment_method`, `ip_country`, `authentication_status`, `product_category`, `delivery_status`).

---

## 5. Key Features

1. **Real-Time Risk Scoring**: Outputs continuous probability values ($0.0 \to 1.0$) and categorizes risk as `LOW` (< 40%), `MEDIUM` (40% - 70%), or `HIGH` (≥ 70%).
2. **Merchant Risk Analyst Engine**:
   - **Key Risk Signals**: Dynamically identifies risk factors (e.g. prior chargebacks, refund history, high AOV ratio).
   - **Key Mitigating Signals**: Dynamically highlights protective indicators (e.g. 3DS authentication success, delivered status, account age).
3. **Policy Evidence Intelligence**: RAG policy engine matches dispute policies against transaction context.
4. **Human-in-the-Loop Audit Workflow**: Enables merchant risk analysts to `APPROVE`, `REJECT`, or `ESCALATE` transactions, recording full reviewer notes and timestamps.
5. **Synthetic Demo Case Selector**: Built-in selector (`Low Risk`, `Medium Risk`, `High Risk`) to demonstrate real end-to-end API workflows without hardcoded scores.

---

## 6. API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /` | `GET` | System health check and status response. |
| `POST /risk-score` | `POST` | Computes ML model chargeback risk probability and risk level. |
| `POST /investigate` | `POST` | Generates evidence-grounded analyst report and retrieves policy snippets. |
| `POST /review` | `POST` | Submits human analyst review decision and persists record to SQLite. |
| `GET /audit` | `GET` | Fetches historical human review audit logs from SQLite DB. |

---

## 7. Dataset & ML Evaluation Methodology

- **Dataset**: `data/processed/model_data.csv` (5,000 synthetic transaction telemetry records).
- **Split**: 70% Stratified Training set (3,500 samples) / 30% Held-Out Test set (1,500 samples).
- **Business Cost Rationale**:
  - **False Positive (FP)**: Unwarranted decline/investigation friction (Cost: ₹500).
  - **False Negative (FN)**: Missed fraud resulting in chargeback loss + fees (Cost: ₹10,000).

### Empirical Evaluation Results (Held-Out Test Set: 1,500 samples)

| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC | False Positives | FP Actual Volume | False Negatives | Total Risk Cost |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 0.5573 | 0.1034 | **0.3699** | **0.1616** | **0.4952** | 555 | ₹2,315,121.12 | 109 | **₹1,367,500** |
| **XGBoost** | 0.8387 | 0.1290 | 0.0694 | 0.0902 | 0.4821 | 81 | ₹281,846.65 | 161 | ₹1,650,500 |
| **Random Forest** | 0.8427 | 0.1294 | 0.0636 | 0.0853 | 0.4896 | 74 | ₹245,085.61 | 162 | ₹1,657,000 |

*Evaluation execution script*: [`evaluation/evaluate_model.py`](file:///c:/Users/ambhu/razorshield-risk-guard/evaluation/evaluate_model.py)

---

## 8. How to Run the Project

### Prerequisites
- Python 3.10+
- Node.js 18+

### Step 1: Install Dependencies
```bash
# Install Python backend dependencies
pip install -r requirements.txt

# Install React frontend dependencies
cd frontend
npm install
cd ..
```

### Step 2: Start FastAPI Backend
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
*Backend runs at `http://127.0.0.1:8000`*

### Step 3: Start Frontend Dashboard
```bash
cd frontend
npm run dev
```
*Frontend runs at `http://localhost:5173`*

---

## 9. Demo Instructions

1. Open `http://localhost:5173` in your browser.
2. Observe the **Demo Transaction Selector** bar at the top.
3. Click **Demo Case — Low Risk** (`DEMO-LOW-001`), **Demo Case — Medium Risk** (`TXN-DEMO-001`), or **Demo Case — High Risk** (`DEMO-HIGH-003`).
4. Watch the real ML model calculate the risk score and the analyst engine retrieve grounded policy evidence.
5. Click **Start Human Review**, select `APPROVE`, `REJECT`, or `ESCALATE`, and view the updated **Audit Trail**.

---

## 10. Defense-Only Statement & System Limitations

> **Defense-Only Disclaimer**: RazorShield AI is strictly a merchant defense decision-support tool. It does NOT automatically reject payments or execute financial clawbacks. All final financial decisions rest exclusively with authorized human merchant analysts.

### Current Limitations
- RAG policy retrieval uses TF-IDF vectorization over curated text policies; dense embedding models (e.g. BGE/OpenAI) can be integrated for higher semantic precision.
- Synthetic training data contains noise; model performance will scale when retrained on live payment gateway production logs.

---

## 11. Future Improvements

- Integration of dense neural vector databases (e.g., ChromaDB / Qdrant) for policy RAG.
- Automated chargeback dispute representment package generation (PDF export).
- Multi-tenant merchant dashboard with role-based access control (RBAC).
