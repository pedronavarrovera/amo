# An adjacency matrix is a way of representing a graph (a network of nodes and edges) in the form of a square matrix
# Suppose you have a graph with n nodes (vertices). You build an n × n matrix A. Each entry A[i][j] tells you whether there is an edge (connection) from node i to node j. 
# This code prompts you for node names and an adjacency matrix. Store them in node_names and adjacency_matrix
#  
# In future releases the matrix can be consulted and updated from a storage server.
# At this release, Either you can enter the matrix and node names manually, or read them from a base64-encoded code.
# for example this code: eyJub2RlcyI6IHsiMCI6ICJBbGljZSIsICIxIjogIkJvYiIsICIyIjogIkNhcm9sIn0sICJtYXRyaXgiOiBbWzAsIDEsIDBdLCBbMSwgMCwgMV0sIFswLCAxLCAwXV19 
# or this code for a 5x5 matrix eyJub2RlcyI6IHsiMCI6ICJQZWRybyIsICIxIjogIlBpbGFyIiwgIjIiOiAiQW5kcmVhIiwgIjMiOiAiRGF2aWQiLCAiNCI6ICJFbGVuYSJ9LCAibWF0cml4IjogW1swLCAxMCwgMCwgMCwgMF0sIFswLCAwLCAyMCwgMCwgMF0sIFswLCAwLCAwLCAzMCwgMF0sIFswLCAwLCAwLCAwLCA0MF0sIFs1MCwgMCwgMCwgMCwgMF1dfQ==
# The code also validates symmetry of the matrix. The code validate if the decoded matrix is square and symmetric.
# 
# The code also provides insights into a debt matrix where: 
#    Nodes represent people
#    adjacency_matrix[i][j] represents how much person i owes to person j
#    Cycle Detection (e.g., Alice → Bob → Carol → Alice) for instance 
#    These indicate circular debt that can be simplified or canceled
#    Suggest indirect debts settlements: resolve the cycle with net balance reduction, avoiding redundant intermediate payments   
# 
# It calculates:
# 1) Total debt per person (how much they owe and are owed)
# 2) Net balance per person (creditor vs debtor)
# 3) Top debtors and creditors
# 4) Cycles (insight into circular debt if needed) detect debt cycles (like A → B → C → A) 
# and 5) suggest debt settlements to reduce total transactions
# 6) It finds the shortest back debt cycle given A and B as well as the matrix
# This means it finds a debt cycle that:Starts at a given node A, Goes directly to node B,Then follows the shortest possible path from B back to A (forming a cycle).
# From the detected cycle:
# 5.1) Find the minimum transferable amount M across the cycle,
# 5.2) Suggest direct payments from each person to the next to settle it
# 6.1) Alternative: Suggested condonations to cancel this cycle
# 6.2) It sends a secure (post-quantum encryption) condonation email if desired via Postmark HTTP API
# the email is sent to all participants in the cycle, where each participant has an email of the form node_name@cybereu.eu
# Reduce all edges in the cycle by M, effectively simplifying the loop
# Postmark API token is set in the environment variable POSTMARK_SERVER_TOKEN for instance dfc99995-7d73-45d0-8bfa-7e6a0f8ad335. On Windows (PowerShell):
# $env:POSTMARK_SERVER_TOKEN="your-real-server-token"
# $env:POSTMARK_STREAM="amoserver1messagestream"
# 6.3) Applies the settlements by subtracting the minimum transferable amount from each debt in the cycle, and shows the resulting matrix after updating the matrix directly
# 
# For instance:
# Pedro owes Pilar 10
# Pilar owes Andrea 20
# Andres Owes David 30
# David owes Pedro 40
# Decoded node names: {0: 'Pedro', 1: 'Pilar', 2: 'Andrea', 3: 'David'}
# Decoded matrix:
# Pedro → 0 10 0 0
# Pilar → 0 0 20 0
# Andrea → 0 0 0 30
# David → 40 0 0 0
# 📊 Debt Analysis
# ========================================
# Person             Owes      Is Owed  Net Balance
# ------------------------------------------------
# Pedro                10           40           30
# Pilar                20           10          -10
# Andrea               30           20          -10
# David                40           30          -10
#
#📌 Insights
#----------------------------------------
#💰 Most Owed To: Pedro (is owed 40)
#🧾 Owes the Most: David (owes 40)
#📈 Top Creditor: Pedro (net +30)
#📉 Top Debtor: Pilar (net -10)
#
#🔁 Debt Cycles
#----------------------------------------
#🔄 Cycle 1: David → Pedro → Pilar → Andrea → David
#   ⚖️ Potential to cancel up to 10 within this cycle
#
#💡 Settlement Suggestions
#----------------------------------------
#💸 Pilar should pay Pedro → 10
#💸 Andrea should pay Pedro → 10
#💸 David should pay Pedro → 10
#
#
#
#
#🔎 Do you want to find a cycle A → B → shortest path back to A? (y/n):y
#
#
#Available node names: ['Pedro', 'Pilar', 'Andrea', 'David']
#Enter the starting node A: Pedro
#Enter the second node B (must be directly owed by A): Pilar
#
#🔁 Debt cycle using shortest path:
#Pedro → Pilar → Andrea → David → Pedro
#   ⚖️ Potential to cancel up to 10
#
#🔁 Debt cycle using shortest path:
#Pedro → Pilar → Andrea → David → Pedro
#   ⚖️ Potential to cancel up to 10
#
#💡 Suggested settlements to cancel this cycle (amount: 10):
#💸 Pedro should pay Pilar → 10
#💸 Pilar should pay Andrea → 10
#💸 Andrea should pay David → 10
#💸 David should pay Pedro → 10
#
#
#🤝 Alternative: Suggested condonations to cancel this cycle (amount: 10):
#🙅‍♂️ Pilar could forgive Pedro → 10
#🙅‍♂️ Andrea could forgive Pilar → 10
#🙅‍♂️ David could forgive Andrea → 10
#🙅‍♂️ Pedro could forgive David → 10
#
#✅ Either option will remove 10 from each link in the cycle.
#
# Uses the networkplot_igraph visualizer to draw the cycle in red on a Fruchterman-Reingold layout
# Arrows point from debtor to creditor
# Red edges show the cycle path
# All node names and edge weights are displayed
# Edge directions now reflect actual debt direction
#
#🔧 Applied settlement: 10 removed from each link in the cycle.
#✅ Updated matrix reflects reduced debts in this cycle.
#
#Updated matrix= [
#    [0, 0, 0, 0],
#    [0, 0, 10, 0],
#    [0, 0, 0, 20],
#    [30, 0, 0, 0],
#]
#
#
#
#
#Do you want to send a secure condonation email? (y/n): y
#
#📄 Email Body to Encrypt:
# Subject: Suggested Condonations to Cancel Debt Cycle
#
#Hello,
#
#Based on the current debt analysis, we identified a cycle of obligations:
#
#Pedro → Pilar → Andrea → David → Pedro → Pedro
#
#The minimum transferable amount in this cycle is: 10 units.
#
#💡 Alternative: Suggested condonations:
#🙅‍♂️ Pilar could forgive Pedro → 10 units
#🙅‍♂️ Andrea could forgive Pilar → 10 units
#🙅‍♂️ David could forgive Andrea → 10 units
#🙅‍♂️ Pedro could forgive David → 10 units
#
#✅ If each creditor forgives this amount, 10 will be removed from every link in the cycle.
#
#Regards,
#DebtCycleAnalyzer
#
#🔐 Encrypted Email (Base64):
# JfG74In+RqmihYfp/2dU5yR6F2Q/I7lUS7Ee0itgmztctMfR+mpEhe1uvy74HwQwd2cUBykUOfTRjekgsxGfWVT4+p0qrJnkpNJjGGlTlVxX8mQV/vcmTanYDHSiW82cXFHRlYGcvv+/LW3CzpnXudAk2elDiUG6LHBIpx+I5BXkMK6UgZfny3eTR2THAiB6d2teJECQUBTbV8HTjHqfxERkuqa3fDcI4G9apppFimGH15f4rEuaGIJIM0xn5bMfHJUXIXuImykWEZU6DYHD8f590iy/7BuVfImMabk3QXVAuw1VFEic5Yz3KM+xUcd3IxN3bgLlJAgOllvxS9IjCrEHzdnALByHLxW8ywAasjjRRTtsmnyzjZWBpF19LQfwFwC27JLMjBRhg+UulPg/vnIdDATeM/RSkYdOL7qHtCznv2SA0rhYn8hvuR30eVEBmSPagB/A19KE1eW9i9yq1vtpVECHkxFRhURrBoYRQORUgLHh3n6U45PzpxJpZ1oLeuBnpDRDoxsBiGzkfNCW4xzzVQke+HnlywNYvPfSOsExAd2iobypy4iNMuqQbm5vq5jSl8ZDKkmV2QeGn3OdVeTk9fhoqmTgknHYFXzL8kQtATicEZUbJRDrEKDQPATrZII/2nyAGvAx80UoB84sBVJ5Fw7yDTEyMjKmkfMiCeU+pA9yOe6eAnG1jf3DtFAggUmDRFFPXKucF9SLRz8+EpvgnsTwS5Tt3qyrAoGVKhPmbDlgLDDusQkvjvt9lQmwRBfUoMM92MESBh5pwabjYcOhVwfdC6gIvaF+kOzwMcmOi0bEz401wRC1JI1Irg+P0bNf0MOcXvj0p4wAordQ8p6ZMqazhDBa6GltDVdEg8M=
#Email sent successfully via Postmark HTTP API.
#Email sent successfully via Postmark HTTP API.
#Email sent successfully via Postmark HTTP API.
#Email sent successfully via Postmark HTTP API.
#
# 🔓 Decrypted Email Message is calculated based on the shared key

