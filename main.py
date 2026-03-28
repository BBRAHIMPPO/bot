import telebot
import sqlite3
import os
import time
import re
from flask import Flask
from threading import Thread
from telebot import types

# --- الإعدادات ---
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554 
ADMIN_SECRET_CODE = "7779900009"
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- نظام حفظ الداتا (SQLite) ---
def init_db():
    conn = sqlite3.connect('joseph_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT)')
    conn.commit()
    conn.close()

def save_user(user_id, name):
    conn = sqlite3.connect('joseph_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)', (user_id, name))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('joseph_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    ids = [r[0] for r in cursor.fetchall()]
    conn.close()
    return ids

# --- رسالة الترحيب الاحترافية ---
def send_welcome(target_id):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL)
    markup.add(btn)
    
    welcome_text = (
        "Welcome to JOSEPH FIXED MATCHES ⚽️\n\n"
        "To get today's 100% GUARANTEED & SECURE fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 Click the button below to join:"
    )
    try:
        bot.send_message(target_id, welcome_text, reply_markup=markup)
        return True
    except:
        return False

# --- Server Keep-Alive ---
@app.route('/')
def home(): return "JOSEPH SYSTEM IS LIVE 🟢"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

# --- معالجة الرسائل ---
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'voice'])
def handle_all(message):
    user_id = message.from_user.id
    text = message.text if message.text else ""

    # 1. تفعيل الأدمن
    if text == ADMIN_SECRET_CODE:
        bot.reply_to(message, "✅ **Welcome Boss!**\nوضع التحكم الكامل مفعل.", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("📊 الإحصائيات", "📢 إرسال للكل"))
        return

    # 2. ميزة إعادة الاستهداف (التحويل الذكي)
    if user_id == ADMIN_ID and "الايدي :" in text:
        # البحث عن رقم الأيدي من النص المحول (مثلا: الايدي : 6124430879)
        found_id = re.search(r'الايدي\s*:\s*(\d+)', text)
        if found_id:
            target_id = found_id.group(1)
            if send_welcome(target_id):
                bot.reply_to(message, f"✅ تم إعادة استهداف العضو `{target_id}` بنجاح!")
            else:
                bot.reply_to(message, f"❌ فشل الإرسال لـ `{target_id}` (ممكن بلوكا البوت).")
        return

    # 3. حفظ أي واحد دخل جديد
    save_user(user_id, message.from_user.first_name)
    
    # 4. رد تلقائي للمستخدمين
    if text == "/start":
        send_welcome(user_id)

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling(skip_pending=False)
