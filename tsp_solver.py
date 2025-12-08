from __future__ import annotations
from typing import List, Tuple, Dict
from utils import euclidean_distance
import random
import math
import time
import config

Point = Tuple[float, float]
BASE: Point = (0.0, 0.0)


# ============================================================
#  TSPSolver – implementacja GA i PSO dla trasowania dronów
# ============================================================

class TSPSolver:

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
        """
        Liczy koszt trasy jako koszt energetyczny E_total zamiast długości geometrycznej.
        """
        # Zamiana permutacji na pełną listę punktów (z bazą)
        BASE = (0.0, 0.0)
        route_coords = [BASE] + [points[i] for i in order] + [BASE]

        # Pobranie parametrów drona (są przechowywane w solverze)
        drone_config = self.current_drone_config

        # Oblicz zużycie energii
        E = self.compute_energy_cost(drone_config, route_coords)

        # Constraint energetyczny – maks 80% baterii
        if E > 0.8 * drone_config["battery_capacity"]:
            return 1e12  # kara – trasa niedopuszczalna

        return E  # normalny koszt trasy

    # -------------------------------------------------------
    #  GENETIC ALGORITHM (GA)
    # -------------------------------------------------------

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
        """Order Crossover (OX)."""
        n = len(p1)
        a, b = sorted(random.sample(range(n), 2))
        child = [None] * n

        # fragment z p1
        child[a:b + 1] = p1[a:b + 1]

        # reszta z p2 (w kolejności)
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
        """
        Główny algorytm genetyczny do TSP dla jednego drona.
        Zwraca:
        - final_route: permutację indeksów punktów
        - best_cost: długość najlepszej trasy (z bazą)
        - history: listę najlepszych wyników z kolejnych generacji
        - duration: czas wykonania w sekundach
        """

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

        # Inicjalizacja populacji
        population = self.initial_population(pop_size, n)
        best_route = min(population, key=lambda r: self.route_length(r, dist, points))
        best_cost = self.route_length(best_route, dist, points)
        history = [best_cost]

        start = time.time()

        # Główna pętla GA
        for _ in range(generations):
            new_pop = []

            while len(new_pop) < pop_size:
                # wybór rodziców
                p1 = self.tournament_selection(population, dist, points, tournament_k)
                p2 = self.tournament_selection(population, dist, points, tournament_k)

                # crossover
                if random.random() < crossover_rate:
                    child = self.order_crossover(p1, p2)
                else:
                    child = p1[:]  # kopia rodzica

                # mutacja
                child = self.swap_mutation(child, mutation_rate)
                new_pop.append(child)

            population = new_pop

            # aktualizacja najlepszego osobnika
            curr_best = min(population, key=lambda r: self.route_length(r, dist, points))
            curr_cost = self.route_length(curr_best, dist, points)

            if curr_cost < best_cost:
                best_cost = curr_cost
                best_route = curr_best[:]

            history.append(best_cost)

        duration = time.time() - start

        return best_route, best_cost, history, duration

    def solve_pso(self, points: List[Point], **params):
        """
        PSO dla problemu TSP (wersja z permutacjami).
        Zwraca:
        - najlepszy znaleziony order (permutacja)
        - koszt trasy
        - czas wykonania
        """

        self.current_drone_config = params["drone_config"]

        iterations = params.get("iterations", config.PSO_PARAMS["iterations"])
        swarm_size = params.get("swarm_size", config.PSO_PARAMS["swarm_size"])
        c1 = params.get("c1", config.PSO_PARAMS["c1"])
        c2 = params.get("c2", config.PSO_PARAMS["c2"])

        n = len(points)
        dist = self.compute_distance_matrix(points)

        # -------------------------------
        # 1. Inicjalizacja cząstek
        # -------------------------------
        particles = []  # pozycje (permutacje)
        velocities = []  # prędkości (listy swapów)
        pbest = []  # najlepsza pozycja cząstki
        pbest_cost = []  # koszt najlepszej pozycji cząstki

        start = time.time()

        for _ in range(swarm_size):
            perm = list(range(n))
            random.shuffle(perm)
            particles.append(perm)

            velocities.append([])  # startowo brak swapów

            cost = self.route_length(perm, dist, points)
            pbest.append(perm[:])
            pbest_cost.append(cost)

        # global best
        gbest_index = min(range(swarm_size), key=lambda i: pbest_cost[i])
        gbest = pbest[gbest_index][:]
        gbest_cost = pbest_cost[gbest_index]

        # -------------------------------
        # 2. Pętla optymalizacyjna PSO
        # -------------------------------
        for _ in range(iterations):

            for i in range(swarm_size):

                # -------------------------------
                # velocity update (swap-based)
                # -------------------------------

                # dotychczasowa prędkość (inertia)
                new_velocity = velocities[i][:]

                # różnica: particle → pbest  (list of swaps)
                diff_pbest = self.permutation_difference(particles[i], pbest[i])
                # różnica: particle → gbest
                diff_gbest = self.permutation_difference(particles[i], gbest)

                # część kognitywna (swapy w strone własnego najlepszego rozwiązania)
                if random.random() < c1:
                    new_velocity.extend(diff_pbest)

                # część społeczna (cząstka zmierza w strone najlepszej trasy w swarmie)
                if random.random() < c2:
                    new_velocity.extend(diff_gbest)

                # zbyt długa prędkość niepotrzebna — limituje:
                if len(new_velocity) > n * 3:
                    new_velocity = new_velocity[-n * 3:]

                velocities[i] = new_velocity

                # -------------------------------
                # position update (apply swaps)
                # -------------------------------

                particles[i] = self.apply_swaps(particles[i], velocities[i])

                # -------------------------------
                # aktualizacja pbest
                # -------------------------------

                cost = self.route_length(particles[i], dist, points)
                if cost < pbest_cost[i]:
                    pbest[i] = particles[i][:]
                    pbest_cost[i] = cost

                    if cost < gbest_cost:
                        gbest = particles[i][:]
                        gbest_cost = cost

        duration = time.time() - start

        return gbest, gbest_cost, duration

    # -------------------------------------------------------
    #  HELPERS FOR PSO + PERMUTATIONS
    # -------------------------------------------------------

    def permutation_difference(self, current: List[int], target: List[int]):
        """
        Zwraca listę swapów, które przekształcają current → target.
        Swap reprezentujemy jako tuple (i, j).
        """
        diffs = []
        curr = current[:]

        index = {value: i for i, value in enumerate(curr)}

        for i in range(len(curr)):
            if curr[i] != target[i]:
                j = index[target[i]]
                diffs.append((i, j))

                # wykonaj swap i odśwież index
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

    # -------------------------------------------------------
    #  ROZWIĄZYWANIE TSP DLA WIELU DRONÓW
    # -------------------------------------------------------

    def compute_energy_cost(self, drone_config, route_coords: List[Point]) -> float:
        """
        Oblicza całkowite zużycie energii dla pełnej trasy:
        BASE -> p1 -> p2 -> ... -> pn -> BASE
        """

        C = drone_config["battery_capacity"]   # mAh
        T = drone_config["flight_time"]        # sekundy
        v = drone_config["speed"]              # m/s
        ts = drone_config["service_time"]      # czas obsługi punktu

        k = C / T  # stała energetyczna

        total_time = 0.0

        # przejście po współrzędnych
        for i in range(len(route_coords) - 1):
            p1 = route_coords[i]
            p2 = route_coords[i + 1]

            # czas przelotu
            total_time += euclidean_distance(p1, p2) / v

            # czas obsługi (tylko gdy p2 nie jest bazą)
            if p2 != BASE:
                total_time += ts

        return k * total_time


    def solve_for_drones(self, task_allocation: Dict[int, List[Point]], **params) -> Dict[int, Dict]:
        """
        Uruchamia wybraną metodę TSP (GA lub PSO) dla każdego drona.
        Zwraca dict:
        {
            dron_id: {
                "order": [... indeksy ...],
                "route_coords": [... współrzędne ...],
                "cost": float,
                "time": float
            }
        }
        """

        results: Dict[int, Dict] = {}

        for drone_id, points in task_allocation.items():
            drone_config = self.drone_configs[drone_id]

            filtered_points = [p for p in points if p != BASE]

            if len(filtered_points) == 0:
                # brak punktów inspekcji - dron tylko siedzi w bazie
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
                # tylko jeden punkt: baza -> punkt -> baza, bez GA
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

            # 2) Rozwiązanie TSP
            # ustaw konfigurację drona dla route_length i compute_energy_cost

            self.current_drone_config = drone_config

            # 2) Rozwiązanie TSP
            if self.method == "ga":
                order, cost, history, duration = self.solve_ga(
                    filtered_points,
                    drone_config=drone_config,
                    **config.GA_PARAMS
                )

            elif self.method == "pso":
                order, cost, duration = self.solve_pso(
                    filtered_points,
                    drone_config=drone_config,
                    **config.PSO_PARAMS
                )

            else:
                raise ValueError(f"Nieznana metoda TSP: {self.method}")

            # 3) Konwersja permutacji indeksów → współrzędne + baza
            route_coords = [BASE] + [filtered_points[i] for i in order] + [BASE]

            real_energy = self.compute_energy_cost(drone_config, route_coords)
            feasible = real_energy <= 0.8 * drone_config["battery_capacity"]

            results[drone_id] = {
                "order": order,
                "route_coords": route_coords,
                "cost": cost,          # to, na czym optymalizował GA/PSO
                "energy": real_energy, # faktyczny E_total
                "feasible": feasible,
                "time": duration,
            }

        return results
