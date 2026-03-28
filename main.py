import telebot
import sqlite3
import os
import re
from flask import Flask  # هادي هي اللي كانت فيها المشكل (f صغيرة)
from threading import Thread
from telebot import types
from datetime import datetime

# ==========================================
# ⚙️ الإعدادات (معلوماتك من الصور)
# ==========================================
API_TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554 
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
app = Flask(__name__)

# ==========================================
# 🛠️ دالة الترحيب الرسمية
# ==========================================
def send_welcome_to_user(target_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL))
    
    text = (
        "<b>Welcome to JOSEPH FIXED MATCHES</b> ⚽️\n\n"
        "To get today's 100% GUARANTEED &amp; SECURE fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 <b>Click the button below to join:</b>"
    )
    try:
        bot.send_message(target_id, text, reply_markup=markup)
        return True
    except:
        return False

# ==========================================
# 🤖 نظام المعالجة الذكي
# ==========================================

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    uid = message.chat.id
    text = message.text if message.text else ""

    # 1. نظام الأدمن (نتا)
    if uid == ADMIN_ID:
        # إرسال مباشر بالأيدي (مثلاً تصيفط: 5077384676)
        if text.isdigit():
            if send_welcome_to_user(text):
                bot.reply_to(message, f"✅ <b>تم الإرسال!</b> للأيدي: <code>{text}</code>")
            else:
                bot.reply_to(message, f"❌ <b>فشل!</b> الأيدي غلط أو المستخدم حظر البوت.")
            return

        # نظام الصيد (تحويل الإشعارات)
        if "الايدي :" in text:
            match = re.search(r'الايدي\s*:\s*(\d+)', text)
            if match:
                target_id = match.group(1)
                if send_welcome_to_user(target_id):
                    bot.reply_to(message, f"🚀 <b>تم بنجاح!</b> صيفت لـ: <code>{target_id}</code>")
                else:
                    bot.reply_to(message, f"❌ <b>فشل!</b>")
            return
        
        return # الأدمن مابيوصلوش ترحيب مكرر

    # 2. نظام المستخدمين
    else:
        send_welcome_to_user(uid)
        notify = f"👾 <b>عضو جديد دخل!</b>\n• الايدي: <code>{uid}</code>"
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
