from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.services.firebase import get_events
from bot.services.firebase import get_events
from datetime import datetime
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")

async def handle_list(update, context):
    current_month = datetime.now(SGT).strftime("%B_%Y")  # "June_2026"
    events = get_events(current_month)
    if not events:
        await update.message.reply_text("📭 You have no upcoming events.")
        return
    for e in events:
        # Each event gets its own message with a "More" button
        text = f"📌 {e['title']}\n📅 {e['date']} {e['time']}"
        keyboard = [[InlineKeyboardButton("More ▼", callback_data=f"more_{e['id']}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Expands an event to show delete and edit buttons"""
    query = update.callback_query
    await query.answer()

    event_id = query.data.split("_", 1)[1]  # extract ID from "more_{id}"

    keyboard = [
        [
            InlineKeyboardButton("🗑 Delete", callback_data=f"delete_{event_id}"),
            InlineKeyboardButton("✏️ Edit", callback_data=f"edit_{event_id}"),
        ],
        [InlineKeyboardButton("▲ Close", callback_data=f"close_{event_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_reply_markup(reply_markup=reply_markup)
    # edit_message_reply_markup replaces the existing buttons without sending a new message

async def handle_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collapses back to just the More button"""
    query = update.callback_query
    await query.answer()

    event_id = query.data.split("_", 1)[1]
    keyboard = [[InlineKeyboardButton("More ▼", callback_data=f"more_{event_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_reply_markup(reply_markup=reply_markup)