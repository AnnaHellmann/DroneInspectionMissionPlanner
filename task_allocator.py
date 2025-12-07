#rozdział punktów między drony (heurystyki, klasteryzacja)
from typing import List, Tuple, Dict
from utils import euclidean_distance

try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    KMeans = None
    SKLEARN_AVAILABLE = False

Point = Tuple[float, float]

def proportional_allocate(points, drone_configs):
    """
    Proporcjonalny podział punktów zależny od mocy dronów.
    Moc = range + 0.1*flight_time + 0.1*battery
    """
    num_drones = len(drone_configs)
    capacities = []

    for d in range(num_drones):
        cfg = drone_configs[d]
        cap = cfg["range"] + 0.1 * cfg["flight_time"] + 0.1 * cfg["battery_capacity"]
        capacities.append(cap)

    total_cap = sum(capacities)
    total_points = len(points)

    # 1. liczymy proporcjonalne udziały
    target_counts = []
    for cap in capacities:
        share = cap / total_cap
        count = max(1, round(share * total_points))  # każdy dostaje min. 1
        target_counts.append(count)

    # korekta: suma musi się zgadzać
    diff = sum(target_counts) - total_points
    if diff > 0:
        # zabierz kilka punktów najmocniejszym
        for _ in range(diff):
            idx = target_counts.index(max(target_counts))
            target_counts[idx] -= 1
    elif diff < 0:
        # dodaj słabszym
        for _ in range(-diff):
            idx = target_counts.index(min(target_counts))
            target_counts[idx] += 1

    # 2. Przygotuj struktury tras
    routes = {i: [(0.0, 0.0)] for i in range(num_drones)}

    # 3. Sortujemy punkty tak, żeby wstępnie dawały sens
    points_sorted = sorted(points)

    # 4. Przydzielamy punkty proporcjonalnie
    idx = 0
    for d in range(num_drones):
        count = target_counts[d]
        for _ in range(count):
            routes[d].append(points_sorted[idx])
            idx += 1

    # 5. każdy dron wraca do bazy
    # for d in routes:
    #     routes[d].append((0.0, 0.0))

    return routes


def route_length(route):
    if len(route) < 2:
        return 0.0

    dist = 0.0

    for i in range(len(route) - 1):
        dist += euclidean_distance(route[i], route[i + 1])
    return dist


def allocate_best_fit(points: List[Point], drone_configs: Dict[int, Dict]) -> Dict[int, List[Point]]:
    """Opcja C — inteligentny podział zadań z uwzględnieniem 'mocy' drona."""
    num_drones = len(drone_configs)
    routes = {i: [(0.0, 0.0)] for i in range(num_drones)}

    for p in points:
        best_drone = None
        best_score = float("inf")

        for drone_id in range(num_drones):
            current = routes[drone_id]
            old_len = route_length(current)
            new_len = route_length(current + [p])
            increase = new_len - old_len

            cfg = drone_configs[drone_id]
            # prosta miara "mocy" drona – możesz później dopieścić w pracy
            capacity = cfg["range"] + cfg["flight_time"] * 0.1 + cfg["battery"] * 0.1

            # im większa moc, tym mniejszy efektywny koszt
            score = increase / (capacity + 1e-9)

            if score < best_score:
                best_score = score
                best_drone = drone_id

        routes[best_drone].append(p)

    # for d in routes:
    #     routes[d].append((0.0, 0.0))

    return routes

def allocate_tasks_equally(points: List[Point], num_drones: int) -> Dict[int, List[Point]]:
    """Prosty podział punktów na drony: równo po kolejności."""
    allocation = {i: [] for i in range(num_drones)}
    for idx, point in enumerate(points):
        drone_id = idx % num_drones
        allocation[drone_id].append(point)
    return allocation

def allocate_tasks_kmeans(points: List[Point], num_drones: int) -> Dict[int, List[Point]]:
    """Podział punktów na podstawie klasteryzacji KMeans"""
    if not SKLEARN_AVAILABLE:
        raise ImportError("scikit-learn nie jest zainstalowany. Zainstaluj pakiet sklearn, aby korzystać z KMeans.")

    kmeans = KMeans(n_clusters=num_drones, n_init=10)
    labels = kmeans.fit_predict(points)

    allocation = {i: [] for i in range(num_drones)}
    for point, label in zip(points, labels):
        allocation[label].append(point)
    return allocation

class TaskAllocator:
    def __init__(self, method: str = "best_fit"):
        self.method = method

    def allocate(self, points, num_drones, drone_configs=None):
        if self.method == "best_fit":
            return proportional_allocate(points, drone_configs)

        elif self.method == "kmeans":
            return allocate_tasks_kmeans(points, num_drones)

        else:
            return allocate_tasks_equally(points, num_drones)




