# ---------------------------------------------
# Task Allocator – inteligentny podział zadań
# ---------------------------------------------
from typing import List, Tuple, Dict
from utils import euclidean_distance

Point = Tuple[float, float]


# ============================================
#   INTELIGENTNY PODZIAŁ ENERGETYCZNY
# ============================================
def energy_based_allocate(points, drone_configs):

    BASE = (0.0, 0.0)
    num_drones = len(drone_configs)

    # --- Sortowanie dronów od najmocniejszego (największa bateria) ---
    drone_order = sorted(
        range(num_drones),
        key=lambda d: drone_configs[d]["battery_capacity"],
        reverse=True
    )

    # Każdy dron zaczyna od bazy
    routes = {d: [BASE] for d in range(num_drones)}

    # Sortowanie punktów wg odległości od bazy (typowa heurystyka)
    points_sorted = sorted(points, key=lambda p: euclidean_distance(BASE, p))

    # -----------------------------
    #  WSTĘPNY PODZIAŁ GREEDY
    # -----------------------------
    for p in points_sorted:
        best_drone = None
        best_increase = float("inf")

        for d in drone_order:
            current = routes[d]

            old_len = route_length(current)
            new_len = route_length(current + [p])
            increase = new_len - old_len

            if increase < best_increase:
                best_increase = increase
                best_drone = d

        routes[best_drone].append(p)

    # ============================================
    #   FUNKCJA LICZĄCA ENERGIĘ DLA CAŁEJ TRASY
    # ============================================
    def compute_energy(drone_id, points_list):

        cfg = drone_configs[drone_id]
        v = cfg["speed"]
        ts = cfg["service_time"]
        C = cfg["battery_capacity"]
        T = cfg["flight_time"]

        k = C / T  # przeliczenie czasu na energię

        route = [BASE] + points_list + [BASE]
        t = 0.0

        for i in range(len(route) - 1):
            t += euclidean_distance(route[i], route[i + 1]) / v
            if route[i + 1] != BASE:
                t += ts

        return k * t

    # ============================================
    #   ETAP 3 – REDUKCJA TRAS SŁABSZYCH DRONÓW
    # ============================================
    changed = True

    while changed:
        changed = False

        for d in range(num_drones):

            pts = routes[d][1:]  # bez bazy
            if len(pts) == 0:
                continue

            E = compute_energy(d, pts)
            limit = 0.8 * drone_configs[d]["battery_capacity"]

            if E > limit:

                # znajdź NAJDALSZY punkt
                farthest = max(pts, key=lambda p: euclidean_distance(BASE, p))
                routes[d].remove(farthest)

                # spróbuj oddać go którykolwiekemu bardziej wydolnemu dronowi
                reassigned = False

                for strong_id in drone_order:
                    if strong_id == d:
                        continue

                    new_list = routes[strong_id][1:] + [farthest]
                    E2 = compute_energy(strong_id, new_list)

                    if E2 <= 0.8 * drone_configs[strong_id]["battery_capacity"]:
                        routes[strong_id].append(farthest)
                        reassigned = True
                        break

                # jeśli żaden dron nie może przejąć → misja niewykonalna
                if not reassigned:
                    raise RuntimeError("ŻADEN DRON nie może przejąć punktu – misja niewykonalna.")

                changed = True

    return routes


# ============================================
#   PROSTA FUNKCJA DYSTANSOWA
# ============================================
def route_length(route):
    if len(route) < 2:
        return 0.0
    dist = 0.0
    for i in range(len(route) - 1):
        dist += euclidean_distance(route[i], route[i + 1])
    return dist


# ============================================
#   INNE HEURYSTYKI (pozostawione bez zmian)
# ============================================
def allocate_tasks_equally(points: List[Point], num_drones: int) -> Dict[int, List[Point]]:
    allocation = {i: [] for i in range(num_drones)}
    for idx, point in enumerate(points):
        allocation[idx % num_drones].append(point)
    return allocation


class TaskAllocator:
    def __init__(self, method: str = "best_fit"):
        self.method = method

    def allocate(self, points, num_drones, drone_configs=None):

        if self.method == "best_fit":
            return energy_based_allocate(points, drone_configs)

        elif self.method == "equal":
            return allocate_tasks_equally(points, num_drones)

        else:
            raise ValueError(f"Nieznana metoda podziału: {self.method}")
