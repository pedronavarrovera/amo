# This software is Open Source as OSI definition.
# Users can open issues and propose code changes without manual approval of (or payments for) accounts.
# This sofware is a research application. You can find the paper associated in the file paper.md. The code solve complex problems in the contex of mathematics and social science to calculate payment transactions routes among users.
# This code has been configured to support the generation of large datasets of random transaction data and supports the execution of reseach experiments in a social network of users.
# This code supports the extraction of knowledge from a large dataset of random transaction data using Power BI data for visualisation and analysis as a research's Proof of Concept. 
# The output for analysys includes: Transaction ID, origin and destination accounts, transaction value, and the corresponding shortest path.
# The major contributor to the software is Pedro Juan Navarro Vera who owns the account pedronavarrovera and the public repository pedronavarrovera/amo in Github. 
# The code can be cloned, browsed online and file tickets created by individuals as well as its issues tracked without registration.
# This code can be used in a way similar to a mathematical library.
# Despite the total line of code (LOC) has been compressed below a thousand lines to be run on small arduinos with 32K of not expandable program memory . This code contains a substantial scholarly effort as it combines knowledge from multidisciplinary areas such as mathematics, social science, software engineering, etc.  
# as described in the associated paper located in the file paper.md 
#
# Description of the core functionality
#    Graph Modeling:
#       Users are represented as nodes in a graph.
#       The graph is modeled using adjacency matrices where edges carry random weights (transaction values).
#   Pathfinding Algorithm:
#       Uses Dijkstra’s algorithm to compute the shortest transaction path from a source user to all others.
#       Outputs include: transaction source and destination, cost, currency symbol (@mo), and route
#   Data Generation:
#       Generates large datasets (e.g., 10,000 random networks of 100 users each) to simulate transactions
#       The output is suitable for analysis and visualization (e.g., with Power BI).    
#   Outputs:
#       Each transaction simulation prints:
#           Transaction ID
#           Source and destination user IDs and names
#           Distance (transaction cost)
#           Currency unit (@mo)
#           Shortest path (as sequence of nodes)
#
# To calculate the shortest path using Dijkstra's algorithm in Python, here are some reliable libraries: 
# Option 1: NetworkX (most popular and beginner-friendly)
# Option 2: scipy.sparse.csgraph (efficient for large sparse graphs)
# Option 3 selected: igraph (very fast, suitable for large networks): Performance-oriented, good for large-scale graphs. Handles millions of nodes and tens of millions of edges efficiently.
# This script below calculates shortest paths in a directed, weighted graph using the igraph library,
# where the graph represents a network of people and the weights represent transaction values or distances
# Input: A randomly generated adjacency matrix (100x100) with integer weights (max 100),
# where matrix[i][j] > 0 indicates a directed edge from node i to node j
# Output: a) All shortest paths from Pedro (node 0) to all others. b) The shortest path from Pedro (0) to Valentina (12)
#
#
# Import required libraries
import numpy as np
from igraph import Graph

# Constants

MONEDA = "@mo" # is the symbol used to represent a custom currency

# Full node name mapping from 0 to 99. Maps numeric node indices to readable names (e.g., for transaction participants)
node_names = {
    0: "Pedro usercybereu",
    1: "Pilar pramos1971",
    2: "Lucas",
    3: "Sofia",
    4: "Emma",
    5: "Mateo",
    6: "Olivia",
    7: "Leo",
    8: "Isabella",
    9: "Noah",
    10: "Camila",
    11: "Liam",
    12: "Valentina",
    13: "Emma",
    14: "Sebastian",
    15: "Mia",
    16: "Thiago",
    17: "Martina",
    18: "David",
    19: "Lucia",
    20: "Gabriel",
    21: "Zoe",
    22: "Daniel",
    23: "Elena",
    24: "Benjamín",
    25: "Luna",
    26: "Tomas",
    27: "Aitana",
    28: "Bruno",
    29: "Sara",
    30: "Dylan",
    31: "Julia",
    32: "Samuel",
    33: "Carla",
    34: "Diego",
    35: "Irene",
    36: "Gael",
    37: "Chloe",
    38: "Nicolas",
    39: "Clara",
    40: "Alex",
    41: "Alma",
    42: "Aaron",
    43: "Paula",
    44: "Hugo",
    45: "Angela",
    46: "Marco",
    47: "Vera",
    48: "Julian",
    49: "Ariadna",
    50: "Andres",
    51: "Lia",
    52: "Ian",
    53: "Marta",
    54: "Axel",
    55: "Nora",
    56: "Rodrigo",
    57: "Lola",
    58: "Adrian",
    59: "Blanca",
    60: "Cristian",
    61: "Celia",
    62: "Pablo",
    63: "Milena",
    64: "Iker",
    65: "Elsa",
    66: "Raul",
    67: "Jimena",
    68: "Fernando",
    69: "Naia",
    70: "Javier",
    71: "Candela",
    72: "Erik",
    73: "Violeta",
    74: "Maximo",
    75: "Belen",
    76: "Alvaro",
    77: "Marina",
    78: "Esteban",
    79: "Isabel",
    80: "Santiago",
    81: "Carmen",
    82: "Jose",
    83: "Amaya",
    84: "Renato",
    85: "Gabriela",
    86: "Cristobal",
    87: "Natalia",
    88: "Mauricio",
    89: "Bianca",
    90: "Ignacio",
    91: "Selena",
    92: "Eduardo",
    93: "Alicia",
    94: "Martin",
    95: "Florencia",
    96: "Rafael",
    97: "Daniela",
    98: "Ramiro",
    99: "Lourdes"
}
#
# Converts a numpy adjacency matrix into an igraph graph
# Adds vertices.
# Adds directed edges where weight > 0.
# Stores weights as edge attributes

