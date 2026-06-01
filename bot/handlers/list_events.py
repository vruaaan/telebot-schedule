from telegram import Update
from telegram.ext import ContextTypes
from bot.services.firebase import get_events

async def handle_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    events = get_events(user_id)

    if not events:
        await update.message.reply_text("📭 You have no upcoming events.")
        return

    lines = [f"📅 {e['title']} — {e['datetime']}\nID: `{e['id']}`" for e in events]
    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")