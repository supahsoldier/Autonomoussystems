from collections import deque, defaultdict
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

# Function to generate the a field of n by n squares
def generate_graph(n):
    graph = defaultdict(list)
    for x in range(-n//2, n//2):
        for y in range(-n//2, n//2):
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (x + dx, y + dy)
                if -n//2 <= neighbor[0] < n//2 and -n//2 <= neighbor[1] < n//2:
                    graph[(x, y)].append(neighbor)
    return graph

def bfs_all_paths(graph, start, target, max_paths):
    print(bfs_all_paths)
    queue = deque([(start, [start])])
    all_paths = []
    visited = set()

    while queue and len(all_paths) < max_paths:
        (vertex, path) = queue.popleft()
        # if vertex not in visited:
        if vertex == target:
            all_paths.append(path)
        else:
            visited.add(vertex)
            for neighbor in graph[vertex]:
                if neighbor not in path:  # avoid cycles
                    queue.append((neighbor, path + [neighbor]))

    all_paths.sort(key=len)
    return all_paths

def checkPathsCollision(path_a, path_b):
    max_length = max(len(path_a), len(path_b))

    prev_a = ()
    prev_b = ()

    for step in range(max_length):
        next_a = path_a[step] if step < len(path_a) else path_a[-1]
        next_b = path_b[step] if step < len(path_b) else path_b[-1]

        if(next_a == next_b):
            return next_a
        if step > 0:
            if next_a == prev_b or prev_a == next_b:
                return path_a[step]
        
        prev_a = next_a
        prev_b = next_b
        
    return False

# Function to simulate movements
def simulate_movements(all_paths):
    print(simulate_movements)

    numOfEntities = len(all_paths)
    final_paths = []

    final_paths.append(all_paths[0][0])

    for i in range(1, numOfEntities):
        paths = all_paths[i]

        for path in paths:
            collision = False
            for f_path in final_paths:
                collision = checkPathsCollision(path, f_path)
                if collision:
                    break
            if not collision:
                final_paths.append(path)
                break
    
    if(len(all_paths) == len(final_paths)):
        return final_paths
    else:
        print(len(all_paths))
        print(len(final_paths))
        print(final_paths)
    
    return None

def getPaths(starting_vertices, target_vertices):
    print(getPaths)
    # Initialize the grid
    n = 22  # for a 40x40 grid (to include -20 to 20 range)
    graph = generate_graph(n)

    # Find the paths from each starting vertex to each target vertex
    all_paths = []
    i = 1
    for start, target in zip(starting_vertices, target_vertices):
        paths = bfs_all_paths(graph, start, target, i*150)
        if paths:
            all_paths.append(paths)
        else:
            print(f"No path found from {start} to {target}")
        i += 1

    return simulate_movements(all_paths)


# # Randomly select 6 different starting vertices
# all_vertices = list(generate_graph(20).keys())
# starting_vertices = [(0, 1), (-1, -1), (1, -1), (-2, 1), (-1, 3), (1, 3)]

# # Randomly select 6 different target vertices
# # target_vertices = random.sample(all_vertices, 6)
# # target_vertices = [(1, 1), (2, 2), (3, 3), (4, 4), (4, 7), (-5, 7)]
# target_vertices = [(3, -2), (-1, 0), (1, -2), (-1, -2), (3, 0), (1, 0)]

# # Print the starting and target vertices
# print("Starting vertices:", starting_vertices)
# print("Target vertices:", target_vertices)

# # Define empty array
# efficient_target_vertices = []

# # Calculate distance matrix
# distance_matrix = cdist(starting_vertices, target_vertices)

# # Apply Hungarian algorithm to find optimal assignment
# row_ind, col_ind = linear_sum_assignment(distance_matrix)

# # Print the assignments
# for i, j in zip(row_ind, col_ind):
#     efficient_target_vertices.append(target_vertices[j])

# # Find the paths from each starting vertex to each target vertex
# paths = getPaths(starting_vertices, efficient_target_vertices)

# for path in paths:
#     print(path)