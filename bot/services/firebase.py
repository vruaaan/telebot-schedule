import firebase_admin
from firebase_admin import credentials, firestore
import os

cred = credentials.Certificate("firebase_service_account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def add_event(user_id: str, event: dict):
    db.collection("users").document(user_id)\
      .collection("events").add(event)

def get_events(user_id: str):
    docs = db.collection("users").document(user_id)\
             .collection("events")\
             .order_by("datetime").stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def delete_event(user_id: str, event_id: str):
    db.collection("users").document(user_id)\
      .collection("events").document(event_id).delete()