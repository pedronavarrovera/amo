# The script builds a graph of people interconnected by weights (e.g., relationships, distances, costs, etc.). 
# It allows the user to either:
# manually define this connection matrix,
# or generate it randomly.
# It then:
# computes the shortest path between two selected people (nodes),
# shows the total cost of that path,
# and visualizes the network, highlighting the route.

import random
import networkx as nx
import matplotlib.pyplot as plt

def generate_random_adjacency_matrix(size, max_weight=10, density=0.3):
    matrix = [[0]*size for _ in range(size)]
    for i in range(size):
        for j in range(i+1, size):
            if random.random() < density:
                weight = random.randint(1, max_weight)
                matrix[i][j] = weight
                matrix[j][i] = weight
    return matrix

def input_adjacency_matrix(size):
    print("Introduce la matriz de adyacencia fila por fila (valores separados por espacio):")
    matrix = []
    for i in range(size):
        while True:
            row = input(f"Fila {i+1}: ")
            try:
                numbers = list(map(int, row.strip().split()))
                if len(numbers) != size:
                    raise ValueError("La fila debe tener exactamente {} números.".format(size))
                matrix.append(numbers)
                break
            except Exception as e:
                print("Error:", e)
    return matrix

# Modo de entrada
modo = input("¿Cómo quieres introducir la matriz? (aleatoria/manual): ").strip().lower()
n = int(input("Número de personas (nodos): "))

# Matriz
if modo == "manual":
    adjacency_matrix = input_adjacency_matrix(n)
else:
    adjacency_matrix = generate_random_adjacency_matrix(n)

# Mostrar matriz
print("\nMatriz de adyacencia generada:")
for fila in adjacency_matrix:
    print(" ".join(f"{num:2d}" for num in fila))

# Crear lista de nodos
people = [f"Persona{i}" for i in range(n)]
print("\nNodos disponibles:", ", ".join(people))

# Selección de nodos
source_index = int(input(f"Selecciona índice de origen (0 a {n-1}): "))
target_index = int(input(f"Selecciona índice de destino (0 a {n-1}): "))
source = people[source_index]
target = people[target_index]

# Crear grafo
G = nx.Graph()
for i in range(n):
    for j in range(n):
        weight = adjacency_matrix[i][j]
        if weight != 0:
            G.add_edge(people[i], people[j], weight=weight)

# Calcular ruta más corta
try:
    path = nx.dijkstra_path(G, source, target, weight='weight')
    path_edges = list(zip(path, path[1:]))
    total_cost = sum(G[u][v]['weight'] for u, v in path_edges)
    print(f"\nRuta más corta encontrada: {' → '.join(path)}")
    print(f"Coste total de la ruta: {total_cost}")
except nx.NetworkXNoPath:
    path = []
    path_edges = []
    print("\nNo hay ruta entre los nodos seleccionados.")

# Visualización
pos = nx.spring_layout(G, seed=42)
edge_labels = nx.get_edge_attributes(G, 'weight')
edge_colors = ['red' if (u, v) in path_edges or (v, u) in path_edges else 'gray' for u, v in G.edges()]

plt.figure(figsize=(12, 10))
nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=1000,
        edge_color=edge_colors, width=2)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.title(f"Ruta más corta de {source} a {target}" + (" (en rojo)" if path else " - NO CONECTADOS"))
plt.show()

