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
ADMIN_ID = 999
ADMIN_CODE = "999"
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
app = Flask('')

admin_state = {}

# ==========================================
# 📊 قاعدة البيانات
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
# 🛠️ دوال مساعدة
# ==========================================
def get_channel_url():
    return db.get_setting('channel_url') or CHANNEL_URL

def get_welcome_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=get_channel_url()))
    return markup

def send_welcome(chat_id):
    text = (
        "<b>Welcome to JOSEPH FIXED MATCHES</b> ⚽️\n\n"
        "To get today's 100% GUARANTEED &amp; SECURE fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 <b>Click the button below to join:</b>"
    )
    try:
        bot.send_message(int(chat_id), text, reply_markup=get_welcome_markup())
        return True
    except Exception as e:
        print(f"send_welcome error for {chat_id}: {e}")
        return False

def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add("📊 الإحصائيات", "📢 إذاعة للكل", "🖼 إذاعة صورة")
    markup.add("📥 تصدير الأيديات", "🔗 تحديث الرابط", "🚫 حظر مستخدم")
    markup.add("✅ فك حظر", "🔍 فحص أيدي", "👥 قائمة الأعضاء")
    markup.add("🧹 تنظيف الداتا", "📋 نسخ اليد", "🔐 إغلاق اللوحة")
    return markup

# ==========================================
# 🤖 معالجة رسائل الأدمن
# ==========================================
def handle_admin(message):
    global admin_state
    uid = message.chat.id
    text = message.text if message.text else ""

    if text == ADMIN_CODE:
        admin_state[uid] = None
        bot.reply_to(message, "✅ <b>Welcome Boss!</b>\nتم تفعيل نظام التحكم الكامل.", reply_markup=admin_keyboard())
        return

    state = admin_state.get(uid)

    if state == "waiting_broadcast_text":
        admin_state[uid] = None
        users = db.get_all_ids()
        success, fail = 0, 0
        bot.reply_to(message, f"⏳ جاري الإذاعة لـ <b>{len(users)}</b> عضو...")
        for user_id in users:
            try:
                bot.copy_message(user_id, uid, message.message_id)
                success += 1
                time.sleep(0.05)
            except:
                fail += 1
        bot.send_message(uid, f"✅ <b>انتهت الإذاعة</b>\n✔️ وصلت: {success}\n❌ فشلت: {fail}", reply_markup=admin_keyboard())
        return

    if state == "waiting_photo_broadcast":
        admin_state[uid] = None
        if message.photo or message.document or message.video:
            users = db.get_all_ids()
            success, fail = 0, 0
            bot.reply_to(message, f"⏳ جاري إرسال الوسائط لـ <b>{len(users)}</b> عضو...")
            for user_id in users:
                try:
                    bot.copy_message(user_id, uid, message.message_id)
                    success += 1
                    time.sleep(0.05)
                except:
                    fail += 1
            bot.send_message(uid, f"✅ <b>انتهت الإذاعة</b>\n✔️ وصلت: {success}\n❌ فشلت: {fail}", reply_markup=admin_keyboard())
        else:
            bot.reply_to(message, "⚠️ أرسل صورة أو فيديو أو ملف.")
        return

    if state == "waiting_ban_id":
        admin_state[uid] = None
        try:
            target = int(text.strip())
            db.ban_user(target)
            bot.reply_to(message, f"🚫 تم حظر <code>{target}</code> بنجاح.", reply_markup=admin_keyboard())
        except:
            bot.reply_to(message, "⚠️ أيدي غير صحيح.", reply_markup=admin_keyboard())
        return

    if state == "waiting_unban_id":
        admin_state[uid] = None
        try:
            target = int(text.strip())
            db.unban_user(target)
            bot.reply_to(message, f"✅ تم فك حظر <code>{target}</code> بنجاح.", reply_markup=admin_keyboard())
        except:
            bot.reply_to(message, "⚠️ أيدي غير صحيح.", reply_markup=admin_keyboard())
        return

    if state == "waiting_check_id":
        admin_state[uid] = None
        try:
            target = int(text.strip())
            banned = db.is_banned(target)
            status = "🚫 محظور" if banned else "✅ نشط"
            bot.reply_to(message, f"🔍 الأيدي: <code>{target}</code>\nالحالة: {status}", reply_markup=admin_keyboard())
        except:
            bot.reply_to(message, "⚠️ أيدي غير صحيح.", reply_markup=admin_keyboard())
        return

    if state == "waiting_new_url":
        admin_state[uid] = None
        new_url = text.strip()
        db.set_setting('channel_url', new_url)
        bot.reply_to(message, f"✅ تم تحديث رابط القناة:\n{new_url}", reply_markup=admin_keyboard())
        return

    # 🔁 الصيد التلقائي
    if "الايدي :" in text or "الايدي:" in text:
        ids_found = re.findall(r'الايدي\s*:\s*(\d+)', text)
        if ids_found:
            results = []
            for target_id in ids_found:
                bot.send_chat_action(uid, 'typing')
                if send_welcome(target_id):
                    results.append(f"✅ <code>{target_id}</code> — تم الإرسال")
                else:
                    results.append(f"❌ <code>{target_id}</code> — فشل")
            bot.reply_to(message, "\n".join(results))
        else:
            bot.reply_to(message, "⚠️ ملقيتش الأيدي فهاد الرسالة.")
        return

    if text == "📊 الإحصائيات":
        bot.reply_to(message, f"📈 <b>إحصائيات البوت</b>\n\n👥 إجمالي الأعضاء: <b>{db.get_total()}</b>")
    elif text == "📢 إذاعة للكل":
        admin_state[uid] = "waiting_broadcast_text"
        bot.reply_to(message, "✏️ أرسل الرسالة اللي بغيتي تذيعها للكل:")
    elif text == "🖼 إذاعة صورة":
        admin_state[uid] = "waiting_photo_broadcast"
        bot.reply_to(message, "🖼 أرسل الصورة أو الفيديو أو الملف:")
    elif text == "📥 تصدير الأيديات":
        users = db.get_all_ids()
        with open("users_list.txt", "w") as f:
            for u in users: f.write(f"{u}\n")
        with open("users_list.txt", "rb") as f:
            bot.send_document(uid, f, caption=f"✅ قائمة الأيديات — {len(users)} عضو.")
        os.remove("users_list.txt")
    elif text == "👥 قائمة الأعضاء":
        users = db.get_all_users()
        with open("members_full.txt", "w", encoding="utf-8") as f:
            f.write(f"قائمة الأعضاء — {len(users)} عضو\n{'='*40}\n")
            for u in users:
                f.write(f"الأيدي: {u[0]} | الاسم: {u[1]} | معرف: {u[2]} | تاريخ: {u[3]}\n")
        with open("members_full.txt", "rb") as f:
            bot.send_document(uid, f, caption=f"👥 قائمة كاملة بـ {len(users)} عضو.")
        os.remove("members_full.txt")
    elif text == "🔗 تحديث الرابط":
        admin_state[uid] = "waiting_new_url"
        bot.reply_to(message, f"🔗 الرابط الحالي:\n<code>{get_channel_url()}</code>\n\nأرسل الرابط الجديد:")
    elif text == "🚫 حظر مستخدم":
        admin_state[uid] = "waiting_ban_id"
        bot.reply_to(message, "🚫 أرسل الأيدي اللي بغيتي تحظره:")
    elif text == "✅ فك حظر":
        admin_state[uid] = "waiting_unban_id"
        bot.reply_to(message, "✅ أرسل الأيدي اللي بغيتي تفك حظره:")
    elif text == "🔍 فحص أيدي":
        admin_state[uid] = "waiting_check_id"
        bot.reply_to(message, "🔍 أرسل الأيدي اللي بغيتي تفحصه:")
    elif text == "🧹 تنظيف الداتا":
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("⚠️ تأكيد الحذف", callback_data="confirm_clean"),
            types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_clean")
        )
        bot.reply_to(message, "⚠️ <b>تحذير!</b> غادي يمسح جميع بيانات الأعضاء.\nواش متأكد؟", reply_markup=markup)
    elif text == "🔐 إغلاق اللوحة":
        admin_state[uid] = None
        bot.reply_to(message, "🔐 تم إغلاق لوحة التحكم.", reply_markup=types.ReplyKeyboardRemove())

