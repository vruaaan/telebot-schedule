# Telegram Scheduler Bot

A personal Telegram bot for scheduling and managing events, built with Python and Firebase Firestore. Events are stored by month with support for reminders, weekly views, and inline event management.

---

## Features

- `/add` — Schedule an event through a step-by-step conversation (title → date → time → remarks → reminder)
- `/list` — View all events this month with expandable inline buttons to delete or edit
- `/week` — Browse upcoming weeks and view events grouped by day
- `/cancel` — Cancel any in-progress command at any time

---

## Project Structure

```
telegram-scheduler-bot/
│
├── bot/
│   ├── handlers/
│   │   ├── add_event.py        # /add conversation handler
│   │   ├── list_events.py      # /list handler + More/Close inline buttons
│   │   ├── delete_event.py     # Delete confirmation + execution
│   │   └── show_week.py        # /week handler + week selection buttons
│   │
│   ├── services/
│   │   └── firebase.py         # Firestore CRUD operations
│   │
│   ├── jobs/
│   │   └── reminders.py        # APScheduler reminder job logic
│   │
│   └── utils/
│       └── parse_datetime.py   # Datetime parsing utility
│
├── .env                        # Secrets (never commit)
├── .env.example                # Template for setup
├── .gitignore
├── main.py                     # Entry point
├── requirements.txt
└── README.md
```

---

## Firestore Structure

Events are stored by month at the root level — no user layer since this is a personal bot.

```
June_2026/                  ← collection per month
  {event_id}/               ← auto-generated document
    title:            "Team Meeting"
    date:             "2026-06-05"
    time:             "15:00"
    remarks:          "Bring laptop"
    reminder_minutes: 30
    created_at:       "2026-06-04T08:00:00+08:00"

July_2026/
  {event_id}/
    ...
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/telegram-scheduler-bot.git
cd telegram-scheduler-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create your Telegram bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the instructions
3. Copy the API token provided

### 4. Set up Firebase

1. Go to the [Firebase Console](https://console.firebase.google.com) and create a new project
2. Navigate to **Firestore Database** → **Create database** and select region `asia-southeast1`
3. Go to **Project Settings** → **Service Accounts** → **Generate new private key**
4. Save the downloaded file as `firebase_service_account.json` in the project root
5. Go to the [Google Cloud Console](https://console.cloud.google.com) and enable the **Cloud Firestore API** for your project

### 5. Configure environment variables

Copy `.env.example` to `.env` and fill in your token:

```bash
cp .env.example .env
```

`.env`:
```
TELEGRAM_BOT_TOKEN=your_token_here
```

### 6. Run the bot

```bash
python main.py
```

---

## Usage

### Adding an event — `/add`

The bot walks you through each field one at a time:

| Step | Input | Example |
|---|---|---|
| Event name | Free text | `Team Meeting` |
| Date | `ddmmyy` | `050626` for 5 Jun 2026 |
| Time | `HHmm` 24hr | `1500` for 3:00 PM |
| Remarks | Free text or press **No Remarks** | `Bring laptop` |
| Reminder | Choose from buttons | 15 min / 30 min / 1 hour / 1 day / None |

Type `/cancel` at any point to abort.

### Listing events — `/list`

Shows all events for the current month, each with a **More ▼** button.

Pressing **More ▼** expands to show:
- **🗑 Delete** — prompts for confirmation before deleting
- **✏️ Edit** — edit event details
- **▲ Close** — collapses back

### Weekly view — `/week`

Shows buttons for the current and next 3 weeks. Selecting a week displays all events grouped by day, with a back button to return to the week picker.

### Reminders

When adding an event, you can opt in to a reminder notification sent directly to you in Telegram at your chosen time before the event. Reminders are automatically cancelled if the event is deleted.

---

## Requirements

```
python-telegram-bot[job-queue]
firebase-admin
apscheduler
python-dotenv
python-dateutil
```

---

## .gitignore

Make sure these are never committed:

```
.env
firebase_service_account.json
__pycache__/
*.pyc
.venv/
```
