from telegram import Update
from telegram.ext import ContextTypes
from bot.services.firebase import add_event
from bot.utils.parse_datetime import parse_dt
from datetime import datetime

async def handle_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: /add Team meeting tomorrow 3pm
    if not context.args:
        await update.message.reply_text("Usage: /add [event] [date/time]")
        return
    text = " ".join(context.args)
    try:
        dt = parse_dt(text)
        if dt is None:
            await update.message.reply_text("⚠️ Couldn't understand the date. Try: /add Meeting Friday 3pm")
            return
    except Exception:
        await update.message.reply_text("⚠️ Invalid date format. Try: /add Meeting Friday 3pm")
        return
    event = {
        "title": text,
        "datetime": dt.isoformat(),
        "created_at": datetime.utcnow().isoformat()
    }
    user_id = str(update.effective_user.id)
    add_event(user_id, event)
    await update.message.reply_text(f"✅ Scheduled: {text}\n📅 {dt.strftime('%d %b %Y, %I:%M %p')}")
    