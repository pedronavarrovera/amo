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


import base64
import json
import networkx as nx
from copy import deepcopy

#
def settle_debts(matrix, node_names, verbose=True):
    """
    Analyzes, suggests, and applies debt settlements on a matrix of debts between people.
    
    Args:
        matrix (List[List[int]]): Original n x n debt matrix (matrix[i][j] = i owes j).
        node_names (Dict[int, str]): Mapping of node index to names.
        verbose (bool): If True, print full analysis and actions.

    Returns:
        adjusted_matrix (List[List[int]]): New matrix after applying settlements.
    """
    n = len(matrix)
    name_to_index = {name: idx for idx, name in node_names.items()}
    adjusted_matrix = deepcopy(matrix)

    # === 1. Calculate totals and net balances ===
    total_owed_by = {}
    total_owed_to = {}
    net_balance = {}

    for i in range(n):
        person = node_names[i]
        owed_by = sum(matrix[i])
        owed_to = sum(matrix[j][i] for j in range(n))
        total_owed_by[person] = owed_by
        total_owed_to[person] = owed_to
        net_balance[person] = owed_to - owed_by

    if verbose:
        print("\n📊 Debt Analysis")
        print("{:<12} {:>10} {:>12} {:>12}".format("Person", "Owes", "Is Owed", "Net Balance"))
        print("-" * 48)
        for person in node_names.values():
            print("{:<12} {:>10} {:>12} {:>12}".format(
                person,
                total_owed_by[person],
                total_owed_to[person],
                net_balance[person]
            ))

    # === 2. Detect cycles ===
    if verbose:
        print("\n🔁 Debt Cycles")
        print("-" * 40)
    G = nx.DiGraph()
    for i in range(n):
        for j in range(n):
            if matrix[i][j] > 0:
                G.add_edge(node_names[i], node_names[j], weight=matrix[i][j])

    cycles = list(nx.simple_cycles(G))
    if not cycles and verbose:
        print("✅ No circular debt found.")
    elif verbose:
        for i, cycle in enumerate(cycles, 1):
            min_transfer = min(G[cycle[k]][cycle[(k+1)%len(cycle)]]['weight'] for k in range(len(cycle)))
            print(f"🔄 Cycle {i}: {' → '.join(cycle)} → {cycle[0]}")
            print(f"   ⚖️ Can cancel up to {min_transfer}")

    # === 3. Suggest & apply settlements ===
    if verbose:
        print("\n💡 Settlement Suggestions")
        print("-" * 40)
    creditors = sorted([(p, b) for p, b in net_balance.items() if b > 0], key=lambda x: -x[1])
    debtors = sorted([(p, b) for p, b in net_balance.items() if b < 0], key=lambda x: x[1])

    i = j = 0
    while i < len(debtors) and j < len(creditors):
        debtor, debt_amt = debtors[i]
        creditor, cred_amt = creditors[j]
        payment = min(-debt_amt, cred_amt)

        if verbose:
            print(f"💸 {debtor} should pay {creditor} → {payment}")

        d_idx = name_to_index[debtor]
        c_idx = name_to_index[creditor]
        adjusted_matrix[d_idx][c_idx] += payment

        debtors[i] = (debtor, debt_amt + payment)
        creditors[j] = (creditor, cred_amt - payment)

        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    if verbose:
        print("\n🧾 Final Adjusted Matrix After Settlements:")
        for i, row in enumerate(adjusted_matrix):
            print(f"{node_names[i]} →", ' '.join(map(str, row)))

    return adjusted_matrix

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

    # Apply those settlements and Return the final adjusted matrix
    matrix = adjacency_matrix
    new_matrix = settle_debts(matrix, node_names)
    print("\nadjacency_matrix = [")
    for row in new_matrix:
        print("    " + str(row) + ",")
    print("]")
    #
    # Provide insights after settlement
    analyze_debt_matrix(new_matrix, node_names)