# import os
# import logging

# FIREBASE_CRED = os.getenv("FIREBASE_CRED_JSON")
# FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
# firebase_initialized = False

# def init_app():
#     global firebase_initialized
#     if firebase_initialized:
#         return
#     try:
#         if FIREBASE_CRED and FIREBASE_DB_URL:
#             import firebase_admin
#             from firebase_admin import credentials, db
#             cred = credentials.Certificate(FIREBASE_CRED)
#             firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})
#             firebase_initialized = True
#             logging.info("Firebase initialized.")
#         else:
#             logging.info("Firebase not configured - running in MOCK mode.")
#     except (ImportError, ValueError, FileNotFoundError) as e:
#         logging.warning("Firebase init failed; running MOCK mode. Error: %s", e)
#         firebase_initialized = False
import os
import logging

firebase_initialized = False
db = None
bucket = None

def init_app():
    """Initialize Firebase Admin SDK using env var FIREBASE_CRED_JSON.
    If the credentials file is not present the module falls back to mock mode
    (db will be None)."""
    global firebase_initialized, db, bucket
    if firebase_initialized:
        return

    cred_path = os.environ.get("FIREBASE_CRED_JSON")
    storage_bucket = os.environ.get("FIREBASE_STORAGE_BUCKET")

    if not cred_path:
        logging.info("FIREBASE_CRED_JSON not set. Running in mock mode.")
        firebase_initialized = False
        db = None
        bucket = None
        return

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, storage

        if not os.path.exists(cred_path):
            raise FileNotFoundError(cred_path)

        cred = credentials.Certificate(cred_path)
        # initialize app only once
        if not firebase_admin._apps:
            if storage_bucket:
                firebase_admin.initialize_app(cred, {"storageBucket": storage_bucket})
            else:
                firebase_admin.initialize_app(cred)

        db = firestore.client()
        try:
            bucket = storage.bucket()
        except Exception:
            bucket = None

        firebase_initialized = True
        logging.info("Firebase initialized from %s", cred_path)
    except Exception as e:
        logging.warning("Firebase init failed; running MOCK mode. Error: %s", e)
        firebase_initialized = False
        db = None
        bucket = None


__all__ = ["init_app", "db", "bucket", "firebase_initialized"]