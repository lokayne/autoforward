from telegram import Update
from telegram.ext import ContextTypes

import database as db
from utils import authorized_only


@authorized_only
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = await db.get_stats()
    sources = await db.get_all_sources()
    active_count = sum(1 for s in sources if s.get("active", True))
    total_targets = sum(len(s.get("targets", [])) for s in sources)
    text = (
        "*Bot Stats*\n\n"
        f"Sources: {len(sources)} ({active_count} active)\n"
        f"Total targets: {total_targets}\n"
        f"Forwarded: {stats.get('forwarded', 0)}\n"
        f"Failed: {stats.get('failed', 0)}"
    )
    await update.effective_message.reply_text(text, parse_mode="Markdown")
