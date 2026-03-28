import telebot
import sqlite3
import os
import re
from flask import Flask
from threading import Thread
from telebot import types
from datetime import datetime

# ==========================================
# ⚙️ الإعدادات (تأكد من الأيدي ديالك)
# ==========================================
API_TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554 # الأيدي ديالك
ADMIN_CODE = "7779900009" # كود اللوحة
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk" #

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
app = Flask('')

# ==========================================
# 📊 نظام قاعدة البيانات
# ==========================================
class Database:
    def __init__(self, db_name="joseph_final.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
        self.conn.commit()

    def add_user(self, uid):
        self.conn.execute("INSERT OR IGNORE INTO users VALUES (?)", (uid,))
        self.conn.commit()

    def get_total(self):
        return self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

db = Database()

# ==========================================
# 🛠️ دالة الترحيب الرسمية
# ==========================================
def send_welcome_msg(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL)) #
    text = (
        "<b>Welcome to JOSEPH FIXED MATCHES</b> ⚽️\n\n"
        "To get today's 100% GUARANTEED &amp; SECURE fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 <b>Click the button below to join:</b>"
    ) #
    try:
        bot.send_message(chat_id, text, reply_markup=markup)
        return True
    except:
        return False

# ==========================================
# 🤖 معالجة الرسائل (التعديل الجديد)
# ==========================================

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'voice'])
def handle_all_messages(message):
    uid = message.chat.id
    text = message.text if message.text else ""

    # 1. إذا كان المرسل هو الأدمن (نتا)
    if uid == ADMIN_ID:
        # تفعيل اللوحة بالكود
        if text == ADMIN_CODE:
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            markup.add("📊 الإحصائيات", "🔐 إغلاق اللوحة")
            bot.reply_to(message, "✅ <b>مرحباً بك يا زعيم!</b> تم تفعيل وضع التحكم الكامل.", reply_markup=markup) #
            return

        # نظام "الصيد" - تحويل الإشعارات
        if "الايدي :" in text:
            match = re.search(r'الايدي\s*:\s*(\d+)', text) #
            if match:
                target_id = match.group(1)
                if send_welcome_msg(target_id):
                    bot.reply_to(message, f"🚀 <b>تم الإرسال بنجاح!</b> للأيدي: <code>{target_id}</code>") #
                else:
                    bot.reply_to(message, f"❌ <b>فشل الإرسال!</b> المستخدم <code>{target_id}</code> حظر البوت.") #
            return

        # أوامر اللوحة
        if text == "📊 الإحصائيات":
            bot.reply_to(message, f"📈 عدد الأعضاء: <b>{db.get_total()}</b>")
        return # الأدمن ما كيوصلوش الترحيب العادي أبداً

    # 2. إذا كان المرسل مستخدم عادي (ماشي نتا)
    else:
        db.add_user(uid)
        total = db.get_total()
        
        # إرسال الترحيب للعضو الجديد
        send_welcome_msg(uid)
        
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
# 🌐 الحفاظ على التشغيل
# ==========================================
@app.route('/')
def home(): return "JOSEPH BOT ACTIVE 🟢"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(skip_pending=True)
