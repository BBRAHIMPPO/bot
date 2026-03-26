import telebot
import sqlite3
import os
from flask import Flask
from threading import Thread
from telebot import types

# --- الإعدادات (Settings) ---
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qB"
ADMIN_ID = 718991554  # الأيدي الجديد ديالك
CHANNEL_USERNAME = "@YourChannelUsername" # ضروري تبدلها بيوزر قناتك باش يخدم القفل
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(TOKEN)

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()
    return [str(u[0]) for u in users]

# --- التحقق من الاشتراك ---
def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# --- Flask Server (لثبات البوت على Render) ---
app = Flask('')
@app.route('/')
def home(): return "JOSEPH FIXED IS RUNNING"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

# --- واجهة المستخدم (ENGLISH) ---
@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.from_user.id
    add_user(user_id)
    
    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("JOIN CHANNEL NOW 📢", url=CHANNEL_URL)
        markup.add(btn)
        msg = (
            "Welcome to **JOSEPH FIXED MATCHES** ⚽️\n\n"
            "To get today's **100% GUARANTEED** fixed scores, "
            "you must join our official channel first!\n\n"
            "👇 Click the button below:"
        )
        bot.send_message(user_id, msg, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(user_id, "✅ **Access Granted!**\n\nSend the match name to get the fixed score.", parse_mode="Markdown")

# --- واجهة الأدمن (العربية) ---
@bot.message_handler(commands=['admin', 'users'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        count = len(get_all_users())
        bot.reply_to(message, f"📊 **لوحة التحكم**\n\nعدد المستخدمين: {count}\n\nصيفط /export باش تاخد الملف.")

@bot.message_handler(commands=['export'])
def export_ids(message):
    if message.from_user.id == ADMIN_ID:
        users = get_all_users()
        with open("ids.txt", "w") as f:
            for u in users: f.write(f"{u}\n")
        with open("ids.txt", "rb") as f:
            bot.send_document(ADMIN_ID, f, caption="📄 ملف الأيديات.")
        os.remove("ids.txt")

# --- نظام التوجيه (Forwarding) ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'voice'])
def handle_msg(message):
    user_id = message.from_user.id
    add_user(user_id)
    
    if user_id == ADMIN_ID: return

    if check_sub(user_id):
        # التوجيه للأدمن
        info = f"👤 من: {message.from_user.first_name}\n🆔 ID: `{user_id}`\n---"
        bot.send_message(ADMIN_ID, info, parse_mode="Markdown")
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        # رد للمستخدم
        bot.send_message(user_id, "⏳ Your request is being processed...")
    else:
        welcome(message)

# --- تشغيل ---
if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling()
