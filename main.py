import telebot
import sqlite3
import os
import time
import re
import logging
from flask import Flask
from threading import Thread
from telebot import types
from datetime import datetime

# ==========================================
# ⚙️ الإعدادات الأساسية
# ==========================================
API_TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554  # أيدي الأدمن الخاص بك
ADMIN_CODE = "0718991554" # كود الدخول للوحة
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk" # رابط القناة

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
app = Flask('')

# ==========================================
# 📊 نظام قاعدة البيانات المتطور
# ==========================================
class Database:
    def __init__(self, db_name="joseph_master.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                          (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, join_date TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
        cursor.execute("INSERT OR IGNORE INTO settings VALUES ('channel_link', ?)", (CHANNEL_URL,))
        self.conn.commit()

    def add_user(self, uid, name, user):
        cursor = self.conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", (uid, name, user, date))
        self.conn.commit()

    def get_stats(self):
        cursor = self.conn.cursor()
        return cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]

db = Database()

# ==========================================
# 🛠️ الدوال الذكية
# ==========================================

def get_welcome_markup():
    url = db.conn.execute("SELECT value FROM settings WHERE key='channel_link'").fetchone()[0]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=url)) #
    return markup

def send_welcome(chat_id):
    """إرسال الرسالة الترحيبية الرسمية كما في الصورة"""
    text = (
        "<b>Welcome to JOSEPH FIXED MATCHES</b> ⚽️\n\n" #
        "To get today's 100% GUARANTEED &amp; SECURE fixed scores, " #
        "you must join our official channel first!\n\n" #
        "👇 <b>Click the button below to join:</b>" #
    )
    try:
        bot.send_message(chat_id, text, reply_markup=get_welcome_markup())
        return True
    except: return False

# ==========================================
# 🛂 لوحة التحكم (10 ميزات +)
# ==========================================

def admin_panel():
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add("📊 إحصائيات دقيقة", "📢 إذاعة نصية", "🖼 إذاعة صورة")
    markup.add("📥 تصدير الأيديات", "🔗 تحديث الرابط", "🔎 فحص مستخدم")
    markup.add("🚫 حظر عام", "✅ فك الحظر", "🛠 حالة النظام")
    markup.add("📝 رسالة مخصصة", "🧹 تنظيف الداتا", "🔐 خروج")
    return markup

# ==========================================
# 🤖 المعالجة الرئيسية (Core Logic)
# ==========================================

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'voice'])
def main_processor(message):
    uid = message.chat.id
    name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
    text = message.text if message.text else ""

    # 1. دخول الأدمن بالكود
    if text == ADMIN_CODE:
        bot.reply_to(message, "✅ <b>مرحباً بك يا زعيم!</b> تم تفعيل وضع التحكم الكامل.", reply_markup=admin_panel())
        return

    # 2. ميزة "الصيد الذكي" للأدمن فقط
    # إذا أرسل الأدمن رسالة الإشعار، البوت يرسل الترحيب لصاحب الأيدي فوراً
    if uid == ADMIN_ID and "الايدي :" in text:
        match = re.search(r'الايدي\s*:\s*(\d+)', text) # استخراج الأيدي من نص الإشعار
        if match:
            target_id = match.group(1)
            if send_welcome(target_id):
                bot.reply_to(message, f"🚀 <b>تم الإرسال بنجاح!</b>\nتم إرسال رسالة الترحيب إلى الأيدي: <code>{target_id}</code>")
            else:
                bot.reply_to(message, "❌ فشل الإرسال (ربما حظر البوت).")
        return

    # 3. إشعار دخول عضو جديد (للأدمن فقط ولغير الأدمن)
    if uid != ADMIN_ID:
        # لا نرسل الإشعار إذا كان الداخل هو الأدمن نفسه
        db.add_user(uid, name, username)
        stats = db.get_stats()
        
        # إرسال إشعار للأدمن عن العضو الجديد
        notify = (
            "تم دخول شخص جديد إلى البوت الخاص بك 👾\n" #
            "-----------------------\n"
            "• معلومات العضو الجديد .\n\n" #
            f"• الاسم : {name}\n" #
            f"• معرف : {username}\n" #
            f"• الايدي : {uid}\n" #
            "-----------------------\n"
            f"• عدد الأعضاء الكلي : {stats}" #
        )
        bot.send_message(ADMIN_ID, notify)
        
        # الرد التلقائي على العضو بالترحيب
        send_welcome(uid)

    # 4. أوامر لوحة التحكم (للأدمن)
    if uid == ADMIN_ID:
        if text == "📊 إحصائيات دقيقة":
            bot.reply_to(message, f"📈 <b>عدد الأعضاء الحالي:</b> {db.get_stats()}")
        elif text == "📥 تصدير الأيديات":
            cursor = db.conn.cursor()
            users = cursor.execute("SELECT user_id FROM users").fetchall()
            with open("users.txt", "w") as f:
                for u in users: f.write(f"{u[0]}\n")
            bot.send_document(ADMIN_ID, open("users.txt", "rb"), caption="✅ قائمة الأيديات المسجلة.")
            os.remove("users.txt")
        elif text == "🔐 خروج":
            bot.reply_to(message, "تم إغلاق لوحة التحكم.", reply_markup=types.ReplyKeyboardRemove())

# ==========================================
# 🌐 تشغيل السيرفر والبوت
# ==========================================

@app.route('/')
def home(): return "JOSEPH SYSTEM IS ONLINE 🟢"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

if __name__ == "__main__":
    keep_alive()
    print("Bot is starting...")
    bot.infinity_polling(skip_pending=True)
