import pygame
import random
import sys

# Configuración inicial
WIDTH, HEIGHT = 1200, 800
BACKGROUND_COLOR = (0, 0, 0)
BACTERIA_COLOR = (0, 255, 0)
TRACE_COLOR = (255, 255, 0)
TRACE_OVERLAP_COLOR = (255, 0, 0)
FOOD_COLOR = (255, 0, 255)
FPS = 1

# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Bacteria")
clock = pygame.time.Clock()

def generate_bacteria_start():
    # Aparece aleatoriamente en una orilla
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        return random.randint(0, WIDTH - 1), 0
    elif side == "bottom":
        return random.randint(0, WIDTH - 1), HEIGHT - 1
    elif side == "left":
        return 0, random.randint(0, HEIGHT - 1)
    else:  # right
        return WIDTH - 1, random.randint(0, HEIGHT - 1)

def generate_food():
    return random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)

def is_inside_screen(x, y):
    return 0 <= x < WIDTH and 0 <= y < HEIGHT

def main():
    # Variables
    num_cycles = 3
    initial_life = 5
    food_energy = 10
    step_size = 10
    debug = True

    # Generar comida
    food_position = generate_food()

    # Ciclo principal
    # Ciclo principal
    for cycle in range(num_cycles):
        # Inicializar bacteria
        bacteria_position = generate_bacteria_start()
        bacteria_life = initial_life
        trace = {}
        moved_steps = -1  # Inicializar en -1 para no contar el punto de aparición

        while moved_steps < initial_life:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Dibujar fondo
            screen.fill(BACKGROUND_COLOR)

            # Dibujar comida
            pygame.draw.circle(screen, FOOD_COLOR, food_position, 5)

            # Dibujar trayectoria
            if debug:
                for point, count in trace.items():
                    color = TRACE_OVERLAP_COLOR if count > 1 else TRACE_COLOR
                    pygame.draw.circle(screen, color, point, 3)

            # Movimiento de la bacteria
            x, y = bacteria_position

            if moved_steps == -1:  # Primera jugada (sin retroceder)
                moves = [(0, step_size), (step_size, 0), (0, -step_size), (-step_size, 0)]
                if x == 0:  # Está en la izquierda
                    moves = [(0, step_size), (step_size, 0), (0, -step_size)]
                elif x == WIDTH - 1:  # Está en la derecha
                    moves = [(0, step_size), (0, -step_size), (-step_size, 0)]
                elif y == 0:  # Está arriba
                    moves = [(step_size, 0), (0, step_size), (-step_size, 0)]
                elif y == HEIGHT - 1:  # Está abajo
                    moves = [(step_size, 0), (0, -step_size), (-step_size, 0)]
            else:  # Movimientos normales
                moves = [(0, step_size), (step_size, 0), (0, -step_size), (-step_size, 0)]

            dx, dy = random.choice(moves)
            new_position = (x + dx, y + dy)

            if is_inside_screen(*new_position):
                bacteria_position = new_position
                moved_steps += 1

                # Registrar trayectoria
                if bacteria_position in trace:
                    trace[bacteria_position] += 1
                else:
                    trace[bacteria_position] = 1

            # Verificar si come comida
            if bacteria_position == food_position:
                moved_steps -= food_energy  # Reducir los pasos realizados
                food_position = generate_food()

            # Dibujar bacteria
            pygame.draw.circle(screen, BACTERIA_COLOR, bacteria_position, 5)

            # Actualizar pantalla
            pygame.display.flip()
            clock.tick(FPS)

    # Salir
    pygame.quit()

if __name__ == "__main__":
    main()