import os
import base64
import json
from copy import deepcopy

import networkx as nx

from core_igraph import dijkstra_igraph_to_target
from networkplot_igraph import visualize_path_directed

from quantum import MLKEM_512, encrypt_message, decrypt_message
from communicationsviaemail import send_email_via_postmark_http


# ==========================
# Helpers & Core Utilities
# ==========================

def canonicalize_cycle(cycle):
    """Return a simple cycle without repeating the first node at the end."""
    if cycle and len(cycle) > 1 and cycle[0] == cycle[-1]:
        return cycle[:-1]
    return cycle


def analyze_debt_matrix(matrix, node_names):
    n = len(matrix)

    print("\n📊 Debt Analysis")
    print("=" * 40)

    total_owed_by = {}   # Total amount each person owes (row sum)
    total_owed_to = {}   # Total amount each person is owed (column sum)
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

    # Build directed graph (i owes j -> edge i -> j with weight)
    for i in range(n):
        for j in range(n):
            if matrix[i][j] > 0:
                G.add_edge(node_names[i], node_names[j], weight=matrix[i][j])

    try:
        cycles = list(nx.simple_cycles(G))
    except Exception:
        cycles = []

    if not cycles:
        print("✅ No circular debt found.")
    else:
        for i, cycle in enumerate(cycles, 1):
            cycle = canonicalize_cycle(cycle)
            ring = cycle + [cycle[0]]
            print(f"🔄 Cycle {i}: {' → '.join(ring)}")
            # Minimum transfer in cycle (consider wrap-around)
            min_transfer = min(
                G[cycle[k]][cycle[(k + 1) % len(cycle)]]['weight']
                for k in range(len(cycle))
            )
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


