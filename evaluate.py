import pandas as pd
import numpy as np
import os
import pickle
os.environ.setdefault("KERAS_BACKEND", "jax")
import keras
from keras.preprocessing.sequence import pad_sequences
from sklearn.metrics import classification_report, accuracy_score, hamming_loss, f1_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'praja_guide_model.h5')
TOK_PATH = os.path.join(BASE_DIR, 'models', 'tokenizer.pickle')
LBL_PATH = os.path.join(BASE_DIR, 'models', 'label_encoder.pickle')
DATA_PATH = os.path.join(BASE_DIR, 'data', 'updated_data.csv')

print("--- Loading Model and Data ---")
model = keras.models.load_model(MODEL_PATH)
with open(TOK_PATH, 'rb') as h:
    tokenizer = pickle.load(h)
with open(LBL_PATH, 'rb') as h:
    label_encoder = pickle.load(h)

df = pd.read_csv(DATA_PATH)

MAX_LEN = 250

def clean_text(text):
    text = str(text).lower()
    text = "".join([c for c in text if c.isalnum() or c.isspace()])
    return text

texts = df['details'].apply(clean_text)
sequences = tokenizer.texts_to_sequences(texts)
X_test = pad_sequences(sequences, maxlen=MAX_LEN, padding='post')

y_true_labels = df['schemeCategory'].apply(lambda x: [cat.strip() for cat in str(x).split(',')] if pd.notnull(x) else [])
y_true = label_encoder.transform(y_true_labels)

print("--- Running Predictions ---")
y_pred_probs = model.predict(X_test)
threshold = 0.3 # Matching your ml_engine.py threshold
y_pred = (y_pred_probs > threshold).astype(int)

print("\n" + "="*30)
print("   MODEL PERFORMANCE REPORT")
print("="*30)

sub_acc = accuracy_score(y_true, y_pred)
print(f"Subset Accuracy: {sub_acc:.4f} (Strict Match)")

h_loss = hamming_loss(y_true, y_pred)
print(f"Hamming Loss:    {h_loss:.4f} (Error Rate)")

f1_macro = f1_score(y_true, y_pred, average='macro')
print(f"Macro F1-Score:  {f1_macro:.4f} (Overall Balance)")

print("\n--- Detailed Category Breakdown ---")
print(classification_report(y_true, y_pred, target_names=label_encoder.classes_))