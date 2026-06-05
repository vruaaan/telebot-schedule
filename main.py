from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters
from bot.handlers.add_event import (
    handle_add, handle_title, handle_date, handle_time,
    handle_remarks, handle_no_remarks, handle_reminder_choice, handle_cancel,
    TITLE, DATE, TIME, REMARKS, REMINDER
)
from bot.handlers.list_events import handle_list, handle_more, handle_close
from bot.handlers.delete_event import handle_delete_confirm, handle_delete_execute
from bot.handlers.show_week import handle_show_week, handle_week_selected, handle_back_to_weeks
from dotenv import load_dotenv
import os
load_dotenv() #reads the .env file and loads bot token into environment

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    add_conversation = ConversationHandler( #/add conversation
        entry_points=[CommandHandler("add", handle_add)],
        states={TITLE:[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title)],
                DATE:[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date)],
                TIME:[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_time)],
                REMARKS:[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_remarks),
                        CallbackQueryHandler(handle_no_remarks, pattern="^no_remarks$")],
                REMINDER: [CallbackQueryHandler(handle_reminder_choice, pattern="^reminder_")]
                },
        fallbacks=[CommandHandler("cancel", handle_cancel)]
    )
    app.add_handler(add_conversation)

    # /list and its inline buttons
    app.add_handler(CommandHandler("list", handle_list))
    app.add_handler(CallbackQueryHandler(handle_more, pattern=r"^more\|"))
    app.add_handler(CallbackQueryHandler(handle_close, pattern=r"^close\|"))

    # delete buttons (triggered from list)
    app.add_handler(CallbackQueryHandler(handle_delete_confirm, pattern=r"^delete\|"))
    app.add_handler(CallbackQueryHandler(handle_delete_execute, pattern=r"^confirmdelete\|"))

    # /week and its inline buttons
    app.add_handler(CommandHandler("week", handle_show_week))
    app.add_handler(CallbackQueryHandler(handle_week_selected, pattern="^week_"))
    app.add_handler(CallbackQueryHandler(handle_back_to_weeks, pattern="^back_to_weeks$"))

    print("Bot is running...")
    app.run_polling()
 # keeps the bot alive

if __name__ == "__main__":
    main()