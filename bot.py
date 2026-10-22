import os

import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


BOT_TOKEN = required_env("BOT_TOKEN")
CHANNEL_ID = int(required_env("CHANNEL_ID"))
BOT_USERNAME = required_env("BOT_USERNAME").lstrip("@")
WEBHOOK_PATH = "/telegram"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# These dictionaries are intentionally kept in memory, matching the original bot.
# A service restart clears active batches and remembered language choices.
user_batches = {}
user_languages = {}

strings = {
    "bn": {
        "welcome": "👋 **হ্যালো {name}!**\n\nআমি একটি অ্যাডভান্সড **File Storage Bot**।\n\n📌 **ব্যবহার করার নিয়মাবলী:**\n▪️ যেকোনো একটি ফাইল সরাসরি আমাকে পাঠান, আমি **সিঙ্গেল লিংক** তৈরি করে দেব।\n▪️ একাধিক ফাইলের জন্য একটি মাত্র লিংক তৈরি করতে টাইপ করুন: /batch",
        "lang_saved": "✅ আপনার ভাষা **বাংলা** হিসেবে সেভ করা হয়েছে!",
        "batch_start": "🔄 **ব্যাচ মোড অ্যাক্টিভ হয়েছে!**\n\n👇 এখন ফাইলগুলো এক এক করে আমাকে পাঠান।\n\n⚠️ সব ফাইল পাঠানো শেষ হলে লিংক জেনারেট করতে টাইপ করুন: /finish",
        "batch_empty": "❌ আপনার কোনো অ্যাক্টিভ ব্যাচ নেই। প্রথমে /batch লিখুন।",
        "batch_success": "✅ **আপনার ব্যাচটি সফলভাবে সেভ করা হয়েছে!**\n\n📦 **মোট ফাইল:** `{count}` টি\n🔗 **আপনার কম্বাইন ব্যাচ লিংক:**\n`{link}`",
        "single_success": "✅ **ফাইলটি সরাসরি স্টোরেজ চ্যানেলে সেভ করা হয়েছে!**\n\n🔗 **আপনার সিঙ্গেল লিংক:** `{link}`",
        "batch_added": "📥 ফাইলটি ব্যাচে যুক্ত হয়েছে (মোট: {count} টি)। শেষ হলে /finish লিখুন।",
        "guide": "💡 **লিংক তৈরি করার গাইড:**\n\n🔹 **সিঙ্গেল ফাইল:** যেকোনো একটি ভিডিও বা ডকুমেন্ট সরাসরি বটে সেন্ড করুন।\n🔹 **মাল্টিপল ফাইল (Batch):** প্রথমে /batch কমান্ড দিন, তারপর ফাইলগুলো পাঠান, শেষে /finish কমান্ড দিন।\n\n🌐 ভাষা পরিবর্তন করতে টাইপ করুন: /language",
        "error": "❌ ফাইলটি পাওয়া যায়নি বা মুছে ফেলা হয়েছে।",
    },
    "en": {
        "welcome": "👋 **Hello {name}!**\n\nI am an advanced **File Storage Bot**.\n\n📌 **How to use:**\n▪️ Send any single file to get a **Single Link**.\n▪️ To combine multiple files into one link, type: /batch",
        "lang_saved": "✅ Your language has been set to **English**!",
        "batch_start": "🔄 **Batch mode activated!**\n\n👇 Now send or forward your files one by one.\n\n⚠️ When finished, type /finish to generate the single link.",
        "batch_empty": "❌ You don't have any active batch. Type /batch first.",
        "batch_success": "✅ **Your batch has been saved successfully!**\n\n📦 **Total Files:** `{count}`\n🔗 **Your Combined Batch Link:**\n`{link}`",
        "single_success": "✅ **File saved to storage channel successfully!**\n\n🔗 **Your Single Link:** `{link}`",
        "batch_added": "📥 File added to batch (Total: {count}). Type /finish when done.",
        "guide": "💡 **Link Generation Guide:**\n\n🔹 **Single File:** Send any video or document directly to the bot.\n🔹 **Multiple Files (Batch):** Type /batch, send your files, and then type /finish.\n\n🌐 To change your language, type: /language",
        "error": "❌ Files not found or may have been deleted.",
    },
}


def get_lang(user_id):
    return user_languages.get(user_id, "en")


def get_lang_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🇧🇩 বাংলা", callback_data="setlang_bn"),
        InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en"),
    )
    return markup


def bot_link(start_parameter: str) -> str:
    return f"https://t.me/{BOT_USERNAME}?start={start_parameter}"


