from fastapi import FastAPI
from pydantic import BaseModel
from app.database import db
from app.schema import UserInput, AnswerInput, BulkAnswerInput
from app.predict import (
    save_user,
    save_prediction,
    predict_text,
    calculate_total_score,
    process_bulk_answers,
)

app = FastAPI()


@app.post("/user/create")
def create_user(data: UserInput):
    """Simpan data user sekali di awal (kembalikan id_user)."""
    id_user = save_user(db, data.nama, data.perguruan_tinggi)
    return {"id_user": id_user, "message": "User berhasil dibuat"}

@app.post("/predict/single")
def save_answer(data: AnswerInput):
    """
    Prediksi 1 jawaban (untuk tiap pertanyaan).
    Tidak membuat user baru, hanya simpan prediksi.
    """
    label, confidence = predict_text(data.jawaban)
    save_prediction(db, data.id_user, data.id_pertanyaan, data.jawaban, label, confidence)
    return {
        "id_user": data.id_user,
        "id_pertanyaan": data.id_pertanyaan,
        "label": label,
        "confidence": confidence
    }

@app.post("/predict/bulk")
def save_bulk(data: BulkAnswerInput):
    """
    Prediksi & simpan semua 9 jawaban sekaligus.
    Hitung skor total & kategori depresi.
    """
    if len(data.jawaban) != 9:
        return {"error": "Harus ada tepat 9 jawaban"}
    
    result = process_bulk_answers(db, data.id_user, data.jawaban)
    return {
        "id_user": data.id_user,
        "total_score": result["total_score"],
        "kategori": result["kategori"]
    }
