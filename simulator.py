# simulator.py
# Symulacja z rzeczywistym czasem + przyspieszenie animacji

import time
import math

BASE = (0.0, 0.0)


class Simulator:
    def __init__(self, paths, drone_configs, timestep=0.05, speedup=50.0):
        """
        paths: {drone_id: [(x1,y1), (x2,y2), ...]} - TRASA W METRACH
        drone_configs: {drone_id: {"speed": ..., "service_time": ...}}
        timestep: odstęp między klatkami animacji [sekundy realne]
        speedup: ile razy przyspieszamy czas rzeczywisty misji
        """
        self.paths = paths
        self.cfg = drone_configs
        self.timestep = timestep
        self.speedup = speedup

        self.segments = self._build_segments()

    def _build_segments(self):
        """Tworzy segmenty dla każdego drona."""
        segments = {}

        for drone_id, route in self.paths.items():
            segs = []

            for i in range(len(route) - 1):
                p1 = tuple(route[i])
                p2 = tuple(route[i + 1])
                is_stop = (p2 != BASE)
                segs.append((p1, p2, is_stop))

            segments[drone_id] = segs

        return segments

    def simulate(self):
        """
        Generator zwracający w każdej klatce pozycje dronów.
        Realny czas liczymy normalnie, ale dzielimy go przez speedup.
        """
        # Stany dronów
        state = {d: "move" for d in self.segments}
        seg_idx = {d: 0 for d in self.segments}
        progress = {d: 0.0 for d in self.segments}
        hover_remaining = {d: 0.0 for d in self.segments}

        while True:

            positions = {}
            all_done = True

            # Ile realnego czasu mija w jednej klatce animacji?
            dt_real = self.timestep * self.speedup

            for drone_id, segs in self.segments.items():

                cfg = self.cfg[drone_id]
                speed = cfg["speed"]
                service = cfg["service_time"]

                if seg_idx[drone_id] >= len(segs):
                    positions[drone_id] = None
                    continue

                all_done = False
                p1, p2, is_stop = segs[seg_idx[drone_id]]

                # --- POSTÓJ ---
                if state[drone_id] == "hover":
                    positions[drone_id] = p2
                    hover_remaining[drone_id] -= dt_real

                    if hover_remaining[drone_id] <= 0:
                        state[drone_id] = "move"
                        seg_idx[drone_id] += 1
                        progress[drone_id] = 0.0

                    continue

                # --- LOT ---
                dist = math.dist(p1, p2)
                t_real = dist / speed if speed > 0 else 0.00001

                delta = dt_real / t_real
                progress[drone_id] += delta

                if progress[drone_id] >= 1.0:
                    # dotarliśmy do p2
                    positions[drone_id] = p2

                    if is_stop:
                        state[drone_id] = "hover"
                        hover_remaining[drone_id] = service
                    else:
                        seg_idx[drone_id] += 1
                        progress[drone_id] = 0.0

                else:
                    # interpolacja punktu
                    t = progress[drone_id]
                    x = p1[0] + (p2[0] - p1[0]) * t
                    y = p1[1] + (p2[1] - p1[1]) * t
                    positions[drone_id] = (x, y)

            yield positions
            time.sleep(self.timestep)

            if all_done:
                return
