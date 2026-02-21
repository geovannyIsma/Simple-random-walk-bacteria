import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
from config import GameConfig, PhysicsConfig, SimulationConfig
from simulation import ejecutar_simulacion

pygame.init()
config = GameConfig()
config.physics.INTERVALO_MOVIMIENTO = 50
config.simulation.num_ciclos = 10
config.simulation.num_particulas = 500
config.simulation.num_comida = 500

pantalla = pygame.display.set_mode((config.display.ANCHO_VENTANA, config.display.ALTO_VENTANA))
reloj = pygame.time.Clock()

try:
    ejecutar_simulacion(pantalla, reloj, config)
except SystemExit:
    pass # Expected when sys.exit called at the end
print("Simulation ran successfully without crashing.")
