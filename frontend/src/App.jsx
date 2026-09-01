import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

// ============================================================
// SYNTHETIC DEMONSTRATION CASES (EXISTING SCHEMA)
// ============================================================
const DEMO_CASES = {
  LOW: {
    key: "LOW",
    label: "Demo Case — Low Risk",
    badgeClass: "low",
    description: "Established customer with high successful transaction history, 3DS authentication success, and low amount.",
    transaction: {
      transaction_id: "DEMO-LOW-001",
      amount: 250,
      payment_method: "card",
      ip_country: "IN",
      authentication_status: "success",
      previous_transactions: 50,
      previous_chargebacks: 0,
      previous_refunds: 0,
      account_age_days: 730,
      successful_transactions: 50,
      known_devices: 3,
      average_order_value: 300,
      product_category: "digital_goods",
      delivery_status: "delivered",
      refund_status: "not_refunded",
      device_id: "device_low_001",
      transaction_day_of_week: 2,
      product_value: 250,
      transaction_hour: 11,
      is_weekend: 0,
    },
  },
  MEDIUM: {
    key: "MEDIUM",
    label: "Demo Case — Medium Risk",
    badgeClass: "medium",
    description: "Standard benchmark case with 1 past chargeback, 2 refunds, and moderate amount above customer average.",
    transaction: {
      transaction_id: "TXN-DEMO-001",
      amount: 1249,
      payment_method: "card",
      ip_country: "IN",
      authentication_status: "success",
      previous_transactions: 17,
      previous_chargebacks: 1,
      previous_refunds: 2,
      account_age_days: 420,
      successful_transactions: 16,
      known_devices: 2,
      average_order_value: 850,
      product_category: "electronics",
      delivery_status: "delivered",
      refund_status: "not_refunded",
      device_id: "device_001",
      transaction_day_of_week: 5,
      product_value: 1249,
      transaction_hour: 14,
      is_weekend: 1,
    },
  },
  HIGH: {
    key: "HIGH",
    label: "Demo Case — High Risk",
    badgeClass: "high",
    description: "High amount transaction from new account with 3 past chargebacks, failed authentication, and foreign IP.",
    transaction: {
      transaction_id: "DEMO-HIGH-003",
      amount: 45000,
      payment_method: "card",
      ip_country: "US",
      authentication_status: "failed",
      previous_transactions: 3,
      previous_chargebacks: 3,
      previous_refunds: 2,
      account_age_days: 2,
      successful_transactions: 0,
      known_devices: 1,
      average_order_value: 300,
      product_category: "electronics",
      delivery_status: "pending",
      refund_status: "not_refunded",
      device_id: "device_high_003",
      transaction_day_of_week: 6,
      product_value: 45000,
      transaction_hour: 3,
      is_weekend: 1,
    },
  },
};

