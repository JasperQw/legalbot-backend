from google.cloud import firestore

_client = None

def get_firestore_client() -> firestore.Client:
    global _client

    if _client is None:
        _client = firestore.Client.from_service_account_json("./serviceAccountKey.json",)

    return _client
