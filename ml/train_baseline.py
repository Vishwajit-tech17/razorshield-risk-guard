import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    confusion_matrix,
)

from xgboost import XGBClassifier


# ============================================================
# RAZORSHIELD AI - DAY 4
# Baseline ML Training
# ============================================================

DATA_PATH = "data/processed/model_data.csv"
MODEL_DIR = "ml/models"

os.makedirs(MODEL_DIR, exist_ok=True)


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

print("=" * 60)
print("RAZORSHIELD AI - BASELINE ML TRAINING")
print("=" * 60)

df = pd.read_csv(DATA_PATH)

print(f"\nDataset shape: {df.shape}")
print("\nColumns:")
print(list(df.columns))


# ------------------------------------------------------------
# 2. TARGET
# ------------------------------------------------------------

TARGET = "chargeback_label"

if TARGET not in df.columns:
    raise ValueError(
        f"Target column '{TARGET}' was not found.\n"
        f"Available columns: {list(df.columns)}"
    )

X = df.drop(columns=[TARGET])
y = df[TARGET].astype(int)

print("\nTarget distribution:")
print(y.value_counts())

print(f"\nChargeback rate: {y.mean():.2%}")


# ------------------------------------------------------------
# 3. REMOVE IDENTIFIERS
# ------------------------------------------------------------

# These fields identify records but should not be predictive
# features for our baseline model.

identifier_columns = [
    "transaction_id",
    "customer_id",
    "order_id",
    "chargeback_id",
]

existing_identifiers = [
    col for col in identifier_columns
    if col in X.columns
]

if existing_identifiers:
    X = X.drop(columns=existing_identifiers)

print("\nRemoved identifier columns:")
print(existing_identifiers)


# ------------------------------------------------------------
# 4. HANDLE DATE/TIME COLUMNS
# ------------------------------------------------------------

datetime_columns = [
    col for col in X.columns
    if "time" in col.lower() or "date" in col.lower()
]

if datetime_columns:
    print("\nRemoving raw datetime columns:")
    print(datetime_columns)

    X = X.drop(columns=datetime_columns)


# ------------------------------------------------------------
# 5. TRAIN / TEST SPLIT
# ------------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

print("\nData split:")
print(f"Training samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}")


# ------------------------------------------------------------
# 6. IDENTIFY FEATURE TYPES
# ------------------------------------------------------------

numeric_features = X_train.select_dtypes(
    include=["int64", "float64", "int32", "float32"]
).columns.tolist()

categorical_features = X_train.select_dtypes(
    include=["object", "category", "bool"]
).columns.tolist()

print("\nNumeric features:")
print(numeric_features)

print("\nCategorical features:")
print(categorical_features)


# ------------------------------------------------------------
# 7. PREPROCESSING
# ------------------------------------------------------------

numeric_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
)

categorical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False,
            ),
        ),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", numeric_pipeline, numeric_features),
        ("categorical", categorical_pipeline, categorical_features),
    ],
    remainder="drop",
)


# ------------------------------------------------------------
# 8. MODELS
# ------------------------------------------------------------

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42,
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    ),

    "XGBoost": XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1,
),
}


# ------------------------------------------------------------
# 9. TRAIN + EVALUATE
# ------------------------------------------------------------

results = []

for name, model in models.items():

    print("\n" + "=" * 60)
    print(f"TRAINING: {name}")
    print("=" * 60)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

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

    cm = confusion_matrix(
        y_test,
        predictions,
    )

    print(f"\nAccuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    print("\nConfusion Matrix:")
    print(cm)

    results.append(
        {
            "model": name,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    )

    # Save each trained pipeline
    filename = name.lower().replace(" ", "_") + ".joblib"

    output_path = os.path.join(
        MODEL_DIR,
        filename,
    )

    joblib.dump(
        pipeline,
        output_path,
    )

    print(f"\nSaved model: {output_path}")


# ------------------------------------------------------------
# 10. MODEL COMPARISON
# ------------------------------------------------------------

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="f1",
    ascending=False,
)

print("\n")
print("=" * 60)
print("MODEL COMPARISON")
print("=" * 60)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}",
    )
)


# ------------------------------------------------------------
# 11. SAVE RESULTS
# ------------------------------------------------------------

results_path = "ml/models/baseline_results.csv"

results_df.to_csv(
    results_path,
    index=False,
)

print(f"\nResults saved to: {results_path}")

best_model = results_df.iloc[0]["model"]

print("\n" + "=" * 60)
print(f"BEST BASELINE MODEL: {best_model}")
print("=" * 60)

print("\nDay 4 baseline training complete.")