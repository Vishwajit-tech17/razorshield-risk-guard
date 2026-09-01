# RazorShield AI — ML Evaluation Report
**Track 02: AI Risk Manager — Razorpay AI Buildathon 2026**

This report documents the empirical evaluation of chargeback risk prediction models evaluated strictly on a held-out test dataset.

---

## 1. Dataset & Split Specifications

- **Total Dataset Size**: `5,000` labeled transactions
- **Training Set Size**: `3,500` samples (70% stratified split)
- **Held-Out Test Set Size**: `1,500` samples (30% stratified split)
- **Positive Class (1)**: `chargeback_label == 1 (Transaction resulted in chargeback dispute)` (`576` positive samples)
- **Negative Class (0)**: `chargeback_label == 0 (Legitimate transaction without dispute)` (`4424` negative samples)

---

## 2. Business Cost & Transaction Amount Assumptions

In chargeback risk management, prediction errors carry asymmetric business costs:

1. **False Positive (FP) Unit Friction Cost**: **₹500 per review**
   - *Rationale*: Cost of manual compliance officer investigation (~30 mins) + potential customer checkout friction.
2. **False Positive Transaction Volume Affected**: Actual sum of transaction amounts (`amount`) for legitimate transactions incorrectly flagged for investigation.
3. **False Negative (FN) Dispute Cost**: **₹10,000 per unmitigated dispute**
   - *Rationale*: Direct unrecovered merchant order loss (average ~₹8,500) + mandatory payment gateway chargeback fee (~₹1,500).

$$\text{Total Business Risk Cost} = (\text{False Positives} \times ₹500) + (\text{False Negatives} \times ₹10,000)$$

---

## 3. Held-Out Test Evaluation Summary

Below are the exact metrics computed **exclusively on the 1,500 held-out test transactions**:

| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC | False Positives | FP Actual Volume | False Negatives | Total Risk Cost |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 0.5573 | 0.1034 | 0.3699 | **0.1616** | 0.4952 | 555 | ₹2,315,121.12 | 109 | ₹1,367,500 |
| **Random Forest** | 0.8427 | 0.1294 | 0.0636 | **0.0853** | 0.4896 | 74 | ₹245,085.61 | 162 | ₹1,657,000 |
| **XGBoost** | 0.8387 | 0.1290 | 0.0694 | **0.0902** | 0.4821 | 81 | ₹281,846.65 | 161 | ₹1,650,500 |

---

## 4. Confusion Matrix Breakdowns (Held-Out Test Set)

```
=== Logistic Regression ===
  True Negatives (TN) : 772   | False Positives (FP): 555  
  False Negatives (FN): 109   | True Positives (TP) : 64   

=== Random Forest ===
  True Negatives (TN) : 1253  | False Positives (FP): 74   
  False Negatives (FN): 162   | True Positives (TP) : 11   

=== XGBoost ===
  True Negatives (TN) : 1246  | False Positives (FP): 81   
  False Negatives (FN): 161   | True Positives (TP) : 12   

```

---

## 5. Selected Production Model

- **Model Name**: **Logistic Regression**
- **Test F1 Score**: `0.1616`
- **Test Precision**: `0.1034`
- **Test Recall**: `0.3699`
- **Test Accuracy**: `0.5573`
- **Test False Positives**: `555` (Affected Volume: `₹2,315,121.12`)
- **Total Estimated Risk Cost**: `₹1,367,500`

### Selection Rationale
Logistic Regression achieved the highest F1 Score (0.1616) and Recall (0.3699) on the held-out test set while minimizing overall business risk cost (₹1,367,500). It effectively balances false-positive review friction costs with false-negative chargeback prevention.
