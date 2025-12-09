# optimizer.py
from task_allocator import TaskAllocator
from tsp_solver import TSPSolver
from typing import List, Tuple, Dict
from config import ALLOC_METHOD

from utils import euclidean_distance
import time

Point = Tuple[float, float]

class Optimizer:
    def __init__(self, drone_configs, tsp_method):
        self.drone_configs = drone_configs
        self.tsp_method = tsp_method

        self.allocator = TaskAllocator(method=ALLOC_METHOD)
        self.solver = TSPSolver(method=tsp_method)



    def optimize(self, points: List[Point], num_drones: int):
        """
        1. dzieli punkty między drony (mTSP)
        2. optymalizuje TSP dla każdego drona
        """

        if num_drones <= 0:
            return None

        self.solver.drone_configs = self.drone_configs

        # --- 1. Alokacja punktów (mTSP → podproblem TSP dla każdego drona)
        task_allocation = self.allocator.allocate(
            points,
            num_drones,
            self.drone_configs
        )

        start_time = time.time()

        # --- 2. Wywołanie solvera TSP (GA / PSO)
        if self.tsp_method == "ga":
            results = self.solver.solve_for_drones(
                task_allocation,
                pop_size=80,
                generations=300,
                mutation_rate=0.1,
                crossover_rate=0.9
            )
        elif self.tsp_method == "pso":
            results = self.solver.solve_for_drones(
                task_allocation,
                iterations=300,
                swarm_size=50,
                w=0.8,
                c1=1.5,
                c2=1.5
            )

        # --- 3. Sprawdzenie, czy wszystkie trasy są energetycznie wykonalne
        all_feasible = True
        for drone_id, data in results.items():
            if not data.get("feasible", True):
                all_feasible = False
                print(f"[OPTIMIZER] Dron {drone_id + 1} nie może wykonać swojej trasy – przekroczony limit energii.")

        total_time = time.time() - start_time
        print(f"[OPTIMIZER] Całkowity czas optymalizacji ({self.tsp_method.upper()}): {total_time:.3f} s")

        if not all_feasible:
            # sygnał do app.py, że misja jest niewykonalna
            return None, total_time

        # --- 3. Przekształcenie wyników do formatu używanego w app.py
        optimized_routes = {}

        for drone_id, data in results.items():
            optimized_routes[drone_id] = data["route_coords"]

        return optimized_routes, total_time
