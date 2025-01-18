import pygame
import random
import sys
import tkinter as tk
from tkinter import messagebox

# Configuración inicial
WINDOW_WIDTH, WINDOW_HEIGHT = 1080, 720
MARGIN = 50
GRID_SIZE = 30

WIDTH = (WINDOW_WIDTH - 2 * MARGIN) // GRID_SIZE * GRID_SIZE
HEIGHT = (WINDOW_HEIGHT - 2 * MARGIN) // GRID_SIZE * GRID_SIZE

# Ajustar márgenes dinámicamente para centrar la cuadrícula
HORIZONTAL_MARGIN = (WINDOW_WIDTH - WIDTH) // 2
VERTICAL_MARGIN = (WINDOW_HEIGHT - HEIGHT) // 2

BACKGROUND_COLOR = (0, 0, 0)
BACTERIA_COLOR = (0, 255, 0)
TRACE_COLOR = (255, 255, 0)
TRACE_OVERLAP_COLOR = (255, 0, 0)
FOOD_COLOR = (255, 0, 255)

FOOD_RADIUS = 5
BACTERIA_RADIUS = 6
COLLISION_DISTANCE = FOOD_RADIUS + BACTERIA_RADIUS
FPS = 1

# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Simulación de Bacteria")
clock = pygame.time.Clock()

def generate_bacteria_start():
    side = random.choice(["top", "bottom", "left", "right"])
    vertical = random.randint(0, WIDTH // GRID_SIZE - 1)
    horizontal = random.randint(0, HEIGHT // GRID_SIZE - 1)

    if side == "top":
        return vertical * GRID_SIZE + HORIZONTAL_MARGIN, VERTICAL_MARGIN
    elif side == "bottom":
        return vertical * GRID_SIZE + HORIZONTAL_MARGIN, HEIGHT + VERTICAL_MARGIN
    elif side == "left":
        return HORIZONTAL_MARGIN, horizontal * GRID_SIZE + VERTICAL_MARGIN
    else:
        return WIDTH + HORIZONTAL_MARGIN, horizontal * GRID_SIZE + VERTICAL_MARGIN

def generate_food(num_food):
    food_positions = []
    while len(food_positions) < num_food:
        x = random.randint(0, WIDTH // GRID_SIZE - 1) * GRID_SIZE + HORIZONTAL_MARGIN
        y = random.randint(0, HEIGHT // GRID_SIZE - 1) * GRID_SIZE + VERTICAL_MARGIN
        food_positions.append((x, y))
    return food_positions

def is_inside_screen(x, y):
    return MARGIN <= x < WIDTH + MARGIN and MARGIN <= y < HEIGHT + MARGIN

def is_collision(bacteria_position, food_position):
    bx, by = bacteria_position
    fx, fy = food_position
    distance = ((bx - fx) ** 2 + (by - fy) ** 2) ** 0.5
    return distance <= COLLISION_DISTANCE

def draw_grid():
    for x in range(HORIZONTAL_MARGIN, WIDTH + HORIZONTAL_MARGIN + 1, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, VERTICAL_MARGIN), (x, HEIGHT + VERTICAL_MARGIN))
    for y in range(VERTICAL_MARGIN, HEIGHT + VERTICAL_MARGIN + 1, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (HORIZONTAL_MARGIN, y), (WIDTH + HORIZONTAL_MARGIN, y))

def solicitar_datos():
    def on_submit():
        try:
            global num_cycles, initial_life, food_energy, num_food
            num_cycles = int(entry_cycles.get())
            initial_life = int(entry_life.get())
            num_food = int(entry_food.get())
            if num_cycles <= 0 or initial_life <= 0 or num_food <= 0:
                raise ValueError
            food_energy = initial_life
            root.destroy()
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese un número entero válido.")
            entry_cycles.delete(0, tk.END)
            entry_life.delete(0, tk.END)
            entry_food.delete(0, tk.END)

    root = tk.Tk()
    root.title("Configuración inicial")
    root.geometry("280x90")
    root.eval('tk::PlaceWindow . center')
    root.resizable(False, False)

    tk.Label(root, text="Número de ciclos:").grid(row=0, column=0)
    entry_cycles = tk.Entry(root)
    entry_cycles.grid(row=0, column=1)

    tk.Label(root, text="Vida inicial de la bacteria:").grid(row=1, column=0)
    entry_life = tk.Entry(root)
    entry_life.grid(row=1, column=1)

    tk.Label(root, text="Número de comidas:").grid(row=2, column=0)
    entry_food = tk.Entry(root)
    entry_food.grid(row=2, column=1)

    submit_button = tk.Button(root, text="Iniciar Simulación", command=on_submit)
    submit_button.grid(row=3, columnspan=2)

    root.mainloop()

def walk():
    orientacion = random.choice([1, -1])
    direccion = random.choice([1, -1])
    if orientacion == 1:
        return "up" if direccion == 1 else "down"
    else:
        return "right" if direccion == 1 else "left"

def main():
    solicitar_datos()
    debug = True

    food_positions = generate_food(num_food)

    for cycle in range(num_cycles):
        bacteria_position = generate_bacteria_start()
        trace = {bacteria_position: 1}
        moved_steps = 0

        while moved_steps < initial_life:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill(BACKGROUND_COLOR)
            draw_grid()
            for food_position in food_positions:
                pygame.draw.circle(screen, FOOD_COLOR, food_position, FOOD_RADIUS)

            if debug:
                for point, count in trace.items():
                    color = TRACE_OVERLAP_COLOR if count > 1 else TRACE_COLOR
                    pygame.draw.circle(screen, color, point, 3)

            x, y = bacteria_position
            move = None

            if x == MARGIN or x == WIDTH + MARGIN or y == MARGIN or y == HEIGHT + MARGIN:
                if (x, y) in [(MARGIN, MARGIN), (WIDTH + MARGIN, MARGIN), (MARGIN, HEIGHT + MARGIN), (WIDTH + MARGIN, HEIGHT + MARGIN)]:
                    while move not in ["left", "up", "right", "down"]:
                        move = walk()
                        if (x == MARGIN and y == MARGIN and move in ["left", "up"]) or \
                           (x == WIDTH + MARGIN and y == MARGIN and move in ["right", "up"]) or \
                           (x == MARGIN and y == HEIGHT + MARGIN and move in ["left", "down"]) or \
                           (x == WIDTH + MARGIN and y == HEIGHT + MARGIN and move in ["right", "down"]):
                            break
                else:
                    while move not in ["left", "right", "up", "down"]:
                        move = walk()
                        if (x == MARGIN and move == "left") or \
                           (x == WIDTH + MARGIN and move == "right") or \
                           (y == MARGIN and move == "up") or \
                           (y == HEIGHT + MARGIN and move == "down"):
                            break
            else:
                move = walk()

            if move == "up":
                y -= GRID_SIZE
            elif move == "down":
                y += GRID_SIZE
            elif move == "right":
                x += GRID_SIZE
            else:
                x -= GRID_SIZE

            new_position = (x, y)

            if is_inside_screen(*new_position):
                bacteria_position = new_position
                moved_steps += 1

                if bacteria_position in trace:
                    trace[bacteria_position] += 1
                else:
                    trace[bacteria_position] = 1

            for food_position in food_positions:
                if is_collision(bacteria_position, food_position):
                    moved_steps -= food_energy
                    food_positions.remove(food_position)
                    break

            pygame.draw.circle(screen, BACTERIA_COLOR, bacteria_position, BACTERIA_RADIUS)
            pygame.display.flip()
            clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()