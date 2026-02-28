from google.cloud import pubsub_v1

_client = None

def get_pubsub_client() -> pubsub_v1.PublisherClient:
    global _client

    if _client is None:
        _client = pubsub_v1.PublisherClient.from_service_account_json("./serviceAccountKey.json",)

    return _client