def build_igraph_from_adjacency(adjacency_matrix):
    size = len(adjacency_matrix)
    edges = []
    weights = []

    for i in range(size):
        for j in range(size):
            weight = adjacency_matrix[i][j]
            if weight > 0:
                edges.append((i, j))
                weights.append(weight)

    g = Graph(directed=True)
    g.add_vertices(size)
    g.add_edges(edges)
    g.es['weight'] = weights
    return g

# Runs Dijkstra's algorithm from one node to all others
def dijkstra_igraph_all(adjacency_matrix, start_vertex, node_names):
    g = build_igraph_from_adjacency(adjacency_matrix)
    distances = g.distances(source=start_vertex, weights="weight")[0]
    paths = g.get_shortest_paths(start_vertex, to=None, weights="weight", output="vpath")

    for target_vertex, (dist, path) in enumerate(zip(distances, paths)):
        if target_vertex != start_vertex:
            print(f"\n{start_vertex} -> {target_vertex}\t{node_names[start_vertex]} -> {node_names[target_vertex]}\t{dist} {MONEDA}\tPath: ", end="")
            for v in path:
                print(f"{v} {node_names.get(v, str(v))}", end=" ")
            print()

# Runs Dijkstra's algorithm to a specific target
def dijkstra_igraph_to_target(adjacency_matrix, start_vertex, destination_vertex, node_names):
    g = build_igraph_from_adjacency(adjacency_matrix)
    dist = g.distances(source=start_vertex, target=destination_vertex, weights="weight")[0][0]
    path = g.get_shortest_paths(start_vertex, to=destination_vertex, weights="weight", output="vpath")[0]

    print(f"\nShortest path from {node_names[start_vertex]} to {node_names[destination_vertex]}")
    print(f"Distance: {dist} {MONEDA}")
    print("Path: ", end="")
    for v in path:
        print(f"{v} {node_names.get(v, str(v))}", end=" ")
    print()

