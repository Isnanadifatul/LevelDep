import numpy as np
import mysql.connector
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from app.preprocess import clean_and_stem

# === Load model & tokenizer sekali di awal ===
MODEL_PATH = "model/bilstm_model.keras"
TOKENIZER_PATH = "model/tokenizer.pkl"
MAXLEN = 50

model = load_model(MODEL_PATH)
with open(TOKENIZER_PATH, "rb") as f:
    tokenizer = pickle.load(f)

# === Helper: convert numpy types to Python native ===
def to_native(val):
    if isinstance(val, (np.generic,)):
        return val.item()
    return val

# === Predict single text ===
def predict_text(text: str):
    # pastikan text string, kalau list/ndarray digabung
    if isinstance(text, (list, np.ndarray)):
        text = " ".join(map(str, text))
    text = clean_and_stem(str(text))

    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=MAXLEN, padding="post")
    prob = model.predict(padded, verbose=0)[0]
    label = int(np.argmax(prob))
    confidence = float(np.max(prob))
    return label, confidence

# === Simpan user hanya sekali ===
def save_user(db, nama: str, perguruan_tinggi: str):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO user (nama, perguruan_tinggi) VALUES (%s, %s)",
        (str(nama), str(perguruan_tinggi)),
    )
    db.commit()
    return cursor.lastrowid  # return id_user

# === Simpan jawaban per pertanyaan ===
def save_prediction(db, id_user: int, id_pertanyaan: int, jawaban: str, label: int, confidence: float):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO prediksi (id_user, id_pertanyaan, jawaban, label, confidence) VALUES (%s, %s, %s, %s, %s)",
        tuple(to_native(x) for x in (id_user, id_pertanyaan, jawaban, label, confidence)),
    )
    db.commit()

def save_total_score(db, id_user: int, total_score: int):
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO score (id_user, score)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE score = VALUES(score)
        """,
        (to_native(id_user), int(total_score)),
    )
    db.commit()
    cursor.close()

# === Hitung total skor depresi dari label semua jawaban user ===
def calculate_total_score(db, id_user: int):
    cursor = db.cursor()
    cursor.execute("SELECT SUM(label) FROM prediksi WHERE id_user = %s", (to_native(id_user),))
    total_score = cursor.fetchone()[0] or 0
    return int(total_score)

# === Tentukan kategori depresi rule-based (PHQ-9) ===
def get_depression_category(score: int):
    if score <= 4:
        return f"Kategori: Tidak ada gejala depresi\n" 
    elif 5 <= score <= 9:
        return f"Kategori: Gejala depresi ringan\n" f"Solusi: Dianjurkan terapi psikoedukasi bila ada perburukan gejala\n"
    elif 10 <= score <= 14:
        return f"Kategori: Depresi ringan\n" f"Solusi: Dianjurkan terapi observasi gejala yang ada dalam satu bulan (perbaikan atau perburukan) dan pertimbangan pemberian antidepresan atau psikoterapi singkat\n"
    elif 15 <= score <= 19:
        return f"Kategori: Depresi sedang\n" f"Solusi: Dianjurkan untuk memberikan antidepresan atau psikoterapi\n"
    else:
        return f"Kategori: Depresi berat\n" f"Solusi: Dianjurkan untuk memberikan antidepresan secara tunggal atau kombinasikan dengan psikoterapi intensif\n"

# === Proses bulk: simpan 9 jawaban, prediksi semua, hitung skor ===
def process_bulk_answers(db, id_user: int, jawaban: list):
    """
    answers: list of 9 strings (jawaban pengguna)
    """
    for idx, ans in enumerate(jawaban, start=1):  # id_pertanyaan = 1-9
        label, confidence = predict_text(ans)
        save_prediction(db, id_user, idx, ans, label, confidence)

    total_score = calculate_total_score(db, id_user)
    save_total_score(db, id_user, total_score)  
    category = get_depression_category(total_score)
    return {"total_score": total_score, "kategori": category}
