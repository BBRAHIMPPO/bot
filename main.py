import telebot
import sqlite3
import os
import re
import logging
from Flask import Flask
from threading import Thread
from telebot import types
from datetime import datetime

# ==========================================
# ⚙️ الإعدادات (تأكد من الأيدي ديالك)
# ==========================================
API_TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554 # الأيدي ديالك
ADMIN_CODE = "7779900009" # كود تفعيل اللوحة
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk" # رابط القناة

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
app = Flask('')

# ==========================================
# 📊 نظام قاعدة البيانات
# ==========================================
class Database:
    def __init__(self, db_name="joseph_final.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, date TEXT)''')
        self.conn.commit()

    def add_user(self, uid):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.conn.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (uid, now))
        self.conn.commit()

    def get_total(self):
        return self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def get_all_ids(self):
        users = self.conn.execute("SELECT user_id FROM users").fetchall()
        return [u[0] for u in users]

db = Database()

# ==========================================
# 🛠️ دالة الترحيب الرسمية (JOSEPH FIXED)
# ==========================================
def send_welcome_to_new_user(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL)) #
    
    # النص الترحيبي الرسمي المطابق للصور
    text = (
        "<b>Welcome to JOSEPH FIXED MATCHES</b> ⚽️\n\n"
        "To get today's 100% GUARANTEED &amp; SECURE fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 <b>Click the button below to join:</b>"
    ) #
    
    try:
        bot.send_message(user_id, text, reply_markup=markup)
        return True
    except:
        return False

# ==========================================
# 🤖 معالجة الرسائل والذكاء الاصطناعي للبوت
# ==========================================

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'voice'])
def handle_messages(message):
    uid = message.chat.id
    text = message.text if message.text else ""

    # 1. نظام الأدمن (نتا فقط)
    if uid == ADMIN_ID:
        # تفعيل اللوحة بالكود
        if text == ADMIN_CODE:
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            markup.add("📊 الإحصائيات", "📥 تصدير الأيديات", "🔐 إغلاق اللوحة")
            bot.reply_to(message, "✅ **مرحباً بك يا زعيم!** تم تفعيل نظام التحكم الكامل.", reply_markup=markup) #
            return

        # نظام "الصيد" - استخراج الأيدي والرد
        if "الايدي :" in text:
            # استخراج الرقم باستخدام Regex من الرسالة
            match = re.search(r'الايدي\s*:\s*(\d+)', text)
            if match:
                target_id = match.group(1)
                bot.send_chat_action(ADMIN_ID, 'typing')
                if send_welcome_to_new_user(target_id):
                    # تقرير النجاح للأدمن
                    bot.reply_to(message, f"🚀 <b>تم الإرسال بنجاح!</b> للأيدي: <code>{target_id}</code>")
                else:
                    # تقرير الفشل للأدمن
                    bot.reply_to(message, f"❌ <b>فشل!</b> المستخدم <code>{target_id}</code> مسدود أو حظر البوت.")
            return

        # أوامر لوحة التحكم للأدمن
        if text == "📊 الإحصائيات":
            bot.reply_to(message, f"📈 عدد الأعضاء الكلي في البوت: <b>{db.get_total()}</b>")
        elif text == "📥 تصدير الأيديات":
            conn = sqlite3.connect("joseph_final.db")
            users = conn.execute("SELECT user_id FROM users").fetchall()
            with open("users.txt", "w") as f:
                for u in users: f.write(f"{u[0]}\n")
            bot.send_document(ADMIN_ID, open("users.txt", "rb"), caption="✅ قائمة الأيديات كاملة.")
            os.remove("users.txt")
        elif text == "🔐 إغلاق اللوحة":
            bot.reply_to(message, "تم إغلاق لوحة التحكم.", reply_markup=types.ReplyKeyboardRemove())
        
        return # الأدمن مابيوصلوش ترحيب مكرر

    # 2. نظام المستخدمين (أي واحد صيفط ميساج)
    else:
        db.add_user(uid)
        total = db.get_total()
        
        # إرسال الترحيب فوراً للعضو الجديد
        send_welcome_to_new_user(uid)
        
        # إرسال إشعار للأدمن (فقط ملي يدخل واحد غريب)
        notify = (
            "تم دخول شخص جديد إلى البوت الخاص بك 👾\n"
            "-----------------------\n"
            f"• الاسم : {message.from_user.first_name}\n"
            f"• الايدي : {uid}\n"
            "-----------------------\n"
            f"• عدد الأعضاء الكلي : {total}"
        ) #
        bot.send_message(ADMIN_ID, notify)

# ==========================================
# 🌐 تشغيل السيرفر والبوت (Keep Alive)
# ==========================================
@app.route('/')
def home(): return "JOSEPH BOT ACTIVE 🟢"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(skip_pending=True)
