# Prompt you for node names and an adjacency matrix
# Store them in node_names and adjacency_matrix
# either enter the matrix and node names manually, or read them from a base64-encoded code
# for example this code: eyJub2RlcyI6IHsiMCI6ICJBbGljZSIsICIxIjogIkJvYiIsICIyIjogIkNhcm9sIn0sICJtYXRyaXgiOiBbWzAsIDEsIDBdLCBbMSwgMCwgMV0sIFswLCAxLCAwXV19 
# provides insights into a debt matrix where: 
#    Nodes represent people
#    adjacency_matrix[i][j] represents how much person i owes to person j
# It calculates:
# Total debt per person (how much they owe and are owed)
# Net balance per person (creditor vs debtor)
# Top debtors and creditors
# Cycles (insight into circular debt if needed) detect debt cycles (like A → B → C → A) 
# and suggest debt settlements to reduce total transactions
# Cycle Detection (e.g., Alice → Bob → Carol → Alice) for instance 
# These indicate circular debt that can be simplified or canceled
# Debt Settlement Suggestions e.g. Suggest direct settlements between people to minimize intermediate transfers — like resolving net balances
# For instance: 
# Before settlement:
# Alice owes Bob 40
# Bob owes Carol 30
# Carol owes Alice 10
# After settlement:
# Alice pays Carol 10 (via net settlement)
# Alice pays Bob 30
# Final matrix reflects direct, minimal transfers, avoiding circular debt and intermediaries
# Finally it finds the debt cycle shortest back given A and B as well as the matrix
# find a debt cycle that:Starts at a given node A, Goes directly to node B, 
# Then follows the shortest possible path from B back to A (forming a cycle).


import base64
import json
import networkx as nx
from copy import deepcopy


#
def analyze_debt_matrix(matrix, node_names):
    n = len(matrix)
    
    print("\n📊 Debt Analysis")
    print("=" * 40)
    
    total_owed_by = {}   # Total amount each person owes
    total_owed_to = {}   # Total amount each person is owed
    net_balance = {}     # Positive if creditor, negative if debtor

    for i in range(n):
        person = node_names[i]
        owed_by_person = sum(matrix[i])  # sum of row i
        owed_to_person = sum(matrix[j][i] for j in range(n))  # sum of column i
        total_owed_by[person] = owed_by_person
        total_owed_to[person] = owed_to_person
        net_balance[person] = owed_to_person - owed_by_person

    print("{:<12} {:>10} {:>12} {:>12}".format("Person", "Owes", "Is Owed", "Net Balance"))
    print("-" * 48)
    for person in node_names.values():
        print("{:<12} {:>10} {:>12} {:>12}".format(
            person,
            total_owed_by[person],
            total_owed_to[person],
            net_balance[person]
        ))

    most_owed = max(total_owed_to.items(), key=lambda x: x[1])
    most_debt = max(total_owed_by.items(), key=lambda x: x[1])
    top_creditor = max(net_balance.items(), key=lambda x: x[1])
    top_debtor = min(net_balance.items(), key=lambda x: x[1])

    print("\n📌 Insights")
    print("-" * 40)
    print(f"💰 Most Owed To: {most_owed[0]} (is owed {most_owed[1]})")
    print(f"🧾 Owes the Most: {most_debt[0]} (owes {most_debt[1]})")
    print(f"📈 Top Creditor: {top_creditor[0]} (net +{top_creditor[1]})")
    print(f"📉 Top Debtor: {top_debtor[0]} (net {top_debtor[1]})")

    detect_debt_cycles(matrix, node_names)
    suggest_settlements(net_balance)


def detect_debt_cycles(matrix, node_names):
    print("\n🔁 Debt Cycles")
    print("-" * 40)

    G = nx.DiGraph()
    n = len(matrix)

    # Build directed graph
    for i in range(n):
        for j in range(n):
            if matrix[i][j] > 0:
                G.add_edge(node_names[i], node_names[j], weight=matrix[i][j])

    try:
        cycles = list(nx.simple_cycles(G))
    except:
        cycles = []

    if not cycles:
        print("✅ No circular debt found.")
    else:
        for i, cycle in enumerate(cycles, 1):
            print(f"🔄 Cycle {i}: {' → '.join(cycle)} → {cycle[0]}")
            # Optionally, show the minimum transfer in cycle
            min_transfer = min(G[cycle[k]][cycle[(k+1)%len(cycle)]]['weight'] for k in range(len(cycle)))
            print(f"   ⚖️ Potential to cancel up to {min_transfer} within this cycle")


def suggest_settlements(net_balance):
    print("\n💡 Settlement Suggestions")
    print("-" * 40)
    creditors = sorted([(p, b) for p, b in net_balance.items() if b > 0], key=lambda x: -x[1])
    debtors = sorted([(p, b) for p, b in net_balance.items() if b < 0], key=lambda x: x[1])

    i = j = 0
    while i < len(debtors) and j < len(creditors):
        debtor, debt_amount = debtors[i]
        creditor, credit_amount = creditors[j]

        payment = min(-debt_amount, credit_amount)
        print(f"💸 {debtor} should pay {creditor} → {payment}")

        # Update balances
        debtors[i] = (debtor, debt_amount + payment)
        creditors[j] = (creditor, credit_amount - payment)

        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

