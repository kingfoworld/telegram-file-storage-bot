# Telegram File Storage Bot

এই bot‑টি GitHub repository থেকে Render **Free Web Service** হিসেবে webhook mode‑এ চালানো যাবে। GitHub শুধু code রাখবে; bot‑এর secret token GitHub‑এ রাখা হবে না।

## 1. আগে নিরাপত্তা ঠিক করুন

যে token আগের file‑এ ছিল সেটি BotFather দিয়ে revoke করুন এবং নতুন token তৈরি করুন। নতুন token `.env` বা hosting dashboard‑এর secret/environment variable হিসেবে রাখবেন—GitHub code‑এ লিখবেন না।

## 2. Render free deployment

Render‑এর Free Web Service ব্যবহার করতে bot‑টি polling-এর বদলে Telegram webhook ব্যবহার করে। Render `RENDER_EXTERNAL_URL` দিলে application নিজে Telegram webhook সেট করে। Free service ১৫ মিনিট inbound traffic না পেলে sleep করতে পারে, তাই এটি hobby/testing use‑এর জন্য; always-on reliability দরকার হলে paid Background Worker ব্যবহার করুন।

Render settings:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn bot:app
Plan: Free
```

Environment variables:

- `BOT_TOKEN`: BotFather থেকে পাওয়া নতুন token
- `CHANNEL_ID`: storage channel‑এর numeric ID
- `BOT_USERNAME`: `@` ছাড়া bot username

## 3. স্থানীয়ভাবে চালানো

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python bot.py
```

`.env` ফাইলে `BOT_TOKEN`, `CHANNEL_ID`, এবং `BOT_USERNAME` পূরণ করতে হবে।

## 4. GitHub + Render deployment

1. এই `telegram-bot` folder‑এর files একটি নতুন **private GitHub repository**‑তে upload করুন।
2. Render‑এ GitHub দিয়ে sign in করে **New > Web Service** নির্বাচন করুন।
3. `kingfoworld/telegram-file-storage-bot` repository নির্বাচন করুন।
4. Environment variables হিসেবে যোগ করুন:
   - `BOT_TOKEN`: BotFather থেকে পাওয়া নতুন token
   - `CHANNEL_ID`: storage channel‑এর numeric ID
   - `BOT_USERNAME`: `@` ছাড়া bot username
5. Plan হিসেবে **Free** নির্বাচন করুন।
6. Deploy শেষ হলে Logs‑এ webhook configured এবং startup message দেখুন।
7. Telegram‑এ `/start` পাঠিয়ে test করুন।

## Telegram permissions

Storage channel‑এ bot‑কে administrator করে অন্তত messages post/send করার permission দিন। Bot‑এর মাধ্যমে channel থেকে file copy করতে হলে bot‑কে channel‑এ access থাকতে হবে।

## Important behavior

বর্তমান design‑এ active batch এবং language preference RAM‑এ থাকে। Service restart বা sleep হলে active batch reset হবে এবং language preference আবার English default হবে। Permanent user state দরকার হলে পরে Redis/SQLite যোগ করা যাবে।
