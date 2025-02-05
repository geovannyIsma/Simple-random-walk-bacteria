import pygame
import math
import random
import os
from resource_manager import ResourceManager

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
        self.running = True
        self.load_assets()
        
    def load_assets(self):
        # Configurar fuente VHS Gothic
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'fonts', 'vhs-gothic.ttf')
        try:
            self.title_font = pygame.font.Font(font_path, 72)
            self.button_font = pygame.font.Font(font_path, 36)
        except Exception as e:
            print(f"Error cargando la fuente VHS Gothic: {e}")
            pygame.quit()
            sys.exit()

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

        # Crear botón con la fuente VHS Gothic
        button_text = "Empezar"
        self.button_text = self.button_font.render(button_text, True, (255, 255, 255))
        self.button_rect = self.button_text.get_rect()
        self.button_rect.center = (screen_width // 2, screen_height * 0.7)
        
        # Título con la fuente VHS Gothic
        title_text = "Simple Random Walk Bacteria"
        self.title = self.title_font.render(title_text, True, (255, 255, 255))
        self.title_rect = self.title.get_rect(center=(screen_width // 2, screen_height * 0.3))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_rect.collidepoint(event.pos):
                    return "start"
        return True

    def run(self):
        time = 0
        while self.running:
            result = self.handle_events()
            if result == "start":
                return True
            elif result == False:
                return False

            # Actualizar animaciones
            for anim in self.animations:
                anim.update(time)

            # Dibujar
            self.screen.fill((0, 0, 0))
            
            # Dibujar animaciones
            for anim in self.animations:
                self.screen.blit(anim.image, anim.rect)
            
            # Dibujar título y botón
            self.screen.blit(self.title, self.title_rect)
            
            # Efecto hover para el botón
            if self.button_rect.collidepoint(pygame.mouse.get_pos()):
                hover_color = (150, 150, 150)
                button_hover = self.button_font.render("Empezar", True, hover_color)
                self.screen.blit(button_hover, self.button_rect)
            else:
                self.screen.blit(self.button_text, self.button_rect)

            pygame.display.flip()
            time += 1
            self.clock.tick(60)
