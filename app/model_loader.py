from tensorflow.keras.models import load_model
import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load model BiLSTM sekali saja
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "bilstm_model.keras")
model = load_model(MODEL_PATH)

# Load tokenizer sekali saja
TOKENIZER_PATH = os.path.join(BASE_DIR, "..", "model", "tokenizer.pkl")
with open(TOKENIZER_PATH, "rb") as handle:
    tokenizer = pickle.load(handle)

MAXLEN = 50  # samakan dengan saat training

__all__ = ["model", "tokenizer", "MAXLEN"]
