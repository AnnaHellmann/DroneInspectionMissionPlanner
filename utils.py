from typing import List, Tuple
import math

UNIT_SCALE = 1.0

Point = Tuple[float, float]

def euclidean_distance(p1: Point, p2: Point) -> float: #Odległość euklidesowa między dwoma punktami jest równa długości odcinka łączącego te punkty
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) * UNIT_SCALE

def total_path_length(points: list[Point]) -> float:
    return sum(euclidean_distance(points[i], points[i+1]) for i in range(len(points)-1))
