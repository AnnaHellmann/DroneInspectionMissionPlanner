from task_allocator import TaskAllocator
from tsp_solver import plan_paths_for_drones
from utils import euclidean_distance


def flatten_route(route):
    """Spłaszcza podtrasy do listy punktów."""
    flat = []
    for item in route:
        if isinstance(item, list):
            for p in item:
                flat.append(p)
        else:
            flat.append(item)
    return flat


class Optimizer:
    def __init__(self, drones_config, task_alloc_method="best_fit"):
        self.drones_config = drones_config
        self.allocator = TaskAllocator(method=task_alloc_method)

        self.energy_cost_per_distance = 1.0
        self.energy_cost_per_second = 0.2
        self.speed = 1.0

    def validate_route(self, drone_id, route):
        total_distance = 0.0
        for i in range(len(route) - 1):
            total_distance += euclidean_distance(route[i], route[i + 1])

        total_time = total_distance / self.speed
        energy_used = (total_distance * self.energy_cost_per_distance) + \
                      (total_time * self.energy_cost_per_second)

        drone = self.drones_config[drone_id]
        errors = []

        if total_distance > drone["range"]:
            errors.append("range")
        if total_time > drone["flight_time"]:
            errors.append("flight_time")
        if energy_used > drone["battery"]:
            errors.append("battery")

        return errors

    def split_route(self, drone_id, route):
        drone = self.drones_config[drone_id]
        max_dist = drone["range"]

        subroutes = []
        current_route = [route[0]]
        current_dist = 0.0

        for i in range(1, len(route)):
            step = euclidean_distance(route[i - 1], route[i])

            if current_dist + step > max_dist:
                current_route.append(route[i - 1])
                subroutes.append(current_route)

                current_route = [route[i - 1]]
                current_dist = 0.0

            current_route.append(route[i])
            current_dist += step

        if len(current_route) > 1:
            subroutes.append(current_route)

        return subroutes

    def optimize(self, points, num_drones):
        allocation = self.allocator.allocate(points, num_drones, self.drones_config)
        routes = plan_paths_for_drones(allocation)

        optimized = {}

        for drone_id, route in routes.items():

            errors = self.validate_route(drone_id, route)

            if not errors:
                optimized[drone_id] = route

            else:
                print(f"[OPTIMIZER] Dron {drone_id} ma za dużą trasę {errors}, dzielę na podtrasy.")
                subroutes = self.split_route(drone_id, route)

                final_route = flatten_route(subroutes)
                optimized[drone_id] = final_route

        return optimized