# ==========================================
# 🤖 معالجة رسائل المستخدمين
# ==========================================
def handle_user(message):
    uid = message.chat.id
    name = message.from_user.first_name or "بدون اسم"
    username = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
    if db.is_banned(uid):
        return
    db.add_user(uid, name, username)
    total = db.get_total()
    notify = (
        "تم دخول شخص جديد إلى البوت الخاص بك 👾\n"
        "-----------------------\n"
        f"• الاسم : {name}\n"
        f"• معرف : {username}\n"
        f"• الايدي : {uid}\n"
        "-----------------------\n"
        f"• عدد الأعضاء الكلي : {total}"
    )
    try:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"🚀 إرسال ترحيب لـ {uid}", callback_data=f"welcome_{uid}"))
        bot.send_message(ADMIN_ID, notify, reply_markup=markup)
    except:
        pass
    send_welcome(uid)

# ==========================================
# 📩 الهاندلر الرئيسي
# ==========================================
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'voice', 'audio', 'sticker'])
def core_processor(message):
    if message.chat.id == ADMIN_ID:
        handle_admin(message)
    else:
        handle_user(message)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    uid = call.message.chat.id
    if call.data.startswith("welcome_") and uid == ADMIN_ID:
        target_id = call.data.split("_")[1]
        if send_welcome(target_id):
            bot.answer_callback_query(call.id, f"✅ تم إرسال الترحيب لـ {target_id}")
            bot.edit_message_reply_markup(uid, call.message.message_id, reply_markup=None)
        else:
            bot.answer_callback_query(call.id, f"❌ فشل الإرسال لـ {target_id}")
    elif call.data == "confirm_clean" and uid == ADMIN_ID:
        db.conn.execute("DELETE FROM users")
        db.conn.commit()
        bot.answer_callback_query(call.id, "✅ تم مسح الداتا")
        bot.edit_message_text("✅ تم تنظيف قاعدة البيانات بنجاح.", uid, call.message.message_id)
    elif call.data == "cancel_clean" and uid == ADMIN_ID:
        bot.answer_callback_query(call.id, "تم الإلغاء")
        bot.edit_message_text("❌ تم إلغاء العملية.", uid, call.message.message_id)

# ==========================================
# 🌐 Keep Alive
# ==========================================
@app.route('/')
def home():
    return "JOSEPH MASTER SYSTEM: ACTIVE 🟢"

def run():
    app.run(host='0.0.0.0', port=9000)

def keep_alive():
    Thread(target=run).start()

if __name__ == "__main__":
    keep_alive()
    print("Joseph Master Pro is starting...")
    try:
        bot.delete_webhook(drop_pending_updates=True)
        print("Webhook cleared.")
    except Exception as e:
        print(f"Webhook clear error: {e}")
    print("Waiting 35s for old sessions to expire...")
    time.sleep(35)
    print("Starting polling...")
    while True:
        try:
            bot.infinity_polling(skip_pending=False, timeout=30, long_polling_timeout=30)
        except Exception as e:
            print(f"Polling error: {e} — restarting in 30 seconds...")
            time.sleep(30)