# Generates a random 100x100 adjacency matrix of weights in range [0, max_weight)
# Calls both dijkstra_igraph_all() from Pedro (node 0) and dijkstra_igraph_to_target() from Pedro to Valentina (node 12)
if __name__ == "__main__":
    # Several predefined adjacency matrices for testing
    adjacency_matrix_example9x9 = [
        [0, 4, 0, 0, 0, 0, 0, 8, 0],
        [4, 0, 8, 0, 0, 0, 0, 11, 0],
        [0, 8, 0, 7, 0, 4, 0, 0, 2],
        [0, 0, 7, 0, 9, 14, 0, 0, 0],
        [0, 0, 0, 9, 0, 10, 0, 0, 0],
        [0, 0, 4, 14, 10, 0, 2, 0, 0],
        [0, 0, 0, 0, 0, 2, 0, 1, 6],
        [8, 11, 0, 0, 0, 0, 1, 0, 7],
        [0, 0, 2, 0, 0, 0, 6, 7, 0],
    ]
    adjacency_matrix_example10x10 = [
        [0, 4, 0, 0, 0, 0, 0, 8, 0, 1],
        [4, 0, 8, 0, 0, 0, 0, 11, 0, 1],
        [0, 8, 0, 7, 0, 4, 0, 0, 2, 1],
        [0, 0, 7, 0, 9, 14, 0, 0, 0, 1],
        [0, 0, 0, 9, 0, 10, 0, 0, 0, 1],
        [0, 0, 4, 14, 10, 0, 2, 0, 0, 1],
        [0, 0, 0, 0, 0, 2, 0, 1, 6, 1],
        [8, 11, 0, 0, 0, 0, 1, 0, 7, 1],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 2],
    ]
    adjacency_matrix_example8x8 = [
        [0, 4, 0, 0, 0, 0, 0, 8],
        [4, 0, 8, 0, 0, 0, 0, 11],
        [0, 8, 0, 7, 0, 4, 0, 0],
        [0, 0, 7, 0, 9, 14, 0, 0],
        [0, 0, 0, 9, 0, 10, 0, 0],
        [0, 0, 4, 14, 10, 0, 2, 0],
        [0, 0, 0, 0, 0, 2, 0, 1],
        [8, 11, 0, 0, 0, 0, 1, 0],
    ]
    adjacency_matrix_example11x11 = [
        [0, 4, 0, 0, 0, 0, 0, 8, 0, 5, 5],
        [4, 0, 8, 0, 0, 0, 0, 11, 0, 5, 5],
        [0, 8, 0, 7, 0, 4, 0, 0, 2, 5, 5],
        [0, 0, 7, 0, 9, 14, 0, 0, 0, 5, 5],
        [0, 0, 0, 9, 0, 10, 0, 0, 0, 5, 5],
        [0, 0, 4, 14, 10, 0, 2, 0, 0, 5, 5],
        [0, 0, 0, 0, 0, 2, 0, 1, 6, 5, 5],
        [8, 11, 0, 0, 0, 0, 1, 0, 7, 5, 5],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 5, 5],
        [0, 0, 2, 0, 0, 0, 6, 7, 1, 5, 5],
        [0, 0, 2, 0, 0, 0, 6, 7, 2, 5, 5],
    ]
    adjacency_matrix_example12x12 = [
        [0, 4, 0, 0, 0, 0, 0, 8, 0, 1, 2, 3],
        [4, 0, 8, 0, 0, 0, 0, 11, 0, 1, 2, 3],
        [0, 8, 0, 7, 0, 4, 0, 0, 2, 1, 2, 3],
        [0, 0, 7, 0, 9, 14, 0, 0, 0, 1, 2, 3],
        [0, 0, 0, 9, 0, 10, 0, 0, 0, 1, 2, 3],
        [0, 0, 4, 14, 10, 0, 2, 0, 0, 1, 2, 3],
        [0, 0, 0, 0, 0, 2, 0, 1, 6, 1, 2, 3],
        [8, 11, 0, 0, 0, 0, 1, 0, 7, 1, 2, 3],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 3],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 5],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 6],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7],
    ]
    adjacency_matrix_example13x13 = [
        [0, 4, 0, 0, 0, 0, 0, 8, 0, 1, 2, 3, 4],
        [4, 0, 8, 0, 0, 0, 0, 11, 0, 1, 2, 3, 4],
        [0, 8, 0, 7, 0, 4, 0, 0, 2, 1, 2, 3, 4],
        [0, 0, 7, 0, 9, 14, 0, 0, 0, 1, 2, 3, 4],
        [0, 0, 0, 9, 0, 10, 0, 0, 0, 1, 2, 3, 4],
        [0, 0, 4, 14, 10, 0, 2, 0, 0, 1, 2, 3, 4],
        [0, 0, 0, 0, 0, 2, 0, 1, 6, 1, 2, 3, 4],
        [8, 11, 0, 0, 0, 0, 1, 0, 7, 1, 2, 3, 4],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 3, 4],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 5, 4],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 6, 4],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 4],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 5],
    ]
    adjacency_matrix_example14x14 = [
        [0, 4, 0, 0, 0, 0, 0, 8, 0, 1, 2, 3, 4, 5],
        [4, 0, 8, 0, 0, 0, 0, 11, 0, 1, 2, 3, 4, 5],
        [0, 8, 0, 7, 0, 4, 0, 0, 2, 1, 2, 3, 4, 5],
        [0, 0, 7, 0, 9, 14, 0, 0, 0, 1, 2, 3, 4, 5],
        [0, 0, 0, 9, 0, 10, 0, 0, 0, 1, 2, 3, 4, 5],
        [0, 0, 4, 14, 10, 0, 2, 0, 0, 1, 2, 3, 4, 5],
        [0, 0, 0, 0, 0, 2, 0, 1, 6, 1, 2, 3, 4, 5],
        [8, 11, 0, 0, 0, 0, 1, 0, 7, 1, 2, 3, 4, 5],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 3, 4, 5],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 5, 4, 5],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 6, 4, 5],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 4, 5],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 5, 5],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 5, 5],
    ]
    adjacency_matrix_example15x15 = [
        [0, 4, 0, 0, 0, 0, 0, 8, 0, 1, 2, 3, 4, 5, 6],
        [4, 0, 8, 0, 0, 0, 0, 11, 0, 1, 2, 3, 4, 5, 6],
        [0, 8, 0, 7, 0, 4, 0, 0, 2, 1, 2, 3, 4, 5, 6],
        [0, 0, 7, 0, 9, 14, 0, 0, 0, 1, 2, 3, 4, 5, 6],
        [0, 0, 0, 9, 0, 10, 0, 0, 0, 1, 2, 3, 4, 5, 6],
        [0, 0, 4, 14, 10, 0, 2, 0, 0, 1, 2, 3, 4, 5, 6],
        [0, 0, 0, 0, 0, 2, 0, 1, 6, 1, 2, 3, 4, 5, 6],
        [8, 11, 0, 0, 0, 0, 1, 0, 7, 1, 2, 3, 4, 5, 6],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 3, 4, 5, 6],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 5, 4, 5, 6],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 6, 4, 5, 6],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 4, 5, 6],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 5, 5, 6],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 5, 5, 6],
    ]
    adjacency_matrix_example16x16 = [
        [0, 4, 0, 0, 0, 0, 0, 8, 0, 1, 2, 3, 4, 5, 6, 7],
        [4, 0, 8, 0, 0, 0, 0, 11, 0, 1, 2, 3, 4, 5, 6, 7],
        [0, 8, 0, 7, 0, 4, 0, 0, 2, 1, 2, 3, 4, 5, 6, 7],
        [0, 0, 7, 0, 9, 14, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7],
        [0, 0, 0, 9, 0, 10, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7],
        [0, 0, 4, 14, 10, 0, 2, 0, 0, 1, 2, 3, 4, 5, 6, 7],
        [0, 0, 0, 0, 0, 2, 0, 1, 6, 1, 2, 3, 4, 5, 6, 7],
        [8, 11, 0, 0, 0, 0, 1, 0, 7, 1, 2, 3, 4, 5, 6, 7],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 5, 4, 5, 6, 7],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 6, 4, 5, 6, 7],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 4, 5, 6, 7],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 5, 5, 6, 7],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 5, 5, 6, 7],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 5, 5, 6, 7],
    ]
    adjacency_matrix_example17x17 = [
        [0, 4, 0, 0, 0, 0, 0, 8, 0, 1, 2, 3, 4, 5, 6, 7, 11],
        [4, 0, 8, 0, 0, 0, 0, 11, 0, 1, 2, 3, 4, 5, 6, 7, 11],
        [0, 8, 0, 7, 0, 4, 0, 0, 2, 1, 2, 3, 4, 5, 6, 7, 11],
        [0, 0, 7, 0, 9, 14, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 11],
        [0, 0, 0, 9, 0, 10, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 11],
        [0, 0, 4, 14, 10, 0, 2, 0, 0, 1, 2, 3, 4, 5, 6, 7, 11],
        [0, 0, 0, 0, 0, 2, 0, 1, 6, 1, 2, 3, 4, 5, 6, 7, 11],
        [8, 11, 0, 0, 0, 0, 1, 0, 7, 1, 2, 3, 4, 5, 6, 7, 11],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 11],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 5, 4, 5, 6, 7, 11],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 6, 4, 5, 6, 7, 11],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 4, 5, 6, 7, 11],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 5, 5, 6, 7, 11],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 5, 5, 6, 7, 11],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 5, 5, 6, 7, 11],
        [0, 0, 2, 0, 0, 0, 6, 7, 0, 1, 2, 7, 5, 5, 6, 7, 11],
    ]
    test_sample = 1
    matrix_size = 100
    max_weight = 100

    for iteration in range(test_sample):
        matrix = np.random.randint(0, max_weight, size=(matrix_size, matrix_size))
        np.fill_diagonal(matrix, 0) # Sets diagonal to zero (no self-loops)

        dijkstra_igraph_all(matrix, 0, node_names)
        dijkstra_igraph_to_target(matrix, 0, 12, node_names)
