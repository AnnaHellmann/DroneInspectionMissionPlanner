# simulator.py
# symulacja przelotu z rzeczywistym czasem postoju

import time
import math


class Simulator:
    def __init__(self, paths, drone_configs, timestep=0.05):
        """
        paths: {drone_id: [(x1,y1), (x2,y2), ...]}
        drone_configs: {drone_id: {"speed": ..., "service_time": ...}}
        """
        self.paths = paths
        self.drone_configs = drone_configs
        self.timestep = timestep

        # prędkość każdego drona
        self.drone_speeds = {
            drone_id: drone_configs[drone_id]["speed"]
            for drone_id in paths.keys()
        }

        # czas obsługi punktu
        self.service_times = {
            drone_id: drone_configs[drone_id]["service_time"]
            for drone_id in paths.keys()
        }

    def simulate(self):
        """
        Generator zwracający w każdej klatce:
        {drone_id: (x, y) albo None}

        Postój na punktach jest mierzony realnym czasem systemowym,
        niezależnie od FPS.
        """

        trajectories = self._build_movement_trajectories()

        # indeks ruchu w trajektorii
        idx = {drone_id: 0 for drone_id in trajectories.keys()}

        # stany dronów
        state = {drone_id: "move" for drone_id in trajectories.keys()}
        hover_start = {drone_id: None for drone_id in trajectories.keys()}

        while True:
            positions = {}
            all_finished = True

            for drone_id, traj in trajectories.items():

                # --- RUCH ---
                if state[drone_id] == "move":
                    all_finished = False

                    # koniec trasy?
                    if idx[drone_id] >= len(traj):
                        positions[drone_id] = None
                        continue

                    pos, is_inspection_point = traj[idx[drone_id]]
                    positions[drone_id] = pos

                    # jeśli to punkt inspekcji → wchodzimy w postój
                    if is_inspection_point:
                        state[drone_id] = "hover"
                        hover_start[drone_id] = time.time()
                    else:
                        idx[drone_id] += 1

                # --- POSTÓJ NA PUNKCIE ---
                elif state[drone_id] == "hover":
                    all_finished = False

                    positions[drone_id] = traj[idx[drone_id]][0]

                    elapsed = time.time() - hover_start[drone_id]
                    if elapsed >= self.service_times[drone_id]:
                        # koniec postoju → przechodzimy do następnej klatki ruchu
                        state[drone_id] = "move"
                        idx[drone_id] += 1

            yield positions
            time.sleep(self.timestep)

            if all_finished:
                return

    def _build_movement_trajectories(self):
        """
        Buduje listę punktów ruchu:
        Zwraca {drone_id: [(pos, is_inspection_point), ...]}
        """

        trajectories = {}

        for drone_id, route in self.paths.items():
            traj = []

            if not route or len(route) < 2:
                trajectories[drone_id] = traj
                continue

            speed = self.drone_speeds[drone_id]

            for i in range(len(route) - 1):
                p1 = route[i]
                p2 = route[i + 1]

                # zamiana na tuple
                p1 = tuple(p1)
                p2 = tuple(p2)

                dist = math.dist(p1, p2)

                if dist == 0:
                    traj.append((p1, True))  # inspekcja
                    continue

                # ruch między punktami
                steps = max(1, int(dist / (speed * self.timestep)))

                for s in range(steps):
                    t = s / steps
                    x = p1[0] + (p2[0] - p1[0]) * t
                    y = p1[1] + (p2[1] - p1[1]) * t
                    traj.append(((x, y), False))

                # p2 = punkt inspekcji
                traj.append((p2, True))

            trajectories[drone_id] = traj

        return trajectories
