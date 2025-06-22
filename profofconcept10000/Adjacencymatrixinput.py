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
    Read an n x n adjacency matrix from the console.
    """
    print(f"Enter the adjacency matrix ({n}x{n}) row by row (space-separated):")
    matrix = []
    for i in range(n):
        row = list(map(int, input(f"{node_names[i]} → ").split()))
        if len(row) != n:
            raise ValueError(f"Row {i} must have {n} elements.")
        matrix.append(row)
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
    Decode a base64 string back into matrix and node names.
    """
    decoded_str = base64.b64decode(code.encode('utf-8')).decode('utf-8')
    data = json.loads(decoded_str)
    matrix = data['matrix']
    node_names = {int(k): v for k, v in data['nodes'].items()}
    return matrix, node_names

# === MAIN EXECUTION ===
if __name__ == "__main__":
    print("📥 Capture adjacency matrix and node names from console")

    n = int(input("Enter number of nodes: "))
    node_names = read_node_names_dict(n)
    adjacency_matrix = read_adjacency_matrix(n, node_names)

    # Encode
    encoded_code = encode_adjacency_matrix(adjacency_matrix, node_names)

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

    print("\n🔁 Decoded Verification:")
    print("Decoded node names:", decoded_names)
    print("Decoded matrix:")
    for i, row in enumerate(decoded_matrix):
        print(f"{decoded_names[i]} →", ' '.join(map(str, row)))
