import pygame
import os

class ResourceManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not ResourceManager._initialized:
            self.images = {}
            self.load_resources()
            ResourceManager._initialized = True

    def load_resources(self):
        """Carga todas las imágenes necesarias una sola vez"""
        base_path = os.path.join(os.path.dirname(__file__), 'assets')
        
        try:
            # Cargar imagen de bacteria
            bacteria_path = os.path.join(base_path, 'bacteria.png')
            if os.path.exists(bacteria_path):
                self.images['bacteria'] = pygame.image.load(bacteria_path).convert_alpha()
            
            # Cargar imagen de comida
            food_path = os.path.join(base_path, 'food.png')
            if os.path.exists(food_path):
                self.images['food'] = pygame.image.load(food_path).convert_alpha()

            # New icon loads
            icons = ['cicle-icon', 'bacteria-icon', 'food-icon', 'hp-icon']
            for icon_name in icons:
                icon_path = os.path.join(base_path, f'{icon_name}.png')
                if os.path.exists(icon_path):
                    self.images[icon_name] = pygame.image.load(icon_path).convert_alpha()
                else:
                    print(f"Warning: Could not load {icon_name}")
                    
        except pygame.error as e:
            print(f"Error al cargar recursos: {e}")

    def get_scaled_image(self, key, size):
        """Obtiene una versión escalada de la imagen, cacheando el resultado"""
        cache_key = f"{key}_{size[0]}_{size[1]}"
        if cache_key not in self.images:
            original = self.images.get(key)
            if original:
                self.images[cache_key] = pygame.transform.scale(original, size)
            else:
                return None
        return self.images[cache_key]
