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

    def add_user(self, uid, name="عضو مستخرج", username="لا يوجد"):
        c = self.conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        # INSERT OR IGNORE تضمن عدم تكرار الأيدي
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", (uid, name, username, now))
        self.conn.commit()

    def get_total(self):
        return self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def get_all_ids(self):
        return [r[0] for r in self.conn.execute("SELECT user_id FROM users").fetchall()]

    def is_banned(self, uid):
        return self.conn.execute("SELECT 1 FROM banned WHERE user_id=?", (uid,)).fetchone() is not None

    def set_setting(self, key, value):
        self.conn.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (key, value))
        self.conn.commit()

db = Database()

# ==========================================
# 🛠️ دوال المساعدة
# ==========================================
def get_welcome_markup():
    url = db.conn.execute("SELECT value FROM settings WHERE key='channel_url'").fetchone()[0]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=url))
    return markup

def send_welcome(chat_id):
    if int(chat_id) == ADMIN_ID: return False
    text = "<b>Welcome to JOSEPH FIXED MATCHES</b> ⚽️\n\nTo get today's 100% GUARANTEED fixed scores, join our channel!"
    try:
        bot.send_message(int(chat_id), text, reply_markup=get_welcome_markup())
        return True
    except: return False

# ==========================================
# 🕹️ لوحة تحكم الأدمن (20 زر)
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
# 🤖 معالجة الملفات والأوامر
# ==========================================
def handle_admin(message):
    global admin_state, ADMIN_ID
    uid = message.chat.id

    # 1. خاصية استقبال ملف IDs (txt) وحفظهم دقة وحدة
    if message.content_type == 'document' and message.document.file_name.endswith('.txt'):
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # قراءة الأيديات من الملف
        content = downloaded_file.decode('utf-8')
        found_ids = re.findall(r'\d+', content)
        
        if found_ids:
            count = 0
            bot.reply_to(message, f"⏳ جاري معالجة {len(found_ids)} أيدي وحفظهم في الداتا...")
            for target_id in found_ids:
                db.add_user(int(target_id))
                count += 1
            bot.send_message(uid, f"✅ تمت العملية بنجاح!\nتمت إضافة {count} أيدي جديد إلى قاعدة البيانات.\nإجمالي الأعضاء الآن: {db.get_total()}")
        return

    # [بقية أوامر البانيل كما هي في الكود السابق لتشغيل الأزرار الـ 20]
    text = message.text if message.text else ""
    
    # استخراج من رسالة نصية (الخاصية القديمة)
    extracted = re.findall(r'الايدي\s*:\s*(\d+)|للأيدي\s*:\s*(\d+)', text)
    if extracted:
        for tup in extracted:
            target = tup[0] or tup[1]
            db.add_user(int(target))
            send_welcome(target)
            bot.send_message(uid, f"✅ تم حفظ واستخراج الأيدي {target}")
        return

    # تفعيل أزرار الإذاعة وغيرها...
    if text == "📊 الإحصائيات":
        bot.reply_to(message, f"📈 إجمالي المشتركين في الداتا: {db.get_total()}")
    elif text == "📢 إذاعة نص" or text == "🖼 إذاعة وسائط":
        admin_state[uid] = "waiting_broadcast"
        bot.reply_to(message, "أرسل الآن ما تريد إذاعته للكل (سيصل لجميع الأيديات المخزنة من الملفات):")
    elif text == "📂 نسخة احتياطية":
        bot.send_document(uid, open("joseph_master_pro.db", "rb"))
    elif text == "🔐 إغلاق اللوحة":
        bot.reply_to(message, "تم الإغلاق.", reply_markup=types.ReplyKeyboardRemove())

# ==========================================
# 📩 المحرك الرئيسي (Core)
# ==========================================
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def core_processor(message):
    global ADMIN_ID
    
    if message.text == ADMIN_CODE:
        ADMIN_ID = message.chat.id
        bot.reply_to(message, "✅ أهلاً بك يا زعيم. لوحة التحكم والملفات جاهزة.", reply_markup=admin_keyboard())
        return

    if message.chat.id == ADMIN_ID:
        handle_admin(message)
    else:
        # المستخدم العادي
        uid = message.chat.id
        if db.is_banned(uid): return
        
        is_new = uid not in db.get_all_ids()
        db.add_user(uid, message.from_user.first_name)
        
        if is_new and ADMIN_ID != 0:
            bot.send_message(ADMIN_ID, f"👾 عضو جديد دخل البوت: {uid}")
        
        # ديما صيفط الترحيب للمستخدم العادي
        send_welcome(uid)

# ==========================================
# 🌐 تشغيل
# ==========================================
@app.route('/')
def home(): return "SYSTEM ACTIVE"

def run_web(): app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling(timeout=60)
