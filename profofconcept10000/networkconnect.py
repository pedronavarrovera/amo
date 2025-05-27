# iN ORDER TO INTERCONNECT 2 PAYMENT NETWORKS THE FOLLOWING PROCESS IS DEFINED
#block matrix composition, is specifically a type of block diagonal concatenation or matrix embedding.
#Operation: Block Matrix Construction / Embedding
# If you have two matrices A and B, and you want to place A in the top-left corner and B in the bottom-right corner of a new, larger matrix — with zeros elsewhere
# — you're constructing a block diagonal matrix (with one block in each corner).
#Example
#Let:
#A be a matrix of shape (m, n)
#B be a matrix of shape (p, q)
#Then the resulting matrix C will have shape (m + p, n + q), and look like this:
# C=[A 0]
#   [0 B]
# Where 0 represents zero matrices of appropriate dimensions to fill the rest of the space.
# In addition, in order to connect the 2 networks for instance the firts items of each network need to be connected (e.g. this is managed by the merge authority)

# You want to build a square matrix D such that:
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

import numpy as np

def construct_matrix_with_A_top_left(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Constructs a square matrix D of shape (a + b, a + b), with:
    - A in the top-left (a x a)
    - B in the bottom-right (b x b)
    - Zeros elsewhere
    - Then sets D[0, a] = 1
    """
    a = A.shape[0]
    b = B.shape[0]

    assert A.shape == (a, a), "Matrix A must be square"
    assert B.shape == (b, b), "Matrix B must be square"

    # Create a square matrix of zeros
    D = np.zeros((a + b, a + b))

    # Insert A in top-left
    D[:a, :a] = A

    # Insert B in bottom-right
    D[a:, a:] = B

    # Set 1 at position (0, a)
    D[0, a] = 1

    return D

# Example usage:
A = np.array([[1, 2], [3, 4]])  # 2x2
B = np.array([[5, 6, 7], [8, 9, 10], [11, 12, 13]])  # 3x3

D = construct_matrix_with_A_top_left(A, B)
print(D)
