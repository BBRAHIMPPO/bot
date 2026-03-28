import telebot
import re
from telebot import types

# ==========================================
# ⚙️ الإعدادات (معلوماتك من الصور)
# ==========================================
API_TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
ADMIN_ID = 718991554 
CHANNEL_URL = "https://t.me/+wZCOH72-1To3YWFk"

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")

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
    except Exception as e:
        return False

# ==========================================
# 🤖 نظام المعالجة الذكي
# ==========================================

@bot.message_handler(func=lambda m: True)
def handle_admin_commands(message):
    uid = message.chat.id
    text = message.text if message.text else ""

    # 1. إذا كان المرسل هو الأدمن (نتا)
    if uid == ADMIN_ID:
        # الحالة أ: صيفطتي رقم أيدي بوحدو (مثلاً: 5077384676)
        if text.isdigit():
            bot.send_chat_action(uid, 'typing')
            if send_welcome_to_user(text):
                bot.reply_to(message, f"✅ <b>تم الإرسال!</b>\nالرسالة وصلت لصاحب الأيدي: <code>{text}</code>")
            else:
                bot.reply_to(message, f"❌ <b>فشل!</b>\nصاحب الأيدي <code>{text}</code> بلوكا البوت أو الأيدي غلط.")
            return

        # الحالة ب: حولتي ليه الإشعار الطويل (الصيد التلقائي)
        if "الايدي :" in text:
            match = re.search(r'الايدي\s*:\s*(\d+)', text)
            if match:
                target_id = match.group(1)
                if send_welcome_to_user(target_id):
                    bot.reply_to(message, f"🚀 <b>تم الصيد بنجاح!</b>\nصيفت لـ: <code>{target_id}</code>")
                else:
                    bot.reply_to(message, f"❌ <b>فشل الصيد!</b> المستخدم حظر البوت.")
            return
            
        # نتا كأدمن، البوت مغيصيفطش ليك "مرحباً بك" نهائياً
        return

    # 2. إذا كان المرسل مستخدم عادي (ماشي نتا)
    else:
        # أي واحد غريب كيدخل، كيصيفط ليه الترحيب أوتوماتيكياً
        send_welcome_to_user(uid)
        
        # إشعار ليك نتا باش تعرف بلي كاين "ضحية" جديد
        notify = (
            "👾 <b>عضو جديد دخل للبوت!</b>\n"
            f"• الاسم: {message.from_user.first_name}\n"
            f"• الايدي: <code>{uid}</code>"
        )
        bot.send_message(ADMIN_ID, notify)

if __name__ == "__main__":
    print("JOSEPH SENDER IS READY...")
    bot.infinity_polling(skip_pending=True)
