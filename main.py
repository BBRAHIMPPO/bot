import telebot
import sqlite3
import os
import time
from flask import Flask
from threading import Thread
from telebot import types

# --- الإعدادات (تأكد من التوكن والأيدي) ---
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554 
ADMIN_CODE = "0718991554" # الكود السري لدخول اللوحة
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk" # رابط القناة

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- قاعدة بيانات لحفظ الأعضاء (ما يضيع والو) ---
def init_db():
    conn = sqlite3.connect('joseph_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()

def save_user(uid):
    conn = sqlite3.connect('joseph_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users VALUES (?)', (uid,))
    conn.commit()
    conn.close()

# --- دالة إرسال رسالة الترحيب الاحترافية ---
def send_pro_welcome(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL)
    markup.add(btn)
    
    # النص اللي طلبتي بالظبط
    welcome_text = (
        "Welcome to JOSEPH FIXED MATCHES ⚽️\n\n"
        "To get today's 100% GUARANTEED & SECURE fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 Click the button below to join:"
    )
    try:
        bot.send_message(chat_id, welcome_text, reply_markup=markup)
    except:
        pass

# --- لوحة التحكم (Admin Panel) ---
def get_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📊 الإحصائيات", "📢 إرسال جماعي")
    markup.add("📥 تحميل الأيديات", "🔐 إغلاق اللوحة")
    return markup

# --- Server Keep-Alive (Render) ---
@app.route('/')
def home(): return "JOSEPH BOT IS ACTIVE 🟢"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

# --- معالجة الرسائل ---
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'voice'])
def main_handler(message):
    uid = message.from_user.id
    text = message.text if message.text else ""

    # 1. لوحة التحكم للأدمن فقط
    if text == ADMIN_CODE:
        bot.reply_to(message, "✅ أهلاً جوزيف! لوحة التحكم مفعلة.", reply_markup=get_admin_keyboard())
        return

    # 2. أوامر اللوحة
    if uid == ADMIN_ID:
        if text == "📊 الإحصائيات":
            conn = sqlite3.connect('joseph_data.db')
            count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            bot.reply_to(message, f"📈 عدد الأعضاء الكلي: {count}")
            conn.close()
            return
        elif text == "📥 تحميل الأيديات":
            conn = sqlite3.connect('joseph_data.db')
            users = conn.execute('SELECT user_id FROM users').fetchall()
            with open("users.txt", "w") as f:
                for u in users: f.write(f"{u[0]}\n")
            bot.send_document(ADMIN_ID, open("users.txt", "rb"))
            conn.close()
            return

    # 3. الرد التلقائي على أي شخص (أي رسالة)
    save_user(uid)
    if uid != ADMIN_ID:
        send_pro_welcome(uid)

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling(skip_pending=False)
