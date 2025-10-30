import os
import logging

FIREBASE_CRED = os.getenv("FIREBASE_CRED_JSON")
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
firebase_initialized = False

def init_app():
    global firebase_initialized
    if firebase_initialized:
        return
    try:
        if FIREBASE_CRED and FIREBASE_DB_URL:
            import firebase_admin
            from firebase_admin import credentials, db
            cred = credentials.Certificate(FIREBASE_CRED)
            firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})
            firebase_initialized = True
            logging.info("Firebase initialized.")
        else:
            logging.info("Firebase not configured - running in MOCK mode.")
    except Exception as e:
        logging.warning("Firebase init failed; running MOCK mode. Error: %s", e)
        firebase_initialized = False
