from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters
from bot.handlers.add_event import (
    handle_add, handle_title, handle_date, handle_time,
    handle_remarks, handle_no_remarks, handle_cancel, 
    TITLE, DATE, TIME, REMARKS
)
from bot.handlers.list_events import handle_list
from dotenv import load_dotenv
import os

load_dotenv() #reads the .env file and loads bot token into environment

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build() #creates the bot using telegram token
    add_conversation = ConversationHandler(
        entry_points=[CommandHandler("add", handle_add)],
        states={TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title)],
                DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date)],
                TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_time)],
                REMARKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_remarks), #REMARKS have 2 possible handlers, 
                CallbackQueryHandler(handle_no_remarks, pattern="^no_remarks$")],
        },fallbacks=[CommandHandler("cancel", handle_cancel)]
    )
    app.add_handler(add_conversation)
    app.add_handler(CommandHandler("list", handle_list))

    print("Bot is running...")
    app.run_polling() # keeps the bot alive

if __name__ == "__main__":
    main()