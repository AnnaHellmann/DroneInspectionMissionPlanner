# optimizer.py
from task_allocator import TaskAllocator
from tsp_solver import TSPSolver
from typing import List, Tuple, Dict

Point = Tuple[float, float]


class Optimizer:
    """
    Główna klasa optymalizacji misji.
    Odpowiada za:
    1. alokację punktów między drony
    2. wywołanie metaheurystyki (GA / PSO / NN)
    """

    def __init__(self, drone_configs: Dict[int, Dict], tsp_method="ga"):
        self.drone_configs = drone_configs
        self.tsp_method = tsp_method   # "ga" lub "pso"

        # domyślna metoda podziału (możesz zmienić na inną)
        self.allocator = TaskAllocator(method="best_fit")

        # solver tras TSP
        self.solver = TSPSolver(method=tsp_method)

    def optimize(self, points: List[Point], num_drones: int):
        """
        1. dzieli punkty między drony (mTSP)
        2. optymalizuje TSP dla każdego drona
        """

        if num_drones <= 0:
            return None

        # --- 1. Alokacja punktów (mTSP → podproblem TSP dla każdego drona)
        task_allocation = self.allocator.allocate(
            points,
            num_drones,
            self.drone_configs
        )

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

        # --- 3. Przekształcenie wyników do formatu używanego w app.py
        optimized_routes = {}

        for drone_id, data in results.items():
            optimized_routes[drone_id] = data["route_coords"]

        return optimized_routes
