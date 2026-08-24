# ============================================================
# RAZORSHIELD AI - DAY 8
# LLM Investigation Engine
# ============================================================

from rag_engine import retrieve_policies


def generate_investigation(
    risk_probability,
    transaction,
    query
):
    """
    Generate an evidence-based chargeback investigation.

    This Day 8 version uses the ML risk score and
    retrieved policy evidence to create a structured
    investigation explanation.
    """

    # --------------------------------------------------------
    # Retrieve relevant policy evidence
    # --------------------------------------------------------

    policies = retrieve_policies(query)

    # --------------------------------------------------------
    # Risk classification
    # --------------------------------------------------------

    if risk_probability >= 0.70:
        risk_level = "HIGH"
    elif risk_probability >= 0.40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # --------------------------------------------------------
    # Build investigation result
    # --------------------------------------------------------

    investigation = {
        "risk_probability": round(float(risk_probability), 4),
        "risk_percentage": round(float(risk_probability) * 100, 2),
        "risk_level": risk_level,

        "transaction_summary": transaction,

        "supporting_policy_evidence": policies,

        "investigation_reasoning": [
            f"ML model assigned a {risk_level} risk level.",
            "Transaction information was evaluated against "
            "relevant chargeback policies.",
            "The investigation is based only on available "
            "transaction and policy evidence."
        ],

        "recommendation": (
            "Escalate for human investigation."
            if risk_level == "HIGH"
            else "Review available evidence before taking action."
            if risk_level == "MEDIUM"
            else "Low immediate risk; continue normal monitoring."
        ),

        "evidence_warning": (
            "Do not invent missing evidence. "
            "Human review is required when evidence is insufficient "
            "or signals conflict."
        )
    }

    return investigation


# ------------------------------------------------------------
# TEST
# ------------------------------------------------------------

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
        "refund_status": "not_refunded"
    }

    result = generate_investigation(
        risk_probability=0.58,
        transaction=test_transaction,
        query="customer transaction history and authentication"
    )

    print("\n" + "=" * 60)
    print("RAZORSHIELD AI - LLM INVESTIGATION TEST")
    print("=" * 60)

    print("\nRisk Level:")
    print(result["risk_level"])

    print("\nRisk Percentage:")
    print(result["risk_percentage"], "%")

    print("\nInvestigation Reasoning:")

    for reason in result["investigation_reasoning"]:
        print("-", reason)

    print("\nRecommendation:")
    print(result["recommendation"])

    print("\nEvidence Warning:")
    print(result["evidence_warning"])

    print("\nSupporting Policy Evidence:")
    print(result["supporting_policy_evidence"])

    print("\n" + "=" * 60)
    print("DAY 8 INVESTIGATION TEST COMPLETE")
    print("=" * 60)