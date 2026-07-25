from telegram import Update
from telegram.ext import ContextTypes

import database as db
from handlers.help_text import START_TEXT, HELP_INTRO, NOT_AUTHORIZED_TEXT
from handlers.keyboards import main_menu_kb, help_menu_kb


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await db.is_authorized(user_id):
        await update.effective_message.reply_text(NOT_AUTHORIZED_TEXT, parse_mode="Markdown")
        return
    await update.effective_message.reply_text(
        START_TEXT, parse_mode="Markdown", reply_markup=main_menu_kb()
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await db.is_authorized(user_id):
        await update.effective_message.reply_text(NOT_AUTHORIZED_TEXT, parse_mode="Markdown")
        return
    await update.effective_message.reply_text(
        HELP_INTRO, parse_mode="Markdown", reply_markup=help_menu_kb()
    )


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    had_pending = bool(context.user_data.get("awaiting"))
    context.user_data["awaiting"] = None
    if had_pending:
        await update.effective_message.reply_text("Cancelled.")
    else:
        await update.effective_message.reply_text("Nothing to cancel.")
