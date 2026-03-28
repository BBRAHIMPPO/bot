import telebot
import sqlite3
import os
import time
import re
from flask import Flask
from threading import Thread
from telebot import types

# --- الإعدادات الأساسية ---
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554 
ADMIN_CODE = "0718991554"
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- قاعدة البيانات لحفظ المستخدمين للأبد ---
def init_db():
    conn = sqlite3.connect('joseph_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT)')
    conn.commit()
    conn.close()

def save_user(user_id, name):
    conn = sqlite3.connect('joseph_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users VALUES (?, ?)', (user_id, name))
    conn.commit()
    conn.close()

# --- رسالة الترحيب الاحترافية مع الرابط ---
def send_welcome_to_id(target_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL))
    
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

# --- Flask Server ---
@app.route('/')
def home(): return "SYSTEM STATUS: ACTIVE 🟢"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

# --- معالجة الرسائل ---
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'voice'])
def master_handler(message):
    user_id = message.from_user.id
    text = message.text if message.text else ""

    # 1. دخول الأدمن
    if text == ADMIN_CODE:
        bot.reply_to(message, "✅ **أهلاً يا زعيم!** تم تفعيل لوحة التحكم.")
        return

    # 2. ميزة إعادة التحويل الجماعي (الذكاء الاصطناعي لاستخراج الأيديات)
    if user_id == ADMIN_ID and "الايدي :" in text:
        # البحث عن كل الأيديات الموجودة في الرسالة المحولة
        found_ids = re.findall(r'الايدي\s*:\s*(\d+)', text)
        
        if found_ids:
            sent_count = 0
            for target in found_ids:
                if send_welcome_to_id(target):
                    sent_count += 1
                    # تبريد بسيط باش تليجرام ما يبلوكيكش فـ الإرسال الجماعي
                    time.sleep(0.1) 
            
            bot.send_message(ADMIN_ID, f"✅ تم معالجة التحويل بنجاح!\n🚀 تم إرسال رسالة الترحيب لـ {sent_count} شخص.")
        return

    # 3. للمستخدمين العاديين
    if user_id != ADMIN_ID:
        save_user(user_id, message.from_user.first_name)
        send_welcome_to_id(user_id)
        
        # إشعار للأدمن (كما في الصورة)
        notify = f"👾 دخول جديد:\n• الاسم: {message.from_user.first_name}\n• الايدي: {user_id}"
        bot.send_message(ADMIN_ID, notify)

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling(skip_pending=False)
