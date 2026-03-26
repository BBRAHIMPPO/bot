import telebot
import sqlite3

# Token ديالك
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
bot = telebot.TeleBot(TOKEN)

# كلمة السر باش تولي Admin
ADMIN_CODE = "0718991554"

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('bot_data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS admins (admin_id INTEGER PRIMARY KEY)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    
    # رسالة الترحيب الافتراضية
    c.execute('INSERT OR IGNORE INTO settings (key, value) VALUES ("reply_msg", "Join my official channel now\nhttps://t.me/+wZCOH72-1To3YWFk")')
    conn.commit()
    conn.close()

init_db()

# دوال مساعدة لقاعدة البيانات
def get_admins():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('SELECT admin_id FROM admins')
    admins = [row[0] for row in c.fetchall()]
    conn.close()
    return admins

def is_admin(user_id):
    return user_id in get_admins()

def get_reply_msg():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('SELECT value FROM settings WHERE key="reply_msg"')
    msg = c.fetchone()[0]
    conn.close()
    return msg

def save_user(user_id, username, first_name):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)', (user_id, username, first_name))
        conn.commit()
        is_new = True
    except sqlite3.IntegrityError:
        is_new = False
    conn.close()
    return is_new

# ==========================================
# أوامر التحكم الخاصة بالأدمن (Admin Commands)
# ==========================================

# 1. أمر الإحصائيات
@bot.message_handler(commands=['stats'])
def bot_stats(message):
    if is_admin(message.chat.id):
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM users')
        count = c.fetchone()[0]
        conn.close()
        bot.reply_to(message, f"📊 Total users in bot: {count}")

# 2. أمر تعديل الرسالة الافتراضية
@bot.message_handler(commands=['setreply'])
def set_reply(message):
    if is_admin(message.chat.id):
        msg = bot.reply_to(message, "Send the new reply message you want the bot to use:")
        bot.register_next_step_handler(msg, save_new_reply)

def save_new_reply(message):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('UPDATE settings SET value=? WHERE key="reply_msg"', (message.text,))
    conn.commit()
    conn.close()
    bot.reply_to(message, "✅ Default reply message updated successfully!")

# 3. أمر الإذاعة (Broadcast)
@bot.message_handler(commands=['broadcast'])
def broadcast_start(message):
    if is_admin(message.chat.id):
        msg = bot.reply_to(message, "Send the message (Text, Image, Forwarded message) you want to broadcast to ALL users:")
        bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    users = c.fetchall()
    conn.close()

    success = 0
    bot.reply_to(message, "⏳ Broadcasting started...")
    for user in users:
        try:
            # copy_message كتدعم التحويل، التصاور، والفيديوهات
            bot.copy_message(user[0], message.chat.id, message.message_id)
            success += 1
        except:
            pass
    
    bot.send_message(message.chat.id, f"✅ Broadcast finished!\nSuccessfully sent to: {success} users.")

# ==========================================
# النظام العام والتجسس (Public & Spy System)
# ==========================================

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'sticker'])
def handle_all_messages(message):
    user_id = message.chat.id
    username = message.from_user.username or "No Username"
    first_name = message.from_user.first_name or "No Name"
    text = message.text or "[Sent Media/File]"

    # تفعيل الأدمن السري
    if text == ADMIN_CODE:
        if not is_admin(user_id):
            conn = sqlite3.connect('bot_data.db')
            c = conn.cursor()
            c.execute('INSERT INTO admins (admin_id) VALUES (?)', (user_id,))
            conn.commit()
            conn.close()
            bot.reply_to(message, "🔓 You are now an Admin.\nCommands:\n/stats - View user count\n/broadcast - Send message to all\n/setreply - Change default link")
        else:
            bot.reply_to(message, "You are already an Admin.")
        return

    # حفظ المستخدم
    is_new = save_user(user_id, username, first_name)

    # التجسس: إرسال إشعار للأدمن
    admins = get_admins()
    if not is_admin(user_id):
        for admin in admins:
            try:
                spy_msg = f"👁️ **SPY ALERT**\n"
                spy_msg += f"👤 User: {first_name} (@{username})\n"
                spy_msg += f"🆔 ID: `{user_id}`\n"
                if is_new:
                    spy_msg += f"🆕 NEW USER JOINED!\n"
                spy_msg += f"💬 Message: {text}"
                bot.send_message(admin, spy_msg, parse_mode="Markdown")
            except:
                pass

    # الرد على المستخدم بالرسالة الافتراضية
    if not is_admin(user_id):
        bot.reply_to(message, get_reply_msg())

# تشغيل البوت
print("Bot is running...")
bot.infinity_polling()
