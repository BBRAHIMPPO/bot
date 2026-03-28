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
# ⚙️ الإعدادات الأساسية (تأكد من التوكن الخاص بك)
# ==========================================
API_TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 0  
ADMIN_CODE = "999"
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
app = Flask('')

admin_state = {}

# ==========================================
# 📊 قاعدة البيانات (ممنوع الحذف - تحفظ كل الأيديات)
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

    def add_user(self, uid, name="عضو مستخرج", username="لا يوجد"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.conn.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", (uid, name, username, now))
        self.conn.commit()

    def get_total(self):
        return self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def get_all_ids(self):
        return [r[0] for r in self.conn.execute("SELECT user_id FROM users").fetchall()]

    def is_banned(self, uid):
        return self.conn.execute("SELECT 1 FROM banned WHERE user_id=?", (uid,)).fetchone() is not None

    def ban_user(self, uid):
        self.conn.execute("INSERT OR IGNORE INTO banned VALUES (?)", (uid,))
        self.conn.commit()

    def unban_user(self, uid):
        self.conn.execute("DELETE FROM banned WHERE user_id=?", (uid,))
        self.conn.commit()

db = Database()

# ==========================================
# 🛠️ دالة الترحيب (تم تعديل النص هنا كما طلبت)
# ==========================================
def get_welcome_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL))
    return markup

def send_welcome(chat_id):
    if int(chat_id) == ADMIN_ID: return
    
    # النص المعدل ليطابق الصورة واحتياجاتك
    welcome_text = (
        "<b>Welcome to JOSEPH FIXED MATCHES</b> ⚽️\n\n"
        "To get today's 100% GUARANTEED & SECURE fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 <b>Click the button below to join:</b>"
    )
    
    try:
        # إرسال الرسالة مع الزر الشفاف
        bot.send_message(chat_id, welcome_text, reply_markup=get_welcome_markup())
    except:
        pass

# ==========================================
# 🕹️ لوحة تحكم الأدمن (20+ خاصية كاملة)
# ==========================================
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add("📊 الإحصائيات", "📢 إذاعة نص", "🖼 إذاعة وسائط")
    markup.add("📥 تصدير IDs", "🚫 حظر مستخدم", "✅ فك حظر")
    markup.add("🔍 فحص أيدي", "👥 قائمة الأعضاء", "📂 نسخة احتياطية")
    markup.add("💬 إرسال لشخص", "🎁 هدية للكل", "🕒 وقت السيرفر")
    markup.add("📡 حالة الاتصال", "🧹 تنظيف الداتا", "📋 معلوماتي")
    markup.add("⚙️ الإعدادات", "🔐 إغلاق اللوحة")
    return markup

# ==========================================
# 🤖 معالجة الملفات والردود السريعة
# ==========================================
def handle_admin(message):
    global admin_state, ADMIN_ID
    uid = message.chat.id
    text = message.text if message.text else ""

    # الرد على DM المستخدمين (Reply)
    if message.reply_to_message and "[ID:" in str(message.reply_to_message.text):
        match = re.search(r'\[ID:(\d+)\]', message.reply_to_message.text)
        if match:
            target_id = match.group(1)
            try:
                bot.copy_message(target_id, uid, message.message_id)
                bot.reply_to(message, "✅ تم إرسال ردك.")
            except: bot.reply_to(message, "❌ فشل الإرسال.")
        return

    # قراءة ملف IDs (txt) وحفظهم دقة وحدة
    if message.content_type == 'document' and message.document.file_name.endswith('.txt'):
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path).decode('utf-8')
        found = re.findall(r'\d+', downloaded)
        if found:
            bot.reply_to(message, f"⏳ جاري دمج {len(found)} أيدي في الداتا...")
            for f_id in found: db.add_user(int(f_id))
            bot.send_message(uid, f"✅ العملية تمت! الإجمالي الآن: {db.get_total()}")
        return

    # استخراج من نصوص (الايدي : ...)
    extracted = re.findall(r'الايدي\s*:\s*(\d+)|للأيدي\s*:\s*(\d+)', text)
    if extracted:
        for tup in extracted:
            target = tup[0] or tup[1]
            db.add_user(int(target))
            send_welcome(target)
            bot.send_message(uid, f"✅ تم حفظ واستخراج {target}")
        return

    # منطق أزرار البانيل
    if text == "📊 الإحصائيات":
        bot.reply_to(message, f"📈 عدد المستخدمين المخزنين: {db.get_total()}")
    elif text == "📢 إذاعة نص" or text == "🖼 إذاعة وسائط":
        admin_state[uid] = "broadcast"
        bot.reply_to(message, "أرسل محتوى الإذاعة (سيصل للكل):")
    elif text == "📥 تصدير IDs":
        with open("all_ids.txt", "w") as f:
            for i in db.get_all_ids(): f.write(f"{i}\n")
        bot.send_document(uid, open("all_ids.txt", "rb"), caption="📁 قاعدة بيانات الأيديات كاملة")
        os.remove("all_ids.txt")
    elif text == "📂 نسخة احتياطية":
        bot.send_document(uid, open("joseph_master_pro.db", "rb"))
    elif text == "🔐 إغلاق اللوحة":
        bot.reply_to(message, "تم الإغلاق.", reply_markup=types.ReplyKeyboardRemove())

    # نظام الإذاعة السريع (Background Thread)
    state = admin_state.get(uid)
    if state == "broadcast":
        admin_state[uid] = None
        ids = db.get_all_ids()
        bot.reply_to(message, f"🚀 جاري الإذاعة لـ {len(ids)} عضو...")
        def run_bc():
            s, f = 0, 0
            for i in ids:
                try: bot.copy_message(i, uid, message.message_id); s += 1
                except: f += 1
                time.sleep(0.04)
            bot.send_message(uid, f"✅ انتهت الإذاعة.\nنجاح: {s}\nفشل: {f}")
        Thread(target=run_bc).start()

# ==========================================
# 📩 المحرك الرئيسي (DM + ترحيب دائم)
# ==========================================
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def core_processor(message):
    global ADMIN_ID
    
    if message.text == ADMIN_CODE:
        ADMIN_ID = message.chat.id
        bot.reply_to(message, "✅ أهلاً بك يا جوزيف. النظام نشط بالكامل.", reply_markup=admin_keyboard())
        return

    if message.chat.id == ADMIN_ID:
        handle_admin(message)
    else:
        uid = message.chat.id
        if db.is_banned(uid): return
        
        is_new = uid not in db.get_all_ids()
        name = message.from_user.first_name or "User"
        db.add_user(uid, name, message.from_user.username)
        
        # 1. إشعار دخول جديد (للمالك)
        if is_new and ADMIN_ID != 0:
            bot.send_message(ADMIN_ID, f"👾 <b>دخول جديد:</b>\n👤 {name}\n🆔 [ID:{uid}]")
        
        # 2. نظام DM (توجيه رسالة المستخدم للمالك)
        if ADMIN_ID != 0:
            bot.send_message(ADMIN_ID, f"💬 <b>رسالة من:</b> {name} [ID:{uid}]")
            bot.copy_message(ADMIN_ID, uid, message.message_id)

        # 3. الرد التلقائي المعدل (دائماً)
        send_welcome(uid)

# ==========================================
# 🌐 تشغيل السيرفر
# ==========================================
@app.route('/')
def home(): return "JOSEPH TURBO SYSTEM ACTIVE"

def run_web(): app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling(skip_pending=True, timeout=60)
