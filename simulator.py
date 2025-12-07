# simulator.py
# symulacja przelotu, obliczanie pozycji dronów w czasie

import time
import math


class Simulator:

    def __init__(self, paths, drone_configs, timestep=0.05):
        """
        paths: {drone_id: [(x1,y1), (x2,y2), ...]}
        drone_configs: {drone_id: {"speed": ...}}
        """
        self.paths = paths
        self.drone_configs = drone_configs
        self.timestep = timestep

        self.drone_speeds = {
            drone_id: drone_configs[drone_id]["speed"]
            for drone_id in paths.keys()
        }

    def simulate(self):
        """
        Generator zwracający w każdej klatce:
        {drone_id: (x, y) albo None}
        """
        trajectories = self._build_trajectories()

        if not trajectories:
            return

        max_len = max(len(traj) for traj in trajectories.values())

        for step in range(max_len):
            positions = {}

            for drone_id, traj in trajectories.items():
                if step < len(traj):
                    positions[drone_id] = traj[step]
                else:
                    positions[drone_id] = None

            yield positions
            time.sleep(self.timestep)

    def _build_trajectories(self):
        """
        Dla każdej trasy buduje listę kolejnych punktów pośrednich,
        po których będzie poruszał się dron.
        """
        trajectories = {}

        for drone_id, route in self.paths.items():
            traj = []

            # jeśli trasa ma mniej niż 2 punkty – nic nie robimy
            if not route or len(route) < 2:
                trajectories[drone_id] = traj
                continue

            for i in range(len(route) - 1):
                p1 = route[i]
                p2 = route[i + 1]

                # upewniamy się, że to tuple (x,y)
                if isinstance(p1, list):
                    p1 = tuple(p1)
                if isinstance(p2, list):
                    p2 = tuple(p2)

                dist = math.dist(p1, p2)

                if dist == 0:
                    # punkt powtórzony – po prostu dodaj raz
                    traj.append(p1)
                    continue

                # ile kroków na tym odcinku
                speed = self.drone_speeds[drone_id]
                steps = max(1, int(dist / (speed * self.timestep)))

                for s in range(steps):
                    t = s / steps
                    x = p1[0] + (p2[0] - p1[0]) * t
                    y = p1[1] + (p2[1] - p1[1]) * t
                    traj.append((x, y))

            # dodaj ostatni punkt trasy
            traj.append(route[-1])
            trajectories[drone_id] = traj

        return trajectories


