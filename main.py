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
# 📊 قاعدة البيانات (ممنوع الحذف)
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

    def get_all_users(self):
        return self.conn.execute("SELECT user_id, name, username, date FROM users").fetchall()

    def get_all_ids(self):
        return [r[0] for r in self.conn.execute("SELECT user_id FROM users").fetchall()]

    def ban_user(self, uid):
        self.conn.execute("INSERT OR IGNORE INTO banned VALUES (?)", (uid,))
        self.conn.commit()

    def unban_user(self, uid):
        self.conn.execute("DELETE FROM banned WHERE user_id=?", (uid,))
        self.conn.commit()

    def is_banned(self, uid):
        return self.conn.execute("SELECT 1 FROM banned WHERE user_id=?", (uid,)).fetchone() is not None

    def get_setting(self, key):
        r = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return r[0] if r else None

    def set_setting(self, key, value):
        self.conn.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (key, value))
        self.conn.commit()

db = Database()

# ==========================================
# 🛠️ دوال المساعدة (تعديل: عدم إرسال ترحيب للأدمن)
# ==========================================
def get_channel_url():
    return db.get_setting('channel_url') or CHANNEL_URL

def get_welcome_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=get_channel_url()))
    return markup

def send_welcome(chat_id):
    # إضافة شرط: إذا كان المستلم هو الأدمن، لا ترسل له رسالة الترحيب العادية
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
# 🕹️ لوحة تحكم الأدمن (20 أمر)
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
# 🤖 معالجة أوامر الأدمن
# ==========================================
def handle_admin(message):
    global admin_state, ADMIN_ID
    uid = message.chat.id
    text = message.text if message.text else ""

    # استخراج تلقائي للأيدي من رسالة الدخول التي ترسلها أنت (الأدمن)
    if "الايدي :" in text or "الايدي:" in text:
        ids = re.findall(r'الايدي\s*:\s*(\d+)', text)
        if ids:
            for target in ids:
                # هنا نرسل الترحيب للعضو المستخرج أيديه
                if send_welcome_to_user_only(target):
                    bot.send_message(uid, f"✅ تم استخراج الأيدي <code>{target}</code> وإرسال الترحيب.")
                else:
                    bot.send_message(uid, f"❌ فشل الإرسال للأيدي <code>{target}</code>.")
        return

    # بقية أوامر الأدمن... (نفس المنطق السابق)
    if text == "📊 الإحصائيات":
        bot.reply_to(message, f"📈 إجمالي المشتركين: {db.get_total()}")
    elif text == "🔐 إغلاق اللوحة":
        bot.reply_to(message, "تم إغلاق اللوحة.", reply_markup=types.ReplyKeyboardRemove())

def send_welcome_to_user_only(chat_id):
    """دالة خاصة لإرسال الترحيب للمستخدمين فقط عبر أداة الاستخراج"""
    text = (
        "<b>Welcome to JOSEPH FIXED MATCHES</b> ⚽️\n\n"
        "To get today's 100% GUARANTEED & SECURE fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 <b>Click the button below to join:</b>"
    )
    try:
        bot.send_message(int(chat_id), text, reply_markup=get_welcome_markup())
        return True
    except: return False

# ==========================================
# 📩 المحرك الرئيسي (Core)
# ==========================================
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def core_processor(message):
    global ADMIN_ID
    
    # 1. التحقق من كود الأدمن
    if message.text == ADMIN_CODE:
        ADMIN_ID = message.chat.id
        bot.reply_to(message, "✅ تم تفعيل لوحة التحكم. لن تصلك رسائل الترحيب العادية بعد الآن.", reply_markup=admin_keyboard())
        return

    # 2. توجيه الرسالة حسب الرتبة
    if message.chat.id == ADMIN_ID:
        handle_admin(message)
    else:
        # للمستخدم العادي فقط: حفظ البيانات + إرسال إشعار للأدمن + إرسال ترحيب
        uid = message.chat.id
        if db.is_banned(uid): return
        
        name = message.from_user.first_name or "User"
        user_name = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
        db.add_user(uid, name, user_name)
        
        # إشعار للأدمن
        notify = (
            "تم دخول شخص جديد إلى البوت الخاص بك 👾\n"
            "-----------------------\n"
            "• معلومات العضو الجديد .\n\n"
            f"• الاسم : {name}\n"
            f"• معرف : {user_name}\n"
            f"• الايدي : {uid}\n"
            "-----------------------\n"
            f"• عدد الأعضاء الكلي : {db.get_total()}"
        )
        if ADMIN_ID != 0:
            bot.send_message(ADMIN_ID, notify)
            
        # إرسال ترحيب للمستخدم (الدالة ستتأكد أنه ليس الأدمن)
        send_welcome(uid)

# ==========================================
# 🌐 تشغيل السيرفر
# ==========================================
@app.route('/')
def home(): return "SYSTEM ONLINE"

def run_web(): app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling(timeout=60)
