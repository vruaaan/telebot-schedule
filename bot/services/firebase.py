import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_service_account.json")
    firebase_admin.initialize_app(cred)

db = firestore.client() # to access the database 

''' format of payload
{"title": title, 
"date": dt.strftime("%Y-%m-%d"),   
"time": dt.strftime("%H:%M"),          
"created_at": datetime.now(SGT).isoformat(),
"remarks": context.user_data.get("remarks", ""),
"reminder_minutes": reminder_minutes  # None if no reminder}
'''

'''structure of database:
month -> event id -> event details
'''

def add_event(payload: dict): #redone
    date_str = payload["date"]  # "2026-06-05"
    month = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B_%Y")  # "June_2026"
    _, doc_ref = db.collection(month).add(payload)
    return doc_ref.id

def get_events(month: str): #get data by month
    docs = db.collection(month).order_by("date").order_by("time").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def get_events_for_week(monday: str, sunday: str): # monday and sunday are "YYYY-MM-DD" strings
    month = datetime.strptime(monday, "%Y-%m-%d").strftime("%B_%Y")
    docs = db.collection(month)\
             .where("date", ">=", monday)\
             .where("date", "<=", sunday)\
             .order_by("date").order_by("time").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def delete_event(month: str, event_id: str):
    db.collection(month).document(event_id).delete()

def get_event(month: str, event_id: str):
    doc = db.collection(month).document(event_id).get()
    if doc.exists:
        return doc.to_dict() | {"id": doc.id}
    return None

def update_event(month: str, event_id: str, updates: dict):
    db.collection(month).document(event_id).update(updates)