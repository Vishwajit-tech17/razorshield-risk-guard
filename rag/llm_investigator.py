# ============================================================
# RAZORSHIELD AI — MERCHANT RISK ANALYST INVESTIGATION ENGINE
# Track 02: AI Risk Manager — Razorpay AI Buildathon 2026
# ============================================================

from typing import Dict, Any, List
from .rag_engine import retrieve_policies
from .review_engine import determine_review_action


def extract_risk_signals(transaction: Dict[str, Any]) -> List[str]:
    """Extract grounded risk signals from actual transaction features."""
    signals = []
    
    cb = transaction.get("previous_chargebacks", 0)
    if cb > 0:
        signals.append(f"Previous chargeback history exists: {cb} past chargeback(s) recorded.")
        
    ref = transaction.get("previous_refunds", 0)
    if ref > 0:
        signals.append(f"Refund history exists: {ref} past refund(s) recorded on account.")
        
    amt = transaction.get("amount", 0)
    aov = transaction.get("average_order_value", 0)
    if amt > 0 and aov > 0 and amt > aov:
        diff_pct = round(((amt - aov) / aov) * 100, 1)
        signals.append(f"Transaction amount (₹{amt:,}) exceeds customer average order value (₹{aov:,}) by {diff_pct}%.")
        
    age = transaction.get("account_age_days", 999)
    if age < 30 or transaction.get("is_new_customer") == 1:
        signals.append(f"Account is relatively new ({age} days since registration).")
        
    auth = str(transaction.get("authentication_status", "")).lower()
    if auth and auth != "success":
        signals.append("Payment authentication status is not marked as successful.")

    return signals


def extract_mitigating_signals(transaction: Dict[str, Any]) -> List[str]:
    """Extract grounded protective/mitigating signals from actual transaction features."""
    signals = []
    
    auth = str(transaction.get("authentication_status", "")).lower()
    if auth == "success":
        signals.append("3D Secure / Payment authentication was completed successfully.")
        
    delivery = str(transaction.get("delivery_status", "")).lower()
    if delivery == "delivered":
        signals.append("Product delivery status is confirmed as successfully delivered.")
        
    age = transaction.get("account_age_days", 0)
    if age >= 90:
        signals.append(f"Established customer account age ({age} days old).")
        
    succ = transaction.get("successful_transactions", 0)
    if succ > 0:
        signals.append(f"Customer has {succ} past successful transaction(s) without dispute.")
        
    devices = transaction.get("known_devices", 0)
    if devices > 1:
        signals.append(f"Transaction originated from a recognized device ({devices} known device(s)).")

    return signals


