# ui/map_info_window.py

import tkinter as tk
from tkinter import ttk
from core.utils import euclidean_distance


class MapInfoWindow:
    """wyświetlanie okna info"""

    @staticmethod
    def show(parent, map_name, points):
        if not points:
            tk.messagebox.showinfo("Informacja", "Brak punktów dla tej mapy.")
            return

        num_points = len(points)

        dists = []
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                dists.append(euclidean_distance(points[i], points[j]))

        max_dist = max(dists) if dists else 0
        min_dist = min(dists) if dists else 0
        avg_dist = sum(dists) / len(dists) if dists else 0

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width = max_x - min_x
        height = max_y - min_y

        win = tk.Toplevel(parent)
        win.title(f"Specyfikacja mapy: {map_name}")
        win.geometry("420x480")
        win.resizable(False, False)

        tk.Label(win, text=f"Mapa: {map_name}", font=("Arial", 12, "bold")).pack(pady=10)

        info_text = (
            f"Liczba punktów: {num_points}\n"
            f"Wymiary mapy (szer. × wys.): {width:.2f}m × {height:.2f}m\n"
            f"Minimalny dystans: {min_dist:.2f}m\n"
            f"Maksymalny dystans: {max_dist:.2f}m\n"
            f"Średni dystans: {avg_dist:.2f}m\n"
            "\nPunkty (x, y):\n"
        )

        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True)

        text_box = tk.Text(frame, wrap="word", height=18)
        scrollbar = ttk.Scrollbar(frame, command=text_box.yview)
        text_box.configure(yscrollcommand=scrollbar.set)

        text_box.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        text_box.insert("end", info_text)

        for p in points:
            text_box.insert("end", f"{p}\n")

        text_box.config(state="disabled")

        ttk.Button(win, text="Zamknij", command=win.destroy).pack(pady=10)
