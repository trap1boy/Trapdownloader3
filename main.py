import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
from downloader import youtube, instagram, tiktok, pinterest
from config import BOT_TOKEN, FORCE_CHANNEL, ADMIN_ID
from keep_alive import keep_alive

bot = telebot.TeleBot(BOT_TOKEN)

# بررسی عضویت در کانال
def is_member(user_id):
    try:
        member = bot.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# دکمه عضویت
def join_button():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{FORCE_CHANNEL.strip('@')}"),
        InlineKeyboardButton("✅ عضویت زدم، بیا", callback_data="refresh")
    )
    return markup

# تشخیص پلتفرم
def get_platform(url):
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "instagram.com" in url:
        return "instagram"
    elif "tiktok.com" in url:
        return "tiktok"
    elif "pinterest.com" in url:
        return "pinterest"
    return "unknown"

# شروع
@bot.message_handler(commands=["start"])
def start_handler(message):
    if not is_member(message.from_user.id):
        bot.send_message(message.chat.id, "🔒 لطفاً ابتدا عضو کانال شوید:", reply_markup=join_button())
        return
    bot.send_message(message.chat.id, "🎬 سلام! لینک ویدیوی YouTube، Instagram، TikTok یا Pinterest رو بفرست تا برات دانلود کنم.")

# دریافت پیام و لینک
@bot.message_handler(func=lambda m: True, content_types=["text"])
def downloader_handler(message):
    if not is_member(message.from_user.id):
        bot.send_message(message.chat.id, "🔒 لطفاً ابتدا عضو کانال شوید:", reply_markup=join_button())
        return

    match = re.search(r"https?://[^\s]+", message.text)
    if not match:
        bot.send_message(message.chat.id, "❌ لطفاً یک لینک معتبر ارسال کن.")
        return

    url = match.group()
    platform = get_platform(url)
    bot.send_message(message.chat.id, "⏳ در حال پردازش لینک...")

    try:
        if platform == "youtube":
            result = youtube.download_youtube(url)
        elif platform == "instagram":
            result = instagram.download_instagram(url)
        elif platform == "tiktok":
            result = tiktok.download_tiktok(url)
        elif platform == "pinterest":
            result = pinterest.download_pinterest(url)
        else:
            bot.send_message(message.chat.id, "❌ پلتفرم این لینک پشتیبانی نمی‌شود.")
            return

        if "error" in result:
            bot.send_message(message.chat.id, f"❌ خطا: {result['error']}")
        else:
            bot.send_message(
                message.chat.id,
                f"✅ عنوان: {result.get('title', 'بدون عنوان')}\n📥 لینک دانلود:\n{result.get('url')}"
            )
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ خطا: {str(e)}")

# بررسی عضویت دوباره
@bot.callback_query_handler(func=lambda call: call.data == "refresh")
def refresh(call):
    if is_member(call.from_user.id):
        bot.edit_message_text("✅ عضویت تأیید شد! حالا لینک رو بفرست.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو نشدی!", show_alert=True)

# اجرای ربات
keep_alive()
print("🤖 Bot is running...")
bot.infinity_polling()