#
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
    Decode a base64 string back into matrix and node names.
    """
    decoded_str = base64.b64decode(code.encode('utf-8')).decode('utf-8')
    data = json.loads(decoded_str)
    matrix = data['matrix']
    node_names = {int(k): v for k, v in data['nodes'].items()}
    return matrix, node_names

def validate_decoded_matrix(matrix):
    """
    Validate if the decoded matrix is square and symmetric.
    """
    n = len(matrix)
    is_square = all(len(row) == n for row in matrix)
    is_symmetric = all(matrix[i][j] == matrix[j][i] for i in range(n) for j in range(n))

    if not is_square:
        print("❌ Error: Decoded matrix is not square.")
    elif not is_symmetric:
        print("⚠️ Warning: Decoded matrix is NOT symmetric.")
    else:
        print("✅ Decoded matrix is valid and symmetric.")

def find_debt_cycle_shortest_back(matrix, node_names, start_node, second_node):
    """
    Find a debt cycle that starts at `start_node`, goes to `second_node`, and returns
    to `start_node` through the shortest weighted path from B back to A.
    """
    G = nx.DiGraph()
    n = len(matrix)

    # Build the graph
    for i in range(n):
        for j in range(n):
            if matrix[i][j] > 0:
                G.add_edge(node_names[i], node_names[j], weight=matrix[i][j])

    if not G.has_edge(start_node, second_node):
        print(f"❌ No direct debt from {start_node} to {second_node}.")
        return None

    try:
        # Find shortest path from B to A
        path_back = nx.shortest_path(G, source=second_node, target=start_node, weight='weight')
    except nx.NetworkXNoPath:
        print(f"❌ No path from {second_node} back to {start_node}.")
        return None

    # Form the full cycle: A → B → shortest path from B to A
    cycle = [start_node, second_node] + path_back[1:]

    print(f"\n🔁 Debt cycle using shortest path:")
    print(" → ".join(cycle))

    # Only evaluate consecutive edges in the cycle (no wraparound)
    try:
        min_transfer = min(
            G[cycle[i]][cycle[i + 1]]['weight']
            for i in range(len(cycle) - 1)
        )
    except KeyError as e:
        print(f"❌ Invalid edge in constructed cycle: {e}")
        return None

    print(f"   ⚖️ Potential to cancel up to {min_transfer}")

    return cycle

def suggest_settlements_from_cycle(matrix, node_names, cycle):
    """
    Suggest direct settlements to cancel a cycle by its minimum transfer amount.

    Args:
        matrix (List[List[int]]): The original adjacency matrix.
        node_names (Dict[int, str]): Mapping from indices to person names.
        cycle (List[str]): The detected cycle, e.g., ['Pedro', 'Pilar', 'David', 'Pedro']
    """
    if not cycle or len(cycle) < 2:
        print("⚠️ Invalid cycle provided.")
        return

    # Create lookup from name to index
    name_to_index = {v: k for k, v in node_names.items()}

    # Compute the minimum transferable amount in the cycle
    min_transfer = float('inf')
    for i in range(len(cycle) - 1):
        u = name_to_index[cycle[i]]
        v = name_to_index[cycle[i + 1]]
        min_transfer = min(min_transfer, matrix[u][v])
    
    print(f"\n💡 Suggested settlements to cancel this cycle (amount: {min_transfer}):")
    for i in range(len(cycle) - 1):
        payer = cycle[i]
        receiver = cycle[i + 1]
        print(f"💸 {payer} should pay {receiver} → {min_transfer}")

    print(f"\n✅ This will remove {min_transfer} from each link in the cycle.")



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
        validate_decoded_matrix(adjacency_matrix)

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
    
    # Provide insights
    analyze_debt_matrix(adjacency_matrix, node_names)

    # === OPTIONAL: Find specific A → B → shortest path back to A cycle ===
    user_choice = input("\n🔎 Do you want to find a cycle A → B → shortest path back to A? (y/n): ").strip().lower()
    if user_choice == 'y':
        print("Available node names:", list(node_names.values()))
        start_node = input("Enter the starting node A: ").strip()
        second_node = input("Enter the second node B (must be directly owed by A): ").strip()
        if start_node not in node_names.values() or second_node not in node_names.values():
            print("❌ One or both names not found.")
        else:
            find_debt_cycle_shortest_back(adjacency_matrix, node_names, start_node, second_node)

    cycle = find_debt_cycle_shortest_back(adjacency_matrix, node_names, "Pedro", "Pilar")
    if cycle:
    suggest_settlements_from_cycle(adjacency_matrix, node_names, cycle)
