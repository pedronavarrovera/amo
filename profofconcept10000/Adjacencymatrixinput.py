# An adjacency matrix is a way of representing a graph (a network of nodes and edges) in the form of a square matrix
# Suppose you have a graph with n nodes (vertices). You build an n × n matrix A. Each entry A[i][j] tells you whether there is an edge (connection) from node i to node j. 
# This code prompts you for node names and an adjacency matrix. Store them in node_names and adjacency_matrix
# Either you can enter the matrix and node names manually, or read them from a base64-encoded code
# for example this code: eyJub2RlcyI6IHsiMCI6ICJBbGljZSIsICIxIjogIkJvYiIsICIyIjogIkNhcm9sIn0sICJtYXRyaXgiOiBbWzAsIDEsIDBdLCBbMSwgMCwgMV0sIFswLCAxLCAwXV19 
# The code also validates symmetry of the matrix. The code validate if the decoded matrix is square and symmetric.
#
#
import base64
import json

def read_node_names_dict(n):
    """
    Read n node names from console input and return as a dict {index: name}.
    """
    print(f"Enter {n} node names:")
    return {i: input(f"Node {i}: ") for i in range(n)}

def read_adjacency_matrix(n, node_names):
    """
    Read an n x n adjacency matrix from the console with validation.
    """
    print(f"Enter the adjacency matrix ({n}x{n}) row by row (space-separated):")
    matrix = []
    for i in range(n):
        row = list(map(int, input(f"{node_names[i]} → ").split()))
        if len(row) != n:
            raise ValueError(f"Row {i} must have {n} elements.")
        matrix.append(row)

    # Validate symmetry
    is_symmetric = all(matrix[i][j] == matrix[j][i] for i in range(n) for j in range(n))
    if not is_symmetric:
        print("⚠️ Warning: The matrix is NOT symmetric.")
    else:
        print("✅ Matrix is symmetric.")

    return matrix

def encode_adjacency_matrix(matrix, node_names):
    """
    Encode the matrix and node names into a base64 string.
    """
    data = {
        "nodes": node_names,
        "matrix": matrix
    }
    json_str = json.dumps(data)
    return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

def decode_adjacency_code(code):
    """
    Decode a Base64 string into (matrix, node_names).

    Supports both:
      1) Combined object: {"nodes": {... or [...]}, "matrix": [[...]]}
      2) Matrix-only: [[...]]  → auto-generate node names {0:"Node0",...}
    """
    decoded_str = base64.b64decode(code.encode('utf-8')).decode('utf-8')
    data = json.loads(decoded_str)

    # --- Case 1: matrix-only (list of lists) ---
    if isinstance(data, list):
        if not all(isinstance(row, list) for row in data):
            raise ValueError("Matrix-only JSON must be a list of lists.")
        n = len(data)
        matrix = [[int(v) for v in row] for row in data]
        node_names = {i: f"Node{i}" for i in range(n)}
        return matrix, node_names

    # --- Case 2: combined object with 'matrix' and 'nodes' ---
    if not isinstance(data, dict):
        raise ValueError("Unsupported JSON: expected object or list.")

    if "matrix" not in data:
        raise ValueError("Missing 'matrix' key in JSON object.")

    matrix = [[int(v) for v in row] for row in data["matrix"]]

    if "nodes" in data:
        nodes_any = data["nodes"]
        if isinstance(nodes_any, list):
            node_names = {i: str(name) for i, name in enumerate(nodes_any)}
        elif isinstance(nodes_any, dict):
            node_names = {int(k): str(v) for k, v in nodes_any.items()}
        else:
            raise ValueError("'nodes' must be a list or dict.")
    else:
        node_names = {i: f"Node{i}" for i in range(len(matrix))}

    return matrix, node_names


def validate_decoded_matrix(matrix, *, directed=True, report_asymmetry=False):
    """
    Validate the decoded adjacency matrix.

    - Always enforces squareness.
    - If directed=True (default), we DO NOT require symmetry.
      Optionally reports how many (i,j) have matrix[i][j] != matrix[j][i].
    - If directed=False, we require symmetry.

    Returns nothing; prints human-friendly diagnostics.
    """
    n = len(matrix)
    is_square = all(isinstance(row, list) and len(row) == n for row in matrix)

    if not is_square:
        print("❌ Error: Decoded matrix is not square.")
        return

    if directed:
        if report_asymmetry:
            asym = sum(
                1
                for i in range(n)
                for j in range(i + 1, n)
                if matrix[i][j] != matrix[j][i]
            )
            print(f"ℹ️ Directed graph detected. Asymmetric pairs: {asym}.")
        else:
            print("✅ Decoded matrix is square (directed; symmetry not required).")
    else:
        is_symmetric = all(matrix[i][j] == matrix[j][i] for i in range(n) for j in range(n))
        if not is_symmetric:
            print("❌ Error: Expected an undirected (symmetric) matrix, but it is NOT symmetric.")
        else:
            print("✅ Decoded matrix is valid and symmetric (undirected).")


# === MAIN EXECUTION ===
if __name__ == "__main__":
    print("📥 Graph Input Options:")
    print("1. Enter matrix and nodes manually")
    print("2. Paste encoded base64 code e.g. eyJub2RlcyI6IHsiMCI6ICJQZWRybyIsICIxIjogIlBpbGFyIiwgIjIiOiAiRGF2aWQifSwgIm1hdHJpeCI6IFtbMCwgMTAsIDBdLCBbMTAsIDAsIDEwXSwgWzAsIDEwLCAwXV19")
    choice = input("Select an option (1 or 2): ").strip()

    if choice == '1':
        n = int(input("Enter number of nodes: "))
        node_names = read_node_names_dict(n)
        adjacency_matrix = read_adjacency_matrix(n, node_names)
        encoded_code = encode_adjacency_matrix(adjacency_matrix, node_names)

    elif choice == '2':
        code = input("Paste the base64-encoded graph code: ").strip()
        adjacency_matrix, node_names = decode_adjacency_code(code)
        encoded_code = code
        print("\n✅ Code successfully decoded.")
        # For BEBDiM output (directed):
        validate_decoded_matrix(adjacency_matrix, directed=True, report_asymmetry=True)

        # If you ever expect an undirected graph, use:
        # validate_decoded_matrix(adjacency_matrix, directed=False)

    else:
        raise ValueError("Invalid option selected.")

    # Display results
    print("\n✅ Variables stored as Python code:")
    print("node_names =")
    print(node_names)
    print("\nadjacency_matrix = [")
    for row in adjacency_matrix:
        print("    " + str(row) + ",")
    print("]")

    print("\n📦 Encoded Base64 Code:")
    print(encoded_code)

    # Decode to verify
    decoded_matrix, decoded_names = decode_adjacency_code(encoded_code)
    validate_decoded_matrix(decoded_matrix)
    print("\n🔁 Decoded Verification:")
    print("Decoded node names:", decoded_names)
    print("Decoded matrix:")
    for i, row in enumerate(decoded_matrix):
        print(f"{decoded_names[i]} →", ' '.join(map(str, row)))