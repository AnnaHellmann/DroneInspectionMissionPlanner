# config.py

ALLOC_METHOD = "D" #D/C/B/A/equally
# TSP_METHOD = "ga"

WINDOW_TITLE = "Symulator Misji Dronów"
WINDOW_SIZE = "1000x650"

BACKGROUND_COLOR = "#f4f4f4"

DEFAULT_DRONE_COUNT = [1, 2, 3, 4, 5]
DEFAULT_TSP_METHODS = ["GA", "PSO"]

DRONE_COLORS = ["red", "orange", "green", "blue", "purple"]
DRONE_NAMES = ["default", "DJI Mini 3 Pro", "DJI Air 2S", "DJI Mavic 3", "DJI Matrice 30"]

SIM_SPEED = 40.0
SIM_TIMESTEP = 0.05
ANIMATION_DELAY = 30

DRONE_MODELS = {
    DRONE_NAMES[0]: {
        "Zasięg [m]": 0,
        "Czas lotu [s]": 0,
        "Pojemność baterii [mAh]": 0,
        "Prędkość [m/s]": 10,
        "Czas obsługi punktu [s]": 5
    },
    DRONE_NAMES[1]: {
        "Zasięg [m]": 18000,
        "Czas lotu [s]": 34 * 60,
        "Pojemność baterii [mAh]": 2453,
        "Prędkość [m/s]": 16,
        "Czas obsługi punktu [s]": 5
    },
    DRONE_NAMES[2]: {
        "Zasięg [m]": 18000,
        "Czas lotu [s]": 31 * 60,
        "Pojemność baterii [mAh]": 3500,
        "Prędkość [m/s]": 19,
        "Czas obsługi punktu [s]": 5
    },
    DRONE_NAMES[3]: {
        "Zasięg [m]": 30000,
        "Czas lotu [s]": 46 * 60,
        "Pojemność baterii [mAh]": 5000,
        "Prędkość [m/s]": 21,
        "Czas obsługi punktu [s]": 5
    },
    DRONE_NAMES[4]: {
        "Zasięg [m]": 30000,
        "Czas lotu [s]": 41 * 60,
        "Pojemność baterii [mAh]": 5880,
        "Prędkość [m/s]": 23,
        "Czas obsługi punktu [s]": 5
    }
}

GA_PARAMS = {
    "pop_size": 100,
    "generations": 800,
    "crossover_rate": 0.9,
    "mutation_rate": 0.2,
    "tournament_k": 3,
}

PSO_PARAMS = {
    "iterations": 1200,
    "swarm_size": 200,
    "w": 0.0,  # inercja niewykorzystywana dla pso permutacji
    "c1": 1.2,  # cognitive component
    "c2": 2.2,  # social component
}