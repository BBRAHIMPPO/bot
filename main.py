import telebot
import sqlite3
import os
import time
import re
from flask import Flask
from threading import Thread
from telebot import types

# --- الأساسيات ---
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554 
ADMIN_CODE = "0718991554"
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- 1. نظام قاعدة البيانات (حفظ الداتا للأبد) ---
def init_db():
    conn = sqlite3.connect('joseph_final_system.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, join_date TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def save_user(uid, name, user, status="active"):
    conn = sqlite3.connect('joseph_final_system.db', check_same_thread=False)
    cursor = conn.cursor()
    date = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?)', (uid, name, user, date, status))
    conn.commit()
    conn.close()

# --- 2. لوحة التحكم المطورة (أكثر من 20 ميزة احترافية) ---
def get_mega_panel():
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add("📊 إحصائيات شاملة", "📢 إرسال نص للكل", "🖼 إرسال صورة للكل")
    markup.add("📥 سحب ملف TXT", "📥 تحميل قاعدة البيانات", "💬 رد مباشر (ID)")
    markup.add("🚫 حظر مستخدم", "✅ فك حظر", "📍 آخر 20 منضم")
    markup.add("🔗 تغيير الرابط", "⚙️ حالة السيرفر", "❌ إغلاق اللوحة")
    return markup

# --- 3. نظام الرد التلقائي ورسالة الترحيب ---
def send_forced_welcome(chat_id):
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
def home(): return "SYSTEM IS RUNNING 24/7"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

# --- 4. معالجة الرسائل والتحكم الكامل ---
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'voice', 'audio', 'sticker'])
def core_system(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "No User"
    text = message.text if message.text else "[Media/File]"

    # دخول الأدمن بالكود
    if text == ADMIN_CODE:
        bot.reply_to(message, "✅ **أهلاً بك يا جوزيف!** تم تفعيل النظام الشامل.", reply_markup=get_mega_panel())
        return

    # إشعارات المراقبة اللحظية للأدمن
    if user_id != ADMIN_ID:
        notify = (
            "🔔 **تحرك جديد!**\n"
            f"👤 العضو: {name} ({username})\n"
            f"🆔 الأيدي: `{user_id}`\n"
            f"💬 كتب: {text}"
        )
        bot.send_message(ADMIN_ID, notify, parse_mode="Markdown")

    # ميزة استخراج الأيديات الجماعية (Forwarding)
    if user_id == ADMIN_ID and "الايدي :" in text:
        ids = re.findall(r'(\d{9,10})', text)
        if ids:
            count = 0
            for uid in ids:
                if send_forced_welcome(uid):
                    count += 1
                    time.sleep(0.1)
            bot.reply_to(message, f"🚀 تم معالجة {len(ids)} أيدي.\n✅ تم الإرسال لـ {count} شخص بنجاح.")
        return

    # حفظ المستخدم والرد عليه أوتوماتيكياً (إجباري)
    save_user(user_id, name, username)
    if user_id != ADMIN_ID:
        send_forced_welcome(user_id)

# --- 5. وظائف لوحة التحكم ---
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_actions(message):
    if message.text == "📊 إحصائيات شاملة":
        conn = sqlite3.connect('joseph_final_system.db')
        count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        bot.reply_to(message, f"📈 إجمالي الأشخاص في قاعدة البيانات: {count}")
        conn.close()
    elif message.text == "📥 سحب ملف TXT":
        conn = sqlite3.connect('joseph_final_system.db')
        users = conn.execute('SELECT user_id FROM users').fetchall()
        with open("all_users.txt", "w") as f:
            for u in users: f.write(f"{u[0]}\n")
        bot.send_document(ADMIN_ID, open("all_users.txt", "rb"))
        conn.close()
    elif message.text == "⚙️ حالة السيرفر":
        bot.reply_to(message, "🟢 السيرفر يعمل بشكل ممتاز على Render.\n⏱ التحديث القادم عبر Cron-job خلال 15 دقيقة.")

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling(skip_pending=False)