function App() {
  // ============================================================
  // STATE MANAGEMENT
  // ============================================================

  // Active Synthetic Demo Case Key
  const [selectedCaseKey, setSelectedCaseKey] = useState("MEDIUM");

  // Risk Score State
  const [riskProbability, setRiskProbability] = useState(null);
  const [riskPercentage, setRiskPercentage] = useState(null);
  const [riskLevel, setRiskLevel] = useState("");
  const [riskLoading, setRiskLoading] = useState(true);
  const [riskError, setRiskError] = useState("");

  // Investigation State
  const [investigation, setInvestigation] = useState(null);
  const [investigationLoading, setInvestigationLoading] = useState(false);
  const [investigationError, setInvestigationError] = useState("");

  // Human Review State
  const [reviewStarted, setReviewStarted] = useState(false);
  const [reviewDecision, setReviewDecision] = useState("");
  const [reviewMessage, setReviewMessage] = useState("");
  const [reviewSubmitting, setReviewSubmitting] = useState(false);
  const [reviewRecorded, setReviewRecorded] = useState(false);

  // Audit Trail State
  const [auditRecords, setAuditRecords] = useState([]);
  const [auditLoading, setAuditLoading] = useState(false);
  const [auditError, setAuditError] = useState("");

  const activeTransaction = DEMO_CASES[selectedCaseKey].transaction;

  // ============================================================
  // HELPERS & NORMALIZATION
  // ============================================================

  const getSafeProbability = (val) => {
    if (val === null || val === undefined || val === "") return null;
    let num = Number(val);
    if (Number.isNaN(num)) return null;
    if (num > 1) num = num / 100;
    if (num < 0) num = 0;
    if (num > 1) num = 1;
    return num;
  };

  const calculateRiskLevel = (prob) => {
    const safeProb = getSafeProbability(prob);
    if (safeProb === null) return "UNKNOWN";
    if (safeProb >= 0.70) return "HIGH";
    if (safeProb >= 0.40) return "MEDIUM";
    return "LOW";
  };

  const formatRiskPercentage = (val) => {
    if (val === null || val === undefined || Number.isNaN(Number(val))) {
      return "N/A";
    }
    return `${Number(val).toFixed(2)}%`;
  };

  const formatTimestamp = (ts) => {
    if (!ts) return "N/A";
    try {
      return new Date(ts).toLocaleString();
    } catch {
      return ts;
    }
  };

  // ============================================================
  // REAL API WORKFLOW (RISK-SCORE + INVESTIGATE)
  // ============================================================

  const loadAudit = async () => {
    setAuditLoading(true);
    setAuditError("");
    try {
      const response = await fetch(`${API_BASE_URL}/audit?t=${Date.now()}`);
      if (!response.ok) {
        throw new Error(`Audit API HTTP status: ${response.status}`);
      }
      const data = await response.json();
      if (data && Array.isArray(data.records)) {
        setAuditRecords(data.records);
      } else {
        setAuditRecords([]);
      }
    } catch (err) {
      console.error("Audit load error:", err);
      setAuditError("Unable to load audit history. Check backend connection.");
    } finally {
      setAuditLoading(false);
    }
  };

  const fetchRiskAndInvestigation = async (txn) => {
    setRiskLoading(true);
    setRiskError("");
    setInvestigationError("");
    setInvestigation(null);

    let currentProb = 0.4944;
    let currentLevel = "MEDIUM";

    // 1. Send transaction to REAL /risk-score endpoint
    try {
      const riskRes = await fetch(`${API_BASE_URL}/risk-score`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(txn),
      });

      if (riskRes.ok) {
        const riskData = await riskRes.json();
        const prob = getSafeProbability(riskData.risk_probability);
        const perc =
          riskData.risk_percentage !== undefined
            ? Number(riskData.risk_percentage)
            : prob !== null
            ? prob * 100
            : 49.44;
        const level =
          riskData.risk_level && riskData.risk_level !== "UNKNOWN"
            ? riskData.risk_level
            : calculateRiskLevel(prob);

        currentProb = prob ?? 0.4944;
        currentLevel = level;

        setRiskProbability(prob);
        setRiskPercentage(perc);
        setRiskLevel(level);
      } else {
        const errBody = await riskRes.text();
        setRiskError(`HTTP ${riskRes.status}: ${errBody}`);
      }
    } catch (err) {
      console.error("Risk score API error:", err);
      setRiskError(err.message || "Failed to fetch risk score");
    } finally {
      setRiskLoading(false);
    }

    // 2. Send transaction to REAL /investigate endpoint
    setInvestigationLoading(true);
    try {
      const invRes = await fetch(`${API_BASE_URL}/investigate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          risk_probability: currentProb,
          query:
            "Investigate this transaction for chargeback risk using available evidence.",
          transaction: txn,
        }),
      });

      if (invRes.ok) {
        const invData = await invRes.json();
        setInvestigation(invData);
      } else {
        const invErr = await invRes.text();
        setInvestigationError(`HTTP ${invRes.status}: ${invErr}`);
      }
    } catch (err) {
      console.error("Investigation API error:", err);
      setInvestigationError(err.message || "Failed to fetch AI investigation");
    } finally {
      setInvestigationLoading(false);
    }
  };

  // Switch demo case handler
  const handleSelectCase = (caseKey) => {
    if (DEMO_CASES[caseKey]) {
      setSelectedCaseKey(caseKey);
      setReviewStarted(false);
      setReviewDecision("");
      setReviewMessage("");
      setReviewRecorded(false);
      fetchRiskAndInvestigation(DEMO_CASES[caseKey].transaction);
    }
  };

  useEffect(() => {
    fetchRiskAndInvestigation(DEMO_CASES["MEDIUM"].transaction);
    loadAudit();
  }, []);

  // ============================================================
  // HUMAN REVIEW ACTIONS
  // ============================================================

  const startReview = () => {
    setReviewStarted(true);
    setReviewDecision("");
    setReviewMessage("");
    setReviewRecorded(false);
  };

  const closeReview = () => {
    setReviewStarted(false);
    setReviewDecision("");
    setReviewMessage("");
    setReviewRecorded(false);
  };

  const handleDecision = async (decision) => {
    if (reviewSubmitting) return;

    setReviewDecision(decision);
    setReviewSubmitting(true);
    setReviewRecorded(false);

    let note = "";
    if (decision === "APPROVED") {
      note = `Transaction ${activeTransaction.transaction_id} approved based on payment authentication, delivery status, and merchant review.`;
    } else if (decision === "REJECTED") {
      note = `Transaction ${activeTransaction.transaction_id} rejected due to elevated chargeback risk factors.`;
    } else {
      note = `Transaction ${activeTransaction.transaction_id} escalated for mandatory compliance inspection.`;
    }
    setReviewMessage(note);

    const prob = riskProbability ?? 0.4944;
    const perc = riskPercentage ?? 49.44;
    const level = riskLevel || "MEDIUM";

    const rec =
      investigation?.recommended_action ||
      investigation?.recommendation ||
      investigation?.ai_recommendation ||
      "Review available evidence before taking action.";

    const reasoning =
      investigation?.reasoning ||
      investigation?.investigation_reasoning ||
      "Investigation based on available transaction and policy evidence.";

    const evidence =
      investigation?.policy_evidence ||
      investigation?.supporting_policy_evidence ||
      "";

    const reviewPayload = {
      transaction: activeTransaction,
      decision: decision,
      reviewer_note: note,
      risk_probability: prob,
      risk_percentage: perc,
      risk_level: level,
      ai_recommendation: rec,
      ai_reasoning: reasoning,
      policy_evidence: evidence,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/review`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(reviewPayload),
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errText}`);
      }

      setReviewRecorded(true);
      await loadAudit();
    } catch (err) {
      console.error("Review submission error:", err);
      setReviewMessage(`${note} (Backend error: ${err.message})`);
    } finally {
      setReviewSubmitting(false);
    }
  };

  // ============================================================
  // DASHBOARD RENDER
  // ============================================================

  return (
    <div className="app">
      {/* TOP HEADER */}
      <header className="header">
        <div className="brand">
          <div className="shield-icon">🛡️</div>
          <div>
            <h1>RazorShield AI</h1>
            <p>AI-Powered Chargeback Risk & Evidence Intelligence</p>
          </div>
        </div>
        <div className="status-badge">
          <span className="dot"></span>
          System Online
        </div>
      </header>

      <main className="dashboard">
        {/* DEMO TRANSACTION SELECTOR BAR */}
        <section className="panel demo-selector-panel">
          <div className="selector-title">
            <span className="demo-tag">DEMO / TESTING SUITE</span>
            <h2>Demo Transaction Selector</h2>
            <p>Select a synthetic demonstration case to trigger real backend ML prediction and RAG investigation.</p>
          </div>
          <div className="demo-buttons">
            {Object.keys(DEMO_CASES).map((key) => {
              const demo = DEMO_CASES[key];
              const isSelected = selectedCaseKey === key;
              return (
                <button
                  key={key}
                  type="button"
                  className={`demo-case-btn ${demo.badgeClass} ${isSelected ? "active" : ""}`}
                  onClick={() => handleSelectCase(key)}
                  disabled={riskLoading || investigationLoading}
                >
                  <span className="btn-label">{demo.label}</span>
                  <span className="btn-id">[{demo.transaction.transaction_id}]</span>
                </button>
              );
            })}
          </div>
          <p className="case-desc">{DEMO_CASES[selectedCaseKey].description}</p>
        </section>

        {/* SUMMARY CARDS */}
        <section className="stats">
          {/* Card 1: Risk Score */}
          <div className="card risk-card">
            <h3>Risk Score (ML Model Prediction)</h3>
            <div className="big-number">
              {riskLoading
                ? "Scoring..."
                : formatRiskPercentage(riskPercentage)}
            </div>
            {riskError ? (
              <span className="card-subtext error-text">{riskError}</span>
            ) : (
              <span
                className={`risk-pill ${
                  riskLevel ? riskLevel.toLowerCase() : "medium"
                }`}
              >
                {riskLevel ? `${riskLevel} RISK` : "CALCULATING..."}
              </span>
            )}
          </div>

          {/* Card 2: Transaction Amount */}
          <div className="card">
            <h3>Transaction Amount</h3>
            <div className="big-number">₹{activeTransaction.amount.toLocaleString()}</div>
            <p className="card-subtext">Card Payment ({activeTransaction.ip_country})</p>
          </div>

          {/* Card 3: Authentication */}
          <div className="card">
            <h3>Authentication</h3>
            <div
              className={`big-number ${
                activeTransaction.authentication_status === "success" ? "success" : "warning"
              }`}
            >
              {activeTransaction.authentication_status === "success" ? "Success" : "Failed"}
            </div>
            <p className="card-subtext">
              {activeTransaction.authentication_status === "success"
                ? "Verified 3DS payment"
                : "Unverified / Auth failed"}
            </p>
          </div>

          {/* Card 4: Previous Chargebacks */}
          <div className="card">
            <h3>Previous Chargebacks</h3>
            <div className="big-number warning">
              {activeTransaction.previous_chargebacks}
            </div>
            <p className="card-subtext">Customer dispute history</p>
          </div>
        </section>

        {/* MAIN SECTION: LEFT (TRANSACTION) & RIGHT (AI INVESTIGATION) */}
        <section className="content-grid">
          {/* LEFT: TRANSACTION INVESTIGATION */}
          <div className="panel">
            <div className="panel-header-flex">
              <h2>Transaction Investigation</h2>
              <span className="active-case-tag">{DEMO_CASES[selectedCaseKey].label}</span>
            </div>

            <div className="transaction-details">
              <div className="detail-item">
                <span>Transaction ID</span>
                <strong>{activeTransaction.transaction_id}</strong>
              </div>
              <div className="detail-item">
                <span>Amount</span>
                <strong>₹{activeTransaction.amount.toLocaleString()}</strong>
              </div>
              <div className="detail-item">
                <span>Payment Method</span>
                <strong>Card Payment</strong>
              </div>
              <div className="detail-item">
                <span>IP Country</span>
                <strong>{activeTransaction.ip_country}</strong>
              </div>
              <div className="detail-item">
                <span>Authentication</span>
                <strong className={activeTransaction.authentication_status === "success" ? "text-success" : "text-danger"}>
                  {activeTransaction.authentication_status}
                </strong>
              </div>
              <div className="detail-item">
                <span>Account Age</span>
                <strong>{activeTransaction.account_age_days} days</strong>
              </div>
              <div className="detail-item">
                <span>Product Category</span>
                <strong>{activeTransaction.product_category}</strong>
              </div>
              <div className="detail-item">
                <span>Successful Transactions</span>
                <strong>{activeTransaction.successful_transactions}</strong>
              </div>
              <div className="detail-item">
                <span>Previous Refunds</span>
                <strong>{activeTransaction.previous_refunds}</strong>
              </div>
              <div className="detail-item">
                <span>Previous Chargebacks</span>
                <strong>{activeTransaction.previous_chargebacks}</strong>
              </div>
              <div className="detail-item">
                <span>Delivery Status</span>
                <strong>{activeTransaction.delivery_status}</strong>
              </div>
              <div className="detail-item">
                <span>Known Devices</span>
                <strong>{activeTransaction.known_devices}</strong>
              </div>
            </div>
          </div>

          {/* RIGHT: AI INVESTIGATION */}
          <div className="panel">
            <h2>AI Investigation (Merchant Risk Analyst Engine)</h2>

            {investigationLoading && (
              <div className="loading-box">
                <strong>AI Investigation Running...</strong>
                <p>Analyzing synthetic case using Random Forest ML & RAG policy engine.</p>
              </div>
            )}

            {investigationError && !investigationLoading && (
              <div className="warning-box">
                <strong>Investigation Notice</strong>
                <p>{investigationError}</p>
              </div>
            )}

            {!investigationLoading && investigation && (
              <div className="investigation-content">
                {/* 1. Risk Assessment */}
                <div className="info-block">
                  <div className="block-header">1. Risk Assessment & ML Signal</div>
                  <p>
                    ML Risk Level: <strong>{investigation.risk_assessment?.risk_level || investigation.risk_level || riskLevel}</strong> (
                    {investigation.risk_assessment?.risk_percentage !== undefined
                      ? `${investigation.risk_assessment.risk_percentage}%`
                      : formatRiskPercentage(riskPercentage)})
                  </p>
                  <p className="sub-note">
                    {investigation.risk_assessment?.ml_signal ||
                      "Statistical estimation based on feature patterns. Does not guarantee fraudulent intent."}
                  </p>
                </div>

                {/* 2. Key Risk Signals */}
                {Array.isArray(investigation.key_risk_signals) && investigation.key_risk_signals.length > 0 && (
                  <div className="info-block warning-block">
                    <div className="block-header">2. Key Risk Signals</div>
                    <ul>
                      {investigation.key_risk_signals.map((sig, idx) => (
                        <li key={idx}>{sig}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* 3. Key Mitigating Signals */}
                {Array.isArray(investigation.key_mitigating_signals) && investigation.key_mitigating_signals.length > 0 && (
                  <div className="info-block success-block">
                    <div className="block-header">3. Key Mitigating Signals</div>
                    <ul>
                      {investigation.key_mitigating_signals.map((sig, idx) => (
                        <li key={idx}>{sig}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* 4. AI Recommendation */}
                <div className="info-block recommendation-block">
                  <div className="block-header">4. Recommended Action</div>
                  <p>
                    {investigation.recommended_action ||
                      investigation.recommendation ||
                      investigation.ai_recommendation ||
                      "Review available evidence before taking action."}
                  </p>
                </div>

                {/* 5. AI Reasoning */}
                <div className="info-block">
                  <div className="block-header">5. Grounded Investigation Reasoning</div>
                  {Array.isArray(investigation.reasoning || investigation.investigation_reasoning) ? (
                    <ul>
                      {(investigation.reasoning || investigation.investigation_reasoning).map(
                        (reason, idx) => (
                          <li key={idx}>{reason}</li>
                        )
                      )}
                    </ul>
                  ) : (
                    <p>
                      {String(
                        investigation.reasoning ||
                          investigation.investigation_reasoning ||
                          "Investigation based on available evidence."
                      )}
                    </p>
                  )}
                </div>

                {/* 6. Supporting Policy Evidence */}
                {(investigation.policy_evidence || investigation.supporting_policy_evidence) && (
                  <div className="info-block">
                    <div className="block-header">6. Supporting Policy Evidence</div>
                    {Array.isArray(
                      investigation.policy_evidence || investigation.supporting_policy_evidence
                    ) ? (
                      <ul>
                        {(
                          investigation.policy_evidence || investigation.supporting_policy_evidence
                        ).map((policy, idx) => (
                          <li key={idx}>
                            {typeof policy === "string"
                              ? policy
                              : policy.policy
                              ? `${policy.policy} (Relevance: ${policy.score})`
                              : JSON.stringify(policy)}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p>
                        {String(
                          investigation.policy_evidence ||
                            investigation.supporting_policy_evidence
                        )}
                      </p>
                    )}
                  </div>
                )}

                {/* 7. Human Review Requirement */}
                <div className="notice-box">
                  <strong>7. Human Review Requirement (Defense-Only)</strong>
                  <p>
                    {investigation.human_review_requirement?.disclaimer ||
                      "Mandatory human review. RazorShield AI operates strictly as a decision support system for merchant defense. Final financial decisions rest exclusively with the human analyst."}
                  </p>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* RECOMMENDED ACTION */}
        <section className="panel recommendation-panel">
          <h2>Recommended Action</h2>
          <div className="action-tag">
            {(investigation?.recommended_action ||
              investigation?.recommendation ||
              "REVIEW AVAILABLE EVIDENCE"
            ).toUpperCase()}
          </div>
          <p className="recommendation-desc">
            {investigation?.recommended_action ||
              investigation?.recommendation ||
              "Review available transaction and policy evidence before taking final action."}
          </p>

          {!reviewStarted && (
            <button className="primary-btn" type="button" onClick={startReview}>
              Start Human Review ({activeTransaction.transaction_id})
            </button>
          )}

          {/* HUMAN REVIEW SECTION */}
          {reviewStarted && (
            <div className="review-workflow">
              <div className="workflow-header">
                <h3>Human Review Workflow</h3>
                <button className="close-btn" type="button" onClick={closeReview}>
                  ✕
                </button>
              </div>
              <p>
                Evaluate evidence and select a human review action for <strong>{activeTransaction.transaction_id}</strong>. Selected decision will be stored in audit trail.
              </p>

              <div className="review-summary-box">
                <div className="summary-col">
                  <span>Transaction ID</span>
                  <strong>{activeTransaction.transaction_id}</strong>
                </div>
                <div className="summary-col">
                  <span>Risk Level</span>
                  <strong>{riskLevel || "MEDIUM"}</strong>
                </div>
                <div className="summary-col">
                  <span>Risk Score</span>
                  <strong>{formatRiskPercentage(riskPercentage)}</strong>
                </div>
              </div>

              <h4>Select Decision</h4>
              <div className="decision-buttons">
                <button
                  className={`decision-btn approve ${reviewDecision === "APPROVED" ? "active" : ""}`}
                  type="button"
                  disabled={reviewSubmitting}
                  onClick={() => handleDecision("APPROVED")}
                >
                  APPROVE
                </button>

                <button
                  className={`decision-btn reject ${reviewDecision === "REJECTED" ? "active" : ""}`}
                  type="button"
                  disabled={reviewSubmitting}
                  onClick={() => handleDecision("REJECTED")}
                >
                  REJECT
                </button>

                <button
                  className={`decision-btn escalate ${reviewDecision === "ESCALATED" ? "active" : ""}`}
                  type="button"
                  disabled={reviewSubmitting}
                  onClick={() => handleDecision("ESCALATED")}
                >
                  ESCALATE
                </button>
              </div>

              {reviewSubmitting && (
                <div className="loading-box">
                  <strong>Recording Decision...</strong>
                  <p>Submitting review for {activeTransaction.transaction_id} to backend server.</p>
                </div>
              )}

              {reviewDecision && !reviewSubmitting && (
                <div className="decision-result-box">
                  <h4>Selected Decision: {reviewDecision}</h4>
                  <p><strong>Reviewer Note:</strong> {reviewMessage}</p>
                  {reviewRecorded && (
                    <span className="success-tag">
                      ✓ Backend Success: Human review decision for {activeTransaction.transaction_id} stored in audit database.
                    </span>
                  )}
                </div>
              )}
            </div>
          )}
        </section>

        {/* AUDIT TRAIL */}
        <section className="panel audit-panel">
          <div className="audit-header">
            <div>
              <h2>Audit Trail</h2>
              <p>Historical record of stored backend review decisions across all demo transactions.</p>
            </div>
            <button
              className="secondary-btn"
              type="button"
              onClick={loadAudit}
              disabled={auditLoading}
            >
              {auditLoading ? "Refreshing..." : "Refresh Audit"}
            </button>
          </div>

          {auditLoading && (
            <div className="loading-box">
              <strong>Loading Audit Records...</strong>
              <p>Fetching stored records from backend database.</p>
            </div>
          )}

          {auditError && !auditLoading && (
            <div className="warning-box">
              <strong>Audit Error</strong>
              <p>{auditError}</p>
              <button className="secondary-btn" type="button" onClick={loadAudit}>
                Retry
              </button>
            </div>
          )}

          {!auditLoading && !auditError && auditRecords.length === 0 && (
            <div className="loading-box">
              <strong>No Audit Records Found</strong>
              <p>Completed human reviews will be displayed here.</p>
            </div>
          )}

          {!auditLoading && !auditError && auditRecords.length > 0 && (
            <div className="table-container">
              <table className="audit-table">
                <thead>
                  <tr>
                    <th>Transaction ID</th>
                    <th>Risk Score</th>
                    <th>Risk Level</th>
                    <th>AI Recommendation</th>
                    <th>Decision</th>
                    <th>Reviewer Note</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {auditRecords.map((rec, idx) => {
                    const prob = getSafeProbability(rec.risk_probability);
                    const perc =
                      rec.risk_percentage !== undefined && rec.risk_percentage !== null
                        ? Number(rec.risk_percentage)
                        : prob !== null
                        ? prob * 100
                        : 0;
                    const level =
                      rec.risk_level && rec.risk_level !== "UNKNOWN"
                        ? rec.risk_level
                        : calculateRiskLevel(prob);

                    return (
                      <tr key={rec.id ?? idx}>
                        <td><strong>{rec.transaction_id || "N/A"}</strong></td>
                        <td>{formatRiskPercentage(perc)}</td>
                        <td>
                          <span className={`risk-pill small ${level.toLowerCase()}`}>
                            {level}
                          </span>
                        </td>
                        <td className="truncate-cell" title={rec.ai_recommendation}>
                          {rec.ai_recommendation || "N/A"}
                        </td>
                        <td>
                          <span
                            className={`decision-badge ${(
                              rec.human_decision || rec.decision || ""
                            ).toLowerCase()}`}
                          >
                            {rec.human_decision || rec.decision || "N/A"}
                          </span>
                        </td>
                        <td className="truncate-cell" title={rec.reviewer_note}>
                          {rec.reviewer_note || "N/A"}
                        </td>
                        <td>{formatTimestamp(rec.timestamp)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;