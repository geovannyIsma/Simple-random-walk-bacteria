import pygame
from config import GameConfig
from gui import TechnicalInput, LabButton

def solicitar_datos_pygame(pantalla, config: GameConfig):
    reloj = pygame.time.Clock()
    fuente_titulo = pygame.font.SysFont("Courier New", 50, bold=True)
    fuente_input = pygame.font.SysFont("Courier New", 25)
    fuente_label = pygame.font.SysFont("Courier New", 15)
    
    ancho, alto = pantalla.get_size()
    
    # Measurements based on interface design scale (padding, symmetrical layouts)
    box_w = 280
    box_h = 45
    start_y = alto // 2 - 120
    gap = 90
    center_x = ancho // 2 - box_w // 2

    inputs = {
        "ciclos": TechnicalInput(pygame.Rect(center_x, start_y, box_w, box_h), "N° Ciclos:", 5, fuente_input, fuente_label, config),
        "vida_inicial": TechnicalInput(pygame.Rect(center_x, start_y + gap, box_w, box_h), "Vida de Bacteria Inicial:", 10, fuente_input, fuente_label, config),
        "num_comida": TechnicalInput(pygame.Rect(center_x, start_y + gap * 2, box_w, box_h), "Cantidad Inicial de Comida:", 5, fuente_input, fuente_label, config),
        "num_particulas": TechnicalInput(pygame.Rect(center_x, start_y + gap * 3, box_w, box_h), "Población Bacteriana Inicial:", 5, fuente_input, fuente_label, config)
    }

    btn_iniciar = LabButton(pygame.Rect(center_x + box_w // 2 + 10, start_y + gap * 4 + 20, 200, 50), "Inicializar Seq.", fuente_input, config)
    btn_volver = LabButton(pygame.Rect(center_x - box_w // 2 - 10, start_y + gap * 4 + 20, 200, 50), "Volver al Menu", fuente_input, config)

    corriendo = True
    resultado = None

    while corriendo:
        dt = reloj.tick(60)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return None
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return None
                
            for v in inputs.values():
                v.handle_event(evento)
                
            if btn_volver.handle_event(evento):
                return None
                
            if btn_iniciar.handle_event(evento):
                corriendo = False
                resultado = (
                    inputs["ciclos"].get_value(),
                    inputs["vida_inicial"].get_value(),
                    inputs["num_comida"].get_value(),
                    inputs["num_particulas"].get_value()
                )

        pantalla.fill((20, 20, 25))

        # Dibujar decoraciones de laboratorio (grilla sutil)
        for i in range(0, ancho, 40):
            pygame.draw.line(pantalla, (30, 30, 35), (i, 0), (i, alto))
        for j in range(0, alto, 40):
            pygame.draw.line(pantalla, (30, 30, 35), (0, j), (ancho, j))

        titulo = fuente_titulo.render("SIMULATION . CONFIGURATION", True, (150, 200, 150))
        pantalla.blit(titulo, (ancho // 2 - titulo.get_width() // 2, 80))

        for v in inputs.values():
            v.update(dt)
            v.draw(pantalla)
            
        btn_iniciar.draw(pantalla)
        btn_volver.draw(pantalla)

        pygame.display.flip()

    return resultado
