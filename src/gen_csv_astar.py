import importlib.util
import time
import math
import csv
import os

# ======= CONFIG =======
MAP_NAME = "maze512-1-0"
MAP_FILE = f"./maps/{MAP_NAME}.map"
SCEN_FILE = f"./maps/{MAP_NAME}.map.scen"
RESULTS_CSV = f"./results/csv/{MAP_NAME}_evaluation.csv"
HEURISTICS = ["manhattan", "euclidean", "diagonal", "hybrid"]
# ======================

# Load astar
spec_astar = importlib.util.spec_from_file_location("astar", "src/astar.py")
astar_module = importlib.util.module_from_spec(spec_astar)
spec_astar.loader.exec_module(astar_module)

# Load heuristics
spec_heur = importlib.util.spec_from_file_location("heuristics", "src/heuristics.py")
heur_module = importlib.util.module_from_spec(spec_heur)
spec_heur.loader.exec_module(heur_module)

# parse map file from moving ai labs
def parse_map(map_path):
    with open(map_path, 'r') as f:
        lines = f.readlines()
    header_idx = next(i for i, line in enumerate(lines) if line.strip().lower() == 'map')
    grid = [list(line.strip()) for line in lines[header_idx + 1:]]
    return grid

# parse scen file from moving ai labs
def parse_scenario(scen_path):
    with open(scen_path, 'r') as f:
        lines = f.readlines()[1:]
    cases = []
    for line in lines:
        parts = line.strip().split()
        sx, sy, gx, gy = int(parts[4]), int(parts[5]), int(parts[6]), int(parts[7])
        benchmark = float(parts[8]) if len(parts) > 8 else None
        cases.append(((sy, sx), (gy, gx), benchmark))  # row, col
    return cases

def cost(a, b):
    return math.sqrt(2) if a[0] != b[0] and a[1] != b[1] else 1

def run_all():
    grid = parse_map(MAP_FILE)
    scenarios = parse_scenario(SCEN_FILE)
    wall_chars = ('@', 'T')
    converted_grid = [[1 if cell in wall_chars else 0 for cell in row] for row in grid]

    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)

    with open(RESULTS_CSV, 'w', newline='') as csvfile:
        fieldnames = [
            'case_id', 'heuristic', 'start', 'goal',
            'expected_cost', 'actual_cost',
            'path_length', 'visited_nodes', 'time_sec',
            'cost_error'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        # run case by case
        for case_id, (start, goal, benchmark) in enumerate(scenarios):
            for heur_name in HEURISTICS:
                heuristic_func = getattr(heur_module, heur_name, None)

                start_time = time.time()
                path, visited = astar_module.a_star(start, goal, converted_grid, heuristic_func)
                end_time = time.time()

                duration = end_time - start_time
                path_length = len(path)
                actual_cost = sum(cost(path[i], path[i+1]) for i in range(len(path) - 1)) if path else 0
                visited_count = len(visited)
                cost_error = abs(actual_cost - benchmark) if benchmark is not None else None

                writer.writerow({
                    'case_id': case_id,
                    'heuristic': heur_name,
                    'start': start,
                    'goal': goal,
                    'expected_cost': f"{benchmark:.5f}" if benchmark else "",
                    'actual_cost': f"{actual_cost:.5f}",
                    'path_length': path_length,
                    'visited_nodes': visited_count,
                    'time_sec': f"{duration:.6f}",
                    'cost_error': f"{cost_error:.5f}" if cost_error is not None else ""
                })

                print(f"[{case_id}] {heur_name}: cost={actual_cost:.2f}, expected={benchmark:.2f}, Δ={cost_error:.4f}")

if __name__ == "__main__":
    run_all()