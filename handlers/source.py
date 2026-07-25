from telegram import Update
from telegram.ext import ContextTypes

import database as db
from utils import authorized_only, parse_int


@authorized_only
async def addsource_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.effective_message.reply_text(
            "Usage: `/addsource <chat_id> [name]`", parse_mode="Markdown"
        )
        return
    source_id = parse_int(args[0])
    if source_id is None:
        await update.effective_message.reply_text("chat_id must be a number.")
        return
    name = " ".join(args[1:]) if len(args) > 1 else ""
    await db.add_source(source_id, name)
    await update.effective_message.reply_text(
        f"Source added: `{source_id}`" + (f" ({name})" if name else ""),
        parse_mode="Markdown",
    )


@authorized_only
async def removesource_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.effective_message.reply_text(
            "Usage: `/removesource <chat_id>`", parse_mode="Markdown"
        )
        return
    source_id = parse_int(args[0])
    if source_id is None:
        await update.effective_message.reply_text("chat_id must be a number.")
        return
    ok = await db.remove_source(source_id)
    if ok:
        await update.effective_message.reply_text(f"Source `{source_id}` removed.", parse_mode="Markdown")
    else:
        await update.effective_message.reply_text("That source isn't registered.")


@authorized_only
async def listsources_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sources = await db.get_all_sources()
    if not sources:
        await update.effective_message.reply_text("No sources registered yet.")
        return
    lines = ["*Registered sources:*"]
    for s in sources:
        status = "active" if s.get("active", True) else "paused"
        lines.append(
            f"[{status}] `{s['_id']}` {s.get('name','')} — "
            f"{len(s.get('targets', []))} target(s), mode: {s.get('mode')}, "
            f"filter: {s.get('filter_type')}"
        )
    await update.effective_message.reply_text("\n".join(lines), parse_mode="Markdown")
