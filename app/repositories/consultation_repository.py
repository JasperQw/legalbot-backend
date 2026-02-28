import uuid
import time
from common.firestore import get_firestore_client

CONSULTATION_COLLECTION = "consultation"
firestore_client = get_firestore_client()

async def select_all_consultation_history():
    docs = firestore_client.collection(CONSULTATION_COLLECTION).get()
    data = []
    for doc in docs:
        doct_dict = doc.to_dict()
        data.append({
            "id": doct_dict["id"],
            "text": doct_dict["text"],
            "role": doct_dict["role"],
            "createdAt": doct_dict["createdAt"],
        })
    return data

async def create_consultation_message(text: str, role: str):
    uid = str(uuid.uuid4())
    createdAt = int(time.time() * 1000)
    new_message = {
        "id": uid,
        "text": text,
        "role": role,
        "createdAt": createdAt
    }

    firestore_client.collection(CONSULTATION_COLLECTION).add(new_message)

    return new_message