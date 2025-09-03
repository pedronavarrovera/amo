# ResusableAzureblobstoragematrix.py
import os
import io
import uuid
from typing import Optional
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceExistsError

# ---------- Config ----------
def _get_connection_string() -> str:
    try:
        return os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    except KeyError as e:
        raise RuntimeError(
            "AZURE_STORAGE_CONNECTION_STRING is not set. "
            "Set it in your environment or .env file."
        ) from e

DEFAULT_CONTAINER = "matrices"  # must be lowercase 3–63 chars

# ---------- Core helpers ----------
def _get_container(container_name: str = DEFAULT_CONTAINER):
    """
    Returns a container client. Creates the container if it does not exist.
    """
    conn_str = _get_connection_string()
    svc = BlobServiceClient.from_connection_string(conn_str)
    container = svc.get_container_client(container_name)
    try:
        container.create_container()
    except ResourceExistsError:
        pass
    return container

# ---------- Public API ----------
def upload_base64_code(
    base64_code: str,
    blob_name: Optional[str] = None,
    container_name: str = DEFAULT_CONTAINER
) -> str:
    """
    Uploads a Base64-encoded matrix code as plain text to Azure Blob Storage.
    Returns the blob name that was written.
    """
    container = _get_container(container_name)
    if not blob_name:
        blob_name = f"matrix-code-{uuid.uuid4()}.b64"

    blob = container.get_blob_client(blob_name)
    blob.upload_blob(
        base64_code.encode("utf-8"),
        overwrite=True,
        content_settings=ContentSettings(content_type="text/plain; charset=utf-8"),
        timeout=30
    )
    return blob_name

def download_base64_code(
    blob_name: str,
    container_name: str = DEFAULT_CONTAINER
) -> str:
    """
    Downloads a Base64-encoded matrix code (stored as text) from Azure Blob Storage.
    Returns the Base64 string.
    """
    container = _get_container(container_name)
    blob = container.get_blob_client(blob_name)
    data = blob.download_blob(timeout=30).readall()
    return data.decode("utf-8")

def list_codes(container_name: str = DEFAULT_CONTAINER) -> list[str]:
    """
    Lists blobs in the container (handy for discovering names).
    """
    container = _get_container(container_name)
    return [b.name for b in container.list_blobs()]

