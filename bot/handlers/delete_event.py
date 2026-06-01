from telegram import Update
from telegram.ext import ContextTypes
from bot.services.firebase import delete_event

async def handle_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: /delete [event_id]
    if not context.args:
        await update.message.reply_text("Usage: /delete [event_id]")
        return

    event_id = context.args[0]
    user_id = str(update.effective_user.id)
    delete_event(user_id, event_id)
    await update.message.reply_text(f"🗑️ Event deleted.")