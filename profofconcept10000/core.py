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

# Import required libraries
import sys
import numpy as np

# Constants
NO_PARENT = -1      # Used in parent array to denote root
MONEDA = "@mo"       # Custom currency symbol used for transactions

# Mapping node indices to user names
# define the names below
# 0 to 99 mapped to person names
node_names = {
    0: "Pedro",
    1: "Juan",
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
# -------------------------------
# Dijkstra Algorithm to a Target
# -------------------------------
#Calculates shortest path from start_vertex to destination_vertex using Dijkstra's algorithm
def dijkstra_to_target(adjacency_matrix, start_vertex, destination_vertex, node_names):
    n_vertices = len(adjacency_matrix[0])
    shortest_distances = [sys.maxsize] * n_vertices         # distance from start to each node
    added = [False] * n_vertices                            # track processed nodes
    parents = [-1] * n_vertices                             # track path (via parents)

    shortest_distances[start_vertex] = 0
    parents[start_vertex] = NO_PARENT
    # Main Dijkstra loop
    for _ in range(n_vertices):
        nearest_vertex = -1
        shortest_distance = sys.maxsize
        # Find unvisited vertex with smallest distance
        for vertex_index in range(n_vertices):
            if not added[vertex_index] and shortest_distances[vertex_index] < shortest_distance:
                nearest_vertex = vertex_index
                shortest_distance = shortest_distances[vertex_index]

        if nearest_vertex == -1:
            break  # no reachable vertex

        added[nearest_vertex] = True

        if nearest_vertex == destination_vertex:
            break  # destination reached
        # Update neighboring vertex distances
        for vertex_index in range(n_vertices):
            edge_distance = adjacency_matrix[nearest_vertex][vertex_index]
            if edge_distance > 0 and shortest_distance + edge_distance < shortest_distances[vertex_index]:
                shortest_distances[vertex_index] = shortest_distance + edge_distance
                parents[vertex_index] = nearest_vertex

    # Output
    print("\nShortest path from", node_names[start_vertex], "to", node_names[destination_vertex])
    print("Distance:", shortest_distances[destination_vertex], MONEDA)
    print("Path: ", end="")
    print_path(destination_vertex, parents, node_names)
    print()

# ----------------------------
# Dijkstra Algorithm (Generic)
# ----------------------------
#Computes shortest paths from a source node to all others.
def dijkstra(adjacency_matrix, start_vertex, node_names):
    n_vertices = len(adjacency_matrix[0])

    # shortest_distances[i] will hold the
    # shortest distance from start_vertex to i
    shortest_distances = [sys.maxsize] * n_vertices

    # added[i] will true if vertex i is
    # included in the shortest path tree
    # or shortest distance from start_vertex to
    # i is finalized
    added = [False] * n_vertices

    # Initialize all distances as
    # INFINITE and added[] as false
    for vertex_index in range(n_vertices):
        shortest_distances[vertex_index] = sys.maxsize
        added[vertex_index] = False

    # Distance of source vertex from
    # itself is always 0
    shortest_distances[start_vertex] = 0

    # Parent array to store shortest
    # path tree
    parents = [-1] * n_vertices

    # The starting vertex does not
    # have a parent
    parents[start_vertex] = NO_PARENT

    # Find the shortest path for all
    # vertices
    for i in range(1, n_vertices):
        # Pick the minimum distance vertex
        # from the set of vertices not yet
        # processed. nearest_vertex is
        # always equal to start_vertex in
        # first iteration.
        nearest_vertex = -1
        shortest_distance = sys.maxsize
        for vertex_index in range(n_vertices):
            if (
                    not added[vertex_index]
                    and shortest_distances[vertex_index] < shortest_distance
            ):
                nearest_vertex = vertex_index
                shortest_distance = shortest_distances[vertex_index]

        # Mark the picked vertex as
        # processed
        added[nearest_vertex] = True

        # Update dist value of the
        # adjacent vertices of the
        # picked vertex.
        for vertex_index in range(n_vertices):
            edge_distance = adjacency_matrix[nearest_vertex][vertex_index]

            if (
                    edge_distance > 0
                    and shortest_distance + edge_distance < shortest_distances[vertex_index]
            ):
                parents[vertex_index] = nearest_vertex
                shortest_distances[vertex_index] = shortest_distance + edge_distance
    # Display result for all nodes
    print_solution(start_vertex, shortest_distances, parents, node_names)


# A utility function to print
# the constructed distances
# array and shortest paths
def print_solution(start_vertex, distances, parents, node_names):
    n_vertices = len(distances)
    #    print("Index\t Vertex\t Distance\tPath")

    for vertex_index in range(n_vertices):
        if vertex_index != start_vertex:
            print(
                "\n",
                vertex_index,
                ",",
                "\t\t",
                start_vertex,
                "->",
                vertex_index,
                ",",
                "\t\t",
                node_names[start_vertex],
                "->",
                node_names[vertex_index],
                ",",            
                "\t\t",
                distances[vertex_index],
                ",",            
                "\t\t",
                MONEDA,
                ",",                
                "\t\t",
                end="",
            )
            print_path(vertex_index, parents, node_names)
            print(",")


# Function to print shortest path
# from source to current_vertex
# using parents array
def print_path(current_vertex, parents, node_names):
    # Base case : Source node has
    # been processed
    if current_vertex == NO_PARENT:
        return
    print_path(parents[current_vertex], parents, node_names)
    print(current_vertex, node_names[current_vertex], end=" ")


# Driver code
# -----------------------------
# Main execution block
# -----------------------------
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
    # Define test parameters
    # The test sample variable defines the number of iterations or transactions 
    test_sample = 2
    # The matrix size variable defines the order of the adjacent matrix or number of nodes interconnected in the sample
    matrix_size = 100
    # The max weight variable defines for each matrix element Aij the max distance or value of a transaction from node i to node j, being sqrt(matrix_size)=number_of_nodes  
    max_weight = 100
    # 1st argument --> numbers ranging from 0 to 9,
    # 2nd argument, row = 2, col = 3
    for iteration in range(1, test_sample):
        # Generate a random weighted adjacency matrix
        array = np.random.randint(max_weight, size=(matrix_size, matrix_size))
        # print("test_sample : "," ","\n",test_sample)
        # print("max size : "," ","\n",matrix_size)
        # print("max weight : "," ","\n",max_weight)
        # print("random adjacency_matrix : "," ","\n",array)
        # calculating the determinant of matrix to understand the increase/decrease factor of the transformation
        # det = np.linalg.det(array)
        # print("\nDeterminant of the adjacency matrix:")
        # print(int(det))
        
        # Run full Dijkstra from node 0 (Pedro) to all
        dijkstra(array, 0, node_names)
        # Run Dijkstra specifically to node 12 (Valentina)
        dijkstra_to_target(array, 0, 12, node_names)  # from Pedro to Valentina
        print(array)

