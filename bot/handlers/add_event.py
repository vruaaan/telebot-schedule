from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup #represents a single incoming event from Telegram (message, button press, etc), received as a parameter by every handler
from telegram.ext import ContextTypes, ConversationHandler #ContextTypes used to type hint the context parameter in handler functions, ConversationHandler used to tell telegram that the conversation is over
from bot.services.firebase import add_event #fucntion to update firebase
from datetime import datetime #used to parse and format dates and times

#creates 3 state constants with values 0, 1, 2
TITLE, DATE, TIME, REMARKS = range(4)
#used by ConversationHandler to know which step of the conversation the user is currently on

async def handle_add(update: Update, context: ContextTypes.DEFAULT_TYPE): #Step 1: User types /add, bot asks for title
    await update.message.reply_text("📝 Key in event name:") #sends prompt and waits
    return TITLE

async def handle_title(update: Update, context: ContextTypes.DEFAULT_TYPE): #Step 2: User sends title, bot asks for date
    context.user_data["title"] = update.message.text #storing title from previous step
    await update.message.reply_text("📅 Key in event date (e.g. 050726 = 5 June 2026):")
    return DATE

async def handle_date(update: Update, context: ContextTypes.DEFAULT_TYPE): #Step 3: User sends date, bot asks for time"""
    context.user_data["date"] = update.message.text #storing date from previous step
    await update.message.reply_text("⏰ Key in time in 24hr format(e.g. 1500)")
    return TIME

async def handle_time(update: Update, context: ContextTypes.DEFAULT_TYPE): #Step 3: User sends date, bot asks for time"""
    context.user_data["time"] = update.message.text #storing time from previous step
    keyboard = [[InlineKeyboardButton("No Remarks", callback_data="no_remarks")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✍️ Key in remarks or press below:", reply_markup=reply_markup)
    return REMARKS
async def handle_remarks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # User typed remarks as text
    context.user_data["remarks"] = update.message.text
    return await save_event(update, context, is_callback=False)

async def handle_no_remarks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # User pressed the "No Remarks" button
    query = update.callback_query
    await query.answer()  # dismisses the loading state on the button
    context.user_data["remarks"] = ""
    return await save_event(update, context, is_callback=True)

async def save_event(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool):
    title = context.user_data["title"]
    date = context.user_data["date"]   # e.g. "050626"
    time = context.user_data["time"]   # e.g. "1500"

    # Parse ddmmyy + HHmm
    try:
        dt = datetime.strptime(f"{date} {time}", "%d%m%y %H%M")
    except ValueError:
        msg = "⚠️ Couldn't parse date/time. Use ddmmyy (e.g. 050626) and HHmm (e.g. 1500). Try /add again."
        if is_callback:
            await update.callback_query.message.reply_text(msg)
        else:
            await update.message.reply_text(msg)
        return ConversationHandler.END

    event = {
        "title": title,
        "datetime": dt.isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "remarks": context.user_data.get("remarks", "")
    }

    user_id = str(
        update.callback_query.from_user.id if is_callback
        else update.effective_user.id
    )
    add_event(user_id, event)

    remarks_line = f"📝 {event['remarks']}\n" if event["remarks"] else ""
    confirmation = (
        f"✅ Scheduled!\n"
        f"📌 {title}\n"
        f"📅 {dt.strftime('%d %b %Y, %H:%M')}\n"
        f"{remarks_line}"
    )

    if is_callback:
        await update.callback_query.message.reply_text(confirmation)
    else:
        await update.message.reply_text(confirmation)

    context.user_data.clear()
    return ConversationHandler.END

async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END