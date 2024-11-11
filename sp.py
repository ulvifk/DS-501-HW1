import random
from collections import defaultdict
from copy import copy


def dijkstra(src: tuple[int, int], dest: tuple[int, int], graph: list[list[int]], directions: list[tuple[int, int]]) -> \
        tuple[list[tuple[int, int]], float]:
    def generate_path():
        path = []
        current = dest
        while current is not None:
            path.append(current)
            current = prev.get(current)
        path.reverse()
        return path

    dist = defaultdict(lambda: float("inf"))
    prev = {}
    visited = set()

    dist[src] = 0

    Q = [(src[0], src[1])]

    while len(Q) > 0:
        x, y = min(Q, key=lambda v: dist[v])
        Q.remove((x, y))

        if (x, y) == dest:
            break

        visited.add((x, y))

        for dx, dy in directions:
            neighbor_x = x + dx
            neighbor_y = y + dy
            if not (0 <= neighbor_x < len(graph) and
                    0 <= neighbor_y < len(graph[0])):
                continue

            neighbor = (neighbor_x, neighbor_y)
            if neighbor in visited:
                continue

            alt = dist[(x, y)] + graph[neighbor_x][neighbor_y]
            if alt < dist[neighbor]:
                dist[neighbor] = alt
                prev[neighbor] = (x, y)
                Q.append(neighbor)

    return generate_path(), dist[dest]


def greedy_dfs(src: tuple[int, int], dest: tuple[int, int], graph: list[list[int]], directions: list[tuple[int, int]]):
    def get_unvisited_neighbors_sorted_by_cost(x, y) -> list[tuple[int, int]]:
        neighbors = []
        for dx, dy in directions:
            neighbor_x = x + dx
            neighbor_y = y + dy
            if not (0 <= neighbor_x < len(graph) and
                    0 <= neighbor_y < len(graph[0])):
                continue
            if (neighbor_x, neighbor_y) in visited:
                continue

            neighbors.append((neighbor_x, neighbor_y))

        return sorted(neighbors, key=lambda v: graph[v[0]][v[1]], reverse=True)

    visited = set()
    stack = [src]
    path = []
    distance = 0

    while len(stack) > 0:
        current_grid = stack.pop()
        path.append(current_grid)
        distance += graph[current_grid[0]][current_grid[1]]

        if current_grid == dest:
            return path, distance

        neighbors = get_unvisited_neighbors_sorted_by_cost(current_grid[0], current_grid[1])

        if len(neighbors) == 0:
            node = path.pop()
            distance -= graph[node[0]][node[1]]

        for neighbor in neighbors:
            stack.append(neighbor)
            visited.add(neighbor)

    return None, 0


def draw_sol(path: list[tuple[int, int]], dist: float, src: tuple[int, int], dest: tuple[int, int],
             graph: list[list[int]]):
    path_graph: list[list] = [copy(row) for row in graph]

    for x, y in path:
        path_graph[x][y] = "X"

    path_graph[src[0]][src[1]] = "S"
    path_graph[dest[0]][dest[1]] = "D"

    print()
    print(f"Distance: {dist}")
    for row in path_graph:
        print(row)


random.seed(0)
N_ROWS = 10
N_COLS = 10
MIN_COST = 25
MAX_COST = 50

SRC = (0, 0)
DEST = (N_ROWS - 1, N_COLS - 1)

graph = [
    [random.randint(MIN_COST, MAX_COST) for _ in range(N_COLS)]
    for _ in range(N_ROWS)
]

path, dist = dijkstra(SRC, DEST, graph, [(0, 1), (1, 0), (0, -1), (-1, 0)])
draw_sol(path, dist, SRC, DEST, graph)

path, dist = greedy_dfs(SRC, DEST, graph, [(0, 1), (1, 0)])
draw_sol(path, dist, SRC, DEST, graph)

# Heuristic algorithm modifies the Depth First Search algorithm to
# prioritize visiting the neighbors with the lowest cost.
# Algorithm terminates upon reaching the destination node.
