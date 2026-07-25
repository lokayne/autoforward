from telegram import Update
from telegram.ext import ContextTypes

import database as db
from utils import authorized_only, parse_int


@authorized_only
async def setmode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2 or args[1] not in ("copy", "clean"):
        await update.effective_message.reply_text(
            "Usage: `/setmode <source_id> copy|clean`", parse_mode="Markdown"
        )
        return
    source_id = parse_int(args[0])
    source = await db.get_source(source_id)
    if not source:
        await update.effective_message.reply_text("That source isn't registered.")
        return
    await db.set_mode(source_id, args[1])
    await update.effective_message.reply_text(f"Mode set to `{args[1]}` for `{source_id}`.", parse_mode="Markdown")


@authorized_only
async def setfilter_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2 or args[1] not in ("all", "media", "text"):
        await update.effective_message.reply_text(
            "Usage: `/setfilter <source_id> all|media|text`", parse_mode="Markdown"
        )
        return
    source_id = parse_int(args[0])
    source = await db.get_source(source_id)
    if not source:
        await update.effective_message.reply_text("That source isn't registered.")
        return
    await db.set_filter(source_id, args[1])
    await update.effective_message.reply_text(f"Filter set to `{args[1]}` for `{source_id}`.", parse_mode="Markdown")


@authorized_only
async def addblacklist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.effective_message.reply_text(
            "Usage: `/addblacklist <source_id> <word>`", parse_mode="Markdown"
        )
        return
    source_id = parse_int(args[0])
    word = " ".join(args[1:])
    source = await db.get_source(source_id)
    if not source:
        await update.effective_message.reply_text("That source isn't registered.")
        return
    await db.add_blacklist_word(source_id, word)
    await update.effective_message.reply_text(f"Blacklisted `{word}` for `{source_id}`.", parse_mode="Markdown")


@authorized_only
async def removeblacklist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.effective_message.reply_text(
            "Usage: `/removeblacklist <source_id> <word>`", parse_mode="Markdown"
        )
        return
    source_id = parse_int(args[0])
    word = " ".join(args[1:])
    await db.remove_blacklist_word(source_id, word)
    await update.effective_message.reply_text(f"Removed `{word}` from blacklist.", parse_mode="Markdown")


@authorized_only
async def pause_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.effective_message.reply_text("Usage: `/pause <source_id>`", parse_mode="Markdown")
        return
    source_id = parse_int(args[0])
    source = await db.get_source(source_id)
    if not source:
        await update.effective_message.reply_text("That source isn't registered.")
        return
    await db.set_active(source_id, False)
    await update.effective_message.reply_text(f"Forwarding paused for `{source_id}`.", parse_mode="Markdown")


@authorized_only
async def resume_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.effective_message.reply_text("Usage: `/resume <source_id>`", parse_mode="Markdown")
        return
    source_id = parse_int(args[0])
    source = await db.get_source(source_id)
    if not source:
        await update.effective_message.reply_text("That source isn't registered.")
        return
    await db.set_active(source_id, True)
    await update.effective_message.reply_text(f"Forwarding resumed for `{source_id}`.", parse_mode="Markdown")
