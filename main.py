from map_generator import generate_random_points
from task_allocator import allocate_tasks_equally
from tsp_solver import plan_paths_for_drones
from visualizer import plot_paths
from app import DroneApp

NUM_POINTS = 30
NUM_DRONES = 3
AREA_X = (0, 100)
AREA_Y = (0, 100)

if __name__ == "__main__":
    app = DroneApp()
    app.mainloop()
    # # generowanie punktów inspekcji
    # points = generate_random_points(NUM_POINTS, AREA_X, AREA_Y)
    #
    # #podział na podstawie kolejnosci taskow
    # task_allocation = allocate_tasks_equally(points, NUM_DRONES)
    #
    # #planowanie sciezki dla dronow (heurystyka nearest neighbor)
    # drone_paths = plan_paths_for_drones(task_allocation)
    #
    # #wizualizacja ścieżki lotu dronów
    # plot_paths(drone_paths, title="Trasy przelotu dronów")

#rozszerzyc kod o realistyczna wersje losowania punktow z siatki