import telebot
import sqlite3
import os
import time
import re # مكتبة البحث عن الأرقام ف النص
from flask import Flask
from threading import Thread
from telebot import types

# --- الإعدادات ---
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554 
ADMIN_SECRET_CODE = "7779900009"
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('joseph_shadow.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT)')
    conn.commit()
    conn.close()

def get_all_ids():
    conn = sqlite3.connect('joseph_shadow.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    ids = [r[0] for r in cursor.fetchall()]
    conn.close()
    return ids

# --- الأزرار ---
def admin_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📊 الإحصائيات", "📢 إرسال للكل (1000+)", "📥 نسخة احتياطية")
    return markup

# --- رسالة الترحيب الاحترافية ---
def send_welcome_to_user(target_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL))
    welcome_text = (
        "Welcome to **JOSEPH FIXED MATCHES** ⚽️\n\n"
        "To get today's **100% GUARANTEED** scores, "
        "join our official channel now!"
    )
    try:
        bot.send_message(target_id, welcome_text, reply_markup=markup, parse_mode="Markdown")
        return True
    except: return False

# --- السيرفر ---
@app.route('/')
def home(): return "JOSEPH SYSTEM: ACTIVE"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

# --- معالجة الرسائل ---

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document'])
def master_handler(message):
    user_id = message.from_user.id
    text = message.text if message.text else ""

    # 1. تفعيل الأدمن
    if text == ADMIN_SECRET_CODE:
        bot.reply_to(message, "✅ وضع التحكم الكامل مفعل.", reply_markup=admin_menu())
        return

    # 2. ميزة "التحويل الذكي" (Smart Forward)
    # إذا حولتي للبوت ميساج فيه "الايدي : "
    if user_id == ADMIN_ID and "الايدي :" in text:
        # البحث عن رقم الأيدي وسط النص باستعمال Regex
        match = re.search(r'الايدي\s*:\s*(\d+)', text)
        if match:
            target_user_id = match.group(1)
            if send_welcome_to_user(target_user_id):
                bot.reply_to(message, f"✅ تم إرسال رسالة الترحيب بنجاح لـ `{target_user_id}`")
            else:
                bot.reply_to(message, "❌ فشل الإرسال (غالباً الشخص بلوكا البوت)")
        return

    # 3. أوامر الأدمن العادية
    if user_id == ADMIN_ID:
        if text == "📢 إرسال للكل (1000+)":
            m = bot.reply_to(message, "صيفط دبا الميساج اللي بغيتي تفرقو على كاع الناس:")
            bot.register_next_step_handler(m, broadcast_to_1000)
            return
        elif text == "📊 الإحصائيات":
            bot.reply_to(message, f"📈 عدد الأعضاء: {len(get_all_ids())}")
            return

    # 4. للمستخدمين العاديين
    # (هنا كيدير البوت الخدمة العادية ديالو فـ الخفاء)
    send_welcome_to_user(user_id)

def broadcast_to_1000(message):
    ids = get_all_ids()
    sent = 0
    bot.send_message(ADMIN_ID, f"🚀 جاري الإرسال لـ {len(ids)} شخص...")
    for uid in ids:
        try:
            bot.copy_message(uid, message.chat.id, message.message_id)
            sent += 1
            if sent % 30 == 0: time.sleep(1) # تبريد باش ما يتبلوكاش البوت
        except: pass
    bot.send_message(ADMIN_ID, f"✅ المهمة تمت! وصل لـ {sent} واحد.")

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling(skip_pending=False)
