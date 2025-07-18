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
import numpy as np
from core_igraph import dijkstra_igraph_all, dijkstra_igraph_to_target  # Updated import

def construct_matrix_with_A_top_left(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    a = A.shape[0]
    b = B.shape[0]

    assert A.shape == (a, a), "Matrix A must be square"
    assert B.shape == (b, b), "Matrix B must be square"

    D = np.zeros((a + b, a + b))
    D[:a, :a] = A
    D[a:, a:] = B
    D[0, a] = 1  # Connect node 0 in A to node 0 in B

    return D

def construct_node_name_with_A_B(node_namesA: dict, node_namesB: dict) -> dict:
    node_namesD = {i: name for i, name in node_namesA.items()}
    offset = len(node_namesA)
    node_namesD.update({i + offset: name for i, name in node_namesB.items()})
    return node_namesD

# Example usage:
A = np.array([[1, 2], [3, 4]])  # 2x2
B = np.array([[5, 6, 7], [8, 9, 10], [11, 12, 13]])  # 3x3

D = construct_matrix_with_A_top_left(A, B)

node_namesA = {0: "Pedro", 1: "Juan"}
node_namesB = {0: "Lucas", 1: "Sofia", 2: "Lourdes"}
node_namesD = construct_node_name_with_A_B(node_namesA, node_namesB)

print("Matrix A:")
print(A)
print("Matrix B:")
print(B)
print("Combined node names:")
print(node_namesD)
print("Combined matrix D:")
print(D)

# Run updated Dijkstra functions
dijkstra_igraph_all(D, 0, node_namesD)
dijkstra_igraph_to_target(D, 0, 4, node_namesD)  # From Pedro to Lourdes