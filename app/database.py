import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",          # ganti sesuai konfigurasi
    database="db_halodepresi"
)
cursor = db.cursor()

def get_or_create_user(nama, perguruan_tinggi):
    cursor.execute("SELECT id_user FROM user WHERE nama=%s AND perguruan_tinggi=%s", (nama, perguruan_tinggi))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO user (nama, perguruan_tinggi) VALUES (%s, %s)", (nama, perguruan_tinggi))
    db.commit()
    return cursor.lastrowid

def save_user_once(nama, perguruan_tinggi):
    # Simpan user hanya sekali
    cursor = db.cursor()
    cursor.execute("INSERT INTO user (nama, perguruan_tinggi) VALUES (%s, %s)", (nama, perguruan_tinggi))
    db.commit()
    return cursor.lastrowid

def save_prediction(id_user, id_pertanyaan, jawaban, label, confidence):
    # Simpan jawaban ke tabel prediksi
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO prediksi (id_user, id_pertanyaan, jawaban, label, confidence)
        VALUES (%s, %s, %s, %s, %s)
    """, (id_user, id_pertanyaan, jawaban, label, confidence))
    db.commit()


def get_total_score(user_id):
    cursor.execute("SELECT SUM(label) FROM prediksi WHERE id_user=%s", (user_id,))
    result = cursor.fetchone()
    return result[0] if result[0] else 0

def save_score(user_id, total_score):
    cursor.execute("INSERT INTO score (id_user, score) VALUES (%s, %s)", (user_id, total_score))
    db.commit()
