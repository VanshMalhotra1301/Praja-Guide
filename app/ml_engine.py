import numpy as np
import re
import pickle
import os
os.environ.setdefault("KERAS_BACKEND", "jax")
import keras
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences

# ==========================================
# 1. SETUP & PATH CONFIGURATION
# ==========================================

# Get the directory where this file (ml_engine.py) is located (e.g., .../praja_guide/app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Go up one level to project root, then into 'models' (e.g., .../praja_guide/models)
MODELS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'models')

# Define specific paths
MODEL_PATH = os.path.join(MODELS_DIR, 'praja_guide_model.h5')
TOKENIZER_PATH = os.path.join(MODELS_DIR, 'tokenizer.pickle')
LABEL_ENCODER_PATH = os.path.join(MODELS_DIR, 'label_encoder.pickle')

# Global artifacts
model = None
tokenizer = None
label_encoder = None
MAX_LEN = 250  # Must match the length used during training

# ==========================================
# 2. ARTIFACT LOADING
# ==========================================

def load_ml_artifacts():
    """
    Loads the Keras model, Tokenizer, and Label Encoder from disk.
    Handles missing files gracefully to prevent app crashes.
    """
    global model, tokenizer, label_encoder
    
    print(f"ML Engine: Looking for ML artifacts in: {MODELS_DIR}")

    try:
        # Check if files exist
        if not (os.path.exists(MODEL_PATH) and os.path.exists(TOKENIZER_PATH) and os.path.exists(LABEL_ENCODER_PATH)):
            print(f"WARNING: One or more model files missing. ML Engine will run in FALLBACK mode.")
            return

        # Load Tokenizer
        with open(TOKENIZER_PATH, 'rb') as handle:
            tokenizer = pickle.load(handle)

        # Load Label Encoder
        with open(LABEL_ENCODER_PATH, 'rb') as handle:
            label_encoder = pickle.load(handle)

        # Load Keras Model
        model = load_model(MODEL_PATH)
        
        print("ML Engine: Model & Artifacts Loaded Successfully.")

    except Exception as e:
        print(f"ML Engine Error: Failed to load artifacts. {e}")
        # Reset to None to ensure safety checks fail gracefully later
        model = None
        tokenizer = None
        label_encoder = None

# Initialize loading on module import
load_ml_artifacts()

# ==========================================
# 3. PREPROCESSING & PREDICTION LOGIC
# ==========================================

def clean_text(text):
    """
    Standardizes input text: lowercase, remove special chars, normalize spaces.
    """
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)  # Keep only alphanumeric and spaces
    text = re.sub(r'\s+', ' ', text).strip() # Collapse multiple spaces
    return text

def predict_category(user_text):
    """
    Analyzes the user profile text and predicts relevant scheme categories.
    
    Args:
        user_text (str): The combined context string from the wizard (Age + Occ + Needs...).
        
    Returns:
        list: A list of predicted category strings (e.g., ['Education', 'Social Welfare']).
    """
    # Default fallback if ML fails or isn't loaded
    default_categories = ["General Welfare", "Social Support"]

    # 1. Safety Check
    if model is None or tokenizer is None or label_encoder is None:
        return default_categories

    try:
        # 2. Preprocess
        cleaned_text = clean_text(user_text)
        if not cleaned_text:
            return default_categories

        # 3. Tokenize & Pad
        seq = tokenizer.texts_to_sequences([cleaned_text])
        padded = pad_sequences(seq, maxlen=MAX_LEN, padding='post', truncating='post')

        # 4. Model Inference
        # Returns a probability array (e.g., [[0.1, 0.8, 0.05...]])
        prediction_probs = model.predict(padded, verbose=0)[0]

        # 5. Thresholding & Decoding
        # We use a threshold to capture multiple relevant categories (Multi-label approach)
        threshold = 0.20  # Adjustable: Lower = more suggestions, Higher = stricter
        
        results = []
        for index, probability in enumerate(prediction_probs):
            if probability > threshold:
                # Map index back to class name
                category_name = label_encoder.classes_[index]
                results.append((category_name, probability))

        # 6. Sort by Confidence
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Extract just the names
        final_categories = [cat for cat, prob in results]

        # Debugging Output (Optional)
        # print(f"🔍 Input: {cleaned_text[:50]}...")
        # print(f"🤖 Prediction: {final_categories}")

        # Always return at least the top result or defaults if nothing crossed threshold
        if not final_categories:
            # Fallback: take the single highest probability class regardless of threshold
            top_index = np.argmax(prediction_probs)
            return [label_encoder.classes_[top_index]]

        return final_categories

    except Exception as e:
        print(f"Prediction Runtime Error: {e}")
        return default_categories