def generate_investigation(
    risk_probability: float,
    transaction: Dict[str, Any],
    query: str
) -> Dict[str, Any]:
    """
    Generate an evidence-grounded merchant risk investigation report.

    Grounded strictly in:
    1. Transaction features
    2. ML model prediction signal
    3. Retrieved chargeback policy evidence

    Does NOT invent customer facts, transaction history, or policy rules.
    Never claims certainty that a transaction is fraudulent.
    System is strictly defense-only.
    """

    # 1. NORMALIZE RISK PROBABILITY & CLASSIFY RISK
    try:
        risk_probability = float(risk_probability)
    except (TypeError, ValueError):
        raise ValueError("risk_probability must be a valid number")

    if risk_probability > 1.0:
        risk_probability = risk_probability / 100.0

    risk_probability = max(0.0, min(1.0, risk_probability))
    risk_percentage = round(risk_probability * 100, 2)

    if risk_probability >= 0.70:
        risk_level = "HIGH"
    elif risk_probability >= 0.40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    if not isinstance(transaction, dict):
        raise ValueError("transaction must be a dictionary")

    # 2. RETRIEVE POLICY EVIDENCE VIA RAG
    policies = retrieve_policies(query)
    if policies is None:
        policies = []
    elif not isinstance(policies, list):
        policies = [policies]

    evidence_available = len(policies) > 0

    # 3. DYNAMIC SIGNAL EXTRACTION (GROUNDED IN TRANSACTION DATA)
    key_risk_signals = extract_risk_signals(transaction)
    key_mitigating_signals = extract_mitigating_signals(transaction)

    # 4. ML SIGNAL DESCRIPTION (NO FRAUD CERTAINTY CLAIM)
    ml_signal = (
        f"Random Forest baseline model assigned a {risk_level} chargeback risk level "
        f"({risk_percentage}% probability). This score represents statistical risk estimation "
        f"based on feature patterns and does not guarantee fraudulent intent."
    )

    # 5. DETERMINE HUMAN REVIEW ACTION
    review_decision = determine_review_action(
        risk_probability=risk_probability,
        evidence_available=evidence_available,
        conflicting_signals=len(key_risk_signals) > 0 and len(key_mitigating_signals) > 0,
        financial_impact="HIGH" if transaction.get("amount", 0) > 5000 else "NORMAL"
    )

    # 6. GROUNDED REASONING (EXPLICITLY DISTINGUISHING ML SIGNAL, EVIDENCE, POLICY, RECOMMENDATION)
    reasoning = [
        f"[ML SIGNAL] {ml_signal}",
        (
            f"[TRANSACTION EVIDENCE] Identified {len(key_risk_signals)} risk signal(s) "
            f"({', '.join(key_risk_signals[:2]) if key_risk_signals else 'None'}) and "
            f"{len(key_mitigating_signals)} mitigating signal(s) "
            f"({', '.join(key_mitigating_signals[:2]) if key_mitigating_signals else 'None'})."
        ),
        (
            f"[POLICY EVIDENCE] Retrieved {len(policies)} relevant chargeback policy snippet(s) matching query."
            if evidence_available
            else "[POLICY EVIDENCE] No relevant policy evidence was retrieved."
        ),
        (
            f"[RECOMMENDATION] Risk profile is balanced. {review_decision.get('reason', 'Review available evidence before taking financial action.')}"
        )
    ]

    # 7. RECOMMENDED ACTION
    if risk_level == "HIGH":
        recommended_action = "ESCALATE FOR MANUAL REVIEW: High ML risk score with elevated risk signals. Verify customer identity and delivery proof before settling funds."
    elif risk_level == "MEDIUM":
        recommended_action = "REVIEW AVAILABLE EVIDENCE: Moderate ML risk score with balanced mitigating and risk signals. Review transaction proof and chargeback history before taking financial action."
    else:
        recommended_action = "MONITOR TRANSACTION: Low immediate chargeback risk. Proceed with standard automated order processing."

    # 8. HUMAN REVIEW REQUIREMENT (DEFENSE-ONLY)
    human_review_requirement = {
        "human_required": review_decision.get("human_required", True),
        "action": review_decision.get("action", "REVIEW"),
        "defense_only": True,
        "disclaimer": (
            "Mandatory human review. RazorShield AI operates strictly as a merchant defense decision-support engine. "
            "Final financial decisions rest exclusively with the human merchant analyst."
        )
    }

    # 9. CONSTRUCT REPORT OBJECT
    report = {
        "risk_assessment": {
            "risk_probability": round(risk_probability, 4),
            "risk_percentage": risk_percentage,
            "risk_level": risk_level,
            "ml_signal": ml_signal
        },
        "key_risk_signals": key_risk_signals,
        "key_mitigating_signals": key_mitigating_signals,
        "recommended_action": recommended_action,
        "recommendation": recommended_action,
        "reasoning": reasoning,
        "investigation_reasoning": reasoning,
        "supporting_policy_evidence": policies,
        "policy_evidence": policies,
        "human_review_requirement": human_review_requirement,
        "human_review": review_decision,
        "transaction_summary": transaction,
        "evidence_warning": (
            "Do not invent missing evidence. AI output is decision support only. "
            "Human review is required when evidence is insufficient or signals conflict."
        )
    }

    return report


if __name__ == "__main__":
    test_transaction = {
        "amount": 1249,
        "payment_method": "card",
        "ip_country": "IN",
        "authentication_status": "success",
        "previous_transactions": 17,
        "previous_chargebacks": 1,
        "previous_refunds": 2,
        "account_age_days": 420,
        "successful_transactions": 16,
        "known_devices": 2,
        "average_order_value": 850,
        "product_category": "electronics",
        "delivery_status": "delivered",
        "refund_status": "not_refunded",
        "device_id": "device_001",
        "transaction_day_of_week": 5,
        "product_value": 1249,
        "transaction_hour": 14,
        "is_weekend": 1
    }

    res = generate_investigation(
        risk_probability=0.4944,
        transaction=test_transaction,
        query="customer transaction history authentication and chargeback policy"
    )

    import json
    print("=== INVESTIGATION ENGINE TEST OUTPUT ===")
    print(json.dumps({
        "risk_assessment": res["risk_assessment"],
        "key_risk_signals": res["key_risk_signals"],
        "key_mitigating_signals": res["key_mitigating_signals"],
        "recommended_action": res["recommended_action"],
        "reasoning": res["reasoning"],
        "human_review_requirement": res["human_review_requirement"]
    }, indent=2))