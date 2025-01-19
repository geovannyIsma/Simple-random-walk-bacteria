import pygame
import random
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QSpinBox, QFormLayout

# Configuración inicial
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 800  # Aumentar tamaño de la ventana
MARGIN = 100  # Aumentar tamaño de los márgenes
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
MOVE_INTERVAL = 800

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
    class InputWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.initUI()

        def initUI(self):
            self.setWindowTitle('Configuración inicial')
            self.setGeometry(100, 100, 500, 300)
            self.setFixedSize(500, 300)
            self.setWindowIcon(QIcon('path/to/icon.png'))  # Add your icon path here
            self.center()

            layout = QVBoxLayout()

            form_layout = QFormLayout()
            self.cycles_label = QLabel('Número de ciclos:')
            self.cycles_input = QSpinBox()
            self.cycles_input.setRange(1, 10000)
            self.cycles_input.setKeyboardTracking(False)
            form_layout.addRow(self.cycles_label, self.cycles_input)

            self.life_label = QLabel('Vida inicial de la bacteria:')
            self.life_input = QSpinBox()
            self.life_input.setRange(1, 10000)
            self.life_input.setKeyboardTracking(False)
            form_layout.addRow(self.life_label, self.life_input)

            self.food_label = QLabel('Número de comidas:')
            self.food_input = QSpinBox()
            self.food_input.setRange(1, 10000)
            self.food_input.setKeyboardTracking(False)
            form_layout.addRow(self.food_label, self.food_input)

            self.particles_label = QLabel('Número de partículas:')
            self.particles_input = QSpinBox()
            self.particles_input.setRange(1, 10000)
            self.particles_input.setKeyboardTracking(False)
            form_layout.addRow(self.particles_label, self.particles_input)

            layout.addLayout(form_layout)

            self.submit_button = QPushButton('Iniciar Simulación')
            self.submit_button.setFixedHeight(40)
            self.submit_button.setFixedWidth(200)
            self.submit_button.clicked.connect(self.on_submit)
            layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)

            self.setLayout(layout)
            self.apply_styles()

        def center(self):
            qr = self.frameGeometry()
            cp = QApplication.desktop().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())

        def apply_styles(self):
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e1e2e;
                    color: #c0c0c0;
                    font-family: 'Roboto', sans-serif;
                    font-size: 16px;
                }
                QLabel {
                    margin-bottom: 10px;
                }
                QSpinBox {
                    background-color: #2e2e3e;
                    border: 1px solid #4e4e6e;
                    padding: 5px;
                    margin-bottom: 15px;
                    color: #c0c0c0;
                }
                QPushButton {
                    background-color: #3e3e5e;
                    border: none;
                    padding: 10px;
                    color: #c0c0c0;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5e5e7e;
                }
            """)

        def on_submit(self):
            try:
                global num_cycles, initial_life, food_energy, num_food, num_particles
                num_cycles = self.cycles_input.value()
                initial_life = self.life_input.value()
                num_food = self.food_input.value()
                num_particles = self.particles_input.value()
                if num_cycles <= 0 or initial_life <= 0 or num_food <= 0 or num_particles <= 0:
                    raise ValueError
                food_energy = initial_life
                self.close()
            except ValueError:
                QMessageBox.critical(self, "Error", "Por favor, ingrese un número entero válido.")
                self.cycles_input.clear()
                self.life_input.clear()
                self.food_input.clear()
                self.particles_input.clear()

    app = QApplication(sys.argv)
    window = InputWindow()
    window.show()
    app.exec_()

def walk():
    orientacion = random.choice([1, -1])
    direccion = random.choice([1, -1])
    if orientacion == 1:
        return "up" if direccion == 1 else "down"
    else:
        return "right" if direccion == 1 else "left"

def draw_debug_info(cycle, bacteria_positions, moved_steps, ate_food, traces, food_positions):
    font = pygame.font.SysFont("Courier New", 16)  # Cambiar la fuente y tamaño
    debug_info = [
        f"Ciclo: {cycle + 1}/{num_cycles}",
        f"Partículas: {len(bacteria_positions)}",
        f"Comida restante: {len(food_positions)}"
    ]
    for i, (pos, steps, ate) in enumerate(zip(bacteria_positions, moved_steps, ate_food)):
        trace_count = traces[i].get(pos, 0)
        debug_info.append(f"Bacteria {i + 1}: Vida {steps}/{initial_life}, {'Comió' if ate else 'No comió'}, Trazas: {trace_count}")

    for i, line in enumerate(debug_info):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (10, 10 + i * 20))

    # Mostrar parámetros ingresados en la esquina inferior
    param_info = [
        f"Parámetros:",
        f"Número de ciclos: {num_cycles}",
        f"Vida inicial de la bacteria: {initial_life}",
        f"Número de comidas: {num_food}",
        f"Número de partículas: {num_particles}"
    ]
    for i, line in enumerate(param_info):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (10, WINDOW_HEIGHT - (len(param_info) - i) * 20 - 10))  # Dibujar en la esquina inferior

def main():
    solicitar_datos()
    debug = True

    bacteria_positions = [generate_bacteria_start() for _ in range(num_particles)]
    traces = [{pos: 1} for pos in bacteria_positions]
    survived_bacteria = [True] * num_particles  # Track survival status

    for cycle in range(num_cycles):
        # Reset food positions and moved steps for each cycle
        food_positions = generate_food(num_food)
        last_move_time = pygame.time.get_ticks()
        moved_steps = [0] * len(bacteria_positions)
        ate_food = [False] * len(bacteria_positions)  # Track if bacteria ate food

        while any(steps < initial_life for steps in moved_steps):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill(BACKGROUND_COLOR)
            draw_grid()
            for food_position in food_positions:
                pygame.draw.circle(screen, FOOD_COLOR, food_position, FOOD_RADIUS)

            if debug:
                for trace in traces:
                    for point, count in trace.items():
                        color = TRACE_OVERLAP_COLOR if count > 1 else TRACE_COLOR
                        pygame.draw.circle(screen, color, point, 3)

            current_time = pygame.time.get_ticks()
            if current_time - last_move_time >= MOVE_INTERVAL:
                last_move_time = current_time

                for i, bacteria_position in enumerate(bacteria_positions):
                    if moved_steps[i] >= initial_life or not survived_bacteria[i]:
                        continue

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
                        bacteria_positions[i] = new_position
                        moved_steps[i] += 1
                        
                        if debug:
                            print(f"Bacteria {i} position: {bacteria_positions[i]}")  # Print the position

                        if new_position in traces[i]:
                            traces[i][new_position] += 1
                        else:
                            traces[i][new_position] = 1

                    for food_position in food_positions:
                        if is_collision(bacteria_positions[i], food_position):
                            ate_food[i] = True  # Mark that this bacteria ate food
                            food_positions.remove(food_position)
                            break

            # Dibujar las bacterias y actualizar la pantalla después de cada movimiento
            screen.fill(BACKGROUND_COLOR)
            draw_grid()
            for food_position in food_positions:
                pygame.draw.circle(screen, FOOD_COLOR, food_position, FOOD_RADIUS)
            for bacteria_position in bacteria_positions:
                pygame.draw.circle(screen, BACTERIA_COLOR, bacteria_position, BACTERIA_RADIUS)
            if debug:
                for trace in traces:
                    for point, count in trace.items():
                        color = TRACE_OVERLAP_COLOR if count > 1 else TRACE_COLOR
                        pygame.draw.circle(screen, color, point, 3)
                draw_debug_info(cycle, bacteria_positions, moved_steps, ate_food, traces, food_positions)  # Draw debug info
            pygame.display.flip()
            clock.tick(60)  # Ajustar la velocidad de la animación

        # Check survival status
        for i in range(len(bacteria_positions)):
            if not ate_food[i]:
                survived_bacteria[i] = False

        # Filter out dead bacteria for the next cycle
        bacteria_positions = [generate_bacteria_start() for i, pos in enumerate(bacteria_positions) if survived_bacteria[i]]
        traces = [{pos: 1} for pos in bacteria_positions]
        survived_bacteria = [True] * len(bacteria_positions)

        pygame.time.delay(500)  # Delay after the last movement to make it visible

    pygame.quit()

if __name__ == "__main__":
    main()