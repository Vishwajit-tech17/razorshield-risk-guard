import sys
from pathlib import Path

# Ensure project root is in sys.path for modules like rag
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Union

import joblib
import pandas as pd

from rag.llm_investigator import generate_investigation

try:
    from backend.audit_db import (
        initialize_database,
        save_review,
        get_all_reviews,
    )
except ImportError:
    from audit_db import (
        initialize_database,
        save_review,
        get_all_reviews,
    )


# ============================================================
# RAZORSHIELD AI
# MAIN FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="RazorShield AI Risk Scoring API",
    description="AI-powered chargeback risk investigation system",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

@app.on_event("startup")
def startup_event():
    initialize_database()


# ============================================================
# LOAD MACHINE LEARNING MODEL
# ============================================================

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "ml"
    / "models"
    / "random_forest.joblib"
)


if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Random Forest model not found at: {MODEL_PATH}"
    )


model = joblib.load(MODEL_PATH)


# ============================================================
# RISK REQUEST SCHEMA
# ============================================================

class RiskRequest(BaseModel):

    transaction_id: str = "TXN-DEMO-001"

    amount: float

    payment_method: str

    ip_country: str

    authentication_status: str

    previous_transactions: int

    previous_chargebacks: int

    previous_refunds: int

    account_age_days: int

    successful_transactions: int

    known_devices: int

    average_order_value: float

    product_category: str

    delivery_status: str

    refund_status: str

    device_id: str

    transaction_day_of_week: int

    product_value: float

    transaction_hour: int

    is_weekend: int


# ============================================================
# ROOT / HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "service": "RazorShield AI",
        "status": "running",
        "version": "1.0.0",
    }


# ============================================================
# RISK LEVEL CALCULATION
# ============================================================

def get_risk_level(probability: float) -> str:

    if probability >= 0.70:
        return "HIGH"

    if probability >= 0.40:
        return "MEDIUM"

    return "LOW"


# ============================================================
# DAY 6 - RISK SCORING API
# ============================================================

@app.post("/risk-score")
def risk_score(request: RiskRequest):

    try:

        # ------------------------------------------------------
        # ENGINEERED FEATURES
        # ------------------------------------------------------

        amount_to_avg_order_ratio = (
            request.amount / request.average_order_value
            if request.average_order_value > 0
            else 0
        )

        has_previous_chargeback = (
            1
            if request.previous_chargebacks > 0
            else 0
        )

        is_new_customer = (
            1
            if request.account_age_days < 30
            else 0
        )

        customer_chargeback_rate = (
            request.previous_chargebacks
            / request.previous_transactions
            if request.previous_transactions > 0
            else 0
        )

        customer_refund_rate = (
            request.previous_refunds
            / request.previous_transactions
            if request.previous_transactions > 0
            else 0
        )

        customer_success_rate = (
            request.successful_transactions
            / request.previous_transactions
            if request.previous_transactions > 0
            else 0
        )

        # ------------------------------------------------------
        # CREATE MODEL INPUT DATAFRAME
        # ------------------------------------------------------

        data = pd.DataFrame(
            [
                {
                    # Original features
                    "amount": request.amount,

                    "payment_method":
                        request.payment_method,

                    "ip_country":
                        request.ip_country,

                    "authentication_status":
                        request.authentication_status,

                    "previous_transactions":
                        request.previous_transactions,

                    "previous_chargebacks":
                        request.previous_chargebacks,

                    "previous_refunds":
                        request.previous_refunds,

                    "account_age_days":
                        request.account_age_days,

                    "successful_transactions":
                        request.successful_transactions,

                    "known_devices":
                        request.known_devices,

                    "average_order_value":
                        request.average_order_value,

                    "product_category":
                        request.product_category,

                    "delivery_status":
                        request.delivery_status,

                    "refund_status":
                        request.refund_status,

                    # Required model features
                    "device_id":
                        request.device_id,

                    "transaction_day_of_week":
                        request.transaction_day_of_week,

                    "product_value":
                        request.product_value,

                    "transaction_hour":
                        request.transaction_hour,

                    "is_weekend":
                        request.is_weekend,

                    # Engineered features
                    "amount_to_avg_order_ratio":
                        amount_to_avg_order_ratio,

                    "has_previous_chargeback":
                        has_previous_chargeback,

                    "is_new_customer":
                        is_new_customer,

                    "customer_chargeback_rate":
                        customer_chargeback_rate,

                    "customer_refund_rate":
                        customer_refund_rate,

                    "customer_success_rate":
                        customer_success_rate,
                }
            ]
        )

        # ------------------------------------------------------
        # MACHINE LEARNING PREDICTION
        # ------------------------------------------------------

        probability = model.predict_proba(data)[0][1]

        probability = float(probability)

        risk_level = get_risk_level(probability)

        risk_percentage = probability * 100

        # ------------------------------------------------------
        # RESPONSE
        # ------------------------------------------------------

        return {

            "transaction_id":
                request.transaction_id,

            "risk_probability":
                round(probability, 4),

            "risk_percentage":
                round(risk_percentage, 2),

            "risk_level":
                risk_level,

            "model":
                "Random Forest",

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Risk scoring failed: {str(e)}",
        )


# ============================================================
# DAY 8 - AI INVESTIGATION API
# ============================================================

class InvestigationRequest(BaseModel):

    risk_probability: float

    query: str

    transaction: Dict[str, Any]


