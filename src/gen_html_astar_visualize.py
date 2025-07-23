
# This file generate heatmap and html visulaizer
import argparse
import math
import importlib.util
import os
import sys
from html import escape
import time
import numpy as np
import matplotlib.pyplot as plt


spec_astar = importlib.util.spec_from_file_location("astar", "src/astar.py")
astar_module = importlib.util.module_from_spec(spec_astar)
spec_astar.loader.exec_module(astar_module)

spec_heur = importlib.util.spec_from_file_location("heuristics", "src/heuristics.py")
heur_module = importlib.util.module_from_spec(spec_heur)
spec_heur.loader.exec_module(heur_module)

def parse_map(map_path):
    with open(map_path, 'r') as f:
        lines = f.readlines()
    header_idx = next(i for i, line in enumerate(lines) if line.strip().lower() == 'map')
    grid = [list(line.strip()) for line in lines[header_idx+1:]]
    return grid

def parse_scenario(scen_path):
    with open(scen_path, 'r') as f:
        lines = f.readlines()[1:]
    cases = []
    for line in lines:
        parts = line.strip().split()
        sx, sy, gx, gy = int(parts[4]), int(parts[5]), int(parts[6]), int(parts[7])
        benchmark = float(parts[8]) if len(parts) > 8 else None
        cases.append(((sy, sx), (gy, gx), benchmark))
    return cases

def get_neighbors(pos, grid):
    directions = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    r, c = pos
    rows, cols = len(grid), len(grid[0])
    result = []

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if not (0 <= nr < rows and 0 <= nc < cols): continue
        if grid[nr][nc] != '.': continue
        if abs(dr) + abs(dc) == 2:
            if grid[r][nc] != '.' or grid[nr][c] != '.':
                continue
        result.append((nr, nc))
    return result

def cost(a, b):
    return math.sqrt(2) if a[0] != b[0] and a[1] != b[1] else 1

def a_star_wrapped(start, goal, grid, heuristic):
    def h(a, b=goal): return heuristic(a, b)
    def wrapped_heur(pos1, pos2): return h(pos1, pos2)
    return astar_module.a_star(start, goal, grid, wrapped_heur)

def render_html(grid, path, visited, start, goal, out_file, duration, path_length, visited_count, cost_total, benchmark):
    cell_classes = {}

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) == start:
                cell_classes[(r, c)] = 'start'
            elif (r, c) == goal:
                cell_classes[(r, c)] = 'goal'
            elif grid[r][c] == '@' or grid[r][c] == 'T':
                cell_classes[(r, c)] = 'wall'
            elif (r, c) in path:
                cell_classes[(r, c)] = 'path'
            elif (r, c) in visited:
                cell_classes[(r, c)] = 'visited'
            else:
                cell_classes[(r, c)] = 'empty'

    with open(out_file, 'w') as f:
        f.write(f'''
<html>
<head>
<style>
  .grid {{
    display: grid;
    grid-template-columns: repeat({len(grid[0])}, 10px);
    width: fit-content;
  }}
  .cell {{
    width: 10px;
    aspect-ratio: 1;
    border: 1px solid #ccc;
  }}
  .empty {{ background: white; }}
  .wall {{ background: black; }}
  .visited {{ background: lightblue; }}
  .path {{ background: green; }}
  .start {{ background: blue; }}
  .goal {{ background: red; }}
  .wallVisited {{ background: tomato; }}
</style>
</head>
<body>
<div class="grid">
''')

        for r in range(len(grid)):
            for c in range(len(grid[0])):
                cls = cell_classes.get((r, c), 'empty')
                f.write(f'<div class="cell {cls}"></div>')
        f.write(f'''
</div>
<br><br>
<div>
  <h3>Run Statistics</h3>
  <ul>
    <li><strong>Time Taken:</strong> {duration:.6f} seconds</li>
    <li><strong>Path Length:</strong> {path_length}</li>
    <li><strong>Nodes Visited:</strong> {visited_count}</li>
    <li><strong>Total Cost:</strong> {cost_total:.2f}</li>
    <li><strong>Expected Cost:</strong> {benchmark:.3f}</li>
  </ul>
</div>
</body>
</html>
''')

    print(f"HTML saved to {out_file}")

def render_heatmap(grid, visited, start, goal, out_file):
    heatmap = np.zeros((len(grid), len(grid[0])), dtype=int)

    for r, c in visited:
        heatmap[r][c] += 1

    plt.figure(figsize=(10, 8))
    plt.imshow(heatmap, cmap='hot', interpolation='nearest')
    plt.colorbar(label="Visit Count")
    plt.title("A* Node Expansion Heatmap")
    plt.scatter(start[1], start[0], c='blue', label='Start', s=50)
    plt.scatter(goal[1], goal[0], c='red', label='Goal', s=50)
    plt.legend()
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()
    print(f"Heatmap saved to {out_file}")

def main():
    mapName = "arena"
    case = 42
    heuristics = ["manhattan", "euclidean", "diagonal", "hybrid"]

    map_path = f"./maps/{mapName}.map"
    scen_path = f"./maps/{mapName}.map.scen"

    grid = parse_map(map_path)
    scenarios = parse_scenario(scen_path)

    if case >= len(scenarios):
        print(f"Invalid case index: {case}")
        return

    start, goal, benchmark = scenarios[case]
    converted_grid = [[1 if cell in ('@', 'T') else 0 for cell in row] for row in grid]

    for heuristic in heuristics:
        heuristic_func = getattr(heur_module, heuristic, None)
        if not heuristic_func:
            print(f"Heuristic '{heuristic}' not found in heuristics.py")
            continue

        print(f"\n▶ Running A* from {start} to {goal} using '{heuristic}' heuristic...")

        start_time = time.time()
        path, visited = astar_module.a_star(start, goal, converted_grid, heuristic_func)
        end_time = time.time()

        duration = end_time - start_time
        path_length = len(path)
        visited_count = len(visited)
        cost_total = sum(cost(path[i], path[i + 1]) for i in range(len(path) - 1)) if path else 0

        print(f"Time Taken: {duration:.6f} seconds")
        print(f"Path Length: {path_length}")
        print(f"Nodes Visited: {visited_count}")
        print(f"Optimal Cost: {cost_total:.2f}")

        out_html = f"./results/htm/{mapName}_{case}_{heuristic}.html"
        out_heatmap = f"./results/heatmap/{mapName}_{case}_{heuristic}.png"

        render_html(grid, path, visited, start, goal, out_html,
                    duration, path_length, visited_count, cost_total, benchmark)
        render_heatmap(grid, visited, start, goal, out_heatmap)

if __name__ == "__main__":
    main()