# ==========================
# I/O helpers
# ==========================

def read_node_names_dict(n):
    """
    Read n node names from console input and return as a dict {index: name}.
    """
    print(f"Enter {n} node names:")
    return {i: input(f"Node {i}: ") for i in range(n)}


def read_adjacency_matrix(n, node_names):
    """
    Read an n x n adjacency matrix from the console with validation.
    Note: Debts are directed; symmetry is not expected.
    """
    print(f"Enter the adjacency matrix ({n}x{n}) row by row (space-separated):")
    matrix = []
    for i in range(n):
        row = list(map(int, input(f"{node_names[i]} → ").split()))
        if len(row) != n:
            raise ValueError(f"Row {i} must have {n} elements.")
        matrix.append(row)

    # Basic square check
    is_square = all(len(row) == n for row in matrix)
    if not is_square:
        raise ValueError("❌ Matrix is not square.")

    print("ℹ️ Note: Treating matrix as a directed debt graph (no symmetry check).")
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
    Validate if the decoded matrix is square.
    (No symmetry requirement; graph is directed.)
    """
    n = len(matrix)
    is_square = all(len(row) == n for row in matrix)
    if not is_square:
        print("❌ Error: Decoded matrix is not square.")
    else:
        print("✅ Decoded matrix is valid (directed).")


# ==========================
# Cycle discovery & settlement (fixed)
# ==========================

def find_debt_cycle_shortest_back(matrix, node_names, start_node, second_node):
    """
    Find and visualize a debt cycle using igraph shortest path back to start.
    Returns a canonical cycle list without repeating the first node at the end.
    """
    name_to_index = {v: k for k, v in node_names.items()}
    index_to_name = {k: v for k, v in node_names.items()}

    if start_node not in name_to_index or second_node not in name_to_index:
        print("❌ Invalid node names.")
        return None

    u = name_to_index[start_node]
    v = name_to_index[second_node]

    if matrix[u][v] <= 0:
        print(f"❌ No direct debt from {start_node} to {second_node}.")
        return None

    path_back_indices = dijkstra_igraph_to_target(matrix, v, u, node_names)

    if not path_back_indices or len(path_back_indices) < 2:
        print(f"❌ No path from {second_node} back to {start_node}.")
        return None

    # path_back_indices is typically [v, ..., u]; build the full ring
    cycle_indices = [u, v] + path_back_indices[1:]
    cycle = [index_to_name[i] for i in cycle_indices]
    cycle = canonicalize_cycle(cycle)  # normalize so last != first

    print(f"\n🔁 Debt cycle using shortest path (via igraph):")
    print(" → ".join(cycle + [cycle[0]]))  # display as closed ring

    # Compute min transferable amount across the whole ring (wrap-around)
    name_to_index = {v: k for k, v in node_names.items()}
    min_transfer = min(
        matrix[name_to_index[cycle[i]]][name_to_index[cycle[(i + 1) % len(cycle)]]]
        for i in range(len(cycle))
    )
    print(f"   ⚖️ Potential to cancel up to {min_transfer}")

    # Visualize (pass a closed path for drawing)
    visualize_path_directed(matrix, node_names, cycle + [cycle[0]], title="🔁 Ciclo de deuda dirigido")

    return cycle


def suggest_settlements_from_cycle(matrix, node_names, cycle):
    """
    Suggest direct settlements or condonations to cancel a cycle by its
    minimum transfer amount. Cycle should be canonical.
    """
    cycle = canonicalize_cycle(cycle)
    if not cycle or len(cycle) < 2:
        print("⚠️ Invalid cycle provided.")
        return

    name_to_index = {v: k for k, v in node_names.items()}

    # Compute the minimum transferable amount in the cycle (wrap-around)
    min_transfer = min(
        matrix[name_to_index[cycle[i]]][name_to_index[cycle[(i + 1) % len(cycle)]]]
        for i in range(len(cycle))
    )

    print(f"\n💡 Suggested settlements to cancel this cycle (amount: {min_transfer}):")
    for i in range(len(cycle)):
        payer = cycle[i]
        receiver = cycle[(i + 1) % len(cycle)]
        print(f"💸 {payer} should pay {receiver} → {min_transfer}")

    print(f"\n🤝 Alternative: Suggested condonations to cancel this cycle (amount: {min_transfer}):")
    for i in range(len(cycle)):
        payer = cycle[i]
        receiver = cycle[(i + 1) % len(cycle)]
        print(f"🙅‍♂️ {receiver} could forgive {payer} → {min_transfer}")

    print(f"\n✅ Either option will remove {min_transfer} from each link in the cycle.")


def apply_cycle_settlement(matrix, node_names, cycle):
    """
    Apply settlements to cancel a cycle by subtracting the minimum transferable amount
    from each debt in the cycle. Modifies the matrix in place.
    """
    cycle = canonicalize_cycle(cycle)
    if not cycle or len(cycle) < 2:
        print("⚠️ Invalid cycle.")
        return

    name_to_index = {v: k for k, v in node_names.items()}

    min_transfer = min(
        matrix[name_to_index[cycle[i]]][name_to_index[cycle[(i + 1) % len(cycle)]]]
        for i in range(len(cycle))
    )

    for i in range(len(cycle)):
        u = name_to_index[cycle[i]]
        v = name_to_index[cycle[(i + 1) % len(cycle)]]
        matrix[u][v] -= min_transfer

    print(f"\n🔧 Applied settlement: {min_transfer} removed from each link in the cycle.")
    print("✅ Updated matrix reflects reduced debts in this cycle.")
    print("\nUpdated matrix= [")
    for row in matrix:
        print("    " + str(row) + ",")
    print("]")


# ==========================
# Email body generator (fixed not to double-close)
# ==========================

def generate_condonation_email(cycle, min_transfer):
    """
    Generate the email body text for suggested condonations in a debt cycle.
    """
    cycle = canonicalize_cycle(cycle)
    if not cycle or len(cycle) < 2:
        return "⚠️ Invalid cycle."

    ring = cycle + [cycle[0]]

    body = "Subject: Suggested Condonations to Cancel Debt Cycle\n\n"
    body += "Hello,\n\nBased on the current debt analysis, we identified a cycle of obligations:\n\n"
    body += " → ".join(ring) + "\n"
    body += f"\nThe minimum transferable amount in this cycle is: {min_transfer} units.\n"
    body += "\n💡 Alternative: Suggested condonations:\n"

    for i in range(len(cycle)):
        payer = cycle[i]
        receiver = cycle[(i + 1) % len(cycle)]
        body += f"🙅‍♂️ {receiver} could forgive {payer} → {min_transfer} units\n"

    body += f"\n✅ If each creditor forgives this amount, {min_transfer} will be removed from every link in the cycle.\n"
    body += "\nRegards,\nDebtCycleAnalyzer"
    return body


# ==========================
# Main
# ==========================
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
            cycle = find_debt_cycle_shortest_back(adjacency_matrix, node_names, start_node, second_node)
            if cycle:
                suggest_settlements_from_cycle(adjacency_matrix, node_names, cycle)

                # === OPTIONAL: Send encrypted condonation email ===
                secure_email_choice = input("\n📧 Do you want to send a secure condonation email? (y/n): ").strip().lower()
                if secure_email_choice == 'y':
                    # Recompute min_transfer with wrap-around
                    name_to_index = {v: k for k, v in node_names.items()}
                    min_transfer = min(
                        adjacency_matrix[name_to_index[cycle[i]]][name_to_index[cycle[(i + 1) % len(cycle)]]]
                        for i in range(len(cycle))
                    )

                    # Generate email content
                    email_body = generate_condonation_email(cycle, min_transfer)
                    print("\n📄 Email Body to Encrypt:\n", email_body)

                    # Quantum-safe key encapsulation
                    kem = MLKEM_512()
                    public_key, secret_key = kem.keygen()
                    ciphertext, shared_secret_sender = kem.encaps(public_key)
                    shared_secret_receiver = kem.decaps(secret_key, ciphertext)

                    # Encrypt message body
                    encrypted = encrypt_message(email_body, shared_secret_sender)
                    print("\n🔐 Encrypted Email (Base64):\n", encrypted)

                    # Construct HTML email (showing the closed ring for clarity)
                    ring = cycle + [cycle[0]]
                    html_body = f"""
                    <h2>🔐 Encrypted Condonation Email</h2>
                    <p>This message has been encrypted using post-quantum AES-256 derived from ML-KEM-512.</p>
                    <p><strong>Participants in the cycle:</strong> {' → '.join(ring)}</p>
                    <pre style="background-color:#f4f4f4;padding:10px;border:1px solid #ccc;">{encrypted}</pre>
                    <p>Each recipient must use the corresponding decryption key to view the message.</p>
                    """

                    # Recipients list: include each cycle participant at {name}@cybereu.eu
                    to_emails = list({f"{name}@cybereu.eu" for name in cycle})

                    # Prefer server token from environment
                    server_token = os.getenv("POSTMARK_SERVER_TOKEN")
                    if not server_token:
                        print("⚠️ POSTMARK_SERVER_TOKEN not set; skipping email sending.")
                    else:
                        for recipient_email in to_emails:
                            send_email_via_postmark_http(
                                server_token=server_token,
                                from_email="info@cybereu.eu",
                                to_email=recipient_email,
                                subject="🔐 Encrypted Condonation Suggestion",
                                html_body=html_body,
                                message_stream=os.getenv("POSTMARK_STREAM", "amoserver1messagestream"),
                            )

                        print("📧 Emails sent (via Postmark).")

                    # Decrypt and verify
                    decrypted = decrypt_message(encrypted, shared_secret_receiver)
                    print("\n🔓 Decrypted Email Message:\n", decrypted)

                    # Apply settlements
                    apply_cycle_settlement(adjacency_matrix, node_names, cycle)
                else:
                    print("🕊️ Secure email skipped.")
    else:
        print("🔎 Cycle search skipped.")
