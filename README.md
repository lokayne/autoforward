# Auto Forward Bot

Telegram bot that auto-forwards posts from source channels to multiple target
channels/groups, with filtering, blacklist words, clean/tagged copy modes,
dead-target cleanup, and sudo user management.

## One-Click Deploy

<p>
<a href="https://heroku.com/deploy?template=https://github.com/lokayne/autoforwardbot">
  <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku">
</a>
</p>

<p>
<a href="https://render.com/deploy?repo=https://github.com/lokayne/autoforwardbot">
  <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render">
</a>
</p>

**Note:** these buttons only work once the code is pushed to *your own* GitHub
repo (replace `YOUR_USERNAME/autoforwardbot` in both links and in `app.json`'s
`repository` field with your actual repo URL). See "Push to GitHub" below.

## Push to GitHub (required for the buttons above)

```bash
cd autoforwardbot
git init
git add .
git commit -m "Auto Forward Bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/autoforwardbot.git
git push -u origin main
```

Then edit the two deploy links in this README (and `repository` in `app.json`)
to point at that repo.

## Manual Setup

1. Create a bot via [@BotFather](https://t.me/BotFather), get the `BOT_TOKEN`.
2. Get a MongoDB connection string (MongoDB Atlas free tier works fine).
3. Get your Telegram numeric user ID (e.g. via @userinfobot) — this goes in `OWNER_IDS`.
4. Add the bot as **admin** to every source channel and every target channel/group.
5. Copy `.env.example` to `.env` and fill in the values (for VPS). For
   Heroku/Render, set these as environment/config variables in their dashboard instead.

```
BOT_TOKEN=xxxx
MONGO_URI=xxxx
DB_NAME=autoforwardbot
OWNER_IDS=123456789
```

## Getting a channel/group's chat_id

Forward any message from that channel/group to @userinfobot or @RawDataBot —
it'll show you the numeric chat ID (channels/supergroups start with `-100`).

## Local / VPS deployment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN=xxxx MONGO_URI=xxxx OWNER_IDS=123456789
python main.py
```

## Basic flow

Two ways to do everything — pick whichever's faster:

**Buttons:** `/start` → tap through 📡 Sources → pick/add a source → tap
Add Target / Mode / Filter / Pause / Blacklist etc. When something needs a
value (like a chat_id), the bot asks you to just type it as your next message.

**Commands:**
```
/addsource -1001111111111 MyChannel
/addtarget -1001111111111 -1002222222222
/addtarget -1001111111111 -1003333333333
/setmode -1001111111111 clean
/setfilter -1001111111111 all
```

Now any post in `MyChannel` auto-forwards to both targets. See `/help` inside
the bot for the full categorized command list (also button-driven).
