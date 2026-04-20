import pandas as pd
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "updated_data.csv")

def load_schemes():
    try:
        df = pd.read_csv(DATA_PATH)
        df.fillna("", inplace=True)
        return df
    except Exception as e:
        print("Error loading schemes:", e)
        return pd.DataFrame()


def search_relevant_schemes(df, query, top_k=5):
    """
    Simple keyword-based retrieval.
    Later this can be upgraded to embeddings.
    """
    query = str(query).lower()

    scores = []
    for _, row in df.iterrows():
        text = (
            str(row.get("scheme_name", "")) + " " +
            str(row.get("schemeCategory", "")) + " " +
            str(row.get("details", "")) + " " +
            str(row.get("eligibility", ""))
        ).lower()

        score = sum(word in text for word in query.split())
        scores.append(score)

    df["score"] = scores
    results = df.sort_values("score", ascending=False).head(top_k)

    return results


def build_context_from_results(results_df):
    """
    Build AI context from relevant schemes only.
    """
    context = ""

    for _, row in results_df.iterrows():
        name = row.get("scheme_name", "")
        category = row.get("schemeCategory", "")
        state = row.get("state", "")
        details = row.get("details", "")[:200]

        context += (
            f"Scheme: {name}\n"
            f"Category: {category}\n"
            f"State: {state}\n"
            f"Details: {details}\n\n"
        )

    return context
