import tkinter as tk
from typing import Dict, List, Tuple
from core.config import BASE

Point = Tuple[float, float]

class Visualizer:

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas

        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0

    def compute_scaling(self, points: List[Point]) -> None:

        if not points:
            return

        all_points = points + [BASE]

        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        map_w = max_x - min_x
        map_h = max_y - min_y

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w <= 1 or canvas_h <= 1 or map_w == 0 or map_h == 0:
            self.canvas.after(50, lambda: self.compute_scaling(points))
            return

        scale_w = canvas_w * 0.9 / map_w
        scale_h = canvas_h * 0.9 / map_h
        self.scale = min(scale_w, scale_h)

        self.offset_x = (canvas_w - map_w * self.scale) / 2 - min_x * self.scale
        self.offset_y = (canvas_h - map_h * self.scale) / 2 - min_y * self.scale

    def transform(self, x: float, y: float) -> Tuple[float, float]:
        return x * self.scale + self.offset_x, y * self.scale + self.offset_y

    def draw_map_points(self, points: List[Point]) -> None:
        self.canvas.delete("all")

        for x, y in points:
            sx, sy = self.transform(x, y)
            self.canvas.create_arc(
                sx - 5, sy - 5, sx + 5, sy + 5,
                start=0, extent=359,
                fill="red",
                outline="black",
                style="pieslice"
            )

    def draw_base(self) -> None:
        bx, by = self.transform(*BASE)
        self.canvas.create_rectangle(bx - 6, by - 6, bx + 6, by + 6, fill="black")
        self.canvas.create_text(bx + 12, by, fill="black", anchor="w")

    def draw_routes(self, routes: Dict[int, List[Point]], colors: List[str]) -> None:
        for drone_id, route in routes.items():
            color = colors[drone_id % len(colors)]
            for i in range(len(route) - 1):
                x1, y1 = self.transform(*route[i])
                x2, y2 = self.transform(*route[i + 1])

                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=color,
                    width=2,
                    dash=(4, 2)
                )

    def draw_drones(
            self,
            routes: Dict[int, List[Point]],
            frame: Dict[int, Tuple[float, float] | None],
            flight_paths: Dict[int, List[Point]],
            last_positions: Dict[int, Tuple[float, float]],
            colors: List[str]
    ) -> None:

        for drone_id in routes.keys():
            current_pos = frame.get(drone_id)
            if current_pos is not None:
                last_positions[drone_id] = current_pos

            pos = last_positions.get(drone_id)
            if pos is None:
                continue

            flight_paths[drone_id].append(pos)

        for drone_id, path in flight_paths.items():
            color = colors[drone_id % len(colors)]
            for i in range(1, len(path)):
                x1, y1 = self.transform(*path[i - 1])
                x2, y2 = self.transform(*path[i])
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

        for drone_id, pos in last_positions.items():
            x, y = self.transform(*pos)
            color = colors[drone_id % len(colors)]
            r = 6
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color)
            self.canvas.create_text(x + 10, y, text=f"{drone_id}", fill=color)

    def draw_legend(
            self,
            routes: Dict[int, List[Point]],
            colors: List[str],
            drone_configs: Dict[int, dict]
    ) -> None:

        legend_x = 20
        legend_y = 20

        self.canvas.create_text(
            legend_x,
            legend_y - 10,
            text="Legenda dronów:",
            fill="black",
            anchor="nw",
            font=("Arial", 10, "bold")
        )

        for drone_id in routes.keys():
            color = colors[drone_id % len(colors)]
            dy = legend_y + 20 * (drone_id + 1)

            self.canvas.create_oval(legend_x, dy, legend_x + 10, dy + 10, fill=color)

            drone_name = drone_configs.get(drone_id, {}).get("name", f"Dron {drone_id}")

            self.canvas.create_text(
                legend_x + 20,
                dy + 5,
                text=drone_name,
                anchor="w",
                fill="black"
            )

    def draw_full_frame(
            self,
            points: List[Point],
            routes: Dict[int, List[Point]],
            frame: Dict[int, Tuple[float, float] | None],
            flight_paths: Dict[int, List[Point]],
            last_positions: Dict[int, Tuple[float, float]],
            colors: List[str],
            drone_configs: Dict[int, dict]
    ) -> None:

        self.canvas.delete("all")

        if points:
            self.draw_map_points(points)
        self.draw_base()

        if routes:
            self.draw_routes(routes, colors)
            self.draw_drones(routes, frame, flight_paths, last_positions, colors)
            self.draw_legend(routes, colors, drone_configs)



