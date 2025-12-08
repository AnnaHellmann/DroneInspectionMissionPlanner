import random
import math
from typing import List, Tuple, Dict


class MapGenerator:
    """Klasa odpowiedzialna za generowanie i przechowywanie punktów map."""

    def __init__(self):
        # słownik: nazwa mapy -> lista punktów
        random.seed()
        self.maps: Dict[str, List[Tuple[float, float]]] = {}

    def generate_random_points(self, n: int, x_range: Tuple[int, int], y_range: Tuple[int, int]) -> List[Tuple[float, float]]:
        """Generuje n losowych punktów w zadanym prostokątnym obszarze."""
        return [(random.uniform(*x_range), random.uniform(*y_range)) for _ in range(n)]

    def generate_grid_points(self, rows: int, cols: int, spacing: float) -> List[Tuple[float, float]]:
        """Generuje siatkę punktów w układzie prostokątnym (np. farma PV)."""
        return [(x * spacing, y * spacing) for x in range(cols) for y in range(rows)]

    def create_maps(self):
        """
        Tworzy przykładowe zestawy punktów (mapy) i zapisuje je w pamięci.
        Przyjęto skalę: 1 jednostka = 1 metr.
        """
        self.maps["Mapa 1"] = self.generate_random_points(8, (100, 400), (100, 500))
        self.maps["Mapa 2"] = self.generate_random_points(40, (-12000, 32000), (-12000, 32000))
        self.maps["Mapa 3"] = self.generate_grid_points(3, 5, 100)

    def get_points(self, map_name: str) -> List[Tuple[float, float]]:
        """Zwraca punkty dla wybranej mapy."""
        return self.maps.get(map_name, [])


if __name__ == "__main__":
    gen = MapGenerator()
    gen.create_maps()
    for name, points in gen.maps.items():
        print(name, points)
