from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")

async def send_reminder(context): #This is the function APScheduler calls at reminder time
    job = context.job
    user_id = job.data["user_id"]
    title = job.data["title"]
    event_time = job.data["event_time"]  # formatted string
    await context.bot.send_message(
        chat_id=user_id,
        text=f"🔔 Reminder!\n📌 {title}\n📅 {event_time}"
    )

def schedule_reminder(app, user_id: str, event_id: str, title: str, event_dt: datetime, minutes_before: int):
    reminder_dt = event_dt - timedelta(minutes=minutes_before)
    now = datetime.now(SGT)
    if reminder_dt <= now:
        return  # reminder time already passed, don't schedule
    app.job_queue.run_once(
        send_reminder,
        when=reminder_dt,
        data={
            "user_id": user_id,
            "title": title,
            "event_time": event_dt.strftime("%d %b %Y, %H:%M")
        },
        name=f"reminder_{event_id}"  # named so you can cancel it later if event is deleted
    )