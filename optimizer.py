from task_allocator import TaskAllocator
from tsp_solver import plan_paths_for_drones
from utils import euclidean_distance


class Optimizer:
    def __init__(self, drones_config, task_alloc_method="best_fit"):
        self.drones_config = drones_config
        self.allocator = TaskAllocator(method=task_alloc_method)

        # współczynniki energetyczne
        self.energy_cost_per_distance = 1.0
        self.energy_cost_per_second = 0.2
        self.speed = 1.0

    # ===============================
    #   Walidacja całej trasy drona
    # ===============================
    def validate_route(self, drone_id, route):
        total_distance = sum(
            euclidean_distance(route[i], route[i + 1])
            for i in range(len(route) - 1)
        )

        total_time = total_distance / self.speed
        energy_used = total_distance * self.energy_cost_per_distance + \
                      total_time * self.energy_cost_per_second

        drone = self.drones_config[drone_id]
        errors = []

        if total_distance > drone["range"]:
            errors.append("range")
        if total_time > drone["flight_time"]:
            errors.append("flight_time")
        if energy_used > drone["battery"]:
            errors.append("battery")

        return errors

    # ===============================
    #       Główna funkcja
    # ===============================
    def optimize(self, points, num_drones):
        # ------------------------------
        # 1. policz minimalny dystans między punktami
        # ------------------------------
        min_step = float("inf")

        if len(points) > 1:
            for i in range(len(points)):
                for j in range(i + 1, len(points)):
                    dist = euclidean_distance(points[i], points[j])
                    if dist < min_step:
                        min_step = dist
        else:
            min_step = 0

        # ------------------------------
        # 2. sprawdź czy którykolwiek dron nie jest zbyt słaby
        # ------------------------------
        for drone_id, cfg in self.drones_config.items():
            if cfg["range"] < min_step:
                print("\n[ERROR] Misja niemożliwa do wykonania!")
                print(f"Dron {drone_id} ma zbyt mały zasięg.")
                print(f"Minimalna odległość między punktami mapy: {min_step:.2f} m")
                print(f"Zasięg drona: {cfg['range']} m\n")
                return None

        # ------------------------------
        # 3. normalny przydział punktów
        # ------------------------------
        allocation = self.allocator.allocate(points, num_drones, self.drones_config)
        routes = plan_paths_for_drones(allocation)

        # ------------------------------
        # 4. sprawdzenie pełnej trasy
        # ------------------------------
        for drone_id, route in routes.items():
            errors = self.validate_route(drone_id, route)
            if errors:
                print("\n[ERROR] Misja niemożliwa — trasa dla drona "
                      f"{drone_id} narusza limity: {errors}\n")
                return None

        # ------------------------------
        # 5. wszystko OK → zwracamy trasy
        # ------------------------------
        return routes
