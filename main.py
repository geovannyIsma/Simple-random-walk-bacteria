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
FOOD_RADIUS = 5
BACTERIA_RADIUS = 5
COLLISION_DISTANCE = FOOD_RADIUS + BACTERIA_RADIUS
FPS = 30
GRID_SIZE = 30

# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Bacteria")
clock = pygame.time.Clock()

def generate_bacteria_start():
    # Aparece aleatoriamente en una orilla alineada con la cuadrícula
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        return random.randint(0, (WIDTH - 1) // GRID_SIZE) * GRID_SIZE, 0
    elif side == "bottom":
        return random.randint(0, (WIDTH - 1) // GRID_SIZE) * GRID_SIZE, HEIGHT - GRID_SIZE
    elif side == "left":
        return 0, random.randint(0, (HEIGHT - 1) // GRID_SIZE) * GRID_SIZE
    else:  # right
        return WIDTH - GRID_SIZE, random.randint(0, (HEIGHT - 1) // GRID_SIZE) * GRID_SIZE

def generate_food(num_food):
    return [(random.randint(0, (WIDTH - 1) // GRID_SIZE) * GRID_SIZE,
             random.randint(0, (HEIGHT - 1) // GRID_SIZE) * GRID_SIZE) for _ in range(num_food)]

def is_inside_screen(x, y):
    return 0 <= x < WIDTH and 0 <= y < HEIGHT

def is_collision(bacteria_position, food_position):
    bx, by = bacteria_position
    fx, fy = food_position
    distance = ((bx - fx) ** 2 + (by - fy) ** 2) ** 0.5
    return distance <= COLLISION_DISTANCE

def main():
    # Variables
    num_cycles = 3
    initial_life = 500
    food_energy = 10
    num_food = 10
    debug = True

    # Generar comida
    food_positions = generate_food(num_food)

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
            for food_position in food_positions:
                pygame.draw.circle(screen, FOOD_COLOR, food_position, FOOD_RADIUS)

            # Dibujar trayectoria
            if debug:
                for point, count in trace.items():
                    color = TRACE_OVERLAP_COLOR if count > 1 else TRACE_COLOR
                    pygame.draw.circle(screen, color, point, 3)

            # Movimiento de la bacteria
            x, y = bacteria_position

            if moved_steps == -1:  # Primera jugada (sin retroceder)
                moves = [(0, GRID_SIZE), (GRID_SIZE, 0), (0, -GRID_SIZE), (-GRID_SIZE, 0)]
                if x == 0:  # Está en la izquierda
                    moves = [(0, GRID_SIZE), (GRID_SIZE, 0), (0, -GRID_SIZE)]
                elif x == WIDTH - GRID_SIZE:  # Está en la derecha
                    moves = [(0, GRID_SIZE), (0, -GRID_SIZE), (-GRID_SIZE, 0)]
                elif y == 0:  # Está arriba
                    moves = [(GRID_SIZE, 0), (0, GRID_SIZE), (-GRID_SIZE, 0)]
                elif y == HEIGHT - GRID_SIZE:  # Está abajo
                    moves = [(GRID_SIZE, 0), (0, GRID_SIZE), (-GRID_SIZE, 0)]
            else:  # Movimientos normales
                moves = [(0, GRID_SIZE), (GRID_SIZE, 0), (0, -GRID_SIZE), (-GRID_SIZE, 0)]

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
            for food_position in food_positions:
                if is_collision(bacteria_position, food_position):
                    moved_steps -= food_energy  # Reducir los pasos realizados
                    food_positions.remove(food_position)
                    food_positions.append(generate_food(1)[0])
                    break

            # Dibujar bacteria
            pygame.draw.circle(screen, BACTERIA_COLOR, bacteria_position, BACTERIA_RADIUS)

            # Actualizar pantalla
            pygame.display.flip()
            clock.tick(FPS)

    # Salir
    pygame.quit()

if __name__ == "__main__":
    main()