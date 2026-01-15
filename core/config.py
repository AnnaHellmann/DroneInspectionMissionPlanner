ALLOC_METHOD = "C"

WINDOW_TITLE = "Symulator Misji Dronów"
WINDOW_SIZE = "1000x650"

SIDEBAR_BG = "#e0e0e0"
CANVAS_BG = "#fafafa"
DRONE_FRAME_BG = "#f0f0f0"
BACKGROUND_COLOR = "#f4f4f4"

DEFAULT_DRONE_COUNT = [1, 2, 3, 4, 5]
DEFAULT_TSP_METHODS = ["GA", "PSO"]

BASE = (0.0, 0.0)
ENERGY_LIMIT_RATIO = 0.8

DRONE_COLORS = ["red", "orange", "green", "blue", "purple"]

EMPTY_DRONE = "— brak —"
DRONE_NAMES = [EMPTY_DRONE, "DJI Mini 3 Pro", "DJI Air 2S", "DJI Mavic 3", "DJI Matrice 30"]

SIM_SPEEDUP = 40.0
SIM_TIMESTEP_S = 0.05
ANIMATION_DELAY_MS = 30

MAP_TO_PROFILE = {
        "Mapa 100": "random100",
        "Mapa 8x8": "8x8",
        "Mapa 10x15": "10x15",
        "Mapa 16x16": "16x16",
        "Mapa 20x20": "20x20"
    }

DRONE_MODELS = {
    EMPTY_DRONE: {
        "Zasięg [m]": 0,
        "Czas lotu [s]": 0,
        "Pojemność baterii [mAh]": 0,
        "Prędkość [m/s]": 0,
        "Czas obsługi punktu [s]": 0
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

GA_PROFILES = {
    "random100": {
            "pop_size": 120,
            "generations": 350,
            "crossover_rate": 0.9,
            "mutation_rate": 0.2,
            "tournament_k": 4,
        },
    "8x8": {
        "pop_size": 50,
        "generations": 150,
        "crossover_rate": 0.8,
        "mutation_rate": 0.1,
        "tournament_k": 2,
    },
    "10x15": {
        "pop_size": 100,
        "generations": 500,
        "crossover_rate": 0.9,
        "mutation_rate": 0.15,
        "tournament_k": 3,
    },
    "16x16": {
        "pop_size": 150,
        "generations": 500,
        "crossover_rate": 0.9,
        "mutation_rate": 0.2,
        "tournament_k": 4,
    },
    "20x20": {
        "pop_size": 200,
        "generations": 600,
        "crossover_rate": 0.9,
        "mutation_rate": 0.3,
        "tournament_k": 5,
    }
}

PSO_PROFILES = {
"random100": {
        "iterations": 300,
        "swarm_size": 600,
        "c1": 1.0,
        "c2": 2.2,
    },
    "8x8": {
        "iterations": 40,
        "swarm_size": 200,
        "c1": 1.5,
        "c2": 1.5,
    },
    "10x15": {
        "iterations": 120,
        "swarm_size": 800,
        "c1": 1.2,
        "c2": 2.0,
    },
    "16x16": {
        "iterations": 250,
        "swarm_size": 600,
        "c1": 1.3,
        "c2": 2.0,
    },
    "20x20": {
        "iterations": 300,
        "swarm_size": 800,
        "c1": 1.3,
        "c2": 2.2,
    },
}