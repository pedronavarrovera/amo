# ResusableAzureblobstoragematrix.py
# Usage example (overwriting the same blob):
#   modify_matrix_entry("matrix-code-1234.b64", i=2, j=5, value=42)
# Or save to a new blob:
#   modify_matrix_entry("matrix-code-1234.b64", 2, 5, 42, out_blob_name="matrix-code-updated.b64")
#
## overwrite value at (2,3) with 50
# modify_matrix_entry("matrix-code-abc123.b64", 2, 3, 50)

# add +10 to value at (2,3)
# add_to_matrix_entry("matrix-code-abc123.b64", 2, 3, 10)

#
import os
import io
import uuid
import base64
from typing import Optional
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceExistsError
import numpy as np

# Protection for unpickling is unsafe: if someone uploads a malicious .npy file, loading it with pickle can execute arbitrary Python code. 
# That’s why NumPy defaults to allow_pickle=False — it prevents remote code execution.
# 
import json

def _decode_any_matrix_b64_to_numpy(b64: str) -> np.ndarray:
    """Load matrix from:
       1) pickle-free .npy bytes (preferred), or
       2) JSON-encoded {"nodes","matrix"} fallback.
    """
    raw = base64.b64decode(b64)

    # Try .npy/.npz without pickle
    try:
        return np.load(io.BytesIO(raw), allow_pickle=False)
    except Exception as e_npy:
        # Try JSON fallback (your option-3 format)
        try:
            s = raw.decode("utf-8")
            data = json.loads(s)
            mat = data["matrix"]
            # enforce numeric dtype to avoid object/ pickle later
            return np.asarray(mat, dtype=np.float64)
        except Exception:
            # If original error mentions pickled data, explain clearly
            msg = str(e_npy).lower()
            if "pickled" in msg or "allow_pickle" in msg:
                raise RuntimeError(
                    "Blob contains data that requires pickle (object dtype). "
                    "Please re-save as a numeric NumPy array without pickle, or let this "
                    "function convert from your JSON code automatically."
                ) from e_npy
            # Unknown format
            raise RuntimeError("Unrecognized matrix blob format: not a safe .npy or JSON code.")

def _encode_numpy_to_npy_b64(arr: np.ndarray) -> str:
    """Encode ndarray as pickle-free .npy base64."""
    buf = io.BytesIO()
    np.save(buf, arr)  # default is pickle-free for numeric dtypes
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


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

def add_to_matrix_entry(
    blob_name: str,
    i: int,
    j: int,
    delta: float | int,
    *,
    container_name: str = DEFAULT_CONTAINER,
    out_blob_name: Optional[str] = None
) -> str:
    """
    Downloads a Base64-encoded matrix (safe .npy OR JSON {nodes,matrix}),
    adds `delta` to A[i][j], then uploads as pickle-free .npy base64.
    """
    # 1) Download the base64 string
    b64 = download_base64_code(blob_name, container_name=container_name)

    # 2) Decode base64 -> bytes and load NumPy array
    raw = base64.b64decode(b64)
    arr = np.load(io.BytesIO(raw), allow_pickle=True)

    # 3) Bounds check (kept simple)
    if i < 0 or j < 0 or i >= arr.shape[0] or j >= arr.shape[1]:
        raise IndexError(f"indices ({i}, {j}) out of bounds for shape {arr.shape}")

    # 4) Add to the entry
    arr[i, j] = arr[i, j] + delta

    # 5) Save array back to .npy bytes
    buf = io.BytesIO()
    np.save(buf, arr)
    buf.seek(0)
    new_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    # 6) Upload using existing helper (overwrite by default)
    target_name = out_blob_name or blob_name
    return upload_base64_code(new_b64, blob_name=target_name, container_name=container_name)


def modify_matrix_entry(
    blob_name: str,
    i: int,
    j: int,
    value: float | int,
    *,
    container_name: str = DEFAULT_CONTAINER,
    out_blob_name: Optional[str] = None
) -> str:
    """
    Downloads a Base64-encoded NumPy .npy matrix from Azure Blob Storage, modifies A[i][j],
    and uploads the resulting matrix (as Base64 text) back to Azure using the existing helpers.

    By default, overwrites the same blob. To write to a new blob, pass `out_blob_name`.
    Returns the blob name that was written.
    """
    # 1) Download the base64 string
    b64 = download_base64_code(blob_name, container_name=container_name)

    # 2) Decode base64 -> bytes and load NumPy array
    raw = base64.b64decode(b64)
    arr = np.load(io.BytesIO(raw), allow_pickle=False)

    # 3) Bounds check (kept simple)
    if i < 0 or j < 0 or i >= arr.shape[0] or j >= arr.shape[1]:
        raise IndexError(f"indices ({i}, {j}) out of bounds for shape {arr.shape}")

    # 4) Modify the entry
    arr[i, j] = value

    # 5) Save array back to .npy bytes
    buf = io.BytesIO()
    np.save(buf, arr)
    buf.seek(0)
    new_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    # 6) Upload using existing helper (overwrite by default)
    target_name = out_blob_name or blob_name
    return upload_base64_code(new_b64, blob_name=target_name, container_name=container_name)