@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.from_user.id
    text = message.text or ""

    if "batch_" in text or "file_" in text:
        lang = get_lang(user_id)
        if "batch_" in text:
            try:
                ids = text.split("batch_", 1)[1].split("_")
                first_id = int(ids[0])
                last_id = int(ids[1])
                for msg_id in range(first_id, last_id + 1):
                    try:
                        bot.copy_message(
                            chat_id=message.chat.id,
                            from_chat_id=CHANNEL_ID,
                            message_id=msg_id,
                        )
                    except Exception:
                        continue
            except Exception:
                bot.reply_to(message, strings[lang]["error"])
        elif "file_" in text:
            try:
                msg_id = int(text.split("file_", 1)[1])
                bot.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=CHANNEL_ID,
                    message_id=msg_id,
                )
            except Exception:
                bot.reply_to(message, strings[lang]["error"])
        return

    bot.reply_to(
        message,
        "🌐 Please select your language / অনুগ্রহ করে ভাষা নির্বাচন করুন:",
        reply_markup=get_lang_keyboard(),
    )


@bot.message_handler(commands=["language"])
def change_language(message):
    bot.reply_to(
        message,
        "🌐 Select Language / ভাষা পরিবর্তন করুন:",
        reply_markup=get_lang_keyboard(),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("setlang_"))
def callback_set_lang(call):
    user_id = call.from_user.id
    lang = call.data.split("_", 1)[1]
    user_languages[user_id] = lang

    bot.answer_callback_query(call.id, strings[lang]["lang_saved"])
    welcome_msg = strings[lang]["welcome"].format(name=call.from_user.first_name)
    bot.edit_message_text(
        welcome_msg,
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["batch"])
def handle_batch_command(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    user_batches[user_id] = []
    bot.reply_to(message, strings[lang]["batch_start"], parse_mode="Markdown")


@bot.message_handler(commands=["finish"])
def handle_finish_command(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)

    if user_id not in user_batches or not user_batches[user_id]:
        bot.reply_to(message, strings[lang]["batch_empty"])
        return

    msg_ids = user_batches[user_id]
    first_id = min(msg_ids)
    last_id = max(msg_ids)
    del user_batches[user_id]

    batch_link = bot_link(f"batch_{first_id}_{last_id}")
    markup = InlineKeyboardMarkup()
    btn_text = "🔗 ওপেন ব্যাচ লিংক" if lang == "bn" else "🔗 Open Batch Link"
    markup.add(InlineKeyboardButton(btn_text, url=batch_link))

    success_msg = strings[lang]["batch_success"].format(
        count=len(msg_ids),
        link=batch_link,
    )
    bot.reply_to(message, success_msg, reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(commands=["genlink"])
def handle_genlink_command(message):
    lang = get_lang(message.from_user.id)
    bot.reply_to(message, strings[lang]["guide"], parse_mode="Markdown")


@bot.message_handler(content_types=["document", "video", "audio", "photo"])
def handle_incoming_files(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)

    try:
        caption_text = message.caption or ""
        uploaded_msg = None

        if message.content_type == "document":
            uploaded_msg = bot.send_document(
                CHANNEL_ID, message.document.file_id, caption=caption_text
            )
        elif message.content_type == "video":
            uploaded_msg = bot.send_video(
                CHANNEL_ID, message.video.file_id, caption=caption_text
            )
        elif message.content_type == "audio":
            uploaded_msg = bot.send_audio(
                CHANNEL_ID, message.audio.file_id, caption=caption_text
            )
        elif message.content_type == "photo":
            uploaded_msg = bot.send_photo(
                CHANNEL_ID, message.photo[-1].file_id, caption=caption_text
            )

        if not uploaded_msg:
            return

        msg_id = uploaded_msg.message_id
        if user_id in user_batches:
            user_batches[user_id].append(msg_id)
            bot.reply_to(
                message,
                strings[lang]["batch_added"].format(
                    count=len(user_batches[user_id])
                ),
            )
            return

        share_link = bot_link(f"file_{msg_id}")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 ওপেন লিংক (Open Link)", url=share_link))
        single_msg = strings[lang]["single_success"].format(link=share_link)
        bot.reply_to(message, single_msg, reply_markup=markup, parse_mode="Markdown")
    except Exception as error:
        bot.reply_to(message, f"❌ Error: {error}")


@app.get("/")
def health_check():
    return {"status": "ok", "service": "telegram-file-storage-bot"}


@app.post(WEBHOOK_PATH)
def telegram_webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200


def configure_webhook():
    external_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("WEBHOOK_URL")
    if not external_url:
        print("Webhook URL is not available yet; HTTP server will still start.")
        return

    webhook_url = f"{external_url.rstrip('/')}{WEBHOOK_PATH}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    print(f"✅ Telegram webhook configured: {webhook_url}")


configure_webhook()


if __name__ == "__main__":
    if os.getenv("POLLING_MODE", "false").lower() == "true":
        bot.remove_webhook()
        print("⚡ মাল্টি-ল্যাঙ্গুয়েজ পাবলিক ব্যাচ বট polling mode‑এ চালু হয়েছে...")
        bot.infinity_polling(timeout=30, long_polling_timeout=30, skip_pending=True)
    else:
        port = int(os.getenv("PORT", "10000"))
        print("⚡ মাল্টি-ল্যাঙ্গুয়েজ পাবলিক ব্যাচ বটের webhook server চালু হয়েছে...")
        app.run(host="0.0.0.0", port=port)
