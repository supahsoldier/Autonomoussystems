from collections import deque, defaultdict
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

# Function to generate the a graph field of n by n squares
def generate_graph(n):
    graph = defaultdict(list)
    for x in range(-n//2, n//2):
        for y in range(-n//2, n//2):
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (x + dx, y + dy)
                if -n//2 <= neighbor[0] < n//2 and -n//2 <= neighbor[1] < n//2:
                    graph[(x, y)].append(neighbor)
    return graph

# function performs modified version of BFS search algorithm to find first amount of {max_paths} from {start} to {target} in the {graph}
def bfs_all_paths(graph, start, target, max_paths):
    # print(bfs_all_paths)
    queue = deque([(start, [start])]) # add starting node to the queue
    all_paths = []
    visited = set()

    # loop through queue and neighbours to the queue, if popped node is equal to the target then add path to all_paths list
    while queue and len(all_paths) < max_paths:
        (vertex, path) = queue.popleft()
        # if vertex not in visited:
        if vertex == target:
            all_paths.append(path)
        else:
            visited.add(vertex)
            for neighbor in graph[vertex]:
                # check whether neighbour is already present in the path to avoid cycles
                if neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))

    all_paths.sort(key=len)
    return all_paths

# function check whether there are collision on two paths at a certain time step
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

# Function to simulate movements and find 6 paths without collisions
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
    n = 22
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