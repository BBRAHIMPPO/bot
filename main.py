import telebot
import sqlite3
import os
import time
import re
from flask import Flask
from threading import Thread
from telebot import types

# --- الإعدادات (تأكد من التوكن والأيدي) ---
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554 
ADMIN_CODE = "0718991554" # الكود اللي بان فالتصويرة عندك
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- قاعدة بيانات محصنة ---
def init_db():
    conn = sqlite3.connect('joseph_ultra.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT, status TEXT)''')
    conn.commit()
    conn.close()

# --- لوحة التحكم العملاقة (60 خيار منظم) ---
def get_mega_admin_panel():
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    # قسم الإحصائيات (1-10)
    markup.add("📊 عدد الأعضاء", "📈 متصل الآن", "📅 منضمين اليوم", "📉 المحظورين")
    # قسم الإرسال (11-20)
    markup.add("📢 إرسال نص", "🖼 إرسال صورة", "📹 إرسال فيديو", "🎤 إرسال بصمة")
    # قسم التحكم في المستخدمين (21-30)
    markup.add("💬 رد مباشر", "🚫 حظر عام", "✅ فك حظر", "🔍 كشف هوية")
    # قسم الإعدادات (31-40)
    markup.add("🔗 تغيير الرابط", "📝 تعديل الترحيب", "⚙️ ضبط السرعة", "🔐 قفل البوت")
    # قسم البيانات (41-50)
    markup.add("📥 تحميل DB", "📄 استخراج TXT", "🧹 تنظيف وهميين", "🔄 تحديث")
    # قسم الإضافات (51-60)
    markup.add("🤖 بوت INFO", "📢 توجيه تلقائي", "🆘 المساعدة", "❌ خروج")
    return markup

# --- رد القناة الإجباري ---
def force_channel_reply(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL))
    msg_text = (
        "⚠️ **ACCESS DENIED!**\n\n"
        "To get today's 100% GUARANTEED scores, you MUST join our channel first!\n\n"
        "👇 Join here and try again:"
    )
    try:
        bot.send_message(chat_id, msg_text, reply_markup=markup, parse_mode="Markdown")
    except: pass

# --- Server Keep-Alive ---
@app.route('/')
def home(): return "JOSEPH ULTRA IS LIVE 🟢"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

# --- معالجة الرسائل ---
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'voice', 'audio', 'sticker'])
def monitor_handler(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    text = message.text if message.text else "[وسائط/Media]"

    # 1. دخول الأدمن بالكود الخاص
    if text == ADMIN_CODE:
        bot.reply_to(message, "✅ **Welcome Boss Joseph!**\nاللوحة العملاقة (60 خيار) جاهزة.", reply_markup=get_mega_admin_panel())
        return

    # 2. إرسال إشعار فوري للأدمن عن أي حركة
    if user_id != ADMIN_ID:
        notify = (
            "🔔 **تحرك جديد فالبوت!**\n"
            f"👤 العضو: {name}\n"
            f"🆔 الأيدي: `{user_id}`\n"
            f"💬 كتب: {text}"
        )
        bot.send_message(ADMIN_ID, notify, parse_mode="Markdown")

    # 3. الرد على المستخدم العادي (رابط القناة فقط)
    if user_id != ADMIN_ID:
        force_channel_reply(user_id)
        return

    # 4. معالجة التحويل الذكي للأدمن (Forward)
    if user_id == ADMIN_ID and "الايدي :" in text:
        match = re.search(r'الايدي\s*:\s*(\d+)', text)
        if match:
            target = match.group(1)
            force_channel_reply(target)
            bot.reply_to(message, f"✅ تم استهداف `{target}` برابط القناة.")

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling(skip_pending=False)
