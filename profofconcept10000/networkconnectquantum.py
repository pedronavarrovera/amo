# Bridge-Embedded Block Diagonal Merge (BEBDiM) 
# In order to interconnect 2 payment networks, the following process is innovated. This process is named "Bridge-Embedded Block Diagonal Merge"
# A block matrix composition, is specifically a type of block diagonal concatenation or matrix embedding.
# Operation: Block Matrix Construction / Embedding also named 'Bridge-Embedded Block Diagonal Merge'.
# Block Diagonal Merge: It means that you are performing a block diagonal embedding of two square matrices (A and B) into a larger square matrix.
# Bridge Embedding: It means that you then explicitly connect the two sub-networks by adding a "bridge" element 
# (e.g., a 1) between a node in A and a node in B — in this case, at position (0, a) — effectively simulating inter-network connectivity
# If you have two matrices A and B, and you want to place A in the top-left corner and B in the bottom-right corner of a new, larger matrix — with zeros elsewhere
# — you're constructing a block diagonal matrix (with one block in each corner).
# Example
# Let:
# A be a matrix of shape (m, n)
# B be a matrix of shape (p, q)
# Then the resulting matrix C will have shape (m + p, n + q), and look like this:
# C=[A 0]
#   [0 B]
# Where 0 represents zero matrices of appropriate dimensions to fill the rest of the space.
# In addition, in order to connect the 2 networks for instance the firts items of each network need to be connected (e.g. this is managed by the merge authority)

# The goal is to build a square matrix D such that:
# Matrix A (shape (a, a)) is placed in the top-left
# Matrix B (shape (b, b)) is placed in the bottom-right
# The full matrix is of shape (a + b, a + b)
# Zeros fill the rest
# Then set the element at position (0, a) (i.e., just right of the last column of A, in the first row) to 1
# example:
#[[ 1.  2.  1.  0.  0.]
# [ 3.  4.  0.  0.  0.]
# [ 0.  0.  5.  6.  7.]
# [ 0.  0.  8.  9. 10.]
# [ 0.  0. 11. 12. 13.]]
# 
# Post-Quantum Encryption Flow
# This flow encrypts the names in node_namesD using encrypt_message and decrypt_message functions located in quantum.py
# This code combines PyCryptodome (for AES encryption) with a post-quantum key exchange using quantcrypt,
# so you get a full quantum-safe encryption flow

import numpy as np
from core_old import dijkstra, dijkstra_to_target
from quantum import encrypt_message, decrypt_message, shared_secret_sender, shared_secret_receiver

def construct_matrix_with_A_top_left(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    a = A.shape[0]
    b = B.shape[0]
    assert A.shape == (a, a), "Matrix A must be square"
    assert B.shape == (b, b), "Matrix B must be square"

    D = np.zeros((a + b, a + b))
    D[:a, :a] = A
    D[a:, a:] = B
    D[0, a] = 1
    return D

def construct_node_name_with_A_B(node_namesA: dict, node_namesB: dict) -> dict:
    node_namesD = {i: name for i, name in node_namesA.items()}
    offset = len(node_namesA)
    node_namesD.update({i + offset: name for i, name in node_namesB.items()})
    return node_namesD

def encrypt_node_names(node_names: dict, key: bytes) -> dict:
    return {i: encrypt_message(name, key) for i, name in node_names.items()}

def decrypt_node_names(encrypted_names: dict, key: bytes) -> dict:
    return {i: decrypt_message(enc, key) for i, enc in encrypted_names.items()}

# Matrix A and B
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6, 7], [8, 9, 10], [11, 12, 13]])
D = construct_matrix_with_A_top_left(A, B)

# Node names
node_namesA = {0: "Pedro", 1: "Juan"}
node_namesB = {0: "Lucas", 1: "Sofia", 2: "Lourdes"}
node_namesD = construct_node_name_with_A_B(node_namesA, node_namesB)

# Encrypt node names with shared secret from quantum.py
encrypted_node_namesD = encrypt_node_names(node_namesD, shared_secret_sender)

print("🔐 Encrypted node names:")
for k, v in encrypted_node_namesD.items():
    print(f"{k}: {v}")

# Run Dijkstra using encrypted labels
dijkstra(D, 0, encrypted_node_namesD)
dijkstra_to_target(D, 0, 4, encrypted_node_namesD)

# Optional: decrypt after analysis
decrypted_node_namesD = decrypt_node_names(encrypted_node_namesD, shared_secret_receiver)
print("\n🔓 Decrypted node names:")
for k, v in decrypted_node_namesD.items():
    print(f"{k}: {v}")


# Generate random symmetric matrices A1 (10x10) and B1 (20x20)
np.random.seed(42)
A1 = np.random.randint(1, 10, size=(10, 10))
B1 = np.random.randint(1, 10, size=(20, 20))
A1 = (A1 + A1.T) // 2  # Make symmetric. A1.T or B1.T, This is the transpose of the matrix. For a matrix A1, the transpose A1.T flips it over its diagonal:A1[i][j] becomes A1[j][i].
B1 = (B1 + B1.T) // 2  # Make symmetric
# The above expresions are used to make the matrices symmetric, 
# which is especially important when modeling undirected graphs, such as payment networks where connections are mutual
# A symmetric adjacency matrix represents an undirected graph, where a connection from node A to B implies a connection from B to A
# It's often needed in algorithms like Dijkstra when analyzing undirected networks (e.g., peer-to-peer payment systems)

# Construct full matrix with bridge
D1 = construct_matrix_with_A_top_left(A1, B1)

# Auto-generate node names
node_namesA1 = {i: f"Alice_{i}" for i in range(10)}
node_namesB1 = {i: f"Bob_{i}" for i in range(20)}
node_namesD1 = construct_node_name_with_A_B(node_namesA1, node_namesB1)

# Encrypt node names
encrypted_node_namesD1 = encrypt_node_names(node_namesD1, shared_secret_sender)

print("🔐 Encrypted node names:")
for k, v in encrypted_node_namesD.items():
    print(f"{k}: {v}")

# Run Dijkstra from node 0 to all others
dijkstra(D1, 0, encrypted_node_namesD1)
dijkstra_to_target(D1, 0, 15, encrypted_node_namesD1)  # Example: target is node 15

# Optional: decrypt after analysis
decrypted_node_namesD1 = decrypt_node_names(encrypted_node_namesD1, shared_secret_receiver)
print("\n🔓 Decrypted node names:")
for k, v in decrypted_node_namesD1.items():
    print(f"{k}: {v}")