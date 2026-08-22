import pandas as pd
import numpy as np
import os

# ============================================================
# RazorShield AI - Day 3
# Feature Engineering
# ============================================================

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)

print("=" * 60)
print("RazorShield AI - Feature Engineering")
print("=" * 60)

# ------------------------------------------------------------
# 1. Load datasets
# ------------------------------------------------------------

transactions = pd.read_csv(
    os.path.join(RAW_DIR, "transactions.csv")
)

customers = pd.read_csv(
    os.path.join(RAW_DIR, "customers.csv")
)

orders = pd.read_csv(
    os.path.join(RAW_DIR, "orders.csv")
)

chargebacks = pd.read_csv(
    os.path.join(RAW_DIR, "chargebacks.csv")
)

print("\nRaw datasets loaded:")
print(f"Transactions : {len(transactions)}")
print(f"Customers    : {len(customers)}")
print(f"Orders       : {len(orders)}")
print(f"Chargebacks  : {len(chargebacks)}")


# ------------------------------------------------------------
# 2. Create target variable
# ------------------------------------------------------------
# Target:
# 1 = transaction eventually resulted in a chargeback
# 0 = transaction did not result in a chargeback
#
# This is our ML prediction target.
# ------------------------------------------------------------

chargeback_transactions = set(
    chargebacks["transaction_id"].astype(str)
)

transactions["chargeback_label"] = (
    transactions["transaction_id"]
    .astype(str)
    .isin(chargeback_transactions)
    .astype(int)
)

print("\nTarget distribution:")
print(
    transactions["chargeback_label"]
    .value_counts()
    .sort_index()
)

print(
    "\nChargeback rate: "
    f"{transactions['chargeback_label'].mean() * 100:.2f}%"
)


# ------------------------------------------------------------
# 3. Merge customer information
# ------------------------------------------------------------

customer_features = customers[
    [
        "customer_id",
        "account_age_days",
        "previous_transactions",
        "successful_transactions",
        "previous_chargebacks",
        "previous_refunds",
        "known_devices",
        "average_order_value"
    ]
].copy()

# transactions.csv already contains previous_transactions.
# Remove it before merging customer data to avoid duplicate columns.

transactions = transactions.drop(
    columns=["previous_transactions"],
    errors="ignore"
)

df = transactions.merge(
    customer_features,
    on="customer_id",
    how="left"
)

print("\nAfter customer merge:", df.shape)


# ------------------------------------------------------------
# 4. Merge order information
# ------------------------------------------------------------

order_features = orders[
    [
        "transaction_id",
        "product_category",
        "product_value"
    ]
].copy()

df = df.merge(
    order_features,
    on="transaction_id",
    how="left"
)

print("After order merge:", df.shape)


# ------------------------------------------------------------
# 5. Convert transaction time
# ------------------------------------------------------------

df["transaction_time"] = pd.to_datetime(
    df["transaction_time"],
    errors="coerce"
)

df["transaction_hour"] = (
    df["transaction_time"].dt.hour
)

df["transaction_day_of_week"] = (
    df["transaction_time"].dt.dayofweek
)

df["is_weekend"] = (
    df["transaction_day_of_week"] >= 5
).astype(int)


# ------------------------------------------------------------
# 6. Numerical feature engineering
# ------------------------------------------------------------

# Difference between transaction amount and customer's
# historical average order value.

df["amount_to_avg_order_ratio"] = (
    df["amount"] /
    df["average_order_value"].replace(0, np.nan)
)

df["amount_to_avg_order_ratio"] = (
    df["amount_to_avg_order_ratio"]
    .replace([np.inf, -np.inf], np.nan)
    .fillna(0)
)

# Historical customer success rate

df["customer_success_rate"] = (
    df["successful_transactions"] /
    df["previous_transactions"].replace(0, np.nan)
)

df["customer_success_rate"] = (
    df["customer_success_rate"]
    .replace([np.inf, -np.inf], np.nan)
    .fillna(0)
)

# Historical chargeback rate

df["customer_chargeback_rate"] = (
    df["previous_chargebacks"] /
    df["previous_transactions"].replace(0, np.nan)
)

df["customer_chargeback_rate"] = (
    df["customer_chargeback_rate"]
    .replace([np.inf, -np.inf], np.nan)
    .fillna(0)
)

# Historical refund rate

df["customer_refund_rate"] = (
    df["previous_refunds"] /
    df["previous_transactions"].replace(0, np.nan)
)

df["customer_refund_rate"] = (
    df["customer_refund_rate"]
    .replace([np.inf, -np.inf], np.nan)
    .fillna(0)
)

# Whether customer has previous chargeback history

df["has_previous_chargeback"] = (
    df["previous_chargebacks"] > 0
).astype(int)

# Whether customer is relatively new

df["is_new_customer"] = (
    df["account_age_days"] < 30
).astype(int)


# ------------------------------------------------------------
# 7. Select ML features
# ------------------------------------------------------------

feature_columns = [
    # Transaction
    "amount",
    "payment_method",
    "device_id",
    "ip_country",
    "authentication_status",

    # Customer
    "account_age_days",
    "previous_transactions",
    "successful_transactions",
    "previous_chargebacks",
    "previous_refunds",
    "known_devices",
    "average_order_value",

    # Order
    "product_category",
    "product_value",

    # Engineered features
    "transaction_hour",
    "transaction_day_of_week",
    "is_weekend",
    "amount_to_avg_order_ratio",
    "customer_success_rate",
    "customer_chargeback_rate",
    "customer_refund_rate",
    "has_previous_chargeback",
    "is_new_customer",

    # Target
    "chargeback_label"
]

model_df = df[
    feature_columns
].copy()


# ------------------------------------------------------------
# 8. Basic data cleaning
# ------------------------------------------------------------

# Replace infinite values

model_df = model_df.replace(
    [np.inf, -np.inf],
    np.nan
)

# Fill numerical missing values

numeric_columns = model_df.select_dtypes(
    include=["int64", "float64"]
).columns

for column in numeric_columns:
    if column != "chargeback_label":
        model_df[column] = model_df[column].fillna(
            model_df[column].median()
        )

# Fill categorical missing values

categorical_columns = model_df.select_dtypes(
    include=["object"]
).columns

for column in categorical_columns:
    model_df[column] = model_df[column].fillna(
        "unknown"
    )


# ------------------------------------------------------------
# 9. Save processed dataset
# ------------------------------------------------------------

output_path = os.path.join(
    PROCESSED_DIR,
    "model_data.csv"
)

model_df.to_csv(
    output_path,
    index=False
)


# ------------------------------------------------------------
# 10. Print summary
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("FEATURE ENGINEERING COMPLETE")
print("=" * 60)

print(f"\nFinal dataset shape: {model_df.shape}")

print("\nFinal columns:")

for column in model_df.columns:
    print(" -", column)

print("\nTarget distribution:")
print(
    model_df["chargeback_label"]
    .value_counts()
)

print("\nMissing values:")
print(
    model_df.isnull().sum().sum()
)

print(f"\nSaved to:")
print(output_path)

print("=" * 60)