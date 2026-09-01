# ============================================================
# RAZORSHIELD AI - DAY 9
# Human Review Decision Engine
# ============================================================


def determine_review_action(
    risk_probability,
    evidence_available,
    conflicting_signals=False,
    financial_impact="NORMAL"
):
    """
    Determine whether a transaction requires human review.

    AI provides decision support only.
    Final financial action remains with a human reviewer.
    """

    # --------------------------------------------------------
    # Risk classification
    # --------------------------------------------------------

    risk_probability = float(risk_probability)

    if risk_probability >= 0.70:
        risk_level = "HIGH"

    elif risk_probability >= 0.40:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"


    # --------------------------------------------------------
    # Normalize financial impact
    # --------------------------------------------------------

    financial_impact = str(financial_impact).upper()


    # --------------------------------------------------------
    # Evidence availability
    # --------------------------------------------------------

    if not evidence_available:

        return {
            "action": "ESCALATE",
            "reason": (
                "Required evidence is unavailable. "
                "The transaction must be reviewed by a human."
            ),
            "priority": "HIGH",
            "risk_level": risk_level,
            "risk_probability": round(risk_probability, 4),
            "human_required": True
        }


    # --------------------------------------------------------
    # Conflicting evidence
    # --------------------------------------------------------

    if conflicting_signals:

        return {
            "action": "ESCALATE",
            "reason": (
                "Available evidence contains conflicting signals. "
                "Human investigation is required before taking action."
            ),
            "priority": "HIGH",
            "risk_level": risk_level,
            "risk_probability": round(risk_probability, 4),
            "human_required": True
        }


    # --------------------------------------------------------
    # HIGH RISK
    # --------------------------------------------------------

    if risk_level == "HIGH":

        return {
            "action": "ESCALATE",
            "reason": (
                "The ML model indicates high chargeback risk. "
                "Human investigation is required before taking action."
            ),
            "priority": "HIGH",
            "risk_level": risk_level,
            "risk_probability": round(risk_probability, 4),
            "human_required": True
        }


    # --------------------------------------------------------
    # MEDIUM RISK
    # --------------------------------------------------------

    if risk_level == "MEDIUM":

        if financial_impact == "HIGH":

            return {
                "action": "ESCALATE",
                "reason": (
                    "The transaction has medium risk with high "
                    "financial impact. Human investigation is required."
                ),
                "priority": "HIGH",
                "risk_level": risk_level,
                "risk_probability": round(risk_probability, 4),
                "human_required": True
            }

        return {
            "action": "REVIEW",
            "reason": (
                "The transaction has medium chargeback risk. "
                "Available evidence should be reviewed by a human "
                "before taking action."
            ),
            "priority": "MEDIUM",
            "risk_level": risk_level,
            "risk_probability": round(risk_probability, 4),
            "human_required": True
        }


    # --------------------------------------------------------
    # LOW RISK
    # --------------------------------------------------------

    return {
        "action": "MONITOR",
        "reason": (
            "The transaction has low immediate chargeback risk. "
            "Continue normal monitoring."
        ),
        "priority": "LOW",
        "risk_level": risk_level,
        "risk_probability": round(risk_probability, 4),
        "human_required": False
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("RAZORSHIELD AI - DAY 9 REVIEW ENGINE TEST")
    print("=" * 60)


    # --------------------------------------------------------
    # Test 1 - HIGH RISK
    # --------------------------------------------------------

    result_high = determine_review_action(
        risk_probability=0.82,
        evidence_available=True,
        conflicting_signals=False,
        financial_impact="NORMAL"
    )

    print("\nHIGH RISK TEST")
    print("Action:", result_high["action"])
    print("Reason:", result_high["reason"])
    print("Priority:", result_high["priority"])


    # --------------------------------------------------------
    # Test 2 - MEDIUM RISK
    # --------------------------------------------------------

    result_medium = determine_review_action(
        risk_probability=0.58,
        evidence_available=True,
        conflicting_signals=False,
        financial_impact="NORMAL"
    )

    print("\nMEDIUM RISK TEST")
    print("Action:", result_medium["action"])
    print("Reason:", result_medium["reason"])
    print("Priority:", result_medium["priority"])


    # --------------------------------------------------------
    # Test 3 - LOW RISK
    # --------------------------------------------------------

    result_low = determine_review_action(
        risk_probability=0.20,
        evidence_available=True,
        conflicting_signals=False,
        financial_impact="NORMAL"
    )

    print("\nLOW RISK TEST")
    print("Action:", result_low["action"])
    print("Reason:", result_low["reason"])
    print("Priority:", result_low["priority"])


    # --------------------------------------------------------
    # Test 4 - Missing evidence
    # --------------------------------------------------------

    result_missing = determine_review_action(
        risk_probability=0.45,
        evidence_available=False,
        conflicting_signals=False,
        financial_impact="NORMAL"
    )

    print("\nMISSING EVIDENCE TEST")
    print("Action:", result_missing["action"])
    print("Reason:", result_missing["reason"])
    print("Priority:", result_missing["priority"])


    # --------------------------------------------------------
    # Test 5 - Conflicting signals
    # --------------------------------------------------------

    result_conflict = determine_review_action(
        risk_probability=0.50,
        evidence_available=True,
        conflicting_signals=True,
        financial_impact="NORMAL"
    )

    print("\nCONFLICTING SIGNALS TEST")
    print("Action:", result_conflict["action"])
    print("Reason:", result_conflict["reason"])
    print("Priority:", result_conflict["priority"])


    print("\n" + "=" * 60)
    print("DAY 9 REVIEW ENGINE TEST COMPLETE")
    print("=" * 60)