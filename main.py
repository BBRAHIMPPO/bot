import telebot
import sqlite3
import os
from flask import Flask
from threading import Thread
from telebot import types

# --- Configuration ---
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_lg"
ADMIN_SECRET_CODE = "0718991554"  # الكود اللي كيعرف بيه البوت باللي أنت هو الأدمن
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(TOKEN)
current_admin_id = 718991554 # الأيدي الافتراضي

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    cursor.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
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

# --- Flask Server ---
app = Flask('')
@app.route('/')
def home(): return "JOSEPH FIXED BOT IS LIVE"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

# --- Promo Message Function ---
def send_promo_msg(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL)
    markup.add(btn)
    
    promo_text = (
        "Welcome to **JOSEPH FIXED MATCHES** ⚽️\n\n"
        "To get today's **100% GUARANTEED & SECURE** fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 Click the button below to join:"
    )
    bot.send_message(chat_id, promo_text, reply_markup=markup, parse_mode="Markdown")

# --- Message Handler ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'voice'])
def handle_all_messages(message):
    global current_admin_id
    user_id = message.from_user.id
    text = message.text if message.text else ""

    # 1. التحقق من كود الأدمن السري
    if text == ADMIN_SECRET_CODE:
        current_admin_id = user_id
        bot.reply_to(message, "✅ **تم تفعيل وضع الأدمن بنجاح!**\n\nدابا أي حاجة صيفطوها الناس غتوصلك هنا.\n\nأوامر التحكم:\n/users - عدد المستخدمين\n/export - سحب قائمة IDs")
        return

    # 2. إذا كان المرسل هو الأدمن الحالي
    if user_id == current_admin_id:
        if text == "/users":
            count = len(get_all_users())
            bot.reply_to(message, f"📊 عدد المستخدمين: {count}")
        elif text == "/export":
            users = get_all_users()
            with open("ids.txt", "w") as f:
                for u in users: f.write(f"{u}\n")
            with open("ids.txt", "rb") as f:
                bot.send_document(user_id, f, caption="📄 قائمة الأيديات.")
            os.remove("ids.txt")
        return

    # 3. للمستخدمين العاديين
    add_user(user_id)
    # توجيه الرسالة للأدمن
    try:
        info = f"👤 من: {message.from_user.first_name}\n🆔 ID: `{user_id}`\n---"
        bot.send_message(current_admin_id, info, parse_mode="Markdown")
        bot.forward_message(current_admin_id, message.chat.id, message.message_id)
    except:
        pass
    
    # الرد التلقائي بالاشتراك
    send_promo_msg(user_id)

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling()
