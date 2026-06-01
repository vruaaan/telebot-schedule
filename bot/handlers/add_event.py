from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.services.firebase import add_event
from datetime import datetime

# Define states
TITLE, DATE, TIME = range(3)

async def handle_add(update: Update, context: ContextTypes.DEFAULT_TYPE): #Step 1: User types /add, bot asks for title
    await update.message.reply_text("📝 Key in event name:")
    return TITLE

async def handle_title(update: Update, context: ContextTypes.DEFAULT_TYPE): #Step 2: User sends title, bot asks for date
    context.user_data["title"] = update.message.text
    await update.message.reply_text("📅 Key in event date (e.g. 050726 = 5 June 2026):")
    return DATE

async def handle_date(update: Update, context: ContextTypes.DEFAULT_TYPE): #Step 3: User sends date, bot asks for time"""
    context.user_data["date"] = update.message.text
    await update.message.reply_text("⏰ Key in event time (e.g. 1500)")
    return TIME

async def handle_time(update: Update, context: ContextTypes.DEFAULT_TYPE): #Step 4: User sends time, bot saves event and ends conversation
    context.user_data["time"] = update.message.text

    # Build the event from collected data
    title = context.user_data["title"]
    date = context.user_data["date"]
    time = context.user_data["time"]

    try:
        dt = datetime.strptime(f"{date} {time}", "%d %B %Y %I%p")
    except ValueError:
        try:
            dt = datetime.strptime(f"{date} {time}", "%d %B %Y %H:%M")
        except ValueError:
            await update.message.reply_text("⚠️ Couldn't parse that time. Try again with /add")
            return ConversationHandler.END

    event = {
        "title": title,
        "datetime": dt.isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "remarks": ""
    }

    user_id = str(update.effective_user.id)
    add_event(user_id, event)

    await update.message.reply_text(
        f"✅ Scheduled!\n"
        f"📌 {title}\n"
        f"📅 {dt.strftime('%d %b %Y, %I:%M %p')}"
    )
    return ConversationHandler.END

async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows user to cancel at any point with /cancel"""
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END