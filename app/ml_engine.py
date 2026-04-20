import numpy as np
import re
import pickle
import os

# ==========================================
# 1. SETUP & PATH CONFIGURATION
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'models')
TOKENIZER_PATH = os.path.join(MODELS_DIR, 'tokenizer.pickle')
LABEL_ENCODER_PATH = os.path.join(MODELS_DIR, 'label_encoder.pickle')

# Global artifacts
tokenizer = None
label_encoder = None
MAX_LEN = 250

# ==========================================
# 2. KEYWORD-BASED CATEGORY MAPPING
# (Lightweight replacement for LSTM model —
#  avoids keras/jax which OOM-kill free tier)
# ==========================================

CATEGORY_KEYWORDS = {
    "Education": [
        "student", "school", "college", "scholarship", "study", "education",
        "learning", "university", "degree", "course", "tuition", "children studying"
    ],
    "Agriculture": [
        "farmer", "agriculture", "farming", "crop", "land", "kisan", "seed",
        "fertilizer", "irrigation", "livestock", "cattle", "animal husbandry",
        "acres", "farm"
    ],
    "Health": [
        "health", "hospital", "illness", "disease", "medical", "ayushman",
        "insurance", "treatment", "doctor", "disability", "chronic", "sick"
    ],
    "Housing": [
        "housing", "house", "home", "shelter", "kutcha", "rented", "awas",
        "construction", "pucca", "accommodation"
    ],
    "Pension": [
        "pension", "widow", "old age", "senior citizen", "retirement",
        "elderly", "above 60", "widowed"
    ],
    "Employment": [
        "employment", "job", "work", "unemployed", "job loss", "skill",
        "training", "vocational", "self employed", "business", "startup",
        "mudra", "msme", "entrepreneur"
    ],
    "Social Welfare": [
        "bpl", "below poverty", "sc", "st", "obc", "minority", "dalit",
        "tribal", "general welfare", "social support", "ration", "food"
    ],
    "Women Welfare": [
        "women", "female", "girl", "mahila", "single parent", "maternity",
        "widow", "self help group", "shg", "beti"
    ],
    "Disability": [
        "disability", "disabled", "handicap", "divyang", "differently abled"
    ],
    "Financial Inclusion": [
        "bank", "loan", "credit", "insurance", "mudra", "pm jan dhan",
        "microfinance", "subsidy", "financial"
    ],
}

def clean_text(text):
    """Standardizes input text."""
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def predict_category(user_text):
    """
    Predicts relevant scheme categories using keyword matching.
    Lightweight replacement for LSTM — no ML framework needed.

    Args:
        user_text (str): Combined context string from the wizard.

    Returns:
        list: List of predicted category strings.
    """
    default_categories = ["General Welfare", "Social Support"]

    if not user_text:
        return default_categories

    cleaned = clean_text(user_text)
    matched = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in cleaned)
        if score > 0:
            matched.append((category, score))

    if not matched:
        return default_categories

    # Sort by match score descending, return top categories
    matched.sort(key=lambda x: x[1], reverse=True)
    return [cat for cat, _ in matched[:5]]  # Return top 5 matches