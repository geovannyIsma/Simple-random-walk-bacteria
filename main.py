import pygame
import random
import sys
import tkinter as tk
from tkinter import messagebox

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
FPS = 1
GRID_SIZE = 30

# Inicialización de Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Bacteria")
clock = pygame.time.Clock()

def simple_random_walk():
    orientacion = random.choice([1,-1])
    direccion = random.choice([1, -1])
    if orientacion == 1:
        return "top" if direccion == 1 else "bottom"
    else:
        return "left" if direccion == 1 else "right"

def generate_bacteria_start():
    # Aparece aleatoriamente en una orilla alineada con la cuadrícula
    side = random.choice(["top", "bottom", "left", "right"])
    # side = simple_random_walk()
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

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))
def solicitar_datos():
    def on_submit():
        try:
            global num_cycles, initial_life, food_energy, num_food
            num_cycles = int(entry_cycles.get())
            initial_life = int(entry_life.get())
            food_energy = initial_life
            num_food = int(entry_food.get())
            root.destroy()
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese un número entero válido.")
            entry_cycles.delete(0, tk.END)
            entry_life.delete(0, tk.END)
            entry_food.delete(0, tk.END)

    root = tk.Tk()
    root.title("Configuración inicial")
    root.geometry("280x90")  # Establecer tamaño específico
    root.resizable(False, False)  # Deshabilitar minimizar y maximizar

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

def main():
    # Solicitar datos
    solicitar_datos()
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

            # Dibujar cuadrícula
            draw_grid()

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