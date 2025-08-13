import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

API_URL = "http://127.0.0.1:8000"
BOT_TOKEN = "7749303236:AAFyVCdlNoB1VWH3ET_ZO3BfIAHbQI7D92k"

# Pertanyaan PHQ-9
PHQ_QUESTIONS = [
    "1. Seberapa sering Anda merasa kurang tertarik atau bergairah dalam melakukan kegiatan apapun?",
    "2. Seberapa sering Anda merasa murung, muram, atau putus asa?",
    "3. Seberapa sering Anda mengalami sulit tidur atau mudah terbangun, atau terlalu banyak tidur?",
    "4. Seberapa sering Anda merasa lelah atau kurang bertenaga?",
    "5. Seberapa sering Anda mengalami penurunan nafsu makan atau makan berlebihan?",
    "6. Seberapa sering Anda merasa kurang percaya diri atau merasa bahwa Anda adalah orang yang gagal atau telah mengecewakan diri sendiri atau keluarga?",
    "7. Seberapa sering Anda mengalami kesulitan berkonsentrasi, misalnya saat membaca koran atau menonton televisi?",
    "8. Seberapa sering Anda bergerak atau berbicara sangat lambat sehingga orang lain memperhatikannya. Atau sebaliknya, merasa resah atau gelisah sehingga Anda lebih sering bergerak dari biasanya?",
    "9. Seberapa sering Anda merasa lebih baik mati atau ingin melukai diri sendiri dengan cara apapun?"
]

# Menyimpan state user di memory (sementara)
user_states = {}

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Selamat datang di Tes PHQ-9🤗👋!\n"
        f"PHQ-9 merupakan metode untuk mendefinisikan depresi tetapi bukan penegakan diagnosis\n"
        f"\nSilakan ketik nama Anda:\n"
    )
    user_states[update.effective_user.id] = {"step": "get_name"}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_id not in user_states:
        await update.message.reply_text("Ketik /start untuk memulai.")
        return
    
    state = user_states[user_id]

    # Step 1: Ambil nama
    if state["step"] == "get_name":
        state["nama"] = text
        state["step"] = "get_univ"
        await update.message.reply_text("Masukkan nama perguruan tinggi Anda:")
    
    # Step 2: Ambil perguruan tinggi
    elif state["step"] == "get_univ":
        state["perguruan_tinggi"] = text
        # Buat user di database
        payload = {"nama": state["nama"], "perguruan_tinggi": state["perguruan_tinggi"]}
        res = requests.post(f"{API_URL}/user/create", json=payload)
        if res.status_code == 200:
            id_user = res.json()["id_user"]
            state["id_user"] = id_user
            state["step"] = "ask_question"
            state["current_q"] = 0
            state["jawaban"] = []
            await update.message.reply_text("Baik, mari mulai tes PHQ-9!")
            await update.message.reply_text(PHQ_QUESTIONS[state["current_q"]])
        else:
            await update.message.reply_text("Gagal membuat user, coba lagi.")

    # Step 3: Tanya 9 pertanyaan satu per satu
    elif state["step"] == "ask_question":
        state["jawaban"].append(text)
        state["current_q"] += 1
        if state["current_q"] < len(PHQ_QUESTIONS):
            await update.message.reply_text(PHQ_QUESTIONS[state["current_q"]])
        else:
            # Sudah dapat 9 jawaban -> kirim ke API bulk
            payload = {"id_user": state["id_user"], "jawaban": state["jawaban"]}
            res = requests.post(f"{API_URL}/predict/bulk", json=payload)
            if res.status_code == 200:
                data = res.json()
                score = data["total_score"]
                kategori = data["kategori"]
                nama = state["nama"]
                await update.message.reply_text(
                    f"Tes telah selesai!, {nama}!😇\n"
                    f"\nSkor depresi Anda: {score}\n"
                    f"{kategori}\n"
                    f"Semangat terus, {nama}!. Jaga selalu kesehatan mental ya 🤗\n"
                    f"Berikut adalah semua rentang skor depresi, klik link jika ingin mengetahui\n"
                    f"https://docs.google.com/document/d/1bsXRNPiZNj_ShZP3yb2DWoKVse7OASpQ0JzfiYlZJLc/edit?usp=sharing"
                )
            else:
                await update.message.reply_text("Gagal memproses hasil, coba lagi.")
            del user_states[user_id]

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ketik /start untuk memulai tes.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
