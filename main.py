import pygame
from config_menu import solicitar_datos_pygame
from simulation import ejecutar_simulacion
from main_menu import MainMenu
from config import GameConfig, SimulationConfig
from help_menu import mostrar_pantalla_ayuda

# Crear instancia central de configuración
config = GameConfig()

pygame.init()
pantalla = pygame.display.set_mode((config.display.ANCHO_VENTANA, config.display.ALTO_VENTANA))
pygame.display.set_caption("Simulación de Bacteria")
reloj = pygame.time.Clock()

def principal():
    estado = "MENU"
    while True:
        if estado == "MENU":
            menu = MainMenu(pantalla)
            resultado = menu.run()
            if resultado == "start":
                estado = "CONFIG"
            elif resultado == "help":
                estado = "HELP"
            elif resultado is False: # Quit event
                break
                
        elif estado == "HELP":
            mostrar_pantalla_ayuda(pantalla, config)
            estado = "MENU" # Regresa al menu principal al cerrar
                
        elif estado == "CONFIG":
            resultado = solicitar_datos_pygame(pantalla, config)
            if resultado is None: # Cancel/Back or Quit
                estado = "MENU"
            else:
                num_ciclos, vida_inicial, num_comida, num_particulas = resultado
                config.simulation = SimulationConfig(
                    num_ciclos=num_ciclos, 
                    vida_inicial=vida_inicial, 
                    num_comida=num_comida, 
                    num_particulas=num_particulas
                )
                estado = "SIMULATION"
                
        elif estado == "SIMULATION":
            resultado = ejecutar_simulacion(pantalla, reloj, config)
            # Returns None if Quit, returns False/True if Return To Menu was pressed
            if resultado == "menu":
                estado = "MENU"
            else:
                break # User closed app from inside simulation directly

    pygame.quit()

if __name__ == "__main__":
    principal()
