import telebot
import sqlite3
import os
import re
import time
import logging
from flask import Flask
from threading import Thread
from telebot import types
from datetime import datetime

# ==========================================
# ⚙️ الإعدادات الأساسية
# ==========================================
API_TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554 
ADMIN_CODE = "7779900009" # كود تفعيل اللوحة
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
app = Flask('')

# ==========================================
# 📊 نظام قاعدة البيانات (للحفاظ على الداتا)
# ==========================================
class Database:
    def __init__(self, db_name="joseph_master_pro.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                          (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, date TEXT)''')
        self.conn.commit()

    def add_user(self, uid, name, user):
        cursor = self.conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", (uid, name, user, now))
        self.conn.commit()

    def get_total(self):
        return self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

db = Database()

# ==========================================
# 🛠️ المهام الذكية والترحيب
# ==========================================

def get_welcome_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL))
    return markup

def send_welcome(chat_id):
    """الرسالة الترحيبية الرسمية المطابقة لصورك"""
    text = (
        "<b>Welcome to JOSEPH FIXED MATCHES</b> ⚽️\n\n"
        "To get today's 100% GUARANTEED &amp; SECURE fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 <b>Click the button below to join:</b>"
    )
    try:
        bot.send_message(chat_id, text, reply_markup=get_welcome_markup())
        return True
    except:
        return False

def admin_keyboard():
    """لوحة التحكم الشاملة (12 خيار)"""
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add("📊 الإحصائيات", "📢 إذاعة للكل", "🖼 إذاعة صورة")
    markup.add("📥 تصدير الأيديات", "🔗 تحديث الرابط", "🚫 حظر مستخدم")
    markup.add("✅ فك حظر", "🔍 فحص أيدي", "⚙️ الإعدادات")
    markup.add("🛡 الحماية", "🧹 تنظيف الداتا", "🔐 إغلاق اللوحة")
    return markup

# ==========================================
# 🤖 معالجة الرسائل والذكاء الاصطناعي للبوت
# ==========================================

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'voice'])
def core_processor(message):
    uid = message.chat.id
    name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
    text = message.text if message.text else ""

    # 1. تفعيل لوحة التحكم بالكود السري
    if text == ADMIN_CODE:
        bot.reply_to(message, "✅ <b>Welcome Boss!</b>\nتم تفعيل نظام التحكم الكامل.", reply_markup=admin_keyboard())
        return

    # 2. نظام "الصيد" والرد التلقائي (خاص بالأدمن فقط)
    if uid == ADMIN_ID and "الايدي :" in text:
        match = re.search(r'الايدي\s*:\s*(\d+)', text) # استخراج الأيدي من نص الإشعار
        if match:
            target_id = match.group(1)
            # إرسال الترحيب للشخص المستهدف
            if send_welcome(target_id):
                # تقرير النجاح للأدمن
                bot.reply_to(message, f"🚀 <b>تم الإرسال بنجاح!</b>\nإلى صاحب الأيدي: <code>{target_id}</code>\n<i>(تم تزويده برابط القناة)</i>")
            else:
                # تقرير الفشل للأدمن
                bot.reply_to(message, f"❌ <b>فشل في الإرسال!</b>\nالأيدي: <code>{target_id}</code>\n<i>(المستخدم غالباً قام بحظر البوت)</i>")
        return

    # 3. نظام الإشعارات (للناس العاديين فقط - حماية الأدمن)
    if uid != ADMIN_ID:
        db.add_user(uid, name, username)
        total = db.get_total()
        
        # إشعار للأدمن عن العضو الجديد
        notify = (
            "تم دخول شخص جديد إلى البوت الخاص بك 👾\n"
            "-----------------------\n"
            "• معلومات العضو الجديد .\n\n"
            f"• الاسم : {name}\n"
            f"• معرف : {username}\n"
            f"• الايدي : {uid}\n"
            "-----------------------\n"
            f"• عدد الأعضاء الكلي : {total}"
        )
        bot.send_message(ADMIN_ID, notify)
        
        # إرسال الترحيب الفوري للعضو الجديد
        send_welcome(uid)

    # 4. أوامر لوحة التحكم (للأدمن)
    if uid == ADMIN_ID:
        if text == "📊 الإحصائيات":
            bot.reply_to(message, f"📈 إجمالي الأعضاء المسجلين: <b>{db.get_total()}</b>")
        elif text == "📥 تصدير الأيديات":
            conn = sqlite3.connect("joseph_master_pro.db")
            users = conn.execute("SELECT user_id FROM users").fetchall()
            with open("users_list.txt", "w") as f:
                for u in users: f.write(f"{u[0]}\n")
            bot.send_document(ADMIN_ID, open("users_list.txt", "rb"), caption="✅ قائمة الأيديات كاملة.")
            os.remove("users_list.txt")
        elif text == "🔐 إغلاق اللوحة":
            bot.reply_to(message, "تم إغلاق لوحة التحكم.", reply_markup=types.ReplyKeyboardRemove())

# ==========================================
# 🌐 الحفاظ على استمرارية البوت (Keep Alive)
# ==========================================
@app.route('/')
def home(): return "JOSEPH MASTER SYSTEM: ACTIVE 🟢"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

if __name__ == "__main__":
    keep_alive()
    print("Joseph Master Pro is starting...")
    bot.infinity_polling(skip_pending=True)
