# implementacja GA i PSO, Funkcja celu oparta jest
# na koszcie energetycznym lotu wyznaczonym z parametrów
# drona (bateria, czas lotu, prędkość, czas
# obsługi punktu), z ograniczeniem do 80% pojemności baterii
from __future__ import annotations
from typing import List, Tuple, Dict
from core.utils import euclidean_distance
import random
import math
import time
from core import config

Point = Tuple[float, float]
BASE: Point = (0.0, 0.0)


class TSPSolver:
    """implementacja GA i PSO, Funkcja celu oparta jest na koszcie energetycznym lotu wyznaczonym z parametrów drona
    (bateria, czas lotu, prędkość, czas obsługi punktu), z ograniczeniem do 80% pojemności baterii"""

    def __init__(self, method):

        self.method = method.lower()
        self.drone_configs = None
        self.current_drone_config = None

    def compute_distance_matrix(self, points: List[Point]):
        """Buduje macierz odległości Euklidesowych między punktami."""
        n = len(points)
        dist = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                dist[i][j] = euclidean_distance(points[i], points[j])
        return dist

    def route_length(self, order, dist, points):
        BASE = (0.0, 0.0)
        route_coords = [BASE] + [points[i] for i in order] + [BASE]

        drone_config = self.current_drone_config

        E = self.compute_energy_cost(drone_config, route_coords)

        if E > 0.8 * drone_config["battery_capacity"]:
            return 1e12

        return E

    #  Genetic Algorithm
    def create_random_route(self, n: int) -> List[int]:
        r = list(range(n))
        random.shuffle(r)
        return r

    def initial_population(self, pop_size: int, n: int):
        return [self.create_random_route(n) for _ in range(pop_size)]

    def tournament_selection(self, population, dist, points: List[Point], k=3):
        candidates = random.sample(population, k)
        best = min(candidates, key=lambda r: self.route_length(r, dist, points))
        return best[:]

    def order_crossover(self, p1: List[int], p2: List[int]):
        n = len(p1)
        a, b = sorted(random.sample(range(n), 2))
        child = [None] * n

        child[a:b + 1] = p1[a:b + 1]

        pos = 0
        for gene in p2:
            if gene not in child:
                while child[pos] is not None:
                    pos += 1
                child[pos] = gene

        return child

    def swap_mutation(self, route: List[int], mutation_rate: float):
        r = route[:]
        if random.random() < mutation_rate:
            i, j = random.sample(range(len(r)), 2)
            r[i], r[j] = r[j], r[i]
        return r

    def solve_ga(self, points: List[Point], **params):

        self.current_drone_config = params["drone_config"]

        pop_size = params.get("pop_size", config.GA_PARAMS["pop_size"])
        generations = params.get("generations", config.GA_PARAMS["generations"])
        crossover_rate = params.get("crossover_rate", config.GA_PARAMS["crossover_rate"])
        mutation_rate = params.get("mutation_rate", config.GA_PARAMS["mutation_rate"])
        tournament_k = params.get("tournament_k", config.GA_PARAMS["tournament_k"])

        n = len(points)
        if n == 0:
            return [], 0.0, [], 0.0

        dist = self.compute_distance_matrix(points)

        population = self.initial_population(pop_size, n)
        best_route = min(population, key=lambda r: self.route_length(r, dist, points))
        best_cost = self.route_length(best_route, dist, points)
        history = [best_cost]

        start = time.time()

        for _ in range(generations):
            new_pop = []

            # --- ELITARYZM: Zachowaj 2 najlepszych osobników ---
            population.sort(key=lambda r: self.route_length(r, dist, points))
            new_pop.extend([p[:] for p in population[:2]])

            while len(new_pop) < pop_size:
                p1 = self.tournament_selection(population, dist, points, tournament_k)
                p2 = self.tournament_selection(population, dist, points, tournament_k)

                if random.random() < crossover_rate:
                    child = self.order_crossover(p1, p2)
                else:
                    child = p1[:]

                child = self.swap_mutation(child, mutation_rate)
                new_pop.append(child)

            population = new_pop

            curr_best = min(population, key=lambda r: self.route_length(r, dist, points))
            curr_cost = self.route_length(curr_best, dist, points)

            if curr_cost < best_cost:
                best_cost = curr_cost
                best_route = curr_best[:]

            history.append(best_cost)

        best_route = self.two_opt(best_route, dist, points)
        best_cost = self.route_length(best_route, dist, points)

        duration = time.time() - start

        return best_route, best_cost, history, duration

    def random_select_swaps(self, diffs: List[Tuple[int, int]], factor: float) -> List[Tuple[int, int]]:
        """Losowo wybiera podzbiór swapów z listy diffs, skalowany przez factor."""

        if not diffs:
            return []

        count = max(1, int(len(diffs) * factor)) if factor > 0 else 0

        if count >= len(diffs):
            return diffs

        return random.sample(diffs, count)

    # Particle Swam Optimization
    def solve_pso(self, points: List[Point], **params):

        self.current_drone_config = params["drone_config"]

        iterations = params.get("iterations", config.PSO_PARAMS["iterations"])
        swarm_size = params.get("swarm_size", config.PSO_PARAMS["swarm_size"])
        c1 = params.get("c1", config.PSO_PARAMS["c1"])
        c2 = params.get("c2", config.PSO_PARAMS["c2"])

        n = len(points)
        dist = self.compute_distance_matrix(points)

        particles = []
        velocities = []
        pbest = []
        pbest_cost = []

        start = time.time()

        for _ in range(swarm_size):
            perm = list(range(n))
            random.shuffle(perm)
            particles.append(perm)

            velocities.append([])

            cost = self.route_length(perm, dist, points)
            pbest.append(perm[:])
            pbest_cost.append(cost)

        gbest_index = min(range(swarm_size), key=lambda i: pbest_cost[i])
        gbest = pbest[gbest_index][:]
        gbest_cost = pbest_cost[gbest_index]

        for _ in range(iterations):

            for i in range(swarm_size):

                new_velocity = velocities[i][int(len(velocities[i]) * 0.9):]

                diff_pbest = self.permutation_difference(particles[i], pbest[i])
                diff_gbest = self.permutation_difference(particles[i], gbest)

                cognitive_swaps = self.random_select_swaps(diff_pbest, c1 / 2.0)
                new_velocity.extend(cognitive_swaps)

                social_swaps = self.random_select_swaps(diff_gbest, c2 / 2.0)
                new_velocity.extend(social_swaps)

                if len(new_velocity) > n * 2:
                    new_velocity = new_velocity[-n * 2:]

                velocities[i] = new_velocity

                particles[i] = self.apply_swaps(particles[i], velocities[i])

                cost = self.route_length(particles[i], dist, points)
                if cost < pbest_cost[i]:
                    pbest[i] = particles[i][:]
                    pbest_cost[i] = cost

                    if cost < gbest_cost:
                        gbest = particles[i][:]
                        gbest_cost = cost

        # Optymalizacja końcowa
        gbest = self.two_opt(gbest, dist, points)
        gbest_cost = self.route_length(gbest, dist, points)

        duration = time.time() - start
        return gbest, gbest_cost, duration

    def permutation_difference(self, current: List[int], target: List[int]):
        """
        Zwraca listę swapów, które przekształcają current → target.
        """
        diffs = []
        curr = current[:]

        index = {value: i for i, value in enumerate(curr)}

        for i in range(len(curr)):
            if curr[i] != target[i]:
                j = index[target[i]]
                diffs.append((i, j))

                curr[i], curr[j] = curr[j], curr[i]
                index[curr[i]] = i
                index[curr[j]] = j

        return diffs

    def apply_swaps(self, perm: List[int], swaps: List[Tuple[int, int]]):
        """Wykonuje sekwencję swapów na permutacji."""
        p = perm[:]
        for i, j in swaps:
            p[i], p[j] = p[j], p[i]
        return p

    def inversion_mutation(self, route: List[int], mutation_rate: float):
        """Odwraca losowy fragment trasy - znacznie skuteczniejsze dla TSP niż swap."""
        r = route[:]
        if random.random() < mutation_rate:
            # Wybieramy dwa punkty i odwracamy wszystko pomiędzy nimi
            i, j = sorted(random.sample(range(len(r)), 2))
            r[i:j + 1] = r[i:j + 1][::-1]
        return r

    def two_opt(self, route: List[int], dist, points) -> List[int]:
        """Lokalna optymalizacja: usuwa skrzyżowania w trasie."""
        best_route = route[:]
        improved = True

        while improved:
            improved = False
            for i in range(1, len(best_route) - 2):
                for j in range(i + 1, len(best_route)):
                    if j - i == 1: continue  # Sąsiednie punkty - pomijamy

                    # Tworzymy nową trasę przez odwrócenie segmentu
                    new_route = best_route[:]
                    new_route[i:j] = best_route[i:j][::-1]

                    # Sprawdzamy, czy nowa trasa jest lepsza (krótsza/mniej energochłonna)
                    if self.route_length(new_route, dist, points) < self.route_length(best_route, dist, points):
                        best_route = new_route
                        improved = True
            if not improved: break
        return best_route

    def compute_energy_cost(self, drone_config, route_coords: List[Point]) -> float:

        C = drone_config["battery_capacity"]
        T = drone_config["flight_time"]
        v = drone_config["speed"]
        ts = drone_config["service_time"]

        k = C / T

        total_time = 0.0

        for i in range(len(route_coords) - 1):
            p1 = route_coords[i]
            p2 = route_coords[i + 1]

            total_time += euclidean_distance(p1, p2) / v

            if p2 != BASE:
                total_time += ts

        return k * total_time

    def solve_for_drones(self, task_allocation: Dict[int, List[Point]], **params) -> Dict[int, Dict]:

        results: Dict[int, Dict] = {}

        for drone_id, points in task_allocation.items():
            drone_config = self.drone_configs[drone_id]

            filtered_points = [p for p in points if p != BASE]

            if len(filtered_points) == 0:
                route_coords = [BASE, BASE]
                energy = 0.0
                feasible = True
                results[drone_id] = {
                    "order": [],
                    "route_coords": route_coords,
                    "cost": 0.0,
                    "energy": energy,
                    "feasible": feasible,
                    "time": 0.0,
                }
                continue

            if len(filtered_points) == 1:
                single = filtered_points[0]
                route_coords = [BASE, single, BASE]

                energy = self.compute_energy_cost(drone_config, route_coords)
                feasible = energy <= 0.8 * drone_config["battery_capacity"]

                cost = (
                        math.dist(BASE, single) +
                        math.dist(single, BASE)
                )

                results[drone_id] = {
                    "order": [],
                    "route_coords": route_coords,
                    "cost": 0.0,
                    "energy": energy,
                    "feasible": feasible,
                    "time": 0.0,
                }
                continue

            self.current_drone_config = drone_config

            ga_params = {**config.GA_PARAMS, "drone_config": drone_config}
            pso_params = {**config.PSO_PARAMS, "drone_config": drone_config}

            for key, val in params.items():
                if key in config.GA_PARAMS:
                    ga_params[key] = val
                if key in config.PSO_PARAMS:
                    pso_params[key] = val

            if self.method == "ga":
                order, cost, history, duration = self.solve_ga(
                    filtered_points,
                    **ga_params
                )

            elif self.method == "pso":
                order, cost, duration = self.solve_pso(
                    filtered_points,
                    **pso_params
                )

            else:
                raise ValueError(f"Nieznana metoda TSP: {self.method}")

            route_coords = [BASE] + [filtered_points[i] for i in order] + [BASE]

            real_energy = self.compute_energy_cost(drone_config, route_coords)
            feasible = real_energy <= 0.8 * drone_config["battery_capacity"]

            results[drone_id] = {
                "order": order,
                "route_coords": route_coords,
                "cost": cost,
                "energy": real_energy,
                "feasible": feasible,
                "time": duration,
            }

        return results