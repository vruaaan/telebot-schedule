from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.services.firebase import delete_event, get_event

async def handle_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows a confirmation prompt before deleting"""
    query = update.callback_query
    await query.answer()

    event_id = query.data.split("_", 1)[1]  # extract from "delete_{id}"
    user_id = str(query.from_user.id)
    event = get_event(user_id, event_id)

    if not event:
        await query.edit_message_text("⚠️ Event not found.")
        return

    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, delete", callback_data=f"confirmdelete_{event_id}"),
            InlineKeyboardButton("❌ No, keep it", callback_data=f"close_{event_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"🗑 Delete this event?\n📌 {event['title']}\n📅 {event['date']} {event['time']}",
        reply_markup=reply_markup
    )

async def handle_delete_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Actually deletes after confirmation"""
    query = update.callback_query
    await query.answer()

    event_id = query.data.split("_", 1)[1]  # extract from "confirmdelete_{id}"
    user_id = str(query.from_user.id)

    # Cancel the reminder job if it exists
    current_jobs = context.application.job_queue.get_jobs_by_name(f"reminder_{event_id}")
    for job in current_jobs:
        job.schedule_removal()

    delete_event(user_id, event_id)
    await query.edit_message_text("🗑 Event deleted.")