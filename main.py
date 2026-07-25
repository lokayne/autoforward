import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from config import BOT_TOKEN
from handlers.menu import start_cmd, help_cmd, cancel_cmd
from handlers.callbacks import menu_callback_handler
from handlers.textinput import pending_text_handler
from handlers.source import addsource_cmd, removesource_cmd, listsources_cmd
from handlers.target import addtarget_cmd, removetarget_cmd, listtargets_cmd
from handlers.settings import (
    setmode_cmd, setfilter_cmd, addblacklist_cmd, removeblacklist_cmd,
    pause_cmd, resume_cmd,
)
from handlers.sudo import addsudo_cmd, removesudo_cmd, listsudo_cmd
from handlers.stats import stats_cmd
from handlers.forward import channel_post_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Silence the noisy per-request HTTP logs from httpx/httpcore/telegram's own
# HTTP client — keep only our own INFO logs and warnings/errors from the rest.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)


def main():
    app = Application.builder().token(BOT_TOKEN).concurrent_updates(20).build()

    # Basic — button-driven menu
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(CallbackQueryHandler(menu_callback_handler))

    # Sources (command syntax — same features as the buttons)
    app.add_handler(CommandHandler("addsource", addsource_cmd))
    app.add_handler(CommandHandler("removesource", removesource_cmd))
    app.add_handler(CommandHandler("listsources", listsources_cmd))

    # Targets
    app.add_handler(CommandHandler("addtarget", addtarget_cmd))
    app.add_handler(CommandHandler("removetarget", removetarget_cmd))
    app.add_handler(CommandHandler("listtargets", listtargets_cmd))

    # Settings
    app.add_handler(CommandHandler("setmode", setmode_cmd))
    app.add_handler(CommandHandler("setfilter", setfilter_cmd))
    app.add_handler(CommandHandler("addblacklist", addblacklist_cmd))
    app.add_handler(CommandHandler("removeblacklist", removeblacklist_cmd))
    app.add_handler(CommandHandler("pause", pause_cmd))
    app.add_handler(CommandHandler("resume", resume_cmd))

    # Sudo
    app.add_handler(CommandHandler("addsudo", addsudo_cmd))
    app.add_handler(CommandHandler("removesudo", removesudo_cmd))
    app.add_handler(CommandHandler("listsudo", listsudo_cmd))

    # Stats
    app.add_handler(CommandHandler("stats", stats_cmd))

    # Free-text replies for button-driven flows (add source/target/blacklist/sudo).
    # Only acts when something is actually pending; otherwise no-op.
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, pending_text_handler))

    # Core forwarding — listens to channel posts (and edits) from any chat,
    # filtering against registered sources happens inside the handler.
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, channel_post_handler))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_CHANNEL_POST, channel_post_handler))

    logger.info("Auto Forward Bot starting...")
    # IMPORTANT: Telegram's getUpdates remembers the allowed_updates you last
    # sent it, server-side, tied to this bot's polling session -- it does
    # NOT reset to "all types" just because a later call omits the
    # parameter. The very first broken version of this bot sent
    # ["message", "channel_post", "edited_channel_post"] (no callback_query),
    # and Telegram kept enforcing that restriction even after we stopped
    # specifying it, which is why buttons kept silently failing. Passing
    # Update.ALL_TYPES explicitly forces Telegram to overwrite that stale
    # filter with everything, including callback_query.
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
