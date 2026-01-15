import tkinter as tk
from tkinter import ttk, messagebox
from core.config import DRONE_FRAME_BG

class DroneManager:
    """Zarządza sekcją dronów w UI oraz waliduje parametry wejściowe."""

    KEY_MAP = {
        "Zasięg [m]": "range",
        "Czas lotu [s]": "flight_time",
        "Pojemność baterii [mAh]": "battery_capacity",
        "Prędkość [m/s]": "speed",
        "Czas obsługi punktu [s]": "service_time"
    }

    LIMITS = {
        "range": (50, 200000),
        "flight_time": (60, 7200),
        "battery_capacity": (500, 30000),
        "speed": (1, 50),
        "service_time": (1, 600)
    }

    def __init__(self, parent_frame, drone_models):
        self.parent = parent_frame
        self.drone_models = drone_models
        self.frames = []

    def build_forms(self, num_drones):
        for frame in self.frames:
            frame.destroy()
        self.frames.clear()

        for i in range(num_drones):
            frame = tk.LabelFrame(
                self.parent,
                text=f"Dron {i + 1}",
                bg=DRONE_FRAME_BG,
                padx=5,
                pady=5
            )
            frame.pack(fill="x", pady=5)
            self.frames.append(frame)

            tk.Label(frame, text="Model:", bg=DRONE_FRAME_BG).grid(row=0, column=0, sticky="w")
            model_combo = ttk.Combobox(
                frame,
                values=list(self.drone_models.keys()),
                state="readonly",
                width=15
            )
            model_combo.grid(row=0, column=1, sticky="w", padx=5)
            model_combo.current(0)

            frame.drone_type_var = model_combo

            entries = {}
            row_index = 1

            default_model = self.drone_models[model_combo.get()]

            for param, val in default_model.items():
                tk.Label(frame, text=f"{param}:", bg=DRONE_FRAME_BG).grid(row=row_index, column=0, sticky="w")
                entry = ttk.Entry(frame, width=12)
                entry.insert(0, val)
                entry.grid(row=row_index, column=1, padx=5, pady=2)
                entries[param] = entry
                row_index += 1

            frame.entries = entries

            def update_from_model(event=None, combo=model_combo, entry_dict=entries):
                new_model = self.drone_models[combo.get()]
                for param, entry in entry_dict.items():
                    entry.delete(0, tk.END)
                    entry.insert(0, new_model[param])

            model_combo.bind("<<ComboboxSelected>>", update_from_model)

    def get_configs(self):
        drone_configs = {}

        for i, frame in enumerate(self.frames):
            params = {}

            drone_name = frame.drone_type_var.get() if hasattr(frame, "drone_type_var") else f"Dron {i}"

            for ui_key, entry in frame.entries.items():
                raw = entry.get().strip()

                try:
                    value = float(raw)
                except ValueError:
                    messagebox.showerror(
                        "Błąd parametrów",
                        f"Dron {i + 1}: parametr '{ui_key}' musi być liczbą."
                    )
                    return None

                if value <= 0:
                    messagebox.showerror(
                        "Błąd parametrów",
                        f"Dron {i + 1}: parametr '{ui_key}' musi być > 0."
                    )
                    return None

                internal_key = self.KEY_MAP[ui_key]

                low, high = self.LIMITS[internal_key]
                if not (low <= value <= high):
                    messagebox.showerror(
                        "Nieprawidłowy zakres",
                        f"Dron {i + 1}: parametr '{ui_key}' musi być w zakresie {low}–{high}."
                    )
                    return None

                params[internal_key] = value

            params["name"] = drone_name

            drone_configs[i] = params

        return drone_configs

