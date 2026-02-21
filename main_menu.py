import pygame
import math
import random
import os
from resource_manager import ResourceManager
from gui import LabButton
from config import GameConfig
class ImageAnimation:
    def __init__(self, image, pos, rotation_speed, movement_radius):
        # Tamaño fijo para todas las imágenes
        self.original_image = pygame.transform.scale(image, (100, 100))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)
        self.angle = random.randint(0, 360)
        self.rotation_speed = rotation_speed
        self.center_x, self.center_y = pos
        self.radius = movement_radius
        self.offset = random.randint(0, 360)
        
    def update(self, time):
        # Rotación
        self.angle += self.rotation_speed
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        
        # Movimiento circular
        rad = math.radians(time + self.offset)
        x = self.center_x + math.cos(rad) * self.radius
        y = self.center_y + math.sin(rad) * self.radius
        self.rect = self.image.get_rect(center=(x, y))

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.resource_manager = ResourceManager()
        self.config = GameConfig()
        self.running = True
        self.load_assets()
        
    def load_assets(self):
        # Configurar fuente VHS Gothic
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'fonts', 'vhs-gothic.ttf')
        try:
            self.title_font = pygame.font.Font(font_path, 50)
            self.button_font = pygame.font.Font(font_path, 25)
        except Exception as e:
            print(f"Warning: VHS Gothic font not found, falling back to Courier New: {e}")
            self.title_font = pygame.font.SysFont("Courier New", 72, bold=True)
            self.button_font = pygame.font.SysFont("Courier New", 36, bold=True)

        # Crear animaciones para cada imagen
        self.animations = []
        images = ['bacteria', 'food', 'cicle-icon', 'bacteria-icon', 'food-icon', 'hp-icon']
        screen_width, screen_height = self.screen.get_size()
        
        for img_name in images:
            image = self.resource_manager.images.get(img_name)
            if image:
                # Crear múltiples instancias con parámetros aleatorios pero tamaño fijo
                for _ in range(2):
                    pos = (random.randint(100, screen_width-100), 
                          random.randint(100, screen_height-100))
                    rotation_speed = random.uniform(-2, 2)
                    movement_radius = random.randint(20, 100)
                    
                    self.animations.append(
                        ImageAnimation(image, pos, rotation_speed, movement_radius)
                    )

        # Use the LabButton from our gui system
        button_rect = pygame.Rect(0, 0, 200, 60)
        button_rect.center = (screen_width // 2, screen_height * 0.65)
        self.btn_iniciar = LabButton(button_rect, "Empezar", self.button_font, self.config)
        
        help_rect = pygame.Rect(0, 0, 200, 60)
        help_rect.center = (screen_width // 2, screen_height * 0.65 + 80)
        self.btn_ayuda = LabButton(help_rect, "[?] Ayuda", self.button_font, self.config)
        
        # Bottom Debug Hint
        self.hint_font = pygame.font.SysFont("Courier New", 18)
        self.hint_text = self.hint_font.render("[Ctrl + D] Activar modo Debug", True, (100, 100, 120))
        self.hint_rect = self.hint_text.get_rect(center=(screen_width // 2, screen_height - 30))
        
        # Título con la fuente VHS Gothic y tonalidad terminal
        title_text = "Simple Random Walk Bacteria"
        self.title = self.title_font.render(title_text, True, (150, 200, 150))
        self.title_rect = self.title.get_rect(center=(screen_width // 2, screen_height * 0.3))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.config.simulation.debug = not self.config.simulation.debug
                    print(f"[Sistema] Modo Debug: {'ACTIVADO' if self.config.simulation.debug else 'DESACTIVADO'}")
            
            if self.btn_iniciar.handle_event(event):
                return "start"
            if self.btn_ayuda.handle_event(event):
                return "help"
        return True

    def run(self):
        time = 0
        while self.running:
            result = self.handle_events()
            if result in ("start", "help", False):
                return result

            # Actualizar animaciones
            for anim in self.animations:
                anim.update(time)

            # Fondo gris oscuro terminal
            self.screen.fill((20, 20, 25))
            
            ancho, alto = self.screen.get_size()
            
            # Dibujar decoraciones de laboratorio (grilla sutil)
            for i in range(0, ancho, 40):
                pygame.draw.line(self.screen, (30, 30, 35), (i, 0), (i, alto))
            for j in range(0, alto, 40):
                pygame.draw.line(self.screen, (30, 30, 35), (0, j), (ancho, j))
            
            # Dibujar animaciones
            for anim in self.animations:
                self.screen.blit(anim.image, anim.rect)
            
            # Dibujar título, botones y hints
            self.screen.blit(self.hint_text, self.hint_rect)
            self.screen.blit(self.title, self.title_rect)
            self.btn_iniciar.draw(self.screen)
            self.btn_ayuda.draw(self.screen)

            pygame.display.flip()
            time += 1
            self.clock.tick(60)
