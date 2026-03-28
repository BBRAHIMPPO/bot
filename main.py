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
ADMIN_CODE = "0718991554"
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- نظام حفظ الداتا (SQLite) - لضمان عدم ضياع الأيديات ---
def init_db():
    conn = sqlite3.connect('joseph_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, join_date TEXT)''')
    conn.commit()
    conn.close()

def save_user(user_id, name, username):
    conn = sqlite3.connect('joseph_database.db', check_same_thread=False)
    cursor = conn.cursor()
    date = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)', (user_id, name, username, date))
    conn.commit()
    conn.close()

# --- لوحة التحكم (10 ميزات تطورية) ---
def admin_panel():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    # 10 ميزات قوية للتحكم الكامل
    markup.add("📊 إحصائيات دقيقة", "📢 إرسال رسالة للكل")
    markup.add("🖼 إرسال صورة للكل", "📥 تحميل ملف الأيديات (TXT)")
    markup.add("💬 رد مباشر على أيدي", "🚫 حظر مستخدم (Ban)")
    markup.add("📍 آخر 10 منضمين", "🛠 فحص حالة السيرفر")
    markup.add("📝 تغيير رابط القناة", "🔐 إغلاق لوحة التحكم")
    return markup

# --- رسالة الترحيب ورابط القناة ---
def send_welcome(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL))
    welcome_msg = (
        "Welcome to JOSEPH FIXED MATCHES ⚽️\n\n"
        "To get today's 100% GUARANTEED & SECURE fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 Click the button below to join:"
    )
    try:
        bot.send_message(chat_id, welcome_msg, reply_markup=markup)
        return True
    except: return False

# --- Server Keep-Alive ---
@app.route('/')
def home(): return "SYSTEM STATUS: ACTIVE 🟢"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

# --- معالجة الرسائل ---
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'voice', 'audio', 'sticker'])
def core_handler(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
    text = message.text if message.text else ""

    # 1. تفعيل الأدمن
    if text == ADMIN_CODE:
        bot.reply_to(message, "✅ **أهلاً يا زعيم!** تم تفعيل اللوحة المتطورة (10 ميزات).", reply_markup=admin_panel())
        return

    # 2. ميزة "الصيد الجماعي" (تحويل 100 ميساج دقة وحدة)
    if user_id == ADMIN_ID and "الايدي :" in text:
        found_ids = re.findall(r'(\d{9,10})', text) # البحث عن أي رقم أيدي فالميساج
        if found_ids:
            success = 0
            for target in found_ids:
                if send_welcome(target):
                    success += 1
                    time.sleep(0.1) # حماية من البلوك
            bot.reply_to(message, f"🚀 تم اصطياد {len(found_ids)} أيدي!\n✅ تم إرسال الترحيب لـ {success} واحد.")
        return

    # 3. إشعارات للأدمن عن أي حركة
    if user_id != ADMIN_ID:
        notify = f"👾 **حركة جديدة:**\n• الاسم: {name}\n• الأيدي: `{user_id}`\n• الرسالة: {text}"
        bot.send_message(ADMIN_ID, notify, parse_mode="Markdown")

    # 4. حفظ المستخدم والرد التلقائي (أي رسالة يرسلها)
    save_user(user_id, name, username)
    if user_id != ADMIN_ID:
        send_welcome(user_id)

# --- تشغيل وظائف اللوحة ---
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_commands(message):
    if message.text == "📊 إحصائيات دقيقة":
        conn = sqlite3.connect('joseph_database.db')
        count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        bot.reply_to(message, f"📈 إجمالي الضحايا المسجلين: {count}")
        conn.close()
    elif message.text == "📥 تحميل ملف الأيديات (TXT)":
        conn = sqlite3.connect('joseph_database.db')
        users = conn.execute('SELECT user_id FROM users').fetchall()
        with open("all_users.txt", "w") as f:
            for u in users: f.write(f"{u[0]}\n")
        bot.send_document(ADMIN_ID, open("all_users.txt", "rb"), caption="✅ هادي هي الداتا ديالك كاملة.")
        conn.close()

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling(skip_pending=False)
