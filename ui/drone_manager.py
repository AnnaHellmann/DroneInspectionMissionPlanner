# ui/drone_manager.py

import tkinter as tk
from tkinter import ttk, messagebox


class DroneManager:
    """
    Zarządza sekcją dronów w UI.
    """

    # Mapa nazw z UI → klucze używane przez algorytmy
    KEY_MAP = {
        "Zasięg [m]": "range",
        "Czas lotu [s]": "flight_time",
        "Pojemność baterii [mAh]": "battery"
    }

    def __init__(self, parent_frame, drone_models):
        self.parent = parent_frame
        self.drone_models = drone_models
        self.frames = []

    # ------------------------------------------------------------------
    #   TWORZENIE FORM DLA DRONÓW
    # ------------------------------------------------------------------
    def build_forms(self, num_drones):
        for frame in self.frames:
            frame.destroy()
        self.frames.clear()

        for i in range(num_drones):
            frame = tk.LabelFrame(self.parent, text=f"Dron {i + 1}", bg="#f0f0f0", padx=5, pady=5)
            frame.pack(fill="x", pady=5)
            self.frames.append(frame)

            tk.Label(frame, text="Model:", bg="#f0f0f0").grid(row=0, column=0, sticky="w")
            model_combo = ttk.Combobox(frame, values=list(self.drone_models.keys()),
                                       state="readonly", width=10)
            model_combo.grid(row=0, column=1, sticky="w", padx=5)
            model_combo.current(0)

            entries = {}
            row_index = 1

            default_model = self.drone_models[model_combo.get()]

            for param, val in default_model.items():
                tk.Label(frame, text=f"{param}:", bg="#f0f0f0").grid(row=row_index, column=0, sticky="w")
                entry = ttk.Entry(frame, width=10)
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

    # ------------------------------------------------------------------
    #   WALIDACJA & KONWERSJA PARAMETRÓW
    # ------------------------------------------------------------------
    def get_configs(self):
        """
        Zwraca słownik:
        {
            0: {"range": 5000, "flight_time": 1200, "battery": 3000},
            1: {...},
            ...
        }
        """

        drone_configs = {}

        for i, frame in enumerate(self.frames):
            params = {}

            for ui_key, entry in frame.entries.items():
                try:
                    value = float(entry.get())
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

                # KONWERSJA nazwy z UI → klucz dla algorytmów
                internal_key = self.KEY_MAP[ui_key]
                params[internal_key] = value

            drone_configs[i] = params

        return drone_configs
