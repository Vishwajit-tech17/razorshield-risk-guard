import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ============================================================
# Configuration
# ============================================================

SEED = 42
NUM_CUSTOMERS = 2000
NUM_TRANSACTIONS = 5000

random.seed(SEED)
np.random.seed(SEED)


# ============================================================
# Paths
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")

os.makedirs(RAW_DIR, exist_ok=True)


# ============================================================
# Helper functions
# ============================================================

def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


# ============================================================
# 1. CUSTOMERS
# ============================================================

customers = []

for i in range(1, NUM_CUSTOMERS + 1):

    customer_id = f"CUST_{i:05d}"

    account_age_days = random.randint(30, 2000)

    previous_transactions = random.randint(1, 50)

    successful_transactions = random.randint(
        max(0, previous_transactions - 10),
        previous_transactions
    )

    previous_chargebacks = np.random.poisson(0.4)
    previous_refunds = np.random.poisson(1.5)

    known_devices = random.randint(1, 4)

    average_order_value = round(
        np.random.lognormal(mean=8.0, sigma=0.7),
        2
    )

    customers.append({
        "customer_id": customer_id,
        "account_age_days": account_age_days,
        "previous_transactions": previous_transactions,
        "successful_transactions": successful_transactions,
        "previous_chargebacks": previous_chargebacks,
        "previous_refunds": previous_refunds,
        "known_devices": known_devices,
        "average_order_value": average_order_value
    })


customers_df = pd.DataFrame(customers)


# ============================================================
# 2. TRANSACTIONS
# ============================================================

transactions = []

start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 8, 15)

payment_methods = ["card", "upi", "netbanking", "wallet"]

countries = ["IN", "US", "GB", "AE", "SG"]

authentication_statuses = [
    "success",
    "success",
    "success",
    "failed"
]

for i in range(1, NUM_TRANSACTIONS + 1):

    customer = customers_df.sample(1).iloc[0]

    transaction_id = f"TXN_{i:06d}"

    customer_id = customer["customer_id"]

    amount = round(
        np.random.lognormal(mean=8.2, sigma=0.8),
        2
    )

    payment_method = random.choice(payment_methods)

    device_id = f"DEV_{random.randint(1, 3000):05d}"

    ip_country = random.choice(countries)

    transaction_time = random_date(start_date, end_date)

    authentication_status = random.choice(
        authentication_statuses
    )

    previous_transactions = int(
        customer["previous_transactions"]
    )

    transactions.append({
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "amount": amount,
        "payment_method": payment_method,
        "device_id": device_id,
        "ip_country": ip_country,
        "transaction_time": transaction_time,
        "authentication_status": authentication_status,
        "previous_transactions": previous_transactions
    })


transactions_df = pd.DataFrame(transactions)


# ============================================================
# 3. ORDERS
# ============================================================

orders = []

product_categories = [
    "electronics",
    "fashion",
    "grocery",
    "home",
    "beauty",
    "software",
    "travel"
]

delivery_statuses = [
    "delivered",
    "delivered",
    "delivered",
    "pending",
    "failed"
]

refund_statuses = [
    "none",
    "none",
    "none",
    "requested",
    "processed"
]

for _, transaction in transactions_df.iterrows():

    transaction_id = transaction["transaction_id"]

    order_id = f"ORD_{transaction_id.replace('TXN_', '')}"

    product_category = random.choice(product_categories)

    product_value = transaction["amount"]

    shipping_address = (
        f"Address_{random.randint(1000, 9999)}, "
        f"India"
    )

    delivery_status = random.choice(delivery_statuses)

    transaction_time = transaction["transaction_time"]

    delivery_date = transaction_time + timedelta(
        days=random.randint(1, 7)
    )

    refund_status = random.choice(refund_statuses)

    orders.append({
        "order_id": order_id,
        "transaction_id": transaction_id,
        "product_category": product_category,
        "product_value": product_value,
        "shipping_address": shipping_address,
        "delivery_status": delivery_status,
        "delivery_date": delivery_date,
        "refund_status": refund_status
    })


