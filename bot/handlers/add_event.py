from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup #represents a single incoming event from Telegram (message, button press, etc), received as a parameter by every handler
#InlineKeyboardButton creates a single clickable button, InlineKeyboardMarkup wraps the buttons into a layout that gets attatched to a message
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler #ContextTypes used to type hint the context parameter in handler functions, ConversationHandler used to tell telegram that the conversation is over
# CallbackQueryHandler listens for button presses specifically : Telegram sends a "callback query" when button pressed instead of a regular message, different handler needed
from bot.services.firebase import add_event #fucntion to update firebase
from bot.jobs.reminders import schedule_reminder
from datetime import datetime #used to parse and format dates and times
from zoneinfo import ZoneInfo

#creates 3 state constants with values 0, 1, 2, 3, 4
TITLE, DATE, TIME, REMARKS, REMINDER = range(5) #used by ConversationHandler to know which step of the conversation the user is currently on
SGT = ZoneInfo("Asia/Singapore")

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
    keyboard = [[InlineKeyboardButton("No Remarks", callback_data="no_remarks")]] #nested list, outer list is rows, inner list is buttons per row
    #callback data is an invisible string that gets sent back to the bot when the button is pressed
    reply_markup = InlineKeyboardMarkup(keyboard) #wraps it in a format for telegram to understand
    await update.message.reply_text("✍️ Key in remarks or press below:", reply_markup=reply_markup) # attaches button layout to message 
    return REMARKS #the bot will wait for either a text reply or button press

async def handle_remarks(update: Update, context: ContextTypes.DEFAULT_TYPE):#triggered when user types remarks as text
    context.user_data["remarks"] = update.message.text # storing remarks
    return await save_event(update, context, is_callback=False) #saves event, is_callback = False to indicate it came from a regular message

async def handle_no_remarks(update: Update, context: ContextTypes.DEFAULT_TYPE): #triggered when user presses the "No Remarks" button
    query = update.callback_query #button presses come through here instead of update.message
    await query.answer()  # dismisses the loading state on the button
    context.user_data["remarks"] = "" #saves empty string since user indicated no remarks
    return await save_event(update, context, is_callback=True) # saves event, is_callback = True to indicate it came from button press

async def ask_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool):
    # Offer reminder time options as buttons
    keyboard = [
        [InlineKeyboardButton("15 min before", callback_data="reminder_15"),
         InlineKeyboardButton("30 min before", callback_data="reminder_30")],
        [InlineKeyboardButton("1 hour before", callback_data="reminder_60"),
         InlineKeyboardButton("1 day before", callback_data="reminder_1440")],
        [InlineKeyboardButton("No Reminder", callback_data="reminder_none")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = "🔔 Set a reminder?"
    if is_callback:
        await update.callback_query.message.reply_text(msg, reply_markup=reply_markup)
    else:
        await update.message.reply_text(msg, reply_markup=reply_markup)

async def handle_reminder_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # callback_data is like "reminder_15" or "reminder_none"
    choice = query.data  # e.g. "reminder_15"
    minutes = None if choice == "reminder_none" else int(choice.split("_")[1])
    context.user_data["reminder_minutes"] = minutes
    return await save_event(update, context, is_callback=True)

async def save_event(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool):
    title = context.user_data["title"]
    date = context.user_data["date"]   # e.g. "050626"
    time = context.user_data["time"]   # e.g. "1500"
    try: # trying to parse ddmmyy + HHmm
        dt = datetime.strptime(f"{date} {time}", "%d%m%y %H%M")
        dt = dt.replace(tzinfo=SGT)
    except ValueError:
        msg = "⚠️ Couldn't parse date/time. Use ddmmyy (e.g. 050626) and HHmm (e.g. 1500)." #error message
        if is_callback:
            await update.callback_query.message.reply_text(msg)
        else:
            await update.message.reply_text(msg)
        return ConversationHandler.END
    reminder_minutes = context.user_data.get("reminder_minutes")
    #creating payload to send in 
    event = {"title": title, 
             "date": dt.strftime("%Y-%m-%d"),      # "2026-06-05" — good for sorting/filtering
             "time": dt.strftime("%H:%M"),          # "15:00"
             "created_at": datetime.now(SGT).isoformat(),
             "remarks": context.user_data.get("remarks", ""),
             "reminder_minutes": reminder_minutes  # None if no reminder
            }
    
    user_id = str(update.callback_query.from_user.id if is_callback 
                  else update.effective_user.id)
    event_id = add_event(user_id, event)

    # Schedule the reminder job if user wanted one
    if reminder_minutes is not None:
        schedule_reminder(
            app=context.application,
            user_id=user_id,
            event_id=event_id,
            title=title,
            event_dt=dt,
            minutes_before=reminder_minutes
        )


    remarks_line = f"📝 {event['remarks']}\n" if event["remarks"] else ""
    reminder_line = f"🔔 Reminder set {reminder_minutes} min before\n" if reminder_minutes else ""
    confirmation = (
        f"✅ Scheduled!\n"
        f"📌 {title}\n"
        f"📅 {dt.strftime('%d %b %Y, %H:%M')}\n"
        f"{remarks_line}"
        f"{reminder_line}"
    )
    if is_callback:
        await update.callback_query.message.reply_text(confirmation) #sends return message back 
    else:
        await update.message.reply_text(confirmation)
    context.user_data.clear() #clears user data so old data doesnt bleed into the next /add call and ends the convo
    return ConversationHandler.END

async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END