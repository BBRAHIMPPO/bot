import telebot
import sqlite3
import os
import time
import re
import logging
import requests
from flask import Flask
from threading import Thread
from telebot import types
from datetime import datetime

# ==========================================
# ⚙️ الإعدادات الأساسية (إياك أن تغير الأسماء)
# ==========================================
API_TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554  #
ADMIN_CODE = "0718991554" 
DEFAULT_CHANNEL = "https://t.me/+wZCOH72-1To3YWFk" #

# إعدادات اللوج (لتتبع الأخطاء)
logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
app = Flask('')

# ==========================================
# 📊 نظام قاعدة البيانات (SQLite3)
# ==========================================
class Database:
    def __init__(self, db_name="joseph_system.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # جدول المستخدمين
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                          (user_id INTEGER PRIMARY KEY, 
                           name TEXT, 
                           username TEXT, 
                           date_joined TEXT, 
                           is_banned INTEGER DEFAULT 0)''')
        # جدول الإعدادات الديناميكية
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings 
                          (key TEXT PRIMARY KEY, value TEXT)''')
        # تعيين الرابط الافتراضي إذا لم يوجد
        cursor.execute("INSERT OR IGNORE INTO settings VALUES ('channel_url', ?)", (DEFAULT_CHANNEL,))
        self.conn.commit()

    def add_user(self, uid, name, username):
        cursor = self.conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT OR IGNORE INTO users (user_id, name, username, date_joined) VALUES (?, ?, ?, ?)", 
                       (uid, name, username, now))
        self.conn.commit()

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE is_banned = 0")
        return [row[0] for row in cursor.fetchall()]

    def get_stats(self):
        cursor = self.conn.cursor()
        total = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        banned = cursor.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1").fetchone()[0]
        return total, banned

    def ban_user(self, uid):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (uid,))
        self.conn.commit()

    def unban_user(self, uid):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (uid,))
        self.conn.commit()

    def set_config(self, key, value):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
        self.conn.commit()

    def get_config(self, key):
        cursor = self.conn.cursor()
        res = cursor.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return res[0] if res else None

db = Database()

# ==========================================
# 🛠️ الدوال المساعدة (Helpers)
# ==========================================

def get_welcome_markup():
    """توليد زر الانضمام للقناة بشكل ديناميكي"""
    url = db.get_config('channel_url')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=url)) #
    return markup

def send_welcome_message(chat_id):
    """إرسال رسالة الترحيب الاحترافية المطلوبة"""
    text = (
        "<b>Welcome to JOSEPH FIXED MATCHES</b> ⚽️\n\n" #
        "To get today's 100% GUARANTEED &amp; SECURE fixed scores, " #
        "you must join our official channel first!\n\n" #
        "👇 <b>Click the button below to join:</b>" #
    )
    try:
        bot.send_message(chat_id, text, reply_markup=get_welcome_markup())
        return True
    except Exception as e:
        logging.error(f"Error sending to {chat_id}: {e}")
        return False

# ==========================================
# 🛂 لوحة تحكم الأدمن (12 ميزة)
# ==========================================

def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    # الميزات المطلوبة
    markup.add("📊 الإحصائيات", "📢 إذاعة نصية", "🖼 إذاعة صورة")
    markup.add("📥 تصدير الأيديات", "🚫 حظر مستخدم", "✅ فك حظر")
    markup.add("🔗 تغيير الرابط", "🔎 فحص أيدي", "🧹 تنظيف قاعدة البيانات")
    markup.add("🌐 حالة السيرفر", "📝 رسالة مخصصة", "🔐 إغلاق اللوحة")
    return markup

