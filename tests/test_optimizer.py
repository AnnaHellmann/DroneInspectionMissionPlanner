# tests/test_optimizer.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # pozwala importować z katalogu głównego

from algorithms.optimizer import Optimizer
from core.map_generator import MapGenerator


def test_optimizer_routes():
    """
    Test integracyjny: sprawdza, czy Optimizer poprawnie generuje trasy dla dronów.
    """
    # --- 1️⃣ Przygotowanie danych ---
    map_gen = MapGenerator()
    map_gen.create_maps()
    points = map_gen.get_points("Mapa 1")

    optimizer = Optimizer(allocation_method="equal")
    routes = optimizer.optimize(points, num_drones=3)

    # --- 2️⃣ Testy logiczne ---
    assert isinstance(routes, dict), "Wynik optymalizacji powinien być słownikiem"
    assert len(routes) == 3, "Powinny istnieć 3 trasy (dla 3 dronów)"

    for drone_id, path in routes.items():
        assert len(path) >= 2, f"Dron {drone_id} powinien mieć co najmniej 2 punkty w trasie"
        assert path[0] == (0.0, 0.0), f"Dron {drone_id} nie zaczyna w bazie (0.0, 0.0)"
        assert path[-1] == (0.0, 0.0), f"Dron {drone_id} nie kończy w bazie (0.0, 0.0)"

    print("Test przeszedł pomyślnie — trasy są poprawne!")


if __name__ == "__main__":
    test_optimizer_routes()
