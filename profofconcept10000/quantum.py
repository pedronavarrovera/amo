# Post-Quantum Encryption Flow
# This code combines PyCryptodome (for AES encryption) with a post-quantum key exchange using quantcrypt,
#  so you get a full quantum-safe encryption flow
# Post-Quantum Key Exchange: MLKEM_512 (Kyber)
# Symmetric Encryption: AES-256 (CBC) via PyCryptodome
# Quantum-safe end-to-end encryption
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
public_key, secret_key = kem.keygen()
ciphertext, shared_secret_sender = kem.encaps(public_key)
shared_secret_receiver = kem.decaps(secret_key, ciphertext)

assert shared_secret_sender == shared_secret_receiver

# 2. AES-256 Encryption using shared post-quantum key
def encrypt_message(message: str, key: bytes) -> str:
    cipher = AES.new(key[:32], AES.MODE_CBC)  # Use 32 bytes for AES-256
    ct = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + ct).decode()

def decrypt_message(enc: str, key: bytes) -> str:
    data = base64.b64decode(enc)
    iv, ct = data[:16], data[16:]
    cipher = AES.new(key[:32], AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size).decode()

# 3. Usage Example
plaintext = "This is a quantum-safe secret message."
encrypted = encrypt_message(plaintext, shared_secret_sender)
decrypted = decrypt_message(encrypted, shared_secret_receiver)

print("Original:", plaintext)
print("Encrypted (base64):", encrypted)
print("Decrypted:", decrypted)
