import telebot
import sqlite3
import os
from flask import Flask
from threading import Thread
from telebot import types

# --- Configuration ---
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_SECRET_CODE = "0718991554" 
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(TOKEN)
current_admin_id = 718991554

# --- Database ---
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
    users = [u[0] for u in cursor.fetchall()]
    conn.close()
    return users

# --- Keyboards (الأزرار) ---
def get_admin_keyboard():
    # هادي هي اللي غاتطلع ليك لتحت بلاصة الكلافي العادية
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("📊 شحال من واحد كاين؟")
    btn2 = types.KeyboardButton("📢 صيفط إعلان للكل")
    btn3 = types.KeyboardButton("📄 جبد ملف IDs")
    btn4 = types.KeyboardButton("🛠 حالة البوت")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

def send_promo(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("JOIN CHANNEL FOR FIXED MATCHES 📢", url=CHANNEL_URL)
    markup.add(btn)
    msg = (
        "Welcome to **JOSEPH FIXED MATCHES** ⚽️\n\n"
        "To get today's **100% GUARANTEED & SECURE** fixed scores, "
        "you must join our official channel first!\n\n"
        "👇 Click the button below to join:"
    )
    bot.send_message(chat_id, msg, reply_markup=markup, parse_mode="Markdown")

# --- Flask for Render ---
app = Flask('')
@app.route('/')
def home(): return "JOSEPH FIXED LIVE"
def run(): app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
def keep_alive(): Thread(target=run).start()

# --- Handlers ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'voice'])
def main_handler(message):
    global current_admin_id
    user_id = message.from_user.id
    text = message.text if message.text else ""

    # تفعيل الأدمن
    if text == ADMIN_SECRET_CODE:
        current_admin_id = user_id
        bot.reply_to(message, "✅ **مرحبا بيك " + message.from_user.first_name + "!**\nتم تفعيل لوحة التحكم بالدارجة. شوف لتحت راه طلعو ليك الأزرار.", reply_markup=get_admin_keyboard())
        return

    # أوامر الأدمن بالأزرار
    if user_id == current_admin_id:
        if text == "📊 شحال من واحد كاين؟":
            count = len(get_all_users())
            bot.reply_to(message, f"📈 عندك {count} واحد فـ البوت دبا.")
        
        elif text == "📄 جبد ملف IDs":
            users = get_all_users()
            with open("users.txt", "w") as f:
                for u in users: f.write(f"{u}\n")
            with open("users.txt", "rb") as f:
                bot.send_document(user_id, f, caption="هاك أخويا ليستة ديال الأيديات.")
            os.remove("users.txt")

        elif text == "📢 صيفط إعلان للكل":
            sent_msg = bot.reply_to(message, "صيفط دبا الميساج اللي بغيتي تفرقو على كاع الناس (نص أو صورة):")
            bot.register_next_step_handler(sent_msg, broadcast_action)
            
        elif text == "🛠 حالة البوت":
            bot.reply_to(message, "✅ البوت ناضي وخدام 24/24.")
        return

    # للمستخدمين العاديين
    add_user(user_id)
    # نظام المراقبة (Forward)
    try:
        header = f"👤 ميساج من: {message.from_user.first_name}\n🆔 ID: `{user_id}`\n---"
        bot.send_message(current_admin_id, header, parse_mode="Markdown")
        bot.forward_message(current_admin_id, message.chat.id, message.message_id)
    except: pass
    
    send_promo(user_id)

def broadcast_action(message):
    users = get_all_users()
    count = 0
    for u_id in users:
        try:
            bot.copy_message(u_id, message.chat.id, message.message_id)
            count += 1
        except: pass
    bot.send_message(current_admin_id, f"✅ تم إرسال الإعلان لـ {count} مستخدم.")

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling()
