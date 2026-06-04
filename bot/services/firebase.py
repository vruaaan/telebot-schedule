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

def add_event(payload: dict): #redone
    date_str = payload["date"]
    month = date_str.datetime.strptime(date_str, "%Y-%m-%d").strftime("%B")
    _, doc_ref = db.collection(month).add(payload)
    return doc_ref.id  

def get_events(user_id: str):
    docs = db.collection("users").document(user_id)\
             .collection("events")\
             .order_by("date").order_by("time").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def get_events_for_week(user_id: str, monday: str, sunday: str):
    # monday and sunday are "YYYY-MM-DD" strings
    docs = db.collection("users").document(user_id)\
             .collection("events")\
             .where("date", ">=", monday)\
             .where("date", "<=", sunday)\
             .order_by("date").order_by("time").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def delete_event(user_id: str, event_id: str):
    db.collection("users").document(user_id)\
      .collection("events").document(event_id).delete()

def get_event(user_id: str, event_id: str):
    doc = db.collection("users").document(user_id)\
            .collection("events").document(event_id).get()
    if doc.exists:
        return doc.to_dict() | {"id": doc.id}
    return None

def update_event(user_id: str, event_id: str, updates: dict):
    db.collection("users").document(user_id)\
      .collection("events").document(event_id).update(updates)