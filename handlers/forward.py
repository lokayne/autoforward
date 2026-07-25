import asyncio
import logging

from telegram import Update
from telegram.error import Forbidden, BadRequest, RetryAfter, TimedOut
from telegram.ext import ContextTypes

import database as db
from config import OWNER_IDS

logger = logging.getLogger(__name__)

MAX_RETRIES = 6
# how many targets to send to at the same time — keeps things fast without
# hammering Telegram hard enough to trigger flood control
MAX_CONCURRENT_SENDS = 5


def _passes_filter(message, filter_type: str) -> bool:
    is_media = bool(
        message.photo or message.video or message.document or message.audio
        or message.animation or message.voice or message.video_note or message.sticker
    )
    if filter_type == "all":
        return True
    if filter_type == "media":
        return is_media
    if filter_type == "text":
        return not is_media and bool(message.text)
    return True


def _hits_blacklist(message, blacklist) -> bool:
    if not blacklist:
        return False
    content = (message.text or message.caption or "").lower()
    return any(word in content for word in blacklist)


async def _send_with_retry(bot, source_id, target_id, message, mode):
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            if mode == "clean":
                await bot.copy_message(
                    chat_id=target_id,
                    from_chat_id=source_id,
                    message_id=message.message_id,
                )
            else:
                await bot.forward_message(
                    chat_id=target_id,
                    from_chat_id=source_id,
                    message_id=message.message_id,
                )
            return True, None
        except RetryAfter as e:
            logger.warning(
                "Flood control: waiting %.1fs to send to %s", e.retry_after, target_id
            )
            await asyncio.sleep(e.retry_after + 1)
            continue
        except TimedOut:
            attempt += 1
            await asyncio.sleep(min(2 * attempt, 20))
        except Forbidden as e:
            # Bot kicked
            return False, ("forbidden", str(e))
        except BadRequest as e:
            return False, ("badrequest", str(e))
        except Exception as e:
            logger.exception("Unexpected forward error sending to %s", target_id)
            attempt += 1
            await asyncio.sleep(min(2 * attempt, 20))
    return False, ("retries_exhausted", "")


async def _handle_one_target(bot, source_id, target_id, message, mode):
    ok, err = await _send_with_retry(bot, source_id, target_id, message, mode)
    return target_id, ok, err


async def channel_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post or update.edited_channel_post
    if not message:
        return

    source_id = message.chat_id
    source = await db.get_source(source_id)
    if not source or not source.get("active", True):
        return

    if not _passes_filter(message, source.get("filter_type", "all")):
        return
    if _hits_blacklist(message, source.get("blacklist", [])):
        return

    targets = source.get("targets", [])
    if not targets:
        return

    mode = source.get("mode", "clean")
    bot = context.bot

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_SENDS)

    async def _bounded(target_id):
        async with semaphore:
            return await _handle_one_target(bot, source_id, target_id, message, mode)

    results = await asyncio.gather(*(_bounded(t) for t in list(targets)))

    forwarded, failed = 0, 0
    for target_id, ok, err in results:
        if ok:
            forwarded += 1
            continue

        failed += 1
        if not err:
            continue

        reason, detail = err
        if reason == "forbidden":
            await db.deactivate_target(source_id, target_id)
            note = (
                f"Removed dead target `{target_id}` from source `{source_id}`"
                f" (bot lost access): {detail}"
            )
        else:
            # Any other permanent failure (retries exhausted, bad request, etc.)
            # gets reported too -- previously these were dropped silently.
            note = (
                f"Failed to forward message `{message.message_id}` from source"
                f" `{source_id}` to target `{target_id}` ({reason}): {detail}"
            )

        for owner in OWNER_IDS:
            try:
                await bot.send_message(owner, note, parse_mode="Markdown")
            except Exception:
                pass

    await db.bump_stats(forwarded=forwarded, failed=failed)
