# config.py

# --- UI CONFIG ---
WINDOW_TITLE = "Symulator Misji Dronów"
WINDOW_SIZE = "1000x650"

BACKGROUND_COLOR = "#f4f4f4"

DEFAULT_DRONE_COUNT = [1, 2, 3, 4, 5]
DEFAULT_TSP_METHODS = ["GA", "PSO"]

DRONE_COLORS = ["red", "orange", "green", "blue", "purple"]

# --- SIMULATION CONFIG ---
SIM_SPEED = 40.0
SIM_TIMESTEP = 0.05
ANIMATION_DELAY = 30

# --- DRONE MODELS ---
DRONE_MODELS = {
    "Model": {
        "Zasięg [m]": 0,
        "Czas lotu [s]": 0,
        "Pojemność baterii [mAh]": 0
    },
    "DJI Mini 3 Pro": {
        "Zasięg [m]": 18000,
        "Czas lotu [s]": 34 * 60,
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

GA_PARAMS = {
    "pop_size": 20,
    "generations": 50,
    "crossover_rate": 0.9,
    "mutation_rate": 0.1,
    "tournament_k": 3,
}

PSO_PARAMS = {
    "iterations": 50, #300
    "swarm_size": 20, #50
    "w": 0.8,  # inertia niewykorzystywana dla pso permutacji
    "c1": 1.5,  # cognitive component
    "c2": 1.5,  # social component
}