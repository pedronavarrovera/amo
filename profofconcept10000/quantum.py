#This Python code uses a post-quantum encryption algorithm via the pqcrypto library, 
# which provides access to NIST-approved post-quantum cryptographic algorithms such as Kyber (KEM - Key Encapsulation Mechanism).
from pqcrypto.kem import kyber512
import base64

# Generate a new Kyber key pair (public key for encryption, secret key for decryption)
public_key, secret_key = kyber512.generate_keypair()

# Simulate a sender encrypting a shared secret using the public key
ciphertext, shared_secret_sender = kyber512.encrypt(public_key)

# Simulate a receiver decrypting the ciphertext using the private key
shared_secret_receiver = kyber512.decrypt(ciphertext, secret_key)

# Check that both shared secrets are the same
assert shared_secret_sender == shared_secret_receiver

# Optional: Use the shared secret to encrypt your message (e.g., AES-256)
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# Encrypt a message using the shared secret
def encrypt_message(message: str, key: bytes) -> bytes:
    cipher = AES.new(key[:32], AES.MODE_CBC)  # use first 32 bytes of Kyber's shared secret
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + ct_bytes)

# Decrypt a message using the shared secret
def decrypt_message(ciphertext_b64: bytes, key: bytes) -> str:
    data = base64.b64decode(ciphertext_b64)
    iv, ct = data[:16], data[16:]
    cipher = AES.new(key[:32], AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode()

# Example message
plaintext = "Quantum-resistant message from the future."

# Encrypt and decrypt
encrypted = encrypt_message(plaintext, shared_secret_sender)
decrypted = decrypt_message(encrypted, shared_secret_receiver)

print("Original message:", plaintext)
print("Encrypted message (base64):", encrypted.decode())
print("Decrypted message:", decrypted)
