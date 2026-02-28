from google.cloud import storage

_client = None

def get_gcs_client() -> storage.Client:
    global _client

    if _client is None:
        _client = storage.Client.from_service_account_json("./serviceAccountKey.json",)

    return _client
