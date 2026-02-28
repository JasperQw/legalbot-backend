import os
import json

from dotenv import load_dotenv

from common.pubsub import get_pubsub_client
from common.schemas import AgreementWriteTaskType, CreateNewAgreementRequest

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
AGREEMENT_ANALYSIS_TOPIC_ID = "agreement-analysis"
AGREEMENT_WRITE_TOPIC_ID = "agreement-write"

pubsub_client = get_pubsub_client()

async def publish_agreement_analysis_message(id: str):
    topic_path = pubsub_client.topic_path(GCP_PROJECT_ID, AGREEMENT_ANALYSIS_TOPIC_ID)
    payload = {"doc_id": id}
    payload_json = json.dumps(payload)
    pubsub_client.publish(topic_path, data=payload_json.encode("utf-8"))

async def publish_revise_agreement_message(id: str, query: str):
    topic_path = pubsub_client.topic_path(GCP_PROJECT_ID, AGREEMENT_WRITE_TOPIC_ID)
    payload = {"task_type": AgreementWriteTaskType.REVISE.value, "agreement_id": id, "query": query}
    payload_json = json.dumps(payload)
    pubsub_client.publish(topic_path, data=payload_json.encode("utf-8"))

async def publish_create_new_agreement_message(id: str, data: CreateNewAgreementRequest):
    topic_path = pubsub_client.topic_path(GCP_PROJECT_ID, AGREEMENT_WRITE_TOPIC_ID)
    payload = {
        "task_type": AgreementWriteTaskType.CREATE.value, 
        "agreement_id": id, 
        "address": data.address, 
        "start_date": data.start_date, 
        "duration": data.duration, 
        "rent": data.rent, 
        "special_clauses": data.special_clauses
    }
    payload_json = json.dumps(payload)
    pubsub_client.publish(topic_path, data=payload_json.encode("utf-8"))