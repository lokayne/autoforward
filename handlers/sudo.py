from telegram import Update
from telegram.ext import ContextTypes

import database as db
from utils import parse_int
from config import OWNER_IDS


def owner_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if not user or user.id not in OWNER_IDS:
            await update.effective_message.reply_text("Owner only command.")
            return
        return await func(update, context)
    return wrapper


@owner_only
async def addsudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.effective_message.reply_text("Usage: `/addsudo <user_id>`", parse_mode="Markdown")
        return
    user_id = parse_int(args[0])
    if user_id is None:
        await update.effective_message.reply_text("user_id must be a number.")
        return
    await db.add_sudo(user_id)
    await update.effective_message.reply_text(f"`{user_id}` added as sudo.", parse_mode="Markdown")


@owner_only
async def removesudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.effective_message.reply_text("Usage: `/removesudo <user_id>`", parse_mode="Markdown")
        return
    user_id = parse_int(args[0])
    ok = await db.remove_sudo(user_id)
    if ok:
        await update.effective_message.reply_text(f"`{user_id}` removed from sudo.", parse_mode="Markdown")
    else:
        await update.effective_message.reply_text("That user isn't a sudo.")


@owner_only
async def listsudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sudos = await db.list_sudo()
    lines = ["*Owners:*"] + [f"`{o}`" for o in OWNER_IDS]
    lines.append("\n*Sudo users:*")
    lines += [f"`{s}`" for s in sudos] if sudos else ["None"]
    await update.effective_message.reply_text("\n".join(lines), parse_mode="Markdown")