# ==========================================
# 🤖 معالجة الرسائل (The Core Logic)
# ==========================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid = message.chat.id
    name = message.from_user.first_name
    user = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
    
    db.add_user(uid, name, user)
    
    if uid != ADMIN_ID:
        send_welcome_message(uid)
        # إشعار للأدمن
        stats = db.get_stats()[0]
        notify = (
            "تم دخول شخص جديد إلى البوت الخاص بك 👾\n"
            "-----------------------\n"
            "• معلومات العضو الجديد .\n\n"
            f"• الاسم : {name}\n"
            f"• معرف : {user}\n"
            f"• الايدي : {uid}\n"
            "-----------------------\n"
            f"• عدد الأعضاء الكلي : {stats}"
        )
        bot.send_message(ADMIN_ID, notify)

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'voice', 'location'])
def master_listener(message):
    uid = message.chat.id
    text = message.text if message.text else ""

    # 1. الدخول للوحة التحكم
    if text == ADMIN_CODE:
        bot.reply_to(message, "✅ <b>مرحباً بك يا زعيم!</b> تم تفعيل وضع التحكم الكامل.", reply_markup=admin_keyboard())
        return

    # 2. خاصية استخراج الأيدي والرد التلقائي (الطلب الأساسي)
    if uid == ADMIN_ID and "الايدي :" in text:
        # استخراج الرقم باستخدام Regex من الرسالة
        match = re.search(r'الايدي\s*:\s*(\d+)', text)
        if match:
            target_id = match.group(1)
            if send_welcome_message(target_id):
                bot.reply_to(message, f"🚀 <b>تم الإرسال بنجاح!</b>\nتم تزويد صاحب الأيدي <code>{target_id}</code> برابط القناة.")
            else:
                bot.reply_to(message, "❌ فشل الإرسال. قد يكون المستخدم قد قام بحظر البوت.")
        return

    # 3. معالجة أوامر لوحة التحكم
    if uid == ADMIN_ID:
        if text == "📊 الإحصائيات":
            total, banned = db.get_stats()
            bot.reply_to(message, f"📈 <b>إحصائيات البوت:</b>\n\n• الأعضاء النشطين: {total}\n• الأعضاء المحظورين: {banned}\n• الحالة: ممتاز ✅")
        
        elif text == "📥 تصدير الأيديات":
            users = db.get_all_users()
            with open("users.txt", "w") as f:
                for u in users: f.write(f"{u}\n")
            bot.send_document(ADMIN_ID, open("users.txt", "rb"), caption="✅ ملف الأيديات جاهز.")
            os.remove("users.txt")

        elif text == "🔗 تغيير الرابط":
            msg = bot.reply_to(message, "ارسل الرابط الجديد للقناة الآن:")
            bot.register_next_step_handler(msg, update_link)

        elif text == "🌐 حالة السيرفر":
            bot.reply_to(message, "🟢 <b>Server Status:</b> Active\n🕒 <b>System Time:</b> " + datetime.now().strftime("%H:%M:%S"))

        elif text == "🔐 إغلاق اللوحة":
            bot.reply_to(message, "تم إغلاق لوحة التحكم بنجاح.", reply_markup=types.ReplyKeyboardRemove())

    # 4. الرد التلقائي على أي شخص آخر
    if uid != ADMIN_ID:
        db.add_user(uid, message.from_user.first_name, message.from_user.username)
        send_welcome_message(uid)

# --- وظائف إضافية للأدمن ---

def update_link(message):
    if message.text and "t.me" in message.text:
        db.set_config('channel_url', message.text)
        bot.reply_to(message, f"✅ تم تحديث الرابط بنجاح إلى:\n{message.text}")
    else:
        bot.reply_to(message, "❌ رابط غير صحيح.")

# ==========================================
# 🌐 تشغيل السيرفر والبوت (24/7)
# ==========================================

@app.route('/')
def home():
    return "Joseph Bot is alive and well!"

def run():
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    logging.info("Starting Joseph Ultimate System...")
    keep_alive()
    # المحاولة المستمرة للتشغيل في حالة انقطاع الاتصال
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            logging.error(f"Polling error: {e}")
            time.sleep(5)
