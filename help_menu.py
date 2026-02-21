import pygame
import sys
from resource_manager import ResourceManager
from config import GameConfig
from gui import LabButton

def mostrar_pantalla_ayuda(pantalla, config: GameConfig):
    reloj = pygame.time.Clock()
    resource_manager = ResourceManager()
    
    fuente_titulo = pygame.font.SysFont("Courier New", 42, bold=True)
    fuente_texto = pygame.font.SysFont("Courier New", 20)
    fuente_leyenda = pygame.font.SysFont("Courier New", 18)
    
    ancho, alto = pantalla.get_size()
    
    btn_volver = LabButton(pygame.Rect(ancho // 2 - 100, alto - 80, 200, 40), "Volver al Menu", fuente_texto, config)
    
    # Textos de descripción
    descripcion = [
        "SISTEMA DE DIAGNÓSTICO BACTERIANO v2.0",
        "",
        "Este entorno de laboratorio simula el comportamiento",
        "de bacterias basándose en un 'Random Walk'. Cada",
        "ente (bacteria) se desplaza erráticamente buscando",
        "nutrientes para sobrevivir."
    ]
    
    # Leyenda de Sprites
    leyenda = [
        ("bacteria", "Bacteria - Se mueve y consume comida."),
        ("food", "Nutriente - Restaura vida."),
        ("hp-icon", "Puntos de Vida (HP) del cultivo."),
        ("cicle-icon", "Ciclos de Tiempo restantes.")
    ]
    
    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return
            if btn_volver.handle_event(evento):
                return
                
        # Dibujar UI
        pantalla.fill((20, 20, 25))
        
        # Grilla sutil
        for i in range(0, ancho, 40):
            pygame.draw.line(pantalla, (30, 30, 35), (i, 0), (i, alto))
        for j in range(0, alto, 40):
            pygame.draw.line(pantalla, (30, 30, 35), (0, j), (ancho, j))
            
        # Draw text description
        start_y = 60
        for i, linea in enumerate(descripcion):
            color = (150, 200, 150) if i == 0 else (200, 220, 200)
            render_texto = (fuente_titulo if i == 0 else fuente_texto).render(linea, True, color)
            rect = render_texto.get_rect(center=(ancho // 2, start_y + i * 35))
            pantalla.blit(render_texto, rect)
            
        # Draw Sprite Legend
        legend_start_y = 300
        legend_x = ancho // 2 - 250
        
        render_leyenda = fuente_texto.render("DIAGNÓSTICO REGISTRADO (KEY):", True, (150, 150, 170))
        pantalla.blit(render_leyenda, (legend_x, legend_start_y))
        
        for i, (sprite_name, desc_text) in enumerate(leyenda):
            y_pos = legend_start_y + 45 + (i * 60)
            
            # Dibujar Caja
            pygame.draw.rect(pantalla, (25, 25, 30), (legend_x, y_pos, 500, 50))
            pygame.draw.rect(pantalla, (100, 100, 120), (legend_x, y_pos, 500, 50), 1)
            
            # Dibujar icono
            imagen = resource_manager.get_scaled_image(sprite_name, (32, 32))
            if imagen:
                pantalla.blit(imagen, (legend_x + 10, y_pos + 9))
                
            # Dibujar Texto
            texto = fuente_leyenda.render(desc_text, True, (200, 220, 200))
            pantalla.blit(texto, (legend_x + 60, y_pos + 16))

        btn_volver.draw(pantalla)
        
        pygame.display.flip()
        reloj.tick(60)
