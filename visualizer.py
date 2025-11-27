#rysowanie mapy, trajektorii, animacje lotów

import matplotlib.pyplot as plt
from typing import List, Tuple, Dict

Point = Tuple[float, float]

def plot_points(points: List[Point], title: str = "Punkty inspekcji"):
    x, y = zip(*points)
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, c='pink', marker='o')
    plt.title(title)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def plot_paths(drone_paths: Dict[int, List[Point]], title: str):
    plt.figure(figsize=(10, 8))
    colors = plt.cm.get_cmap('tab10', len(drone_paths))

    for drone_id, path in drone_paths.items():
        x, y = zip(*path)
        plt.plot(x, y, marker='o', label=f"Dron {drone_id}", color=colors(drone_id))
        plt.scatter(x[0], y[0], color=colors(drone_id), s=100, marker='s', label=f"Start {drone_id}")

        for i, (px, py) in enumerate(path):
            plt.text(px, py + 0.8, str(i), fontsize=8, ha='center', color=colors(drone_id))

    plt.title(title)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.axis('equal')
    plt.show()