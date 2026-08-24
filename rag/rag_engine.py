import os
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# RAZORSHIELD AI - DAY 7
# RAG POLICY RETRIEVAL ENGINE
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

POLICY_FILE = os.path.join(
    BASE_DIR,
    "chargeback_policies.txt"
)


# ------------------------------------------------------------
# 1. LOAD POLICY DOCUMENT
# ------------------------------------------------------------

def load_policies():

    if not os.path.exists(POLICY_FILE):
        raise FileNotFoundError(
            f"Policy file not found: {POLICY_FILE}"
        )

    with open(
        POLICY_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    return text


# ------------------------------------------------------------
# 2. SPLIT DOCUMENT INTO POLICY CHUNKS
# ------------------------------------------------------------

def split_into_chunks(text):

    chunks = re.split(
        r"\n(?=POLICY \d+:)",
        text.strip()
    )

    chunks = [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]

    return chunks


# ------------------------------------------------------------
# 3. CREATE TF-IDF KNOWLEDGE BASE
# ------------------------------------------------------------

policy_text = load_policies()

policy_chunks = split_into_chunks(policy_text)

vectorizer = TfidfVectorizer(
    stop_words="english"
)

policy_vectors = vectorizer.fit_transform(
    policy_chunks
)


# ------------------------------------------------------------
# 4. RETRIEVE RELEVANT POLICIES
# ------------------------------------------------------------

def retrieve_policies(
    query,
    top_k=3
):

    query_vector = vectorizer.transform(
        [query]
    )

    similarities = cosine_similarity(
        query_vector,
        policy_vectors
    )[0]

    ranked_indices = similarities.argsort()[::-1]

    results = []

    for index in ranked_indices[:top_k]:

        results.append(
            {
                "policy": policy_chunks[index],
                "score": round(
                    float(similarities[index]),
                    4
                ),
            }
        )

    return results


# ------------------------------------------------------------
# 5. TEST RAG ENGINE
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("RAZORSHIELD AI - RAG POLICY RETRIEVAL")
    print("=" * 60)

    query = (
        "Customer claims unauthorized transaction "
        "but payment authentication was successful"
    )

    print("\nQuery:")
    print(query)

    print("\nRetrieved Policies:")

    results = retrieve_policies(
        query,
        top_k=3
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        print("\n" + "-" * 60)
        print(f"RESULT {i}")
        print(f"Similarity Score: {result['score']}")
        print("-" * 60)

        print(result["policy"])

    print("\n" + "=" * 60)
    print("RAG RETRIEVAL TEST COMPLETE")
    print("=" * 60)