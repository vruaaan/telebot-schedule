from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.services.firebase import get_events
from datetime import datetime
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")

async def handle_list(update, context):
    user_id = str(update.effective_user.id)
    current_month = datetime.now(SGT).strftime("%B_%Y")
    events = get_events(user_id, current_month)
    if not events:
        await update.message.reply_text("📭 You have no upcoming events.")
        return
    for e in events:
        month = datetime.strptime(e['date'], "%Y-%m-%d").strftime("%B_%Y")
        text = f"📌 {e['title']}\n📅 {e['date']} {e['time']}"
        keyboard = [[InlineKeyboardButton("More ▼", callback_data=f"more|{month}|{e['id']}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, month, event_id = query.data.split("|")

    keyboard = [
        [
            InlineKeyboardButton("🗑 Delete", callback_data=f"delete|{month}|{event_id}"),
            InlineKeyboardButton("✏️ Edit", callback_data=f"edit|{month}|{event_id}"),
        ],
        [InlineKeyboardButton("▲ Close", callback_data=f"close|{month}|{event_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_reply_markup(reply_markup=reply_markup)

async def handle_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, month, event_id = query.data.split("|")
    keyboard = [[InlineKeyboardButton("More ▼", callback_data=f"more|{month}|{event_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_reply_markup(reply_markup=reply_markup)
