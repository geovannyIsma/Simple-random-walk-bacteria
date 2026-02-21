import pygame
from config import GameConfig

class LabButton:
    def __init__(self, rect, text, font, config: GameConfig):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.config = config
        self.is_hovered = False
        
    def draw(self, surface):
        # Intent: Clean borders-only depth structure, feeling like medical terminal.
        # Background slightly lighter than deep slate when hovering
        bg_color = (60, 60, 80) if self.is_hovered else (40, 40, 60)
        border_color = (100, 100, 140) if self.is_hovered else (70, 70, 100)
        
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
        # Text rendering (Typography priority)
        text_surface = self.font.render(self.text, True, (220, 220, 230))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

class TechnicalInput:
    def __init__(self, rect, label, initial_value, font, label_font, config: GameConfig):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.value = str(initial_value)
        self.font = font
        self.label_font = label_font
        self.config = config
        self.is_active = False
        self.is_hovered = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def draw(self, surface):
        # Draw Label (Tertiary text, metadata hierarchy)
        label_surf = self.label_font.render(self.label, True, (150, 150, 170))
        surface.blit(label_surf, (self.rect.x, self.rect.y - 25))
        
        # Draw Input Surface (Dark inset, borders-only depth)
        bg_color = (25, 25, 35)
        border_color = (120, 200, 120) if self.is_active else (80, 80, 100)
        if self.is_hovered and not self.is_active:
            border_color = (100, 100, 120)
            
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
        # Primary Value Text
        text_surf = self.font.render(self.value, True, (200, 220, 200) if self.is_active else (180, 180, 190))
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 8))
        
        # Cursor
        if self.is_active and self.cursor_visible:
            cursor_x = self.rect.x + 10 + text_surf.get_width() + 2
            pygame.draw.line(surface, (120, 200, 120), (cursor_x, self.rect.y + 8), (cursor_x, self.rect.bottom - 8), 2)
            
    def update(self, delta_time):
        if self.is_active:
            self.cursor_timer += delta_time
            if self.cursor_timer >= 500:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
        else:
            self.cursor_visible = False
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.is_active = self.rect.collidepoint(event.pos)
                if self.is_active:
                    self.cursor_visible = True
                    self.cursor_timer = 0
                    
        elif event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.unicode.isdigit():
                self.value += event.unicode
                
    def get_value(self):
        try:
            return int(self.value) if self.value else 0
        except ValueError:
            return 0
