import telebot
import sqlite3
import os
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
ADMIN_ID = 718991554 # الأيدي ديالك
ADMIN_CODE = "7779900009" # الكود اللي كيبان فالتصاور ديالك
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk" # رابط القناة

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
app = Flask('')

# ==========================================
# 📊 نظام قاعدة البيانات
# ==========================================
class Database:
    def __init__(self, db_name="joseph_pro.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, date_joined TEXT)''')
        self.conn.commit()

    def add_user(self, uid):
        cursor = self.conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (uid, now))
        self.conn.commit()

    def get_total(self):
        return self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

db = Database()

# ==========================================
# 🛠️ المهام الذكية
# ==========================================

def get_welcome_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL)) #
    return markup

def send_welcome(chat_id):
    """الرسالة الترحيبية الرسمية من الصور"""
    text = (
        "<b>Welcome to JOSEPH FIXED MATCHES</b> ⚽️\n\n" #
        "To get today's 100% GUARANTEED &amp; SECURE fixed scores, " #
        "you must join our official channel first!\n\n" #
        "👇 <b>Click the button below to join:</b>" #
    )
    try:
        bot.send_message(chat_id, text, reply_markup=get_welcome_markup())
        return True
    except:
        return False

def admin_keyboard():
    """لوحة التحكم (10 خيارات +)"""
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add("📊 الإحصائيات", "📢 إذاعة للكل", "🖼 إذاعة صورة")
    markup.add("📥 تصدير الأيديات", "🔗 تحديث الرابط", "🚫 حظر مستخدم")
    markup.add("✅ فك حظر", "🔍 فحص أيدي", "⚙️ إعدادات البوت")
    markup.add("🛡 حماية النظام", "🧹 تنظيف الداتا", "🔐 إغلاق اللوحة")
    return markup

# ==========================================
# 🤖 معالجة الرسائل
# ==========================================

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'voice'])
def handle_messages(message):
    uid = message.chat.id
    text = message.text if message.text else ""

    # 1. تفعيل لوحة التحكم بالكود السري
    if text == ADMIN_CODE:
        bot.reply_to(message, "✅ **Welcome Boss!**\nوضع التحكم الكامل مفعل.", reply_markup=admin_keyboard()) #
        return

    # 2. ميزة استخراج الأيدي والرد التلقائي (خاصة بالأدمن)
    if uid == ADMIN_ID and "الايدي :" in text:
        match = re.search(r'الايدي\s*:\s*(\d+)', text) # استخراج الرقم من نص الإشعار
        if match:
            target_id = match.group(1)
            bot.send_chat_action(uid, 'typing')
            if send_welcome(target_id):
                bot.reply_to(message, f"🚀 <b>تم الإرسال بنجاح!</b>\nتم إرسال رسالة الترحيب لصاحب الأيدي: <code>{target_id}</code>") #
            else:
                bot.reply_to(message, f"❌ <b>فشل الإرسال!</b>\nالمستخدم <code>{target_id}</code> قد قام بحظر البوت أو الأيدي خاطئ.") #
        return

    # 3. نظام الإشعارات (للناس العاديين فقط)
    if uid != ADMIN_ID:
        db.add_user(uid)
        total = db.get_total()
        
        # إشعار للأدمن (فقط ملي يدخل شي واحد غريب)
        notify = (
            "تم دخول شخص جديد إلى البوت الخاص بك 👾\n" #
            "-----------------------\n"
            "• معلومات العضو الجديد .\n\n" #
            f"• الاسم : {message.from_user.first_name}\n" #
            f"• معرف : @{message.from_user.username if message.from_user.username else 'لا يوجد'}\n" #
            f"• الايدي : {uid}\n" #
            "-----------------------\n"
            f"• عدد الأعضاء الكلي : {total}" #
        )
        bot.send_message(ADMIN_ID, notify)
        
        # إرسال الترحيب للعضو الجديد
        send_welcome(uid)

    # 4. أوامر لوحة التحكم
    if uid == ADMIN_ID:
        if text == "📊 الإحصائيات":
            bot.reply_to(message, f"📈 عدد الأعضاء الكلي في البوت: <b>{db.get_total()}</b>")
        elif text == "🔐 إغلاق اللوحة":
            bot.reply_to(message, "تم إخلاق اللوحة.", reply_markup=types.ReplyKeyboardRemove())

# ==========================================
# 🌐 تشغيل السيرفر والبوت
# ==========================================
@app.route('/')
def home(): return "JOSEPH BOT ACTIVE 🟢"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

if __name__ == "__main__":
    keep_alive()
    print("Bot is running...")
    bot.infinity_polling()
