# Generate a 100×100 NumPy matrix of random positive integers.
# Serialize it (.npy) into memory.
# Upload to an Azure Blob Container.
# Download back and restore into NumPy
# Set environment variables (for safety, don’t hardcode keys):
# export AZURE_STORAGE_CONNECTION_STRING="your-connection-string" for instance DefaultEndpointsProtocol=https;AccountName=amomatrixstorage;AccountKey=ic1fy617RPPCHKiwyIck1kG6a7Afrc8Z4gcd+TSjN/Kz81naAfCUygFHUdjGjLUES/eCveLJl/N7+AStmb9u4Q==;EndpointSuffix=core.windows.net

import os, io, uuid, numpy as np
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError

# --- config ---
CONN_STR = os.environ["AZURE_STORAGE_CONNECTION_STRING"]  # or paste your conn string
CONTAINER = "matrices"  # must be lowercase, 3–63 chars

# --- clients ---
svc = BlobServiceClient.from_connection_string(CONN_STR)

# create container if it doesn't exist
container = svc.get_container_client(CONTAINER)
if not container.exists():
    svc.create_container(CONTAINER)  # private by default

# --- make a 100x100 positive int matrix ---
arr = np.random.randint(1, 1000, size=(100, 100), dtype=np.int32)

# serialize as .npy in-memory
buf = io.BytesIO()
np.save(buf, arr)
buf.seek(0)

# --- upload ---
blob_name = f"matrix-{uuid.uuid4()}.npy"
blob = container.get_blob_client(blob_name)
blob.upload_blob(buf.getvalue(), overwrite=True)
print("✅ uploaded:", blob_name)

# --- download & restore ---
data = blob.download_blob().readall()
restored = np.load(io.BytesIO(data))
print("✅ restored shape:", restored.shape, "sample:", restored[0, :10])