orders_df = pd.DataFrame(orders)


# ============================================================
# 4. CHARGEBACKS
# ============================================================

chargebacks = []

reason_codes = [
    "fraudulent",
    "product_not_received",
    "product_not_as_described",
    "duplicate_transaction",
    "credit_not_processed"
]

customer_reasons = [
    "Customer does not recognize transaction",
    "Customer claims product was not received",
    "Customer claims product was different from description",
    "Customer claims duplicate charge",
    "Customer claims refund was not received"
]

chargeback_statuses = [
    "open",
    "under_review",
    "won",
    "lost"
]

# Approximately 12% of transactions receive a chargeback
chargeback_probability = 0.12

for _, transaction in transactions_df.iterrows():

    if random.random() < chargeback_probability:

        transaction_id = transaction["transaction_id"]

        chargeback_id = (
            f"CB_{len(chargebacks) + 1:06d}"
        )

        reason_index = random.randint(
            0,
            len(reason_codes) - 1
        )

        claimed_amount = transaction["amount"]

        claim_date = transaction["transaction_time"] + timedelta(
            days=random.randint(5, 45)
        )

        chargebacks.append({
            "chargeback_id": chargeback_id,
            "transaction_id": transaction_id,
            "reason_code": reason_codes[reason_index],
            "claimed_amount": claimed_amount,
            "claim_date": claim_date,
            "customer_reason": customer_reasons[reason_index],
            "status": random.choice(chargeback_statuses)
        })


chargebacks_df = pd.DataFrame(chargebacks)


# ============================================================
# 5. EVIDENCE
# ============================================================

evidence = []

evidence_counter = 1

for _, transaction in transactions_df.iterrows():

    transaction_id = transaction["transaction_id"]

    # Payment authentication evidence
    evidence.append({
        "evidence_id": f"EV_{evidence_counter:06d}",
        "transaction_id": transaction_id,
        "evidence_type": "payment_authentication",
        "content": (
            f"Payment authentication status was "
            f"{transaction['authentication_status']}."
        )
    })

    evidence_counter += 1

    # Delivery evidence
    order = orders_df[
        orders_df["transaction_id"] == transaction_id
    ].iloc[0]

    evidence.append({
        "evidence_id": f"EV_{evidence_counter:06d}",
        "transaction_id": transaction_id,
        "evidence_type": "delivery_confirmation",
        "content": (
            f"Order delivery status: "
            f"{order['delivery_status']}. "
            f"Delivery date: "
            f"{order['delivery_date'].date()}."
        )
    })

    evidence_counter += 1

    # Refund evidence
    evidence.append({
        "evidence_id": f"EV_{evidence_counter:06d}",
        "transaction_id": transaction_id,
        "evidence_type": "refund_record",
        "content": (
            f"Refund status: "
            f"{order['refund_status']}."
        )
    })

    evidence_counter += 1


evidence_df = pd.DataFrame(evidence)


# ============================================================
# Save datasets
# ============================================================

customers_df.to_csv(
    os.path.join(RAW_DIR, "customers.csv"),
    index=False
)

transactions_df.to_csv(
    os.path.join(RAW_DIR, "transactions.csv"),
    index=False
)

orders_df.to_csv(
    os.path.join(RAW_DIR, "orders.csv"),
    index=False
)

chargebacks_df.to_csv(
    os.path.join(RAW_DIR, "chargebacks.csv"),
    index=False
)

evidence_df.to_csv(
    os.path.join(RAW_DIR, "evidence.csv"),
    index=False
)


# ============================================================
# Summary
# ============================================================

print("=" * 60)
print("RazorShield AI - Synthetic Dataset Generated")
print("=" * 60)

print(f"Customers:    {len(customers_df)}")
print(f"Transactions: {len(transactions_df)}")
print(f"Orders:       {len(orders_df)}")
print(f"Chargebacks:  {len(chargebacks_df)}")
print(f"Evidence:     {len(evidence_df)}")

print()
print("Files saved to:")
print(RAW_DIR)

print("=" * 60)