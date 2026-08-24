import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    confusion_matrix,
)


# ============================================================
# RAZORSHIELD AI - DAY 5
# Model Evaluation + Threshold Analysis
# ============================================================

DATA_PATH = "data/processed/model_data.csv"
MODEL_DIR = "ml/models"

TARGET = "chargeback_label"

# Business costs
FALSE_POSITIVE_COST = 500
FALSE_NEGATIVE_COST = 10000


print("=" * 60)
print("RAZORSHIELD AI - DAY 5 EVALUATION")
print("=" * 60)


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv(DATA_PATH)

print(f"\nDataset shape: {df.shape}")

if TARGET not in df.columns:
    raise ValueError(
        f"Target column '{TARGET}' was not found.\n"
        f"Available columns: {list(df.columns)}"
    )

X = df.drop(columns=[TARGET])
y = df[TARGET].astype(int)


# ------------------------------------------------------------
# 2. REMOVE IDENTIFIER COLUMNS
# ------------------------------------------------------------

identifier_columns = [
    "transaction_id",
    "customer_id",
    "order_id",
    "chargeback_id",
]

existing_identifiers = [
    col
    for col in identifier_columns
    if col in X.columns
]

if existing_identifiers:
    X = X.drop(columns=existing_identifiers)

print("\nRemoved identifier columns:")
print(existing_identifiers)


# ------------------------------------------------------------
# 3. REMOVE RAW DATE/TIME COLUMNS
# ------------------------------------------------------------

datetime_columns = [
    col
    for col in X.columns
    if "time" in col.lower() or "date" in col.lower()
]

if datetime_columns:
    X = X.drop(columns=datetime_columns)

print("\nRemoved datetime columns:")
print(datetime_columns)


# ------------------------------------------------------------
# 4. 70 / 15 / 15 DATA SPLIT
# ------------------------------------------------------------

# 70% Training
# 15% Validation
# 15% Test

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y,
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp,
)


print("\nData split:")
print(f"Training samples:   {len(X_train)}")
print(f"Validation samples: {len(X_val)}")
print(f"Testing samples:    {len(X_test)}")


# ------------------------------------------------------------
# 5. LOAD BASELINE RESULTS
# ------------------------------------------------------------

results_path = os.path.join(
    MODEL_DIR,
    "baseline_results.csv"
)

if not os.path.exists(results_path):
    raise FileNotFoundError(
        f"Could not find: {results_path}\n"
        "Run Day 4 training first."
    )

results_df = pd.read_csv(results_path)

results_df = results_df.sort_values(
    by="f1",
    ascending=False
)

best_model_name = results_df.iloc[0]["model"]

print("\n" + "=" * 60)
print("BEST BASELINE MODEL")
print("=" * 60)

print(best_model_name)


# ------------------------------------------------------------
# 6. LOAD BEST MODEL
# ------------------------------------------------------------

filename = (
    best_model_name
    .lower()
    .replace(" ", "_")
    + ".joblib"
)

model_path = os.path.join(
    MODEL_DIR,
    filename
)

if not os.path.exists(model_path):
    raise FileNotFoundError(
        f"Could not find model: {model_path}\n"
        "Run Day 4 training first."
    )

pipeline = joblib.load(model_path)

print(f"Loaded model: {model_path}")


# ------------------------------------------------------------
# 7. GET PREDICTED PROBABILITIES
# ------------------------------------------------------------

# We use probabilities instead of predict()
# because Day 5 evaluates different thresholds.

test_probabilities = pipeline.predict_proba(
    X_test
)[:, 1]


# ------------------------------------------------------------
# 8. THRESHOLD ANALYSIS
# ------------------------------------------------------------

thresholds = [
    0.30,
    0.40,
    0.50,
    0.60,
    0.70,
    0.80,
    0.90,
]

threshold_results = []


print("\n" + "=" * 60)
print("THRESHOLD ANALYSIS")
print("=" * 60)


for threshold in thresholds:

    # Convert probability into prediction
    predictions = (
        test_probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(
        y_test,
        predictions
    ).ravel()

    # Business cost
    total_cost = (
        fp * FALSE_POSITIVE_COST
        +
        fn * FALSE_NEGATIVE_COST
    )

    threshold_results.append(
        {
            "threshold": threshold,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
            "true_positive": tp,
            "estimated_cost": total_cost,
        }
    )

    print("\n----------------------------------------")
    print(f"Threshold: {threshold:.2f}")
    print("----------------------------------------")

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    print(f"True Negative : {tn}")
    print(f"False Positive: {fp}")
    print(f"False Negative: {fn}")
    print(f"True Positive : {tp}")

    print(f"Estimated Cost: Rs.{total_cost:,}")


# ------------------------------------------------------------
# 9. SAVE THRESHOLD ANALYSIS
# ------------------------------------------------------------

threshold_df = pd.DataFrame(
    threshold_results
)

threshold_path = os.path.join(
    MODEL_DIR,
    "threshold_analysis.csv"
)

threshold_df.to_csv(
    threshold_path,
    index=False
)

print("\nThreshold analysis saved to:")
print(threshold_path)


# ------------------------------------------------------------
# 10. FIND LOWEST-COST THRESHOLD
# ------------------------------------------------------------

best_cost_row = threshold_df.loc[
    threshold_df["estimated_cost"].idxmin()
]

best_threshold = best_cost_row["threshold"]


print("\n" + "=" * 60)
print("RECOMMENDED BUSINESS THRESHOLD")
print("=" * 60)

print(
    f"Recommended threshold: "
    f"{best_threshold:.2f}"
)

print(
    f"Estimated cost: "
    f"Rs.{best_cost_row['estimated_cost']:,.0f}"
)

print(
    f"Precision: "
    f"{best_cost_row['precision']:.4f}"
)

print(
    f"Recall: "
    f"{best_cost_row['recall']:.4f}"
)

print(
    f"F1 Score: "
    f"{best_cost_row['f1']:.4f}"
)

print(
    f"False Positives: "
    f"{int(best_cost_row['false_positive'])}"
)

print(
    f"False Negatives: "
    f"{int(best_cost_row['false_negative'])}"
)


# ------------------------------------------------------------
# 11. FINAL CONFUSION MATRIX
# ------------------------------------------------------------

final_predictions = (
    test_probabilities >= best_threshold
).astype(int)

final_cm = confusion_matrix(
    y_test,
    final_predictions
)

print("\n" + "=" * 60)
print("FINAL CONFUSION MATRIX")
print("=" * 60)

print(final_cm)


# ------------------------------------------------------------
# 12. FINAL SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("DAY 5 EVALUATION COMPLETE")
print("=" * 60)

print(f"\nBest model       : {best_model_name}")
print(f"Best threshold   : {best_threshold:.2f}")
print(
    f"Estimated cost   : "
    f"Rs.{best_cost_row['estimated_cost']:,.0f}"
)

print("\nSaved file:")
print(threshold_path)

print("\nReady for Day 5 analysis.")