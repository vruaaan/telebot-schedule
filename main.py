from telegram.ext import Application, CommandHandler
from bot.handlers.add_event import handle_add
from bot.handlers.list_events import handle_list
from bot.handlers.delete_event import handle_delete
from dotenv import load_dotenv
import os

load_dotenv() #reads the .env file and loads bot token into environment

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build() #creates the bot using telegram token
    app.add_handler(CommandHandler("add", handle_add))
    app.add_handler(CommandHandler("list", handle_list))
    app.add_handler(CommandHandler("delete", handle_delete))

    print("Bot is running...")
    app.run_polling() # keeps the bot alive

if __name__ == "__main__":
    main()