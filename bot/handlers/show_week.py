from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.services.firebase import get_events_for_week
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")

def get_week_mondays(n_weeks=4):
    """Returns the Monday of the current week and the next n_weeks-1 weeks"""
    today = datetime.now(SGT).date()
    # Find this week's Monday (weekday() = 0 for Monday)
    this_monday = today - timedelta(days=today.weekday())
    return [this_monday + timedelta(weeks=i) for i in range(n_weeks)]

async def handle_show_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows buttons for upcoming weeks"""
    mondays = get_week_mondays(n_weeks=4)

    keyboard = []
    for monday in mondays:
        sunday = monday + timedelta(days=6)
        label = f"{monday.strftime('%d %b')} – {sunday.strftime('%d %b')}"
        callback = f"week_{monday.strftime('%Y-%m-%d')}"
        keyboard.append([InlineKeyboardButton(label, callback_data=callback)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📆 Select a week to view:", reply_markup=reply_markup)

async def handle_week_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows all events for the selected week"""
    query = update.callback_query
    await query.answer()

    monday_str = query.data.split("_", 1)[1]  # extract from "week_2026-06-01"
    monday = datetime.strptime(monday_str, "%Y-%m-%d").date()
    sunday = monday + timedelta(days=6)

    user_id = str(query.from_user.id)
    events = get_events_for_week(user_id, monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d"))

    header = f"📆 {monday.strftime('%d %b')} – {sunday.strftime('%d %b %Y')}\n\n"

    if not events:
        await query.edit_message_text(header + "📭 No events this week.")
        return

    # Group events by day
    from collections import defaultdict
    by_day = defaultdict(list)
    for e in events:
        by_day[e["date"]].append(e)

    lines = []
    for date_str in sorted(by_day.keys()):
        date_label = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %d %b")  # e.g. "Monday, 02 Jun"
        lines.append(f"📅 {date_label}")
        for e in by_day[date_str]:
            remarks = f" — {e['remarks']}" if e.get("remarks") else ""
            lines.append(f"  • {e['time']} {e['title']}{remarks}")
        lines.append("")  # blank line between days

    # Add back button to return to week picker
    keyboard = [[InlineKeyboardButton("◀ Back to weeks", callback_data="back_to_weeks")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(header + "\n".join(lines), reply_markup=reply_markup)

async def handle_back_to_weeks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Goes back to the week picker"""
    query = update.callback_query
    await query.answer()

    mondays = get_week_mondays(n_weeks=4)
    keyboard = []
    for monday in mondays:
        sunday = monday + timedelta(days=6)
        label = f"{monday.strftime('%d %b')} – {sunday.strftime('%d %b')}"
        callback = f"week_{monday.strftime('%Y-%m-%d')}"
        keyboard.append([InlineKeyboardButton(label, callback_data=callback)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📆 Select a week to view:", reply_markup=reply_markup)