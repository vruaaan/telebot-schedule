# telebot-schedule

A small Telegram bot to let users add, list and delete scheduled events backed by Firestore.

**Tech stack**: Python, python-telegram-bot, Firebase Admin (Firestore), dotenv.

**Status**: Minimal scaffolding present. `add` handler and Firebase service exist; some helper handlers/modules referenced in `main.py` may be missing and require implementation.

**Quick links**
- Main entry: [main.py](main.py)
- Add handler: [bot/handlers/add_event.py](bot/handlers/add_event.py)
- Firebase service: [bot/services/firebase.py](bot/services/firebase.py)
- Dependencies: [requirement.txt](requirement.txt)

## Features
- Create an event with `/add` (natural-language datetime parsing expected).
- List and delete events with `/list` and `/delete` (handlers referenced in `main.py`).
- Events are stored per-user in Firestore under `users/{user_id}/events`.

## Prerequisites
- Python 3.9+
- A Telegram bot token (from BotFather).
- A Firebase project and a service account JSON with Firestore access.

## Install
1. (Recommended) create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirement.txt
```

## Configuration
1. Create a `.env` file in the project root with the following value:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

2. Place your Firebase service account JSON file in the project root as `firebase_service_account.json` (the project currently contains `firebase_service_account.json.json` — rename it to the single `.json` filename expected by the code).

## Run
Start the bot:

```bash
python main.py
```

You should see `Bot is running...` and the bot will poll for updates.

## Usage
- Add an event:

```text
/add Team meeting tomorrow 3pm
```

The `add` handler will parse the date/time from the message text, store the event in Firestore, and reply with a confirmation.

- List events: `/list` (handler referenced in `main.py` — implement `bot/handlers/list_events.py` to call `bot.services.firebase.get_events`).
- Delete event: `/delete <event_id>` (handler referenced in `main.py` — implement `bot/handlers/delete_event.py` to call `bot.services.firebase.delete_event`).

## Notes & TODO
- `bot/utils/parse_datetime.py` is referenced by the add handler but is not present — implement a parser (you can use `dateparser`, `dateutil`, or simple heuristics).
- `bot/handlers/list_events.py` and `bot/handlers/delete_event.py` are referenced in `main.py` but not found in the repository. Add these handlers to complete functionality.
- The Firebase service expects the credentials file at `firebase_service_account.json` — ensure it exists and has proper Firestore permissions.
- The dependency file is named `requirement.txt` (singular). Consider renaming to `requirements.txt` for convention, and pin exact versions if needed.

## Troubleshooting
- Import errors for missing handlers/modules: implement the missing files listed above.
- Firebase initialization errors: check the service account JSON path and contents.
- `python-telegram-bot` version: `requirement.txt` lists `python-telegram-bot==21.x` — ensure compatibility with the v21 API used in `main.py`.

## Contributing
Feel free to open issues or submit PRs to add the missing handlers, improve datetime parsing, and add scheduling/notification features (e.g., deliver reminders with `apscheduler`).

---
If you'd like, I can:
- implement `list_events.py` and `delete_event.py` handlers,
- add a `parse_datetime` utility (with `dateparser` or `dateutil`), or
- fix the credential filename and dependency file naming.
Tell me which one to do next.