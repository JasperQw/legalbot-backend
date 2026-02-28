import time
import uuid
from fastapi import UploadFile
from common.gcs import get_gcs_client

gcs_client = get_gcs_client()
GCS_BUCKET = "legalbot-documents"

async def upload_agreement_to_gcs(id: str, file: UploadFile):
        uid = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)
        pdf_bytes = await file.read()

        bucket = gcs_client.bucket(GCS_BUCKET)
        file_key = f"agreements/{id}/{timestamp}-{uid}"
        blob = bucket.blob(file_key)
        blob.upload_from_string(pdf_bytes, content_type="application/pdf")
        return f"gs://{GCS_BUCKET}/{file_key}"