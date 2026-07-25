from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

from database import is_authorized


def authorized_only(func):
    """Decorator: only OWNER_IDS or sudo users can run this command."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        if not user or not await is_authorized(user.id):
            await update.effective_message.reply_text(
                "You're not authorized to use this command."
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


def parse_int(text: str):
    try:
        return int(text)
    except (ValueError, TypeError):
        return None
