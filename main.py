import pygame
from input_window import solicitar_datos
from simulation import ejecutar_simulacion

# Configuración inicial
ANCHO_VENTANA, ALTO_VENTANA = 1280, 800
MARGEN = 100
TAMANO_CELDA = 30

ANCHO = (ANCHO_VENTANA - 2 * MARGEN) // TAMANO_CELDA * TAMANO_CELDA
ALTO = (ALTO_VENTANA - 2 * MARGEN) // TAMANO_CELDA * TAMANO_CELDA

MARGEN_HORIZONTAL = (ANCHO_VENTANA - ANCHO) // 2
MARGEN_VERTICAL = (ALTO_VENTANA - ALTO) // 2

COLOR_FONDO = (0, 0, 0)
COLOR_BACTERIA = (0, 255, 0)
COLOR_TRAZA = (255, 255, 0)
COLOR_SUPERPOSICION_TRAZA = (255, 0, 0)
COLOR_COMIDA = (255, 0, 255)

RADIO_COMIDA = 5
RADIO_BACTERIA = 6
DISTANCIA_COLISION = RADIO_COMIDA + RADIO_BACTERIA
INTERVALO_MOVIMIENTO = 500

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Simulación de Bacteria")
reloj = pygame.time.Clock()

def principal():
    resultado = solicitar_datos()
    if resultado:
        num_ciclos, vida_inicial, num_comida, num_particulas = resultado
        ejecutar_simulacion(pantalla, reloj, ANCHO, ALTO, TAMANO_CELDA, MARGEN, MARGEN_HORIZONTAL, MARGEN_VERTICAL,
                       COLOR_FONDO, COLOR_BACTERIA, COLOR_TRAZA, COLOR_SUPERPOSICION_TRAZA, COLOR_COMIDA,
                       RADIO_COMIDA, RADIO_BACTERIA, DISTANCIA_COLISION, INTERVALO_MOVIMIENTO,
                       num_ciclos, vida_inicial, num_comida, num_particulas, ALTO_VENTANA, ANCHO_VENTANA, debug=False)

if __name__ == "__main__":
    principal()
