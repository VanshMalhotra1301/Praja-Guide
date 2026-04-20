import pandas as pd
import numpy as np
import re
import pickle
import tensorflow as tf
import os  
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Bidirectional, Dropout, GlobalMaxPool1D
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'updated_data.csv')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')

os.makedirs(MODELS_DIR, exist_ok=True)

print(f"Script Location: {BASE_DIR}")
print(f"Looking for data at: {DATA_PATH}")
print(f"Models will be saved to: {MODELS_DIR}")

MAX_WORDS = 20000      
MAX_LEN = 250          
EMBEDDING_DIM = 100    
LSTM_UNITS = 128       
BATCH_SIZE = 32        
EPOCHS = 10            
TEST_SIZE = 0.2        
RANDOM_STATE = 42

print("Loading data...")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"CRITICAL ERROR: Could not find 'updated_data.csv' at {DATA_PATH}. \nPlease make sure you created a 'data' folder and put the CSV file inside it.")

df = pd.read_csv(DATA_PATH)

# Combine relevant text columns
df['text_combined'] = df['scheme_name'].fillna('') + " " + \
                      df['details'].fillna('') + " " + \
                      df['benefits'].fillna('') + " " + \
                      df['eligibility'].fillna('')

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

print("Cleaning text...")
df['clean_text'] = df['text_combined'].apply(clean_text)

print("Processing labels...")
# Convert "Agri, Social" -> ['Agri', 'Social']
df['categories'] = df['schemeCategory'].fillna('').apply(lambda x: [i.strip() for i in x.split(',')])

mlb = MultiLabelBinarizer()
y = mlb.fit_transform(df['categories'])
classes = mlb.classes_
print(f"Total Categories: {len(classes)}")

# ==========================================
# 3. Tokenization
# ==========================================
print("Tokenizing text...")
tokenizer = Tokenizer(num_words=MAX_WORDS, oov_token="<OOV>")
tokenizer.fit_on_texts(df['clean_text'])

sequences = tokenizer.texts_to_sequences(df['clean_text'])
X = pad_sequences(sequences, maxlen=MAX_LEN, padding='post', truncating='post')

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE)

# ==========================================
# 4. Model Architecture
# ==========================================
print("Building model...")
model = Sequential()
model.add(Embedding(input_dim=MAX_WORDS, output_dim=EMBEDDING_DIM, input_length=MAX_LEN))
model.add(Bidirectional(LSTM(LSTM_UNITS, return_sequences=True)))
model.add(GlobalMaxPool1D())
model.add(Dropout(0.3))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.3))
model.add(Dense(len(classes), activation='sigmoid'))

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


print("Starting training...")
history = model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE, validation_data=(X_test, y_test), verbose=1)


print("Saving model and tools...")

model_save_path = os.path.join(MODELS_DIR, 'praja_guide_model.h5')
model.save(model_save_path)


tokenizer_path = os.path.join(MODELS_DIR, 'tokenizer.pickle')
with open(tokenizer_path, 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Save Label Encoder
label_path = os.path.join(MODELS_DIR, 'label_encoder.pickle')
with open(label_path, 'wb') as handle:
    pickle.dump(mlb, handle, protocol=pickle.HIGHEST_PROTOCOL)

print(f"SUCCESS! Files saved in: {MODELS_DIR}")
print(f"1. {model_save_path}")
print(f"2. {tokenizer_path}")
print(f"3. {label_path}")