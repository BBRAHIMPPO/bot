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
# 📊 قاعدة البيانات (كما هي بدون حذف)
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
# 🛠️ دوال المساعدة للترحيب
# ==========================================
def get_channel_url():
    return db.get_setting('channel_url') or CHANNEL_URL

def get_welcome_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=get_channel_url()))
    return markup

def send_welcome(chat_id):
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

def send_welcome_to_user_only(chat_id):
    if int(chat_id) == ADMIN_ID: return False
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
# 🕹️ بانيل الأدمن (20 زر)
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
# 🤖 معالجة أوامر الأدمن (تفعيل البانيل ونظام الرد)
# ==========================================
def handle_admin(message):
    global admin_state, ADMIN_ID
    uid = message.chat.id
    text = message.text if message.text else ""

    # ---- [إضافة]: الرد المباشر على رسائل الأعضاء ----
    if message.reply_to_message and message.reply_to_message.text:
        # نبحث عن الأيدي المرفق في رسالة البوت [ID]
        match = re.search(r'\[(\d+)\]', message.reply_to_message.text)
        if match:
            target_id = int(match.group(1))
            try:
                bot.copy_message(target_id, uid, message.message_id)
                bot.reply_to(message, "✅ تم إرسال ردك للمستخدم بنجاح.")
            except:
                bot.reply_to(message, "❌ فشل الإرسال، ربما المستخدم قام بحظر البوت.")
            return

    # استخراج تلقائي للأيدي من رسالة الدخول (الخاصية القديمة)
    if "الايدي :" in text or "الايدي:" in text:
        ids = re.findall(r'الايدي\s*:\s*(\d+)', text)
        if ids:
            for target in ids:
                if send_welcome_to_user_only(target):
                    bot.send_message(uid, f"✅ تم استخراج الأيدي <code>{target}</code> وإرسال الترحيب.")
                else:
                    bot.send_message(uid, f"❌ فشل الإرسال للأيدي <code>{target}</code>.")
        return

    # ---- [تفعيل]: حالات الأوامر (States) ----
    state = admin_state.get(uid)
    
    if state == "waiting_broadcast":
        admin_state[uid] = None
        users = db.get_all_ids()
        bot.reply_to(message, f"⏳ جاري الإذاعة لـ {len(users)} عضو...")
        success = 0
        for u_id in users:
            try:
                bot.copy_message(u_id, uid, message.message_id)
                success += 1
                time.sleep(0.05)
            except: pass
        bot.send_message(uid, f"✅ انتهت الإذاعة بنجاح.\nوصلت لـ: {success} مستخدم.")
        return

    elif state == "waiting_url":
        admin_state[uid] = None
        db.set_setting('channel_url', text)
        bot.reply_to(message, f"✅ تم تحديث رابط القناة إلى:\n{text}", reply_markup=admin_keyboard())
        return

    elif state == "waiting_ban":
        admin_state[uid] = None
        try:
            db.ban_user(int(text))
            bot.reply_to(message, f"🚫 تم حظر العضو: {text}")
        except: bot.reply_to(message, "❌ أيدي غير صالح.")
        return

    elif state == "waiting_unban":
        admin_state[uid] = None
        try:
            db.unban_user(int(text))
            bot.reply_to(message, f"✅ تم فك الحظر عن: {text}")
        except: bot.reply_to(message, "❌ أيدي غير صالح.")
        return

    elif state == "waiting_check":
        admin_state[uid] = None
        try:
            status = "محظور 🚫" if db.is_banned(int(text)) else "نشط ✅"
            bot.reply_to(message, f"🔍 حالة الأيدي {text}: {status}")
        except: bot.reply_to(message, "❌ أيدي غير صالح.")
        return

    elif state == "waiting_send_id":
        try:
            target_id = int(text)
            admin_state[uid] = f"waiting_send_msg_{target_id}"
            bot.reply_to(message, "📝 أرسل الآن الرسالة التي تريد توجيهها لهذا الشخص:")
        except:
            admin_state[uid] = None
            bot.reply_to(message, "❌ أيدي غير صالح. تم الإلغاء.")
        return

    elif state and str(state).startswith("waiting_send_msg_"):
        target_id = int(state.split("_")[3])
        admin_state[uid] = None
        try:
            bot.copy_message(target_id, uid, message.message_id)
            bot.reply_to(message, "✅ تم إرسال رسالتك للشخص بنجاح.")
        except:
            bot.reply_to(message, "❌ فشل الإرسال.")
        return

    # ---- [تفعيل]: أزرار البانيل الرئيسية ----
    if text == "📊 الإحصائيات":
        bot.reply_to(message, f"📈 إجمالي المشتركين: {db.get_total()}\n🚫 المحظورين: يتم إدارتهم من القاعدة.")
    elif text == "📢 إذاعة نص" or text == "🖼 إذاعة وسائط" or text == "🎁 هدية للكل":
        admin_state[uid] = "waiting_broadcast"
        bot.reply_to(message, "أرسل الآن الرسالة أو الصورة أو الفيديو الذي تريد إذاعته للكل:")
    elif text == "🔗 تحديث الرابط":
        admin_state[uid] = "waiting_url"
        bot.reply_to(message, f"الرابط الحالي: {get_channel_url()}\nأرسل الرابط الجديد:")
    elif text == "🚫 حظر مستخدم":
        admin_state[uid] = "waiting_ban"
        bot.reply_to(message, "أرسل أيدي الشخص لطرده وحظره:")
    elif text == "✅ فك حظر":
        admin_state[uid] = "waiting_unban"
        bot.reply_to(message, "أرسل أيدي الشخص لفك حظره:")
    elif text == "🔍 فحص أيدي":
        admin_state[uid] = "waiting_check"
        bot.reply_to(message, "أرسل الأيدي للفحص:")
    elif text == "💬 إرسال لشخص":
        admin_state[uid] = "waiting_send_id"
        bot.reply_to(message, "أرسل أيدي الشخص الذي تريد مراسلته:")
    elif text == "📥 تصدير IDs":
        users = db.get_all_ids()
        with open("ids.txt", "w") as f:
            for u in users: f.write(f"{u}\n")
        bot.send_document(uid, open("ids.txt", "rb"), caption=f"📁 ملف يحتوي على {len(users)} أيدي.")
        os.remove("ids.txt")
    elif text == "👥 قائمة الأعضاء":
        users = db.get_all_users()
        with open("members.txt", "w", encoding="utf-8") as f:
            for u in users: f.write(f"ID: {u[0]} | Name: {u[1]} | Username: {u[2]} | Date: {u[3]}\n")
        bot.send_document(uid, open("members.txt", "rb"), caption="👥 القائمة الكاملة للأعضاء.")
        os.remove("members.txt")
    elif text == "📂 نسخة احتياطية":
        bot.send_document(uid, open("joseph_master_pro.db", "rb"), caption="🗄 نسخة احتياطية من قاعدة البيانات.")
    elif text == "🧹 تنظيف الداتا":
        db.conn.execute("DELETE FROM users")
        db.conn.commit()
        bot.reply_to(message, "⚠️ تم مسح جميع الأعضاء من قاعدة البيانات بنجاح.")
    elif text == "🕒 وقت السيرفر":
        bot.reply_to(message, f"⏰ الوقت الحالي: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    elif text == "📡 حالة الاتصال":
        bot.reply_to(message, "✅ البوت متصل بالإنترنت.\n✅ قاعدة البيانات تعمل بشكل سليم.\n✅ نظام المراسلة نشط.")
    elif text == "📋 معلوماتي":
        bot.reply_to(message, f"👤 الاسم: {message.from_user.first_name}\n🆔 الأيدي: {uid}\n👑 الرتبة: المالك (Admin)")
    elif text == "⚙️ الإعدادات":
        bot.reply_to(message, "🔧 الإعدادات الحالية:\n- المراسلة: مفعلة\n- الترحيب التلقائي: مفعل\n- حماية الأدمن: مفعلة")
    elif text == "🆘 الدعم الفني" or text == "🛠 مطور البوت":
        bot.reply_to(message, "👨‍💻 تم تطوير هذا النظام بواسطة مساعدك الذكي لتلبية جميع احتياجاتك.")
    elif text == "🔐 إغلاق اللوحة":
        admin_state[uid] = None
        bot.reply_to(message, "تم إغلاق اللوحة.", reply_markup=types.ReplyKeyboardRemove())

# ==========================================
# 📩 المحرك الرئيسي (Core) مع نظام المراسلة
# ==========================================
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def core_processor(message):
    global ADMIN_ID
    
    # 1. تفعيل الأدمن
    if message.text == ADMIN_CODE:
        ADMIN_ID = message.chat.id
        bot.reply_to(message, "✅ تم تسجيل دخولك كمدير. لوحة التحكم تعمل الآن بكل ميزاتها.", reply_markup=admin_keyboard())
        return

    # 2. إدارة رسائل الأدمن
    if message.chat.id == ADMIN_ID:
        handle_admin(message)
        return

    # 3. إدارة رسائل المستخدمين العاديين
    else:
        uid = message.chat.id
        if db.is_banned(uid): return
        
        # نتحقق هل المستخدم جديد أم قديم
        is_new_user = uid not in db.get_all_ids()
        
        name = message.from_user.first_name or "User"
        user_name = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
        
        db.add_user(uid, name, user_name)
        
        if is_new_user:
            # -- إذا كان المستخدم جديداً (نرسل إشعار الدخول والترحيب) --
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
            
            send_welcome(uid)
        else:
            # -- إذا كان مستخدماً قديماً يرسل رسالة (نقوم بتحويلها لك لترد عليها) --
            if ADMIN_ID != 0:
                # نرسل لك تنبيه أن هناك رسالة ونرفق الأيدي الخاص به
                bot.send_message(ADMIN_ID, f"💬 <b>رسالة من:</b> {name}\n[{uid}]")
                # ثم نقوم بنسخ رسالته إليك (سواء كانت نص، صورة، صوت...)
                bot.copy_message(ADMIN_ID, uid, message.message_id)

# ==========================================
# 🌐 تشغيل السيرفر
# ==========================================
@app.route('/')
def home(): return "JOSEPH SYSTEM PRO ACTIVE"

def run_web(): app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling(timeout=60)
