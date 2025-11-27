#obliczanie tras dla drona (np. nearest neighbor, mTSP)
from typing import List, Tuple
from utils import euclidean_distance

Point = Tuple[float, float]
DRONE_START = (0.0, 0.0)

def nearest_neighbor_tsp(points: List[Point], start: Point | None = None) -> List[Point]:
    if not points:
        return [start] if start else []

    unvisited = points.copy()
    path = []

    if start is None:
        current = unvisited.pop()
        path.append(current)
        start = current
    else:
        current = start
        path.append(start)

    while unvisited:
        next_point = min(unvisited, key=lambda p: euclidean_distance(current, p))
        path.append(next_point)
        unvisited.remove(next_point)
        current = next_point

    path.append(start)
    return path

# Funkcja planująca trasy dla wielu dronów
def plan_paths_for_drones(task_allocation: dict[int, List[Point]]) -> dict[int, List[Point]]:
    planned_paths = {}
    for drone_id, points in task_allocation.items():
        tsp_path = nearest_neighbor_tsp(points, start=DRONE_START)
        planned_paths[drone_id] = tsp_path
    return planned_paths
    # return {drone_id: nearest_neighbor_tsp(points) for drone_id, points in task_allocation.items()}

# To już jest gotowy „silnik” TSP,
# Później dodam GA i PSO to w osobnych funkcjach np.:
# def tsp_ga(points): ...
# def tsp_pso(points): ...