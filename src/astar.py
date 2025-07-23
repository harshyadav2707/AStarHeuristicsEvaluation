import math
import heapq

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

# A* pathfinding algorithm for 8-directional grid movement with corner cutting prevention
def a_star(start, goal, grid, heuristic):
    if grid[start[0]][start[1]] == 1 or grid[goal[0]][goal[1]] == 1:
        return [], set()

    open_set = [] 
    heapq.heappush(open_set, (0, heuristic(start, goal), start))

    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    visited_nodes = set() 
    closed_set = set()

    while open_set:
        _, _, current = heapq.heappop(open_set)

        if current in closed_set:
            continue

        closed_set.add(current)
        visited_nodes.add(current)

        if current == goal:
            return reconstruct_path(came_from, current), visited_nodes

        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
            neighbor = (current[0] + dx, current[1] + dy)

            # Check boundaries
            if 0 <= neighbor[0] < len(grid) and 0 <= neighbor[1] < len(grid[0]):
                if grid[neighbor[0]][neighbor[1]] == 1:
                    continue  # Wall

                # Prevent diagonal corner cutting
                if dx != 0 and dy != 0:
                    if grid[current[0] + dx][current[1]] == 1 or grid[current[0]][current[1] + dy] == 1:
                        continue

                move_cost = math.sqrt(2) if dx != 0 and dy != 0 else 1
                tentative_g = g_score[current] + move_cost

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], heuristic(neighbor, goal), neighbor))

    return [], visited_nodes