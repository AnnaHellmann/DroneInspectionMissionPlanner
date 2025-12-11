# app.py
import tkinter as tk
from tkinter import ttk, messagebox
import platform

from core.map_generator import MapGenerator
from algorithms.optimizer import Optimizer
from simulation.simulator import Simulator
from ui.visualizer import Visualizer
from core import config
from core.config import DEFAULT_DRONE_COUNT, DEFAULT_TSP_METHODS

from ui.map_info_window import MapInfoWindow
from ui.drone_manager import DroneManager
from ui.scroll_frame import ScrollFrame


class DroneApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.flight_paths = {}
        self.last_positions = {}
        self.drone_colors = config.DRONE_COLORS
        self.drone_time = {}

        self.tk_setPalette(background=config.BACKGROUND_COLOR, foreground="black")
        style = ttk.Style(self)
        style.theme_use('default')

        self.title("Symulator Misji Dronów")
        self.geometry("1000x650")
        self.configure(bg=config.BACKGROUND_COLOR)

        self.system_os = platform.system()

        self.map_generator = MapGenerator()
        self.map_generator.create_maps()
        self.map_points = self.map_generator.maps

        self.drone_models = config.DRONE_MODELS

        self.sidebar = tk.Frame(self, width=320, bg="#e0e0e0", padx=10, pady=10)
        self.sidebar.pack(side="left", fill="y")

        self.main_area = tk.Frame(self, bg="white", relief="sunken", bd=2)
        self.main_area.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.create_sidebar_widgets()
        self.create_main_canvas()

        self.drone_manager = DroneManager(self.drones_section, self.drone_models)
        self.drone_manager.build_forms(int(self.drone_count.get()))

    def create_sidebar_widgets(self):
        tk.Label(self.sidebar, text="Ustawienia misji", bg="#e0e0e0",
                 font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(self.sidebar, text="Liczba dronów:", bg="#e0e0e0").pack(anchor="w", pady=(10, 0))
        self.drone_count = ttk.Combobox(self.sidebar, values=DEFAULT_DRONE_COUNT, state="readonly")
        self.drone_count.current(0)
        self.drone_count.pack(fill="x", pady=5)
        self.drone_count.bind(
            "<<ComboboxSelected>>",
            lambda e: self.drone_manager.build_forms(int(self.drone_count.get()))
        )

        tk.Label(self.sidebar, text="Mapa obszaru:", bg="#e0e0e0").pack(anchor="w", pady=(10, 0))
        self.map_choice = ttk.Combobox(self.sidebar, values=list(self.map_points.keys()), state="readonly")
        self.map_choice.current(0)
        self.map_choice.pack(fill="x", pady=5)
        self.map_choice.bind("<<ComboboxSelected>>", self.show_selected_map)

        ttk.Button(self.sidebar, text="Informacje o mapie", command=self.show_map_info) \
            .pack(fill="x", pady=(5, 10))

        tk.Label(self.sidebar, text="Algorytm TSP:", bg="#e0e0e0").pack(anchor="w", pady=(10, 0))
        self.tsp_method = ttk.Combobox(self.sidebar, values=DEFAULT_TSP_METHODS, state="readonly")
        self.tsp_method.current(0)
        self.tsp_method.pack(fill="x", pady=5)

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", pady=10)

        scroll_frame = ScrollFrame(self.sidebar, bg="#e0e0e0")
        scroll_frame.pack(fill="both", expand=True)
        self.drones_section = scroll_frame.get_frame()

        ttk.Button(self.sidebar, text="Wyznacz harmonogram", command=self.calculate_schedule) \
            .pack(fill="x", pady=(15, 5))
        ttk.Button(self.sidebar, text="Symuluj loty", command=self.run_simulation) \
            .pack(fill="x", pady=10)
        ttk.Button(self.sidebar, text="Reset", command=self.reset_app) \
            .pack(fill="x")

    def create_main_canvas(self):
        self.canvas = tk.Canvas(self.main_area, bg="#fafafa")
        self.canvas.pack(expand=True, fill="both")
        self.canvas.create_text(500, 300, text="Wybierz mapę",
                                font=("Arial", 14), fill="#666")
        self.visualizer = Visualizer(self.canvas)

    def run_simulation(self):
        if not hasattr(self, "optimized_routes"):
            messagebox.showerror("Błąd", "Najpierw wyznacz trasy!")
            return

        if not hasattr(self, "current_points"):
            messagebox.showerror("Błąd", "Najpierw wybierz mapę!")
            return

        self.sim = Simulator(
            self.optimized_routes,
            self.drone_configs,
            timestep=0.05,
            speedup=50.0
        )

        self.sim_gen = self.sim.simulate()

        self.flight_paths = {d: [] for d in self.optimized_routes.keys()}
        self.last_positions = {}
        self.drone_time = {d: 0.0 for d in self.optimized_routes.keys()}

        self.animate()

    def animate(self):
        try:
            frame = next(self.sim_gen)
            points = getattr(self, "current_points", [])

            dt = self.sim.timestep
            for d, pos in frame.items():
                if pos is not None:
                    self.drone_time[d] += dt

            self.visualizer.draw_full_frame(
                points,
                self.optimized_routes,
                frame,
                self.flight_paths,
                self.last_positions,
                self.drone_colors,
                self.drone_configs
            )

            self.after(30, self.animate)

        except StopIteration:
            print("Symulacja zakończona.")

            lines = []
            for d, t in self.drone_time.items():
                drone_name = self.drone_configs[d].get("name", f"Dron {d}")
                lines.append(f"{drone_name}: {t:.2f} s")

            result = "\n".join(lines)

            print("\nCzas pracy dronów:")
            print(result)

            messagebox.showinfo("Czas pracy dronów", result)

    def reset_app(self):
        if hasattr(self, "sim_gen"):
            del self.sim_gen
        if hasattr(self, "sim"):
            del self.sim
        if hasattr(self, "optimized_routes"):
            del self.optimized_routes
        if hasattr(self, "current_points"):
            del self.current_points

        self.flight_paths = {}
        self.last_positions = {}

        self.map_choice.set("")

        self.canvas.delete("all")
        self.canvas.create_text(500, 300, text="Zresetowano.",
                                font=("Arial", 14), fill="#333")

    def show_selected_map(self, event=None):
        map_name = self.map_choice.get()
        points = self.map_generator.get_points(map_name)

        self.current_points = points

        self.visualizer.compute_scaling(points)
        self.visualizer.draw_map_points(points)
        self.visualizer.draw_base()

        self.canvas.delete("title")
        self.canvas.create_text(
            self.canvas.winfo_width() // 2,
            30,
            text=f"{map_name}",
            font=("Arial", 13, "bold"),
            fill="#333",
            tags="title"
        )

    def show_map_info(self):
        MapInfoWindow.show(
            parent=self,
            map_name=self.map_choice.get(),
            points=self.map_generator.get_points(self.map_choice.get())
        )

    def calculate_schedule(self):
        if not hasattr(self, "current_points"):
            messagebox.showerror("Błąd", "Najpierw wybierz mapę!")
            return

        map_sel = self.map_choice.get()
        points = self.map_generator.get_points(map_sel)

        if not points:
            messagebox.showerror("Błąd", "Brak punktów dla tej mapy.")
            return

        drone_configs = self.drone_manager.get_configs()
        self.drone_configs = drone_configs

        if drone_configs is None:
            return

        method = self.tsp_method.get().lower()
        optimizer = Optimizer(drone_configs, tsp_method=method)
        # optimizer = Optimizer(drone_configs)

        optimized_routes, exec_time = optimizer.optimize(points, len(drone_configs))

        if optimized_routes is None:
            messagebox.showerror(
                "Błąd",
                "Parametry dronów niewystarczające do wykonania misji."
            )
            return

        self.optimized_routes = optimized_routes

        messagebox.showinfo(
            "Harmonogram",
            f"Trasy wyznaczone.\nCzas optymalizacji: {exec_time:.3f}s"
        )


if __name__ == "__main__":
    app = DroneApp()
    app.mainloop()
