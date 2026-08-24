from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import os


# ============================================================
# RAZORSHIELD AI - DAY 6
# Risk Scoring API
# ============================================================

app = FastAPI(
    title="RazorShield AI Risk Scoring API",
    description="ML-based chargeback risk scoring service",
    version="1.0.0",
)


# ------------------------------------------------------------
# LOAD MODEL
# ------------------------------------------------------------

MODEL_PATH = "ml/models/random_forest.joblib"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model not found at: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)


# ------------------------------------------------------------
# REQUEST SCHEMA
# ------------------------------------------------------------

class RiskRequest(BaseModel):

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

    # Additional features required by Day 4 model
    device_id: str

    transaction_day_of_week: int

    product_value: float

    transaction_hour: int

    is_weekend: int


# ------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------

@app.get("/")
def root():

    return {
        "service": "RazorShield AI",
        "status": "running",
        "version": "1.0.0",
    }


# ------------------------------------------------------------
# RISK LEVEL
# ------------------------------------------------------------

def get_risk_level(probability: float):

    if probability >= 0.70:
        return "HIGH"

    elif probability >= 0.40:
        return "MEDIUM"

    else:
        return "LOW"


# ------------------------------------------------------------
# RISK SCORING ENDPOINT
# ------------------------------------------------------------

@app.post("/risk-score")
def risk_score(request: RiskRequest):

    try:

        # ----------------------------------------------------
        # ENGINEERED FEATURES
        # ----------------------------------------------------

        amount_to_avg_order_ratio = (
            request.amount / request.average_order_value
            if request.average_order_value > 0
            else 0
        )

        has_previous_chargeback = (
            1 if request.previous_chargebacks > 0 else 0
        )

        is_new_customer = (
            1 if request.account_age_days < 30 else 0
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


        # ----------------------------------------------------
        # CREATE DATAFRAME
        # ----------------------------------------------------

        data = pd.DataFrame(
            [
                {

                    "amount": request.amount,

                    "payment_method": request.payment_method,

                    "ip_country": request.ip_country,

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


                    # ------------------------------------------------
                    # REQUIRED MODEL FEATURES
                    # ------------------------------------------------

                    "device_id":
                        request.device_id,

                    "transaction_day_of_week":
                        request.transaction_day_of_week,

                    "product_value":
                        request.product_value,


                    # ------------------------------------------------
                    # ENGINEERED FEATURES
                    # ------------------------------------------------

                    "amount_to_avg_order_ratio":
                        amount_to_avg_order_ratio,

                    "has_previous_chargeback":
                        has_previous_chargeback,

                    "is_new_customer":
                        is_new_customer,

                    "transaction_hour":
                        request.transaction_hour,

                    "customer_chargeback_rate":
                        customer_chargeback_rate,

                    "customer_refund_rate":
                        customer_refund_rate,

                    "customer_success_rate":
                        customer_success_rate,

                    "is_weekend":
                        request.is_weekend,
                }
            ]
        )


        # ----------------------------------------------------
        # PREDICTION
        # ----------------------------------------------------

        probability = model.predict_proba(data)[0][1]

        risk_level = get_risk_level(probability)


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {

            "risk_probability":
                round(float(probability), 4),

            "risk_percentage":
                round(float(probability) * 100, 2),

            "risk_level":
                risk_level,

            "model":
                "Random Forest",

        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )