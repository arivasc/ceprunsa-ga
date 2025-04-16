from google.cloud import storage
from datetime import timedelta
from django.conf import settings

def get_signed_url(blob_path, expiration_minutes=60):
  client = storage.Client(credentials=getattr(settings, "GS_CREDENTIALS", None))
  bucket = client.bucket(settings.GS_BUCKET_NAME)
  blob = bucket.blob(blob_path)

  return blob.generate_signed_url(
    version="v4",
    expiration=timedelta(minutes=expiration_minutes),
    method="GET",
  )