# ============================================================
# RAZORSHIELD AI - DAY 9
# HUMAN REVIEW & POLICY ESCALATION ENGINE
# ============================================================

# ------------------------------------------------------------
# HUMAN REVIEW DECISION
# ------------------------------------------------------------

def determine_review_action(
    risk_probability,
    evidence_available=True,
    conflicting_signals=False,
    financial_impact="NORMAL"
):
    """
    Determine whether a chargeback investigation should be
    handled automatically or escalated to a human investigator.

    RazorShield AI follows a human-in-the-loop approach.
    """

    # --------------------------------------------------------
    # 1. Insufficient evidence
    # --------------------------------------------------------

    if not evidence_available:

        return {
            "action": "HUMAN_REVIEW",
            "reason": "Insufficient evidence available.",
            "priority": "HIGH"
        }

    # --------------------------------------------------------
    # 2. Conflicting signals
    # --------------------------------------------------------

    if conflicting_signals:

        return {
            "action": "HUMAN_REVIEW",
            "reason": "Conflicting transaction risk signals detected.",
            "priority": "HIGH"
        }

    # --------------------------------------------------------
    # 3. High financial impact
    # --------------------------------------------------------

    if financial_impact.upper() == "HIGH":

        return {
            "action": "HUMAN_REVIEW",
            "reason": "Transaction has high financial impact.",
            "priority": "HIGH"
        }

    # --------------------------------------------------------
    # 4. High ML risk
    # --------------------------------------------------------

    if risk_probability >= 0.70:

        return {
            "action": "HUMAN_REVIEW",
            "reason": "ML model assigned high chargeback risk.",
            "priority": "HIGH"
        }

    # --------------------------------------------------------
    # 5. Medium risk
    # --------------------------------------------------------

    if risk_probability >= 0.40:

        return {
            "action": "REVIEW_EVIDENCE",
            "reason": "Medium risk requires evidence review.",
            "priority": "MEDIUM"
        }

    # --------------------------------------------------------
    # 6. Low risk
    # --------------------------------------------------------

    return {
        "action": "NORMAL_MONITORING",
        "reason": "Low immediate chargeback risk detected.",
        "priority": "LOW"
    }


# ------------------------------------------------------------
# TEST
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("RAZORSHIELD AI - HUMAN REVIEW TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # TEST 1 - HIGH RISK
    # --------------------------------------------------------

    print("\nTEST 1: High Risk")

    result = determine_review_action(
        risk_probability=0.82,
        evidence_available=True,
        conflicting_signals=False,
        financial_impact="NORMAL"
    )

    print("Action:", result["action"])
    print("Reason:", result["reason"])
    print("Priority:", result["priority"])

    # --------------------------------------------------------
    # TEST 2 - MEDIUM RISK
    # --------------------------------------------------------

    print("\nTEST 2: Medium Risk")

    result = determine_review_action(
        risk_probability=0.58,
        evidence_available=True,
        conflicting_signals=False,
        financial_impact="NORMAL"
    )

    print("Action:", result["action"])
    print("Reason:", result["reason"])
    print("Priority:", result["priority"])

    # --------------------------------------------------------
    # TEST 3 - INSUFFICIENT EVIDENCE
    # --------------------------------------------------------

    print("\nTEST 3: Insufficient Evidence")

    result = determine_review_action(
        risk_probability=0.30,
        evidence_available=False,
        conflicting_signals=False,
        financial_impact="NORMAL"
    )

    print("Action:", result["action"])
    print("Reason:", result["reason"])
    print("Priority:", result["priority"])

    # --------------------------------------------------------
    # TEST 4 - CONFLICTING SIGNALS
    # --------------------------------------------------------

    print("\nTEST 4: Conflicting Signals")

    result = determine_review_action(
        risk_probability=0.35,
        evidence_available=True,
        conflicting_signals=True,
        financial_impact="NORMAL"
    )

    print("Action:", result["action"])
    print("Reason:", result["reason"])
    print("Priority:", result["priority"])

    # --------------------------------------------------------
    # TEST 5 - HIGH FINANCIAL IMPACT
    # --------------------------------------------------------

    print("\nTEST 5: High Financial Impact")

    result = determine_review_action(
        risk_probability=0.25,
        evidence_available=True,
        conflicting_signals=False,
        financial_impact="HIGH"
    )

    print("Action:", result["action"])
    print("Reason:", result["reason"])
    print("Priority:", result["priority"])

    print("\n" + "=" * 60)
    print("DAY 9 HUMAN REVIEW TEST COMPLETE")
    print("=" * 60)