from telegram import Update
from telegram.ext import ContextTypes

import database as db
from utils import authorized_only, parse_int


@authorized_only
async def addtarget_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.effective_message.reply_text(
            "Usage: `/addtarget <source_id> <target_id>`", parse_mode="Markdown"
        )
        return
    source_id, target_id = parse_int(args[0]), parse_int(args[1])
    if source_id is None or target_id is None:
        await update.effective_message.reply_text("Both IDs must be numbers.")
        return
    source = await db.get_source(source_id)
    if not source:
        await update.effective_message.reply_text(
            "That source isn't registered. Use /addsource first."
        )
        return
    await db.add_target(source_id, target_id)
    await update.effective_message.reply_text(
        f"Target `{target_id}` added to source `{source_id}`.", parse_mode="Markdown"
    )


@authorized_only
async def removetarget_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.effective_message.reply_text(
            "Usage: `/removetarget <source_id> <target_id>`", parse_mode="Markdown"
        )
        return
    source_id, target_id = parse_int(args[0]), parse_int(args[1])
    if source_id is None or target_id is None:
        await update.effective_message.reply_text("Both IDs must be numbers.")
        return
    await db.remove_target(source_id, target_id)
    await update.effective_message.reply_text(
        f"Target `{target_id}` removed from source `{source_id}`.", parse_mode="Markdown"
    )


@authorized_only
async def listtargets_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.effective_message.reply_text(
            "Usage: `/listtargets <source_id>`", parse_mode="Markdown"
        )
        return
    source_id = parse_int(args[0])
    source = await db.get_source(source_id)
    if not source:
        await update.effective_message.reply_text("That source isn't registered.")
        return
    targets = source.get("targets", [])
    if not targets:
        await update.effective_message.reply_text("No targets configured for this source.")
        return
    lines = [f"*Targets for* `{source_id}`:"]
    lines += [f"`{t}`" for t in targets]
    await update.effective_message.reply_text("\n".join(lines), parse_mode="Markdown")
