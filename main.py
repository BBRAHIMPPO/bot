import telebot
import sqlite3
import os
import re
import time
from flask import Flask
from threading import Thread
from telebot import types
from datetime import datetime

# ==========================================
# ⚙️ الإعدادات الأساسية
# ==========================================
API_TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 0  
ADMIN_CODE = "999"
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
app = Flask('')

admin_state = {}

# ==========================================
# 📊 قاعدة البيانات (ثابتة لا تتغير)
# ==========================================
class Database:
    def __init__(self, db_name="joseph_master_pro.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS banned
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS settings
                     (key TEXT PRIMARY KEY, value TEXT)''')
        self.conn.commit()
        self._init_settings()

    def _init_settings(self):
        c = self.conn.cursor()
        c.execute("INSERT OR IGNORE INTO settings VALUES ('channel_url', ?)", (CHANNEL_URL,))
        self.conn.commit()

    def add_user(self, uid, name, username):
        c = self.conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", (uid, name, username, now))
        self.conn.commit()

    def get_total(self):
        return self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def get_all_ids(self):
        return [r[0] for r in self.conn.execute("SELECT user_id FROM users").fetchall()]

    def is_banned(self, uid):
        return self.conn.execute("SELECT 1 FROM banned WHERE user_id=?", (uid,)).fetchone() is not None

    def get_setting(self, key):
        r = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return r[0] if r else None

db = Database()

# ==========================================
# 🛠️ دالة الترحيب (معدلة لمنع إزعاج الأدمن)
# ==========================================
def get_welcome_markup():
    markup = types.InlineKeyboardMarkup()
    url = db.get_setting('channel_url') or CHANNEL_URL
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=url))
    return markup

def send_welcome(chat_id):
    # لا نرسل ترحيب للأدمن أبداً
    if int(chat_id) == ADMIN_ID:
        return False
        
    text = (
        "<b>Welcome to JOSEPH FIXED MATCHES</b> ⚽️\n\n"
        "To get today's 100% GUARANTEED & SECURE fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 <b>Click the button below to join:</b>"
    )
    try:
        bot.send_message(int(chat_id), text, reply_markup=get_welcome_markup())
        return True
    except:
        return False

# ==========================================
# 🕹️ لوحة تحكم الأدمن (البانيل الكاملة)
# ==========================================
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add("📊 الإحصائيات", "📢 إذاعة نص", "🖼 إذاعة وسائط")
    markup.add("📥 تصدير IDs", "🔗 تحديث الرابط", "🚫 حظر مستخدم")
    markup.add("✅ فك حظر", "🔍 فحص أيدي", "👥 قائمة الأعضاء")
    markup.add("🧹 تنظيف الداتا", "📋 معلوماتي", "🔐 إغلاق اللوحة")
    markup.add("🕒 وقت السيرفر", "📡 حالة الاتصال", "📂 نسخة احتياطية")
    markup.add("💬 إرسال لشخص", "🎁 هدية للكل", "⚙️ الإعدادات")
    markup.add("🆘 الدعم الفني", "🛠 مطور البوت")
    return markup

# ==========================================
# 🤖 معالجة أوامر الأدمن + استخراج الأيدي
# ==========================================
def handle_admin(message):
    global ADMIN_ID
    uid = message.chat.id
    text = message.text if message.text else ""

    # خاصية الاستخراج: ابحث عن أي رقم أيدي داخل الرسالة وأرسل له ترحيب
    if "الايدي :" in text or "الايدي:" in text or "ID:" in text:
        ids = re.findall(r'(\d{7,15})', text) # يستخرج أي رقم طويل يشبه الأيدي
        if ids:
            for target in ids:
                if int(target) == ADMIN_ID: continue
                if send_welcome(target):
                    bot.send_message(uid, f"✅ تم إرسال الترحيب للأيدي: <code>{target}</code>")
                else:
                    bot.send_message(uid, f"❌ فشل الإرسال للأيدي: <code>{target}</code>")
        return

    # أوامر البانيل
    if text == "📊 الإحصائيات":
        bot.reply_to(message, f"📈 المشتركين: {db.get_total()}")
    elif text == "🔐 إغلاق اللوحة":
        bot.reply_to(message, "🔐 تم الحفظ وإغلاق اللوحة.", reply_markup=types.ReplyKeyboardRemove())

# ==========================================
# 📩 المحرك الرئيسي (معدل لحل مشكلة Render)
# ==========================================
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def core_processor(message):
    global ADMIN_ID
    
    # 1. تفعيل الأدمن ومنع الترحيب عنه
    if message.text == ADMIN_CODE:
        ADMIN_ID = message.chat.id
        bot.reply_to(message, "✅ أهلاً بك يا زعيم. لوحة التحكم نشطة الآن.", reply_markup=admin_keyboard())
        return

    # 2. إذا كان أدمن: عالج أوامر البانيل والاستخراج
    if message.chat.id == ADMIN_ID:
        handle_admin(message)
        return

    # 3. إذا كان مستخدم عادي: سجل بياناته، أرسل ترحيب، أرسل إشعار للأدمن
    else:
        uid = message.chat.id
        if db.is_banned(uid): return
        
        db.add_user(uid, message.from_user.first_name, f"@{message.from_user.username}")
        
        # إشعار للأدمن (الصيغة المطلوبة)
        notify = (
            "تم دخول شخص جديد إلى البوت الخاص بك 👾\n"
            "-----------------------\n"
            "• معلومات العضو الجديد .\n\n"
            f"• الاسم : {message.from_user.first_name}\n"
            f"• معرف : @{message.from_user.username}\n"
            f"• الايدي : {uid}\n"
            "-----------------------\n"
            f"• عدد الأعضاء الكلي : {db.get_total()}"
        )
        if ADMIN_ID != 0:
            bot.send_message(ADMIN_ID, notify)
            
        send_welcome(uid)

# ==========================================
# 🌐 نظام الـ Web وشيفرة استقرار Render
# ==========================================
@app.route('/')
def home(): return "SYSTEM ACTIVE"

def run_web(): app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run_web).start()
    
    # حل مشكلة Conflict (Error 409)
    try:
        bot.remove_webhook()
        time.sleep(2)
    except:
        pass

    print("Joseph Master Pro is running...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=5)
        except Exception as e:
            time.sleep(10) # انتظار في حال حدوث خطأ في الشبكة
