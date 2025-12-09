import random
import math
from typing import List, Tuple, Dict

# =============================
#  WALIDACJA MAPY
# =============================

def validate_map(points: List[Tuple[float, float]]):
    """
    Sprawdza czy mapa ma realistyczne wymiary.
    Zwraca (True, None) jeśli ok lub (False, "komunikat").
    """

    if not points:
        return False, "Mapa nie zawiera żadnych punktów."

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    width = max(xs) - min(xs)
    height = max(ys) - min(ys)

    # Realistyczne minimalne wymiary (żeby nie było mapy 1x1 metr)
    if width < 50 or height < 50:
        return False, f"Mapa jest zbyt mała ({width:.1f}x{height:.1f} m). Minimalne wymiary: 50x50 m."

    # Realistyczny maksymalny obszar dla misji dronów inspekcyjnych
    if width > 5000 or height > 5000:
        return False, f"Mapa jest zbyt duża ({width:.1f}x{height:.1f} m). Maksymalne wymiary: 5000x5000 m."

    # Sprawdzenie absurdalnie dużych odległości
    max_dist = 0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = math.dist(points[i], points[j])
            if d > max_dist:
                max_dist = d

    if max_dist > 10000:
        return False, f"Najdalsze punkty są oddalone o {max_dist:.1f} m (>10 km). Mapa nierealistyczna."

    return True, None


# =============================
#  GENERATOR MAP
# =============================

class MapGenerator:
    """Klasa odpowiedzialna za generowanie i przechowywanie punktów map."""

    def __init__(self):
        random.seed()
        self.maps: Dict[str, List[Tuple[float, float]]] = {}

    def generate_random_points(self, n: int, x_range: Tuple[int, int], y_range: Tuple[int, int]) -> List[Tuple[float, float]]:
        return [(random.uniform(*x_range), random.uniform(*y_range)) for _ in range(n)]

    def generate_grid_points(self, rows: int, cols: int, spacing: float) -> List[Tuple[float, float]]:
        return [(x * spacing, y * spacing) for x in range(cols) for y in range(rows)]

    def create_maps(self):
        """Tworzy przykładowe mapy i automatycznie je waliduje."""

        raw_maps = {
            "Mapa 1": self.generate_random_points(40, (-1000, 1000), (-1000, 1000)),
            "Mapa 2": self.generate_random_points(100, (100, 3500), (100, 3500)),
            "Mapa 8x8": self.generate_grid_points(8, 8, 10.0),
            "Mapa 10x15": self.generate_grid_points(10, 15, 10.0),
            "Mapa 20x20": self.generate_grid_points(20, 20, 10.0)
        }

        for name, pts in raw_maps.items():
            ok, msg = validate_map(pts)
            if ok:
                self.maps[name] = pts
            else:
                print(f"[ODRZUCONO] {name}: {msg}")

    def get_points(self, map_name: str) -> List[Tuple[float, float]]:
        return self.maps.get(map_name, [])


if __name__ == "__main__":
    gen = MapGenerator()
    gen.create_maps()
    for name, points in gen.maps.items():
        print(name, len(points), "punktów")
