
from typing import List, Tuple, Dict
from core.utils import euclidean_distance

try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    KMeans = None
    SKLEARN_AVAILABLE = False

Point = Tuple[float, float]
BASE = (0.0, 0.0)

class TaskAllocator:
    def __init__(self, method):
        self.method = method

    def allocate(self, points, num_drones, drone_configs):
        if self.method == "C":
            return allocate_option_C(points, drone_configs)

        else:
            return {
                i: points[i::num_drones]
                for i in range(num_drones)
            }

def route_energy(pts: List[Point], cfg: Dict) -> float:
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
    return route_energy(pts, cfg) <= 0.8 * cfg["battery_capacity"]

# Power-Weighted KMeans Allocation

def drone_power(cfg):
    return (
        0.4 * cfg["speed"] +
        0.3 * (cfg["flight_time"] / 60) +
        0.3 * (cfg["battery_capacity"] / 1000)
    )

def allocate_option_C(points: List[Point], drone_configs: Dict[int, Dict]):

    num = len(drone_configs)
    if not SKLEARN_AVAILABLE:
        raise RuntimeError("KMeans wymaga scikit-learn")

    kmeans = KMeans(n_clusters=num, n_init=10)
    labels = kmeans.fit_predict(points)

    routes = {d: [] for d in range(num)}
    for p, lab in zip(points, labels):
        routes[lab].append(p)

    powers = [drone_power(drone_configs[d]) for d in range(num)]
    total_power = sum(powers)
    proportions = [p / total_power for p in powers]

    total_points = len(points)
    target = [max(1, round(prop * total_points)) for prop in proportions]

    diff = sum(target) - total_points
    while diff > 0:
        i = target.index(max(target))
        target[i] -= 1
        diff -= 1
    while diff < 0:
        i = target.index(min(target))
        target[i] += 1
        diff += 1

    improved = True
    while improved:
        improved = False

        for d in range(num):
            pts = routes[d]

            while len(pts) > target[d]:
                far = max(pts, key=lambda p: euclidean_distance(kmeans.cluster_centers_[d], p))
                pts.remove(far)

                candidate = min(range(num), key=lambda x: len(routes[x]) - target[x])
                routes[candidate].append(far)
                improved = True

            while len(pts) < target[d]:
                donor = max(range(num), key=lambda x: len(routes[x]) - target[x])
                if donor == d or len(routes[donor]) <= target[donor]:
                    break

                near = min(
                    routes[donor],
                    key=lambda p: euclidean_distance(kmeans.cluster_centers_[d], p)
                )

                routes[donor].remove(near)
                pts.append(near)
                improved = True

    changed = True
    while changed:
        changed = False

        for d in range(num):
            pts = routes[d]
            if not pts:
                continue

            if not energy_ok(pts, drone_configs[d]):
                center_d = kmeans.cluster_centers_[d]
                far = max(pts, key=lambda p: euclidean_distance(center_d, p))
                routes[d].remove(far)

                candidates = [i for i in range(num) if i != d]

                def score(idx):
                    dist = euclidean_distance(kmeans.cluster_centers_[idx], far)
                    return dist / (powers[idx] + 1e-6)

                best = min(candidates, key=score)

                routes[best].append(far)
                changed = True

    return routes
