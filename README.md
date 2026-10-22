# Telegram File Storage Bot

এই bot‑টি GitHub repository থেকে Render Background Worker হিসেবে চালানো যাবে। GitHub শুধু code রাখবে; bot‑এর secret token GitHub‑এ রাখা হবে না।

## 1. আগে নিরাপত্তা ঠিক করুন

যে token আগের file‑এ ছিল সেটি BotFather দিয়ে revoke করুন এবং নতুন token তৈরি করুন। নতুন token `.env` বা hosting dashboard‑এর secret/environment variable হিসেবে রাখবেন—GitHub code‑এ লিখবেন না।

## 2. স্থানীয়ভাবে চালানো

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python bot.py
```

`.env` ফাইলে `BOT_TOKEN`, `CHANNEL_ID`, এবং `BOT_USERNAME` পূরণ করতে হবে।

## 3. GitHub + Render deployment

1. এই `telegram-bot` folder‑এর files একটি নতুন **private GitHub repository**‑তে upload করুন।
2. Render‑এ GitHub দিয়ে sign in করে **New > Blueprint** নির্বাচন করুন।
3. এই repository এবং `render.yaml` নির্বাচন করুন।
4. Environment variables হিসেবে যোগ করুন:
   - `BOT_TOKEN`: BotFather থেকে পাওয়া নতুন token
   - `CHANNEL_ID`: storage channel‑এর numeric ID
   - `BOT_USERNAME`: `@` ছাড়া bot username
5. Deploy শেষ হলে Logs‑এ `বট সফলভাবে চালু হয়েছে` ধরনের startup message দেখুন।
6. Telegram‑এ `/start` পাঠিয়ে test করুন।

## Telegram permissions

Storage channel‑এ bot‑কে administrator করে অন্তত messages post/send করার permission দিন। Bot‑এর মাধ্যমে channel থেকে file copy করতে হলে bot‑কে channel‑এ access থাকতে হবে।

## Important behavior

বর্তমান design‑এ active batch এবং language preference RAM‑এ থাকে। Service restart হলে active batch reset হবে এবং language preference আবার English default হবে। Permanent user state দরকার হলে পরে Redis/SQLite যোগ করা যাবে।
