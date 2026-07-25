import logging

from telegram import Update
from telegram.ext import ContextTypes

import database as db
from config import OWNER_IDS
from handlers.help_text import START_TEXT, HELP_INTRO, HELP_SECTIONS
from handlers.keyboards import (
    main_menu_kb, help_menu_kb, help_section_kb, sources_list_kb,
    source_detail_kb, source_settings_kb, source_blacklist_kb,
    remove_source_confirm_kb, targets_list_kb,
    back_kb, sudo_list_kb,
)

logger = logging.getLogger(__name__)


async def _edit(query, text, kb=None):
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)


async def _require_auth(query, user_id) -> bool:
    if not await db.is_authorized(user_id):
        await query.answer("Not authorized.", show_alert=True)
        return False
    return True


async def _require_owner(query, user_id) -> bool:
    if user_id not in OWNER_IDS:
        await query.answer("Owner only.", show_alert=True)
        return False
    return True


async def _render_source_detail(query, source_id):
    source = await db.get_source(source_id)
    if not source:
        await _edit(query, "That source no longer exists.", back_kb("menu:sources"))
        return
    text = (
        f"*Source* `{source_id}`\n"
        f"Name: {source.get('name') or '—'}\n"
        f"Status: {'active' if source.get('active', True) else 'paused'}\n"
        f"Mode: {source.get('mode')}\n"
        f"Filter: {source.get('filter_type')}\n"
        f"Targets: {len(source.get('targets', []))}"
    )
    await _edit(query, text, source_detail_kb(source))


async def _render_source_settings(query, source_id):
    source = await db.get_source(source_id)
    if not source:
        await _edit(query, "That source no longer exists.", back_kb("menu:sources"))
        return
    text = (
        f"*Settings for* `{source_id}`\n\n"
        f"Mode: {source.get('mode')}\n"
        f"Filter: {source.get('filter_type')}"
    )
    await _edit(query, text, source_settings_kb(source))


async def _render_source_blacklist(query, source_id):
    source = await db.get_source(source_id)
    if not source:
        await _edit(query, "That source no longer exists.", back_kb("menu:sources"))
        return
    blacklist = ", ".join(source.get("blacklist", [])) or "none"
    text = f"*Blacklist for* `{source_id}`\n\n{blacklist}"
    await _edit(query, text, source_blacklist_kb(source))


async def menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    data = query.data
    await query.answer()

    # Pressing any menu button means the user isn't answering a pending
    # text prompt anymore -- clear it so a later unrelated message doesn't
    # get misread as e.g. a blacklist word from an abandoned flow.
    context.user_data["awaiting"] = None

    try:
        await _dispatch(query, user_id, data, context)
    except Exception:
        logger.exception("Error handling callback_data=%r from user_id=%s", data, user_id)
        try:
            await query.answer("Something went wrong, check bot logs.", show_alert=True)
        except Exception:
            pass


