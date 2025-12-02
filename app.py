# app.py
import tkinter as tk
from tkinter import ttk, messagebox
import platform
from map_generator import MapGenerator
from optimizer import Optimizer
from simulator import Simulator


class DroneApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.flight_paths={}

        self.drone_colors = ["red", "orange", "green", "blue", "purple"]

        self.tk_setPalette(background="#f4f4f4", foreground="black")
        style = ttk.Style(self)
        style.theme_use('default')

        self.title("Symulator Misji Dronów")
        self.geometry("1000x650")
        self.configure(bg="#f4f4f4")

        self.scale = 1.0 #skalowanie mapy
        self.offset_x = 0
        self.offset_y = 0
        self.last_positions = {}  #last position, zeby drony nie znikaly

        self.system_os = platform.system()

        # generator map
        self.map_generator = MapGenerator()
        self.map_generator.create_maps()
        self.map_points = self.map_generator.maps

        self.drone_models = {
            "Model": {
                "Zasięg [m]": 0,
                "Czas lotu [s]": 0,
                "Pojemność baterii [mAh]": 0
            },
            "DJI Mini 3 Pro": {
                "Zasięg [m]": 18000,  # 18 km
                "Czas lotu [s]": 34 * 60,  # 34 min
                "Pojemność baterii [mAh]": 2453
            },
            "DJI Air 2S": {
                "Zasięg [m]": 18000,
                "Czas lotu [s]": 31 * 60,
                "Pojemność baterii [mAh]": 3500
            },
            "DJI Mavic 3": {
                "Zasięg [m]": 30000,
                "Czas lotu [s]": 46 * 60,
                "Pojemność baterii [mAh]": 5000
            },
            "DJI Matrice 30": {
                "Zasięg [m]": 30000,
                "Czas lotu [s]": 41 * 60,
                "Pojemność baterii [mAh]": 5880
            }
        }

        # główny layout
        self.sidebar = tk.Frame(self, width=320, bg="#e0e0e0", padx=10, pady=10)
        self.sidebar.pack(side="left", fill="y")
        self.main_area = tk.Frame(self, bg="white", relief="sunken", bd=2)
        self.main_area.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.drone_frames = []
        self.create_sidebar_widgets()
        self.create_main_canvas()

    # ========= SIDEBAR =========
    def create_sidebar_widgets(self):
        tk.Label(self.sidebar, text="Ustawienia misji", bg="#e0e0e0",
                 font=("Arial", 12, "bold")).pack(pady=10)

        # liczba dronów
        tk.Label(self.sidebar, text="Liczba dronów:", bg="#e0e0e0").pack(anchor="w", pady=(10, 0))
        self.drone_count = ttk.Combobox(self.sidebar, values=[1, 2, 3, 4, 5], state="readonly")
        self.drone_count.current(0)
        self.drone_count.pack(fill="x", pady=5)
        self.drone_count.bind("<<ComboboxSelected>>", self.update_drone_sections)

        # wybór mapy
        tk.Label(self.sidebar, text="Mapa obszaru:", bg="#e0e0e0").pack(anchor="w", pady=(10, 0))
        self.map_choice = ttk.Combobox(self.sidebar, values=list(self.map_points.keys()), state="readonly")
        self.map_choice.current(0)
        self.map_choice.pack(fill="x", pady=5)
        self.map_choice.bind("<<ComboboxSelected>>", self.show_selected_map)

        ttk.Button(self.sidebar, text="Informacje o mapie", command=self.show_map_info) \
            .pack(fill="x", pady=(5, 10))

        # Wybór metody TSP
        tk.Label(self.sidebar, text="Algorytm optymalizacji TSP:", bg="#e0e0e0").pack(anchor="w", pady=(10, 0))

        self.tsp_method = ttk.Combobox(
            self.sidebar,
            values=["GA", "PSO"],
            state="readonly"
        )
        self.tsp_method.current(0)  # default = GA
        self.tsp_method.pack(fill="x", pady=5)

        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", pady=10)

        # PRZEWIJANA SEKCJA DRONÓW
        self.scroll_canvas = tk.Canvas(self.sidebar, bg="#e0e0e0", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.sidebar, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollable_frame = tk.Frame(self.scroll_canvas, bg="#e0e0e0")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        )

        self.scroll_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.drones_section = self.scrollable_frame
        self.scroll_canvas.bind("<Enter>", self._bind_mousewheel)
        self.scroll_canvas.bind("<Leave>", self._unbind_mousewheel)

        # PRZYCISKI
        ttk.Button(self.sidebar, text="Wyznacz harmonogram", command=self.calculate_schedule)\
            .pack(fill="x", pady=(15, 5))

        ttk.Button(self.sidebar, text="Symuluj loty", command=self.run_simulation)\
            .pack(fill="x", pady=(0, 10))

        ttk.Button(self.sidebar, text="Reset", command=self.reset_app) \
            .pack(fill="x", pady=(0, 10))

        self.update_drone_sections()

    # ========= CANVAS =========
    def create_main_canvas(self):
        self.canvas = tk.Canvas(self.main_area, bg="#fafafa")
        self.canvas.pack(expand=True, fill="both")
        self.canvas.create_text(500, 300, text="Wybierz mapę, aby zobaczyć punkty inspekcji",
                                font=("Arial", 14), fill="#666")

    def draw_frame(self, frame):
        self.canvas.delete("all")

        # --- punkty inspekcji ---
        if hasattr(self, "current_points"):
            for (px, py) in self.current_points:
                sx = px * self.scale + self.offset_x
                sy = py * self.scale + self.offset_y
                self.canvas.create_oval(sx - 4, sy - 4, sx + 4, sy + 4, fill="blue")

        # --- baza ---
        base_x = 0 * self.scale + self.offset_x
        base_y = 0 * self.scale + self.offset_y
        self.canvas.create_rectangle(base_x - 6, base_y - 6, base_x + 6, base_y + 6, fill="black")
        self.canvas.create_text(base_x + 12, base_y, text="Baza", fill="black", anchor="w")

        # --- trasy dronów (statyczne) ---
        if hasattr(self, "optimized_routes"):
            for drone_id, route in self.optimized_routes.items():
                color = self.drone_colors[drone_id % len(self.drone_colors)]
                for i in range(len(route) - 1):
                    x1, y1 = route[i]
                    x2, y2 = route[i + 1]
                    x1 = x1 * self.scale + self.offset_x
                    y1 = y1 * self.scale + self.offset_y
                    x2 = x2 * self.scale + self.offset_x
                    y2 = y2 * self.scale + self.offset_y
                    self.canvas.create_line(
                        x1, y1, x2, y2,
                        fill=color,
                        width=2,
                        dash=(4, 2)
                    )

        # --- dynamiczny ślad lotu ---
        for drone_id, path in self.flight_paths.items():
            color = self.drone_colors[drone_id % len(self.drone_colors)]
            for i in range(1, len(path)):
                x1, y1 = path[i - 1]
                x2, y2 = path[i]
                x1 = x1 * self.scale + self.offset_x
                y1 = y1 * self.scale + self.offset_y
                x2 = x2 * self.scale + self.offset_x
                y2 = y2 * self.scale + self.offset_y
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

        # --- rysowanie dronów (bez migania) ---
        for drone_id in self.optimized_routes.keys():

            # aktualizacja ostatniej pozycji (jeśli jest nowa)
            if drone_id in frame and frame[drone_id] is not None:
                self.last_positions[drone_id] = frame[drone_id]

            # użycie ostatniej znanej pozycji
            pos = self.last_positions.get(drone_id)
            if pos is None:
                continue

            # zapisz punkt do śladu lotu
            self.flight_paths[drone_id].append(pos)

            # rysowanie drona
            x, y = pos
            x = x * self.scale + self.offset_x
            y = y * self.scale + self.offset_y

            color = self.drone_colors[drone_id % len(self.drone_colors)]
            r = 6

            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color)
            self.canvas.create_text(x + 10, y, text=f"{drone_id}", fill=color)

        # --- legenda ---
        legend_x = 20
        legend_y = 20
        self.canvas.create_text(
            legend_x, legend_y - 10,
            text="Legenda dronów:",
            fill="black",
            anchor="nw",
            font=("Arial", 10, "bold")
        )

        for drone_id in self.optimized_routes.keys():
            color = self.drone_colors[drone_id % len(self.drone_colors)]
            dy = legend_y + 20 * (drone_id + 1)
            self.canvas.create_oval(legend_x, dy, legend_x + 10, dy + 10, fill=color)
            self.canvas.create_text(legend_x + 20, dy + 5, text=f"Dron {drone_id}", anchor="w", fill="black")

    # ========= SYMULACJA =========
    def run_simulation(self):
        print("RUN SIMULATION START")
        if not hasattr(self, "optimized_routes") or len(self.optimized_routes) == 0:
            messagebox.showerror("Błąd", "Najpierw wyznacz trasy!")
            return

        # utwórz symulator i generator klatek
        self.sim = Simulator(self.optimized_routes, speed=40.0, timestep=0.05)
        self.sim_gen = self.sim.simulate()

        self.flight_paths = {drone_id: [] for drone_id in self.optimized_routes.keys()}
        self.last_positions = {}

        # rozpocznij animację
        self.animate()

        print(self.optimized_routes)

    def animate(self):
        try:
            frame = next(self.sim_gen)
            self.draw_frame(frame)
            self.after(30, self.animate)
        except StopIteration:
            print("Symulacja zakończona.")

    # ======== RESET =========

    def reset_app(self):
        # zatrzymaj animację
        if hasattr(self, "animating") and self.animating:
            self.animating = False

        # usuń stare obiekty symulacji
        if hasattr(self, "sim"):
            del self.sim
        if hasattr(self, "sim_gen"):
            del self.sim_gen
        if hasattr(self, "optimized_routes"):
            del self.optimized_routes

        # wyczyść Canvas
        self.canvas.delete("all")
        self.canvas.create_text(500, 300, text="Zresetowano ustawienia.",
                                font=("Arial", 14), fill="#333")

        # usuń aktualne punkty mapy
        if hasattr(self, "current_points"):
            del self.current_points

    # ========= MAPY =========
    def show_selected_map(self, event=None):
        self.canvas.delete("all")

        map_name = self.map_choice.get()
        points = self.map_generator.get_points(map_name)

        self.current_points = points
        self.compute_map_scaling(points)

        # rysuj punkty mapy w skali i centrowane
        for (x, y) in points:
            sx = x * self.scale + self.offset_x
            sy = y * self.scale + self.offset_y
            self.canvas.create_arc(
                sx - 5, sy - 5, sx + 5, sy + 5,
                start=0, extent=359,
                fill="red",
                outline="black",
                style="pieslice"
            )

        self.canvas.create_text(500, 30, text=f"Punkty inspekcji - {map_name}",
                                font=("Arial", 13, "bold"), fill="#333")

    def show_map_info(self):
        """Wyświetla okno z informacjami o aktualnie wybranej mapie."""
        map_name = self.map_choice.get()
        points = self.map_generator.get_points(map_name)

        if not points:
            messagebox.showinfo("Informacja", "Brak punktów dla tej mapy.")
            return

        # policz podstawowe metryki
        num_points = len(points)

        # oblicz dystanse między wszystkimi punktami
        dists = []
        from utils import euclidean_distance
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                dists.append(euclidean_distance(points[i], points[j]))

        max_dist = max(dists) if dists else 0
        min_dist = min(dists) if dists else 0
        avg_dist = sum(dists) / len(dists) if dists else 0

        # utwórz okno modalne
        info_win = tk.Toplevel(self)
        info_win.title(f"Specyfikacja mapy: {map_name}")
        info_win.geometry("420x480")
        info_win.resizable(False, False)

        # nagłówek
        tk.Label(info_win, text=f"Mapa: {map_name}", font=("Arial", 12, "bold")).pack(pady=10)

        # WYMIARY MAPY — bounding box
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width = max_x - min_x
        height = max_y - min_y

        # podstawowe dane
        text = (
            f"Liczba punktów: {num_points}\n"
            f"Wymiary mapy (szer. × wys.): {width:.2f}m × {height:.2f}m\n"
            f"Minimalny dystans: {min_dist:.2f}m\n"
            f"Maksymalny dystans: {max_dist:.2f}m\n"
            f"Średni dystans: {avg_dist:.2f}m\n"
            "\nPunkty (x, y):\n"
        )

        # textarea scrollowalna
        frame = tk.Frame(info_win)
        frame.pack(fill="both", expand=True)

        text_box = tk.Text(frame, wrap="word", height=18)
        scrollbar = ttk.Scrollbar(frame, command=text_box.yview)
        text_box.configure(yscrollcommand=scrollbar.set)

        text_box.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # wpisz tekst
        text_box.insert("end", text)

        # wypisz punkty
        for p in points:
            text_box.insert("end", f"{p}\n")

        # zablokuj edycję
        text_box.config(state="disabled")

        # przycisk zamknięcia
        ttk.Button(info_win, text="Zamknij", command=info_win.destroy).pack(pady=10)

    def compute_map_scaling(self, points):
        if not points:
            return

        # dodajemy punkt startowy dronów do mapy:
        all_points = points + [(0, 0)]

        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        map_w = max_x - min_x
        map_h = max_y - min_y

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w == 1 or canvas_h == 1:
            # Canvas jeszcze nie zainicjalizowany
            self.after(50, lambda: self.compute_map_scaling(points))
            return

        # skalowanie – 90% szerokości/ wysokości
        scale_w = canvas_w * 0.9 / map_w
        scale_h = canvas_h * 0.9 / map_h
        self.scale = min(scale_w, scale_h)

        # wycentrowanie
        self.offset_x = (canvas_w - map_w * self.scale) / 2 - min_x * self.scale
        self.offset_y = (canvas_h - map_h * self.scale) / 2 - min_y * self.scale

    # ========= DRONY =========
    def update_drone_sections(self, event=None):
        for frame in self.drone_frames:
            frame.destroy()
        self.drone_frames.clear()

        num_drones = int(self.drone_count.get())
        for i in range(num_drones):
            frame = tk.LabelFrame(self.drones_section, text=f"Dron {i+1}", bg="#f0f0f0", padx=5, pady=5)
            frame.pack(fill="x", pady=5)
            self.drone_frames.append(frame)

            tk.Label(frame, text="Model:", bg="#f0f0f0").grid(row=0, column=0, sticky="w")
            model_combo = ttk.Combobox(frame, values=list(self.drone_models.keys()), state="readonly", width=10)
            model_combo.grid(row=0, column=1, sticky="w", padx=5)
            model_combo.current(0)

            entries = {}
            row_index = 1
            for param, val in self.drone_models["Model"].items():
                tk.Label(frame, text=f"{param}:", bg="#f0f0f0").grid(row=row_index, column=0, sticky="w")
                entry = ttk.Entry(frame, width=10)
                entry.insert(0, val)
                entry.grid(row=row_index, column=1, padx=5, pady=2)
                entries[param] = entry
                row_index += 1

            frame.entries = entries

            def update_params(event=None, combo=model_combo, entry_dict=entries):
                model = combo.get()
                defaults = self.drone_models[model]
                for param, entry in entry_dict.items():
                    entry.delete(0, tk.END)
                    entry.insert(0, defaults[param])

            model_combo.bind("<<ComboboxSelected>>", update_params)

    # ========= OBLICZENIA =========
    def calculate_schedule(self):

        drones = int(self.drone_count.get())
        map_sel = self.map_choice.get()
        points = self.map_generator.get_points(map_sel)

        drone_configs = {}

        for i, frame in enumerate(self.drone_frames):
            entries = frame.entries

            range_val = float(entries["Zasięg [m]"].get())
            flight_time_val = float(entries["Czas lotu [s]"].get())
            battery_val = float(entries["Pojemność baterii [mAh]"].get())

            if range_val <= 0 or flight_time_val <= 0 or battery_val <= 0:
                messagebox.showerror(
                    "Błąd parametrów",
                    f"Dron {i + 1} ma niepoprawne parametry (0 lub mniej)."
                )
                return

            drone_configs[i] ={
            "range": range_val,
            "flight_time": flight_time_val,
            "battery": battery_val,
            }

        selected_method = self.tsp_method.get().lower()  # "ga" lub "pso"
        optimizer = Optimizer(drone_configs, tsp_method=selected_method)

        optimized_routes, exec_time = optimizer.optimize(points, drones)

        if optimized_routes is None:
            messagebox.showerror("Błąd", "Parametry dronów są niewystarczające do wykonania misji.\n\n"
                                         "Zwiększ parametry lub zmień liczbę dronów.")
            return

        self.optimized_routes = optimized_routes
        if not optimized_routes or len(optimized_routes) == 0:
            messagebox.showerror(
                "Błąd",
                "Nie udało się wyznaczyć tras dla dronów."
            )
            return


        messagebox.showinfo(
            "Harmonogram",
            f"Trasy wyznaczone pomyślnie.\n\n"
            f"Czas optymalizacji: {exec_time:.3f} s"
        )

        print(self.optimized_routes)

    # ========= SCROLL =========
    def _bind_mousewheel(self, event):
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.scroll_canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.scroll_canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _unbind_mousewheel(self, event):
        self.scroll_canvas.unbind_all("<MouseWheel>")
        self.scroll_canvas.unbind_all("<Button-4>")
        self.scroll_canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if self.system_os == "Darwin":
            self.scroll_canvas.yview_scroll(-1 * int(event.delta), "units")
        else:
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.scroll_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.scroll_canvas.yview_scroll(1, "units")


if __name__ == "__main__":
    app = DroneApp()
    app.mainloop()
