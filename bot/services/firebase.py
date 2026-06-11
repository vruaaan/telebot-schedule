import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_service_account.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def _col(user_id: str, month: str):
    return db.collection("users").document(user_id).collection(month)

def add_event(user_id: str, payload: dict):
    date_str = payload["date"]
    month = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B_%Y")
    _, doc_ref = _col(user_id, month).add(payload)
    return doc_ref.id

def get_events(user_id: str, month: str):
    docs = _col(user_id, month).order_by("date").order_by("time").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def get_events_for_week(user_id: str, monday: str, sunday: str):
    month = datetime.strptime(monday, "%Y-%m-%d").strftime("%B_%Y")
    docs = _col(user_id, month)\
             .where("date", ">=", monday)\
             .where("date", "<=", sunday)\
             .order_by("date").order_by("time").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def delete_event(user_id: str, month: str, event_id: str):
    _col(user_id, month).document(event_id).delete()

def get_event(user_id: str, month: str, event_id: str):
    doc = _col(user_id, month).document(event_id).get()
    if doc.exists:
        return doc.to_dict() | {"id": doc.id}
    return None

def update_event(user_id: str, month: str, event_id: str, updates: dict):
    _col(user_id, month).document(event_id).update(updates)
