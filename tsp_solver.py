from __future__ import annotations
from typing import List, Tuple, Dict
from utils import euclidean_distance
import random
import math
import time

Point = Tuple[float, float]
BASE: Point = (0.0, 0.0)


# ============================================================
#  TSPSolver – implementacja GA i PSO dla trasowania dronów
# ============================================================

class TSPSolver:
    """
    Klasa odpowiedzialna za rozwiązywanie problemu TSP
    metodami metaheurystycznymi: GA oraz PSO.
    """

    def __init__(self, method: str = "ga"):
        """
        method: "ga" lub "pso"
        """
        self.method = method.lower()

    # -------------------------------------------------------
    #  HELPERY
    # -------------------------------------------------------

    def compute_distance_matrix(self, points: List[Point]):
        """Buduje macierz odległości Euklidesowych między punktami."""
        n = len(points)
        dist = [[0.0] * n for _ in range(n)]
        for i in range(n):
            x1, y1 = points[i]
            for j in range(n):
                x2, y2 = points[j]
                dist[i][j] = math.hypot(x1 - x2, y1 - y2)
        return dist

    def route_length(self, route: List[int], dist_matrix, points: List[Point]) -> float:
        """
        Liczy koszt trasy:
        BASE -> pierwszy punkt -> ... -> ostatni punkt -> BASE
        """
        # baza -> pierwszy punkt
        first = route[0]
        cost = math.dist(BASE, points[first])

        # punkty między sobą
        for i in range(len(route) - 1):
            a = route[i]
            b = route[i + 1]
            cost += dist_matrix[a][b]

        # ostatni punkt -> baza
        last = route[-1]
        cost += math.dist(points[last], BASE)

        return cost

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

    def solve_ga(
        self,
        points: List[Point],
        pop_size: int = 100,
        generations: int = 300,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        tournament_k: int = 3,
    ):
        """
        Główny algorytm genetyczny do TSP dla jednego drona.
        Zwraca:
        - final_route: permutację indeksów punktów
        - best_cost: długość najlepszej trasy (z bazą)
        - history: listę najlepszych wyników z kolejnych generacji
        - duration: czas wykonania w sekundach
        """

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

    # -------------------------------------------------------
    #  PARTICLE SWARM OPTIMIZATION (PSO) – placeholder
    # -------------------------------------------------------

    def solve_pso(
        self,
        points: List[Point],
        iterations: int = 300,
        swarm_size: int = 50,
    ):
        """
        Placeholder – w kolejnej iteracji możesz tu dopisać PSO pod TSP.
        """
        raise NotImplementedError("PSO zostanie dopisane w kolejnym kroku.")

    # -------------------------------------------------------
    #  ROZWIĄZYWANIE TSP DLA WIELU DRONÓW
    # -------------------------------------------------------

    def solve_for_drones(
        self,
        task_allocation: Dict[int, List[Point]],
        **params
    ) -> Dict[int, Dict]:
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

            # 1) Filtr bezpieczeństwa: wyrzucamy bazę z listy punktów inspekcyjnych,
            #    nawet jeśli TaskAllocator przypadkiem ją tam dodał.
            filtered_points = [p for p in points if p != BASE]

            if len(filtered_points) == 0:
                # brak punktów inspekcji - dron tylko siedzi w bazie
                route_coords = [BASE, BASE]
                results[drone_id] = {
                    "order": [],
                    "route_coords": route_coords,
                    "cost": 0.0,
                    "time": 0.0,
                }
                continue

            if len(filtered_points) == 1:
                # tylko jeden punkt: baza -> punkt -> baza, bez GA
                single = filtered_points[0]
                route_coords = [BASE, single, BASE]
                cost = (
                    math.dist(BASE, single) +
                    math.dist(single, BASE)
                )
                results[drone_id] = {
                    "order": [0],
                    "route_coords": route_coords,
                    "cost": cost,
                    "time": 0.0,
                }
                continue

            # 2) Rozwiązanie TSP
            if self.method == "ga":
                order, cost, history, duration = self.solve_ga(filtered_points, **params)

            elif self.method == "pso":
                # PSO jeszcze niezaimplementowane, placeholder
                order, cost, duration = self.solve_pso(filtered_points, **params)

            else:
                raise ValueError(f"Nieznana metoda TSP: {self.method}")

            # 3) Konwersja permutacji indeksów → współrzędne + baza
            route_coords = [BASE] + [filtered_points[i] for i in order] + [BASE]

            results[drone_id] = {
                "order": order,
                "route_coords": route_coords,
                "cost": cost,
                "time": duration,
            }

        return results
