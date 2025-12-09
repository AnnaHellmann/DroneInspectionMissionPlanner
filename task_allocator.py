# task_allocator.py
# Ulepszony podział punktów między drony (mTSP)

from typing import List, Tuple, Dict
from utils import euclidean_distance

# ==========================================
# Opcjonalny import KMeans
# ==========================================
try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    KMeans = None
    SKLEARN_AVAILABLE = False

Point = Tuple[float, float]
BASE = (0.0, 0.0)


# ==========================================================
# POMOCNICZE
# ==========================================================

def route_energy(pts: List[Point], cfg: Dict) -> float:
    """Liczy energię potrzebną na trasę BASE → pts → BASE."""
    v = cfg["speed"]
    ts = cfg["service_time"]
    C = cfg["battery_capacity"]
    T = cfg["flight_time"]
    k = C / T

    route = [BASE] + pts + [BASE]
    total_t = 0.0

    for i in range(len(route) - 1):
        total_t += euclidean_distance(route[i], route[i + 1]) / v
        if route[i + 1] != BASE:
            total_t += ts

    return k * total_t


def energy_ok(pts, cfg) -> bool:
    """Czy dron jest w stanie wykonać trasę energetycznie?"""
    return route_energy(pts, cfg) <= 0.8 * cfg["battery_capacity"]


# ==========================================================
# OPCJA A:
# Heurystyka z lokalnym ulepszaniem podziału (SWAP + REASSIGN)
# ==========================================================

def allocate_option_A(points: List[Point], drone_configs: Dict[int, Dict]):
    """
    1. Start: proportional best-fit
    2. Lokalne ulepszanie:
        • swap punktów między dronami
        • przerzucanie punktów z przeciążonych do mocniejszych
    Wynik: bardziej zbalansowany, energo-optymalny podział.
    """

    num = len(drone_configs)
    routes = {d: [] for d in range(num)}

    # --- STARTOWY PODZIAŁ: proportional best-fit ---
    sorted_points = sorted(points, key=lambda p: (p[0], p[1]))
    capacities = [
        cfg["range"] + 0.1 * cfg["flight_time"] + 0.1 * cfg["battery_capacity"]
        for cfg in drone_configs.values()
    ]

    total_cap = sum(capacities)
    target = [max(1, round(c / total_cap * len(points))) for c in capacities]

    # korekta sumy
    diff = sum(target) - len(points)
    while diff > 0:
        i = target.index(max(target))
        target[i] -= 1
        diff -= 1
    while diff < 0:
        i = target.index(min(target))
        target[i] += 1
        diff += 1

    idx = 0
    for d in range(num):
        for _ in range(target[d]):
            routes[d].append(sorted_points[idx])
            idx += 1

    # ==============================================
    # KROK 2: ULEPSZANIE PODZIAŁU (LOCAL SWAPS)
    # ==============================================

    improved = True
    while improved:
        improved = False

        for d1 in range(num):
            for d2 in range(num):
                if d1 == d2:
                    continue

                pts1 = routes[d1]
                pts2 = routes[d2]

                for p in pts1:
                    # sprawdź czy przerzucenie punktu p z d1 do d2 daje lepszy wynik
                    new1 = [x for x in pts1 if x != p]
                    new2 = pts2 + [p]

                    if not new1:
                        continue

                    E1 = route_energy(new1, drone_configs[d1])
                    E2 = route_energy(new2, drone_configs[d2])

                    if E1 <= 0.8*drone_configs[d1]["battery_capacity"] and \
                       E2 <= 0.8*drone_configs[d2]["battery_capacity"]:

                        # poprawa: równomierniejsza liczba punktów
                        if abs(len(new1) - len(new2)) < abs(len(pts1) - len(pts2)):
                            routes[d1] = new1
                            routes[d2] = new2
                            improved = True
                            break

    return routes


# ==========================================================
# OPCJA B:
# KMeans → division → Energy fix
# ==========================================================

def allocate_option_B(points: List[Point], drone_configs: Dict[int, Dict]):
    """
    1. Klasteryzacja KMeans – grupy przestrzenne
    2. Energy fix – przerzucanie punktów między dronami
    """

    num = len(drone_configs)
    if not SKLEARN_AVAILABLE:
        raise RuntimeError("KMeans wymaga scikit-learn")

    # --- KMEANS ---
    kmeans = KMeans(n_clusters=num, n_init=10)
    labels = kmeans.fit_predict(points)

    routes = {d: [] for d in range(num)}
    for p, lab in zip(points, labels):
        routes[lab].append(p)

    # --- ENERGY FIX ---
    changed = True
    while changed:
        changed = False

        for d in range(num):
            pts = routes[d]
            if not pts:
                continue

            if not energy_ok(pts, drone_configs[d]):
                # oddaj najdalszy punkt
                far = max(pts, key=lambda p: euclidean_distance(BASE, p))
                routes[d].remove(far)

                # daj mocniejszemu
                strongest = max(
                    range(num),
                    key=lambda idx: drone_configs[idx]["battery_capacity"]
                )
                routes[strongest].append(far)
                changed = True

    return routes
def allocate_equally(points: List[Point], num_drones: int) -> Dict[int, List[Point]]:
    import random
    """
    Najprostsza metoda podziału zadań:
    - Każdy dron dostaje prawie tę samą liczbę punktów.
    - Brak uwzględnienia energii, odległości, mocy drona.
    - Dobra jako baseline do porównań w pracy inżynierskiej.
    """

    # potasuj punkty, aby ich kolejność nie wpływała na wynik
    shuffled = points[:]
    random.shuffle(shuffled)

    routes = {i: [(0.0, 0.0)] for i in range(num_drones)}

    for idx, point in enumerate(shuffled):
        drone_id = idx % num_drones
        routes[drone_id].append(point)

    return routes



# ==========================================================
# KLASY GŁÓWNEJ
# ==========================================================

class TaskAllocator:
    def __init__(self, method="equally"):
        """
        method:
            • "A" → opcja A (local improvement)
            • "B" → opcja B (KMeans + energy fix)
            • "best_fit" → fallback bardzo prosty
        """
        self.method = method

    def allocate(self, points, num_drones, drone_configs):
        if self.method == "A":
            return allocate_option_A(points, drone_configs)

        elif self.method == "B":
            return allocate_option_B(points, drone_configs)

        elif self.method == "equally":
            return allocate_equally(points, num_drones)

        else:
            # fallback: prosty, ale zawsze działa
            return {
                i: points[i::num_drones]
                for i in range(num_drones)
            }
