# Post-Quantum Encryption Flow
# This code combines PyCryptodome (for AES encryption) with a post-quantum key exchange using quantcrypt,
#  so you get a full quantum-safe encryption flow
# Post-Quantum Key Exchange: MLKEM_512 (Kyber)
# Symmetric Encryption: AES-256 (CBC) via PyCryptodome
# Quantum-safe end-to-end encryption
# Post-quantum safe: Even if an attacker intercepts the ciphertext, they cannot derive the shared secret
# unless they can break Kyber (which resists quantum attacks)
# ML-KEM-512, also known as Kyber512, is a post-quantum cryptographic algorithm designed for key encapsulation 
# — the secure exchange of encryption keys — even in the presence of quantum computers
# ML-KEM = Module-Lattice–based Key Encapsulation Mechanism
# Selected by NIST in 2022 as the primary standard for post-quantum public key encryption and key exchange.
# Lattice-based cryptography is a type of cryptographic system that builds its security on the hardness of certain mathematical problems involving lattices
#  — regular grid-like arrangements of points in multi-dimensional space

from quantcrypt.kem import MLKEM_512
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes
import base64

# 1. Key Encapsulation with ML-KEM-512 (Kyber512)

kem = MLKEM_512()
public_key, secret_key = kem.keygen()       # generates a public/private key pair

# from the sender’s side
ciphertext, shared_secret_sender = kem.encaps(public_key)       # uses the public key to generate a ciphertext and a shared secret (from the sender’s side)

# the receiver’s side
shared_secret_receiver = kem.decaps(secret_key, ciphertext)     # uses the private key and the ciphertext to reconstruct the same shared secret (on the receiver’s side).

assert shared_secret_sender == shared_secret_receiver           # ensures that both sides now hold identical shared secrets, without ever transmitting the key directly — crucial for quantum-safe communication

# 2. AES-256 Encryption using shared post-quantum key

def encrypt_message(message: str, key: bytes) -> str:
    cipher = AES.new(key[:32], AES.MODE_CBC)  # Use 32 bytes for AES-256
    ct = cipher.encrypt(pad(message.encode(), AES.block_size))      # Encrypts using AES-256 in CBC mode (using the first 32 bytes of the shared key). The message is padded to match the AES block size (16 bytes).
    return base64.b64encode(cipher.iv + ct).decode()                # The result is Base64-encoded to make it safe for transmission or storage. A random IV (Initialization Vector) is automatically generated and prepended to the ciphertext

def decrypt_message(enc: str, key: bytes) -> str:
    data = base64.b64decode(enc)            # decodes the Base64 string
    iv, ct = data[:16], data[16:]           # Extracts the IV and the ciphertext
    cipher = AES.new(key[:32], AES.MODE_CBC, iv)        # Uses AES with the same key and IV to decrypt the message
    return unpad(cipher.decrypt(ct), AES.block_size).decode()       # Removes the padding and converts the plaintext back to a string

# ---- Quantum-safe message transmission during traversal ----
def send_secure_message(sender: str, receiver: str, message: str, key: bytes) -> str:
    print(f"\n🔐 Sending from {sender} to {receiver}:")
    encrypted_msg = encrypt_message(message, key)
    print(f"Encrypted: {encrypted_msg}")
    decrypted_msg = decrypt_message(encrypted_msg, key)
    print(f"Decrypted: {decrypted_msg}")
    return encrypted_msg

# 3. Usage Example
plaintext = "This is a quantum-safe secret message."
encrypted = encrypt_message(plaintext, shared_secret_sender)
decrypted = decrypt_message(encrypted, shared_secret_receiver)

print("Original:", plaintext)
# print("Public Key:", public_key)
# print("Secret Key:", secret_key)
print("Encrypted (base64):", encrypted)
print("Decrypted:", decrypted)
