# RazorShield AI — System Diagnostic & Root Cause Analysis

**Project**: RazorShield AI  
**Target**: Razorpay AI Buildathon 2026 (Track 02 — AI Risk Manager)  
**Date**: August 31, 2026  
**Status**: Diagnostic Complete — Pending Approval Before Modification  

---

## 1. Current Architecture

RazorShield AI consists of a Python FastAPI backend, a scikit-learn Machine Learning risk scoring engine, a TF-IDF RAG policy retrieval engine, an SQLite audit database, and a React + Vite dashboard frontend.

```
┌─────────────────────────────────────────────────────────────┐
│                      React + Vite Dashboard                 │
│                          (App.jsx)                          │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│                     (backend/main.py)                       │
├───────────────┬──────────────────────────────┬──────────────┤
│ ML Model      │ RAG Policy Engine            │ Audit DB     │
│ Random Forest │ TF-IDF Vectorizer            │ SQLite       │
│ (.joblib)     │ (rag/rag_engine.py)          │ (audit_db.py)│
└───────────────┴──────────────────────────────┴──────────────┘
```

---

## 2. Working Components

- **Random Forest ML Model (`ml/models/random_forest.joblib`)**:
  - Model loads and executes correctly with 25 engineered features.
  - Demo transaction `TXN-DEMO-001` yields a valid probability of **0.4944** (**49.44% risk**, **MEDIUM** risk level).
- **RAG Policy Engine (`rag/rag_engine.py`)**:
  - Successfully parses `rag/chargeback_policies.txt` into policy chunks.
  - TF-IDF vectorizer + Cosine Similarity correctly retrieves policy evidence (e.g. Policy 7 Chargeback History, Policy 6 New Customer Risk).
- **Human Review Decision Engine (`rag/review_engine.py`)**:
  - Evaluates risk probability + policy evidence to suggest review action (`REVIEW` / `ESCALATE` / `MONITOR`).
- **SQLite Database Schema (`backend/audit_db.py`)**:
  - Database table `review_audit` initializes properly on FastAPI startup.

---

## 3. Broken Components & Symptoms

1. **`POST /review` & `save_review` SQLite Parameter Binding**:
   - Passing `ai_reasoning` or `policy_evidence` as a Python `list` causes `sqlite3.ProgrammingError: Error binding parameter 7: type 'list' is not supported`, throwing **HTTP 500 Internal Server Error**.
2. **Backend/Frontend Schema Payload Mismatch**:
   - `ReviewRequest` expects `risk_probability`, `risk_percentage`, and `risk_level` at the **top level** of the JSON payload.
   - `App.jsx` sent these fields **nested inside `transaction`**, causing Pydantic to fall back to top-level default `risk_probability: 0.0`, `risk_percentage: 0.0`, and `risk_level: "UNKNOWN"`.
3. **Audit Database Contamination**:
   - Because of the payload mismatch, 24 out of 25 audit rows in `razorshield_audit.db` were saved with `0.0` risk probability and `"UNKNOWN"` risk level.
4. **Frontend Error Cascade & Monolithic `App.jsx`**:
   - Combined fetch calls in `loadData` inside `App.jsx` caused any single API error to crash the entire load cycle, setting state to `null` and displaying `"Investigation Unavailable"` or `0.00%`.
   - `App.jsx` contains duplicated JSX rendering blocks and redundant helper calculations across 1,985 lines.

---

## 4. Exact Root Cause of Each UI Problem

| # | Problem Visible in UI | Exact Root Cause |
|---|---|---|
| **1** | **Risk Score becomes 0.00% or stays Loading** | `getSafeProbability` defaults uninitialized or failed state to `0`. If `/risk-score` fetch fails or is delayed by coupled `/investigate` errors, `riskProbability` remains `null`/`0`. |
| **2** | **Risk Level becomes LOW unexpectedly** | `calculateRiskLevel(0)` evaluates `0 < 0.40` which returns `"LOW"`. When submitting reviews, missing top-level payload fields caused backend fallback to `"UNKNOWN"`/`"LOW"`. |
| **3** | **AI Investigation shows "Investigation Unavailable"** | `/risk-score` and `/investigate` fetches were tied in a single `try` block. A failure in one endpoint (or SQLite parameter error) triggered `catch`, setting `investigation` to `null`. |
| **4** | **Audit stores 0.00% Risk** | Payload nesting bug: `App.jsx` sent `risk_probability` inside `payload.transaction` instead of top-level `payload`. Backend Pydantic schema fell back to `0.0` default. |
| **5** | **Duplicated/Incomplete JSX & Syntax Errors** | `App.jsx` (1,985 lines) accumulated copy-pasted rendering blocks, inline array joins, and unhandled promise states. |
| **6** | **Fragile Prototype** | Lack of fallback parameter extraction in backend `/review`, unhandled non-string types in SQLite binding, and missing isolated frontend API error handling. |

---

## 5. Files Requiring Modification

- `backend/main.py`: Fix payload extraction in `/review`, add defensive fallback for nested transaction risk parameters, stringify list fields before saving to audit DB.
- `backend/audit_db.py`: Enforce string serialization for list/dict arguments in `save_review`.
- `frontend/src/App.jsx`: Fix `/review` payload structure, decouple API calls in `useEffect`, eliminate duplicated JSX, ensure robust state presentation.
- `frontend/src/App.css`: Ensure clean visual layout for risk levels, review workflow, and audit trail table.

---

## 6. Recommended Fix Strategy

1. **Backend Payload Alignment (`backend/main.py`)**:
   - Update `/review` endpoint to extract `risk_probability`, `risk_percentage`, and `risk_level` from top-level `request` OR nested `request.transaction`.
   - Ensure `ai_reasoning` and `policy_evidence` are converted to `str` before calling `save_review`.
2. **SQLite Safeguard (`backend/audit_db.py`)**:
   - Convert `ai_reasoning` and `policy_evidence` inputs with `str()` if not already string instances.
3. **Frontend Resilience (`frontend/src/App.jsx`)**:
   - Structure `reviewPayload` with top-level risk metrics.
   - Isolate `risk-score`, `investigate`, and `audit` API calls so failure in one does not clear the others.
   - Refactor JSX into modular, clean sections.

---

## 7. Commands to Run and Test the System

### Backend Startup & Test
```powershell
# Run backend server
python -m uvicorn backend.main:app --reload --port 8000
```

### Endpoints Verification Commands
```powershell
# 1. Test Risk Score
curl -X POST http://127.0.0.1:8000/risk-score -H "Content-Type: application/json" -d '{"transaction_id":"TXN-DEMO-001","amount":1249,"payment_method":"card","ip_country":"IN","authentication_status":"success","previous_transactions":17,"previous_chargebacks":1,"previous_refunds":2,"account_age_days":420,"successful_transactions":16,"known_devices":2,"average_order_value":850,"product_category":"electronics","delivery_status":"delivered","refund_status":"not_refunded","device_id":"device_001","transaction_day_of_week":5,"product_value":1249,"transaction_hour":14,"is_weekend":1}'

# 2. Test Audit History
curl http://127.0.0.1:8000/audit
```

### Frontend Startup
```powershell
cd frontend
npm run dev
```
