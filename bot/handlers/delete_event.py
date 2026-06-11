from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.services.firebase import delete_event, get_event

async def handle_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    _, month, event_id = query.data.split("|")  # "delete|June_2026|aB3xK9"
    event = get_event(user_id, month, event_id)

    if not event:
        await query.edit_message_text("⚠️ Event not found.")
        return

    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, delete", callback_data=f"confirmdelete|{month}|{event_id}"),
            InlineKeyboardButton("❌ No, keep it", callback_data=f"close|{month}|{event_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"🗑 Delete this event?\n📌 {event['title']}\n📅 {event['date']} {event['time']}",
        reply_markup=reply_markup
    )

async def handle_delete_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    _, month, event_id = query.data.split("|")  # "confirmdelete|June_2026|aB3xK9"

    # Cancel the reminder job if it exists
    current_jobs = context.application.job_queue.get_jobs_by_name(f"reminder_{event_id}")
    for job in current_jobs:
        job.schedule_removal()

    delete_event(user_id, month, event_id)
    await query.edit_message_text("🗑 Event deleted.")