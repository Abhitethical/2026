
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from vercel.blob import sync as blob
from pathlib import PurePosixPath
import uuid


@deconstructible
class VercelBlobStorage(Storage):

    def _save(self, name, content):
        extension = PurePosixPath(name).suffix.lower()
        filename = f"{uuid.uuid4().hex}{extension}"
        pathname = f"uploads/{filename}"

        result = blob.put_blob(
            pathname,
            content.chunks(),
            access="public",
            content_length=content.size,
            add_random_suffix=True,
            content_type=getattr(content, "content_type", None),
        )

        return result.pathname

    def url(self, name):
        if name.startswith("https://"):
            return name

        return blob.head_blob(name).url

    def exists(self, name):
        try:
            blob.head_blob(name)
            return True
        except Exception:
            return False

    def delete(self, name):
        blob.delete_blob(name)
