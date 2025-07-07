# The script builds a graph of people interconnected by weights (e.g., relationships, distances, costs, etc.). 
# It allows the user to either:
# manually define this connection matrix,
# or generate it randomly.
# It then:
# computes the shortest path between two selected people (nodes),
# shows the total cost of that path,
# and visualizes the network, highlighting the route.
## To calculate the shortest path using Dijkstra's algorithm in Python, here are some reliable libraries: 
# Option 1: NetworkX (most popular and beginner-friendly)
# Option 2: scipy.sparse.csgraph (efficient for large sparse graphs)
# Option 3 selected: igraph (very fast, suitable for large networks): Performance-oriented, good for large-scale graphs. Handles millions of nodes and tens of millions of edges efficiently.
import random
import matplotlib.pyplot as plt
import numpy as np
from igraph import Graph

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

if modo == "manual":
    adjacency_matrix = input_adjacency_matrix(n)
else:
    adjacency_matrix = generate_random_adjacency_matrix(n)

print("\nMatriz de adyacencia generada:")
for fila in adjacency_matrix:
    print(" ".join(f"{num:2d}" for num in fila))

people = [f"Persona{i}" for i in range(n)]
print("\nNodos disponibles:", ", ".join(people))

source_index = int(input(f"Selecciona índice de origen (0 a {n-1}): "))
target_index = int(input(f"Selecciona índice de destino (0 a {n-1}): "))
source = source_index
target = target_index

edges = []
weights = []
for i in range(n):
    for j in range(i+1, n):
        weight = adjacency_matrix[i][j]
        if weight != 0:
            edges.append((i, j))
            weights.append(weight)

g = Graph(edges=edges, directed=False)
g.add_vertices(n - len(g.vs))  # ensure n nodes
g.es["weight"] = weights
g.vs["label"] = people

# Shortest path
try:
    path = g.get_shortest_paths(source, to=target, weights="weight", output="vpath")[0]
    if not path:
        raise ValueError("No hay ruta disponible.")
    print(f"\nRuta más corta encontrada: {' → '.join(people[i] for i in path)}")
    print("Saltos y costes:")
    total_cost = 0
    path_edges = []
    for i in range(len(path) - 1):
        eid = g.get_eid(path[i], path[i+1])
        w = g.es[eid]['weight']
        total_cost += w
        path_edges.append((path[i], path[i+1]))
        print(f"  {people[path[i]]} → {people[path[i+1]]}: coste {w}")
    print(f"Coste total de la ruta: {total_cost}")
except:
    path = []
    path_edges = []
    print("\nNo hay ruta entre los nodos seleccionados.")

# Matplotlib visualization similar to networkx
coords = g.layout("fr")
pos = {i: coords[i] for i in range(n)}

plt.figure(figsize=(12, 10))
for edge in g.es:
    i, j = edge.tuple
    color = 'red' if (i, j) in path_edges or (j, i) in path_edges else 'gray'
    x = [pos[i][0], pos[j][0]]
    y = [pos[i][1], pos[j][1]]
    plt.plot(x, y, color=color, linewidth=2)

# Draw nodes
for i in range(n):
    x, y = pos[i]
    plt.scatter(x, y, s=1000, c='lightblue', edgecolors='black', zorder=3)
    plt.text(x, y, people[i], ha='center', va='center', fontsize=9, weight='bold')

# Draw edge labels
for edge in g.es:
    i, j = edge.tuple
    x = (pos[i][0] + pos[j][0]) / 2
    y = (pos[i][1] + pos[j][1]) / 2
    label = edge["weight"]
    plt.text(x, y, str(label), fontsize=8, ha='center', va='center', backgroundcolor='white')

plt.title(f"Ruta más corta de {people[source]} a {people[target]}" + (" (en rojo)" if path else " - NO CONECTADOS"))
plt.axis('off')
plt.show()