@app.post("/investigate")
def investigate(
    request: InvestigationRequest
):

    try:

        result = generate_investigation(
            risk_probability=request.risk_probability,
            transaction=request.transaction,
            query=request.query,
        )

        # Ensure schema keys are present for both frontend & API requirement
        result["recommendation"] = (
            result.get("recommendation")
            or result.get("ai_recommendation")
            or "Review available transaction and policy evidence before taking action."
        )
        result["reasoning"] = (
            result.get("investigation_reasoning")
            or result.get("reasoning")
            or []
        )
        result["policy_evidence"] = (
            result.get("supporting_policy_evidence")
            or result.get("policy_evidence")
            or []
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Investigation failed: {str(e)}",
        )


# ============================================================
# DAY 9 + DAY 10
# HUMAN REVIEW + AUDIT API
# ============================================================

class ReviewRequest(BaseModel):
    transaction: Dict[str, Any]

    decision: str

    reviewer_note: str = ""

    # Risk information sent directly from frontend
    risk_probability: float = 0.0
    risk_percentage: float = 0.0
    risk_level: str = "UNKNOWN"

    # AI investigation information
    ai_recommendation: str = ""
    ai_reasoning: Any = ""
    policy_evidence: Any = ""


# ============================================================
# HUMAN REVIEW SUBMISSION
# ============================================================

@app.post("/review")
def submit_review(request: ReviewRequest):

    # ========================================================
    # VALIDATE DECISION
    # ========================================================

    allowed_decisions = {
        "APPROVED",
        "REJECTED",
        "ESCALATED"
    }

    if request.decision not in allowed_decisions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid review decision. "
                "Use APPROVED, REJECTED, or ESCALATED."
            )
        )

    # ========================================================
    # TRANSACTION
    # ========================================================

    transaction = request.transaction or {}

    # ========================================================
    # TRANSACTION ID
    # ========================================================

    transaction_id = transaction.get(
        "transaction_id",
        "TXN-DEMO-001"
    )

    # ========================================================
    # RISK INFORMATION
    #
    # Read from top-level request OR fallback to transaction dict
    # ========================================================

    risk_probability = float(
        request.risk_probability or transaction.get("risk_probability", 0.0)
    )

    risk_percentage = float(
        request.risk_percentage or transaction.get("risk_percentage", 0.0)
    )

    risk_level = (
        request.risk_level
        if request.risk_level and request.risk_level != "UNKNOWN"
        else transaction.get("risk_level", "UNKNOWN")
    )

    # ========================================================
    # SAFETY FALLBACK
    # ========================================================

    if risk_probability == 0.0 and risk_percentage > 0:
        risk_probability = risk_percentage / 100.0

    if risk_percentage == 0.0 and risk_probability > 0:
        risk_percentage = risk_probability * 100.0

    if (risk_level == "UNKNOWN" or not risk_level) and risk_probability > 0:

        if risk_probability >= 0.70:
            risk_level = "HIGH"

        elif risk_probability >= 0.40:
            risk_level = "MEDIUM"

        else:
            risk_level = "LOW"

    # ========================================================
    # AI INFORMATION
    # ========================================================

    ai_recommendation = (
        request.ai_recommendation
        or transaction.get("ai_recommendation")
        or transaction.get("recommendation")
        or "Review available evidence before taking action."
    )

    ai_reasoning = (
        request.ai_reasoning
        or transaction.get("ai_reasoning")
        or transaction.get("reasoning")
        or transaction.get("investigation_reasoning")
        or "Investigation based on available transaction and policy evidence."
    )

    policy_evidence = (
        request.policy_evidence
        or transaction.get("policy_evidence")
        or transaction.get("supporting_policy_evidence")
        or ""
    )

    # ========================================================
    # DEBUG LOG
    # ========================================================

    print("\n========================================")
    print("HUMAN REVIEW")
    print("========================================")
    print("Transaction ID:", transaction_id)
    print("Risk Probability:", risk_probability)
    print("Risk Percentage:", risk_percentage)
    print("Risk Level:", risk_level)
    print("AI Recommendation:", ai_recommendation)
    print("Decision:", request.decision)
    print("========================================\n")

    # ========================================================
    # SAVE TO AUDIT DATABASE
    # ========================================================

    try:

        audit_record = save_review(

            transaction_id=transaction_id,

            amount=transaction.get(
                "amount",
                0
            ),

            risk_probability=risk_probability,

            risk_percentage=risk_percentage,

            risk_level=risk_level,

            ai_recommendation=ai_recommendation,

            ai_reasoning=ai_reasoning,

            policy_evidence=policy_evidence,

            human_decision=request.decision,

            reviewer_note=request.reviewer_note
        )

    except Exception as e:

        print(
            "AUDIT SAVE ERROR:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save audit record: {str(e)}"
            )
        )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "success": True,

        "transaction_id":
            transaction_id,

        "risk_probability":
            risk_probability,

        "risk_percentage":
            risk_percentage,

        "risk_level":
            risk_level,

        "ai_recommendation":
            ai_recommendation,

        "decision":
            request.decision,

        "reviewer_note":
            request.reviewer_note,

        "audit_record":
            audit_record,

        "message":
            (
                "Human review successfully recorded "
                f"as {request.decision}."
            )
    }

# ============================================================
# DAY 10 - AUDIT HISTORY
# ============================================================

@app.get("/audit")
def get_audit_history():

    try:

        records = get_all_reviews()

        return {

            "success": True,

            "count":
                len(records),

            "records":
                records,

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve audit history: "
                f"{str(e)}"
            ),
        )