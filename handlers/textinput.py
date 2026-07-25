from telegram import Update
from telegram.ext import ContextTypes

import database as db
from handlers.keyboards import back_kb, targets_list_kb, source_blacklist_kb


async def pending_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles free-text replies for flows started by inline buttons
    (e.g. 'Add Source' asks for a chat_id). Only fires when something
    is actually pending; otherwise it's a no-op so normal chatting/commands
    aren't affected.
    """
    awaiting = context.user_data.get("awaiting")
    if not awaiting:
        return

    text = (update.effective_message.text or "").strip()
    action = awaiting.get("action")
    context.user_data["awaiting"] = None  # consume it either way

    if action == "addsource":
        parts = text.split(maxsplit=1)
        try:
            source_id = int(parts[0])
        except (ValueError, IndexError):
            await update.effective_message.reply_text("That doesn't look like a valid chat_id. Try /start again.")
            return
        name = parts[1] if len(parts) > 1 else ""
        await db.add_source(source_id, name)
        await update.effective_message.reply_text(
            f"Source added: `{source_id}`" + (f" ({name})" if name else ""),
            parse_mode="Markdown",
        )
        return

    if action == "addtarget":
        source_id = awaiting["source_id"]
        try:
            target_id = int(text)
        except ValueError:
            await update.effective_message.reply_text("That doesn't look like a valid chat_id.")
            return
        await db.add_target(source_id, target_id)
        source = await db.get_source(source_id)
        targets = source.get("targets", []) if source else []
        await update.effective_message.reply_text(
            f"Target `{target_id}` added.", parse_mode="Markdown",
            reply_markup=targets_list_kb(source_id, targets)
        )
        return

    if action == "addblacklist":
        source_id = awaiting["source_id"]
        await db.add_blacklist_word(source_id, text)
        source = await db.get_source(source_id)
        await update.effective_message.reply_text(
            f"Blacklisted `{text}`.", parse_mode="Markdown", reply_markup=source_blacklist_kb(source)
        )
        return

    if action == "removeblacklist":
        source_id = awaiting["source_id"]
        await db.remove_blacklist_word(source_id, text)
        source = await db.get_source(source_id)
        await update.effective_message.reply_text(
            f"Removed `{text}` from blacklist.", parse_mode="Markdown", reply_markup=source_blacklist_kb(source)
        )
        return

    if action == "addsudo":
        try:
            user_id = int(text)
        except ValueError:
            await update.effective_message.reply_text("That doesn't look like a valid user_id.")
            return
        await db.add_sudo(user_id)
        await update.effective_message.reply_text(
            f"`{user_id}` added as sudo.", parse_mode="Markdown", reply_markup=back_kb("menu:sudo")
        )
        return