async def _dispatch(query, user_id, data, context):
    # ---- main navigation ----
    if data == "menu:main":
        await _edit(query, START_TEXT, main_menu_kb())
        return

    if data == "menu:help":
        await _edit(query, HELP_INTRO, help_menu_kb())
        return

    if data.startswith("help:"):
        section = data.split(":", 1)[1]
        text = HELP_SECTIONS.get(section, "Not found.")
        await _edit(query, text, help_section_kb())
        return

    # everything below requires authorization
    if not await _require_auth(query, user_id):
        return

    if data == "menu:stats":
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
        await _edit(query, text, back_kb())
        return

    if data == "menu:sources":
        sources = await db.get_all_sources()
        if not sources:
            await _edit(
                query,
                "No sources registered yet. Tap Add Source to register one.",
                sources_list_kb([]),
            )
        else:
            await _edit(query, "*Registered sources:*", sources_list_kb(sources))
        return

    if data == "menu:addsource":
        context.user_data["awaiting"] = {"action": "addsource"}
        await _edit(
            query,
            "Send the source *chat_id* (and optionally a name), e.g.:\n`-1001111111111 MyChannel`",
            back_kb("menu:sources"),
        )
        return

    # ---- source detail ----
    if data.startswith("src:"):
        parts = data.split(":")
        source_id = int(parts[1])

        if len(parts) == 2:
            await _render_source_detail(query, source_id)
            return

        action = parts[2]

        if action == "targets":
            source = await db.get_source(source_id)
            targets = source.get("targets", []) if source else []
            if not targets:
                await _edit(query, "No targets configured yet.", targets_list_kb(source_id, []))
            else:
                await _edit(query, f"*Targets for* `{source_id}`:", targets_list_kb(source_id, targets))
            return

        if action == "settings":
            await _render_source_settings(query, source_id)
            return

        if action == "blacklist":
            await _render_source_blacklist(query, source_id)
            return

        if action == "addtarget":
            context.user_data["awaiting"] = {"action": "addtarget", "source_id": source_id}
            await _edit(query, "Send the *target chat_id* to add.", back_kb(f"src:{source_id}:targets"))
            return

        if action == "tgt":
            target_id = int(parts[3])
            sub_action = parts[4]
            if sub_action == "remove":
                await db.remove_target(source_id, target_id)
                source = await db.get_source(source_id)
                targets = source.get("targets", []) if source else []
                await _edit(query, f"Removed `{target_id}`.\n\n*Targets for* `{source_id}`:", targets_list_kb(source_id, targets))
            return

        if action == "mode":
            mode = parts[3]
            await db.set_mode(source_id, mode)
            await _render_source_settings(query, source_id)
            return

        if action == "filter":
            ftype = parts[3]
            await db.set_filter(source_id, ftype)
            await _render_source_settings(query, source_id)
            return

        if action in ("pause", "resume"):
            await db.set_active(source_id, action == "resume")
            await _render_source_detail(query, source_id)
            return

        if action == "addblacklist":
            context.user_data["awaiting"] = {"action": "addblacklist", "source_id": source_id}
            await _edit(query, "Send the word to *blacklist*.", back_kb(f"src:{source_id}:blacklist"))
            return

        if action == "removeblacklist":
            context.user_data["awaiting"] = {"action": "removeblacklist", "source_id": source_id}
            await _edit(query, "Send the blacklisted word to *remove*.", back_kb(f"src:{source_id}:blacklist"))
            return

        if action == "remove":
            if len(parts) > 3 and parts[3] == "confirm":
                await db.remove_source(source_id)
                sources = await db.get_all_sources()
                await _edit(query, f"Source `{source_id}` removed.", sources_list_kb(sources))
            else:
                await _edit(
                    query,
                    f"Remove source `{source_id}` and all its config?",
                    remove_source_confirm_kb(source_id),
                )
            return

    # ---- sudo (owner only) ----
    if data.startswith("menu:sudo") or data.startswith("sudo:"):
        if not await _require_owner(query, user_id):
            return

        if data == "menu:sudo":
            sudo_ids = await db.list_sudo()
            text = "*Owners:*\n" + "\n".join(f"`{o}`" for o in OWNER_IDS)
            text += "\n\n*Sudo users:* (tap to remove)"
            await _edit(query, text, sudo_list_kb(OWNER_IDS, sudo_ids))
            return

        if data == "menu:addsudo":
            context.user_data["awaiting"] = {"action": "addsudo"}
            await _edit(query, "Send the *user_id* to grant sudo access.", back_kb("menu:sudo"))
            return

        if data.startswith("sudo:remove:"):
            uid = int(data.split(":")[2])
            await db.remove_sudo(uid)
            sudo_ids = await db.list_sudo()
            text = "*Owners:*\n" + "\n".join(f"`{o}`" for o in OWNER_IDS)
            text += "\n\n*Sudo users:* (tap to remove)"
            await _edit(query, text, sudo_list_kb(OWNER_IDS, sudo_ids))
            return
