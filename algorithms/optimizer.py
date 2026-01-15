from algorithms.task_allocator import TaskAllocator
from algorithms.tsp_solver import TSPSolver
from typing import List, Tuple
from core.config import ALLOC_METHOD, GA_PROFILES, PSO_PROFILES

from core.utils import euclidean_distance
import time

Point = Tuple[float, float]

class Optimizer:

    def __init__(self, drone_configs, tsp_method):
        self.drone_configs = drone_configs
        self.tsp_method = tsp_method

        self.allocator = TaskAllocator(method=ALLOC_METHOD)
        self.solver = TSPSolver(method=tsp_method)

        self.ga_params = None
        self.pso_params = None

    def optimize(self, points, num_drones, *, profile: str):

        if profile not in GA_PROFILES or profile not in PSO_PROFILES:
            raise ValueError(f"Nieznany profil algorytmu: {profile}")

        self.ga_params = GA_PROFILES[profile]
        self.pso_params = PSO_PROFILES[profile]

        if num_drones <= 0:
            return None

        self.solver.drone_configs = self.drone_configs

        task_allocation = self.allocator.allocate(
            points,
            num_drones,
            self.drone_configs
        )

        start_time = time.time()

        results = self.solver.solve_for_drones(task_allocation, ga_params=self.ga_params, pso_params=self.pso_params)

        all_feasible = True
        for drone_id, data in results.items():
            if not data.get("feasible", True):
                all_feasible = False
                print(f"[OPTIMIZER] Dron {drone_id + 1} nie może wykonać swojej trasy – przekroczony limit energii.")

        total_time = time.time() - start_time

        if not all_feasible:
            return None, total_time

        optimized_routes = {}

        for drone_id, data in results.items():
            optimized_routes[drone_id] = data["route_coords"]

        print("\nobciążenie dronów")
        for drone_id, pts in task_allocation.items():
            route = results[drone_id]["route_coords"]

            n_points = len(pts)

            length = 0
            for i in range(len(route) - 1):
                length += euclidean_distance(route[i], route[i + 1])

            cfg = self.drone_configs[drone_id]

            print(
                f"Dron {drone_id}: "
                f"punkty={n_points}, "
                f"długość trasy={length:.1f} m, "
                f"bateria={cfg['battery_capacity']}, "
                f"czas lotu={cfg['flight_time']}, "
                f"prędkość={cfg['speed']}"
            )

        return optimized_routes, total_time
