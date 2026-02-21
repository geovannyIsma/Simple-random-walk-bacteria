import pygame
import random
import sys
from bacteria import Bacteria
import os
from resource_manager import ResourceManager


def generar_inicio_bacteria(ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL):
    """Genera una posición inicial para una bacteria sin verificar colisiones"""
    lado = random.choice(["arriba", "abajo", "izquierda", "derecha"])
    vertical = random.randint(0, ANCHO // TAMANO_CELDA - 1)
    horizontal = random.randint(0, ALTO // TAMANO_CELDA - 1)

    if lado == "arriba":
        return vertical * TAMANO_CELDA + MARGEN_HORIZONTAL, MARGEN_VERTICAL
    elif lado == "abajo":
        return vertical * TAMANO_CELDA + MARGEN_HORIZONTAL, ALTO + MARGEN_VERTICAL
    elif lado == "izquierda":
        return MARGEN_HORIZONTAL, horizontal * TAMANO_CELDA + MARGEN_VERTICAL
    else:
        return ANCHO + MARGEN_HORIZONTAL, horizontal * TAMANO_CELDA + MARGEN_VERTICAL


def generar_comida(num_comida, ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL):
    posiciones_comida = set()  # Usar set en lugar de lista para evitar duplicados
    intentos = 0
    max_intentos = num_comida * 10  # Límite de intentos para evitar bucles infinitos

    while len(posiciones_comida) < num_comida and intentos < max_intentos:
        # Ajustar los límites para que la comida no se genere en el borde
        x = random.randint(1, (ANCHO // TAMANO_CELDA) - 2) * TAMANO_CELDA + MARGEN_HORIZONTAL
        y = random.randint(1, (ALTO // TAMANO_CELDA) - 2) * TAMANO_CELDA + MARGEN_VERTICAL

        # Verificar que la posición está dentro del área jugable
        if (MARGEN_HORIZONTAL <= x <= ANCHO + MARGEN_HORIZONTAL - TAMANO_CELDA and
                MARGEN_VERTICAL <= y <= ALTO + MARGEN_VERTICAL - TAMANO_CELDA):
            posiciones_comida.add((x, y))
        
        intentos += 1

    # Retornar directamente el set en lugar de lista para posibilitar búsquedas O(1)
    return posiciones_comida


def esta_dentro_pantalla(x, y, MARGEN, ANCHO, ALTO, TAMANO_CELDA):
    return (MARGEN <= x <= ANCHO + MARGEN - TAMANO_CELDA and
            MARGEN <= y <= ALTO + MARGEN - TAMANO_CELDA)


def hay_colision(posicion_bacteria, posicion_comida, config):
    bx, by = posicion_bacteria
    fx, fy = posicion_comida
    # Verificar que la comida está dentro del área jugable antes de detectar colisión
    if not esta_dentro_pantalla(fx, fy, config.display.MARGEN, config.display.ANCHO, config.display.ALTO, config.display.TAMANO_CELDA):
        return False
    # Optimización: evitar usar math.sqrt comparando cuadrados
    dist_cuadrada = (bx - fx) ** 2 + (by - fy) ** 2
    return dist_cuadrada <= (config.physics.DISTANCIA_COLISION ** 2)


def dibujar_cuadricula(pantalla, config):
    for x in range(config.display.MARGEN_HORIZONTAL, config.display.ANCHO + config.display.MARGEN_HORIZONTAL + 1, config.display.TAMANO_CELDA):
        pygame.draw.line(pantalla, (50, 50, 50), (x, config.display.MARGEN_VERTICAL), (x, config.display.ALTO + config.display.MARGEN_VERTICAL))
    for y in range(config.display.MARGEN_VERTICAL, config.display.ALTO + config.display.MARGEN_VERTICAL + 1, config.display.TAMANO_CELDA):
        pygame.draw.line(pantalla, (50, 50, 50), (config.display.MARGEN_HORIZONTAL, y), (config.display.ANCHO + config.display.MARGEN_HORIZONTAL, y))


def caminar():
    orientacion = random.choice([1, -1])
    direccion = random.choice([1, -1])
    if orientacion == 1:
        return "arriba" if direccion == 1 else "abajo"
    else:
        return "derecha" if direccion == 1 else "izquierda"


def dibujar_info_debug(pantalla, ciclo, bacterias, posiciones_comida, config):
    fuente = pygame.font.SysFont("Courier New", 16)
    info_debug = [
        f"Ciclo: {ciclo + 1}/{config.simulation.num_ciclos}",
        f"Partículas: {len(bacterias)}",
        f"Comida restante: {len(posiciones_comida)}"
    ]
    for i, linea in enumerate(info_debug):
        texto = fuente.render(linea, True, (255, 255, 255))
        pantalla.blit(texto, (10, 10 + i * 20))

    # Información de bacterias en blanco
    for i, bacteria in enumerate(bacterias):
        cuenta_trazas = bacteria.trazas.get(bacteria.posicion, 0)
        info_bacteria = f"Bacteria {bacteria.id}: Vida {bacteria.vida}/{config.simulation.vida_inicial}, {'Comió' if bacteria.comio_comida else 'No comió'}, Trazas: {cuenta_trazas}"
        texto = fuente.render(info_bacteria, True, (255, 255, 255))
        pantalla.blit(texto, (10, 70 + i * 40))

        # Agregar contador de comidas y velocidad en azul
        info_stats = f"Comidas en este ciclo: {bacteria.comidas_este_ciclo} | Velocidad actual: {bacteria.velocidad}x"
        texto_stats = fuente.render(info_stats, True, (0, 191, 255))  # Azul claro
        pantalla.blit(texto_stats, (30, 90 + i * 40))

    info_parametros = [
        f"Parámetros:",
        f"Número de ciclos: {config.simulation.num_ciclos}",
        f"Vida inicial de la bacteria: {config.simulation.vida_inicial}",
        f"Número de comidas: {config.simulation.num_comida}",
        f"Número de partículas: {config.simulation.num_particulas}"
    ]
    for i, linea in enumerate(info_parametros):
        texto = fuente.render(linea, True, (255, 255, 255))
        pantalla.blit(texto, (10, config.display.ALTO_VENTANA - (len(info_parametros) - i) * 20 - 10))


def dibujar_bacteria_con_numeros(pantalla, bacterias, config):
    fuente = pygame.font.SysFont("Courier New", 16)
    for bacteria in bacterias:
        if bacteria.imagen:
            bacteria.actualizar_rect()
            pantalla.blit(bacteria.imagen, bacteria.rect)
        else:
            # Fallback al círculo si no hay imagen
            pygame.draw.circle(pantalla, config.colors.BACTERIA, bacteria.posicion, config.physics.RADIO_BACTERIA)
        
        # Dibujar el ID de la bacteria
        texto = fuente.render(str(bacteria.id), True, (255, 255, 255))
        pantalla.blit(texto, (bacteria.posicion[0] + config.physics.RADIO_BACTERIA, bacteria.posicion[1] - config.physics.RADIO_BACTERIA))


def resolver_competencia_comida(bacterias_competidoras):
    """Selecciona aleatoriamente una bacteria ganadora entre las competidoras"""
    return random.choice(bacterias_competidoras)


def dibujar_info_boxes(pantalla, ciclo, config, bacterias_vivas, num_comida_actual, resource_manager):
    """Dibuja los cuadros de información en la parte superior"""
    box_width = 150
    box_height = 40
    box_margin = 20
    icon_size = 30
    start_x = 300  # Posición inicial X ajustada
    y = config.display.MARGEN_VERTICAL // 2 - box_height // 2  # Centrado verticalmente en el margen superior
    
    # Configuración de fuente personalizada
    try:
        font_path = os.path.join(os.path.dirname(__file__), 'assets', 'fonts', 'vhs-gothic.ttf')
        fuente = pygame.font.Font(font_path, 16)
    except:
        # Fallback a la fuente del sistema si no se puede cargar la fuente personalizada
        print("No se pudo cargar la fuente VHS Gothic, usando fuente del sistema")
        fuente = pygame.font.SysFont("Courier New", 16)
    
    # Datos para los cuadros
    boxes = [
        ("cicle-icon", f"{ciclo + 1}/{config.simulation.num_ciclos}"),
        ("bacteria-icon", str(len(bacterias_vivas))),
        ("food-icon", str(num_comida_actual)),
        ("hp-icon", str(config.simulation.vida_inicial))
    ]
    
    for i, (icon_name, value) in enumerate(boxes):
        # Posición del cuadro
        box_x = start_x + (box_width + box_margin) * i
        
        # Dibujar el fondo del cuadro oscuro laboratorio
        pygame.draw.rect(pantalla, (25, 25, 30), (box_x, y, box_width, box_height))
        
        # Dibujar el borde del cuadro (color más sutil, sin brillo total)
        pygame.draw.rect(pantalla, (100, 100, 120), (box_x, y, box_width, box_height), 1)
        
        # Cargar y dibujar el icono
        icon = resource_manager.get_scaled_image(icon_name, (icon_size, icon_size))
        if icon:
            icon_x = box_x + 5
            icon_y = y + (box_height - icon_size) // 2
            pantalla.blit(icon, (icon_x, icon_y))
        
        # Dibujar el texto en colores terminal (Gris perla)
        texto = fuente.render(value, True, (200, 220, 200))
        text_x = box_x + icon_size + 10
        text_y = y + (box_height - texto.get_height()) // 2
        pantalla.blit(texto, (text_x, text_y))


def ejecutar_simulacion(pantalla, reloj, config):
    
    resource_manager = ResourceManager()
    # Aumentar el tamaño de la comida (multiplicar RADIO_COMIDA por 3 en lugar de 2)
    food_image = resource_manager.get_scaled_image('food', (config.physics.RADIO_COMIDA * 8, config.physics.RADIO_COMIDA * 8))
    
    # Crear bacterias sin verificar posiciones ocupadas
    bacterias = []
    for i in range(config.simulation.num_particulas):
        b = Bacteria(
            i + 1,
            generar_inicio_bacteria(config.display.ANCHO, config.display.ALTO, config.display.TAMANO_CELDA, config.display.MARGEN_HORIZONTAL, config.display.MARGEN_VERTICAL),
            config.simulation.vida_inicial
        )
        b.cargar_imagen(int(config.display.TAMANO_CELDA * 0.75))
        bacterias.append(b)
    
    # Imagen cargada directamente mediante el constructor y param
    # No es necesario cargar manualmente al reducir variables
    pass

    def dibujar_comida(pantalla, posiciones_comida):
        # food_image está garantizado de ser un pygame.Surface ya sea real o de fallback
        for pos in posiciones_comida:
            rect = food_image.get_rect(center=pos)
            pantalla.blit(food_image, rect)

    posiciones_comida = generar_comida(config.simulation.num_comida, config.display.ANCHO, config.display.ALTO, config.display.TAMANO_CELDA, config.display.MARGEN_HORIZONTAL, config.display.MARGEN_VERTICAL)

    ciclos_restantes = 0  # Inicializar en 0 en lugar de num_ciclos
    bacterias_iniciales = config.simulation.num_particulas
    comida_inicial = config.simulation.num_comida

    # Add HUD "Salir" Button
    from gui import LabButton
    btn_font = pygame.font.SysFont("Courier New", 18, bold=True)
    # Position top-right
    btn_salir_rect = pygame.Rect(config.display.ANCHO_VENTANA - 120, 10, 100, 30)
    btn_salir = LabButton(btn_salir_rect, "Salir", btn_font, config)

    for ciclo in range(config.simulation.num_ciclos):
        if config.debug:
            print(f"\n=== CICLO {ciclo + 1} ===")
        # Imprimir posiciones y velocidades iniciales
        print("\nPosiciones de las bacterias:")
        for bacteria in bacterias:
            print(f"Bacteria {bacteria.id}: Posición {bacteria.posicion}, Velocidad: {bacteria.velocidad}")

        # Removemos get_ticks en favor de un acumulador delta_time
        tiempo_acumulado = 0.0

        if len(bacterias) == 0:
            ciclos_restantes = config.simulation.num_ciclos - ciclo
            break

        while any(bacteria.vida > 0 for bacteria in bacterias):
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.mod & pygame.KMOD_CTRL and evento.key == pygame.K_d:
                        config.debug = not config.debug
                        
                if btn_salir.handle_event(evento):
                    return "menu"

            pantalla.fill(config.colors.FONDO)
            dibujar_cuadricula(pantalla, config)
            dibujar_comida(pantalla, posiciones_comida)

            if config.debug:
                for bacteria in bacterias:
                    for punto, cuenta in bacteria.trazas.items():
                        color = config.colors.SUPERPOSICION_TRAZA if cuenta > 1 else config.colors.TRAZA
                        pygame.draw.circle(pantalla, color, punto, 3)

            delta_time = reloj.tick(60)
            # Evitar aceleraciones bruscas si el tick inicial fue muy largo (ej. tras cargar o inicializar)
            if delta_time > 100:
                delta_time = 100
                
            tiempo_acumulado += delta_time
            
            # Update de la lógica de simulación en pasos fijos discretos
            if tiempo_acumulado >= config.physics.INTERVALO_MOVIMIENTO:
                tiempo_acumulado -= config.physics.INTERVALO_MOVIMIENTO

                # Diccionario para rastrear qué bacterias intentan comer cada comida
                competencia_comida = {}

                # Primera pasada: registrar todas las bacterias que intentan comer
                for bacteria in bacterias:
                    if bacteria.vida <= 0:
                        continue

                    posicion_anterior = bacteria.posicion
                    # Optimización: pasar lista completa y evitar recrear 'otras_bacterias' en memoria en cada iteración
                    comidas_encontradas = bacteria.mover(config, posiciones_comida, bacterias)
                    
                    # Imprimir cuando una bacteria se mueve
                    if posicion_anterior != bacteria.posicion:
                        print(f"Bacteria {bacteria.id} se movió de {posicion_anterior} a {bacteria.posicion}")
                    elif bacteria.tiempo_espera > 0:
                        print(f"Bacteria {bacteria.id} esperando en {bacteria.posicion} (tiempo de espera: {bacteria.tiempo_espera})")

                    # Registrar las comidas encontradas en el camino
                    for comida in comidas_encontradas:
                        if comida not in competencia_comida:
                            competencia_comida[comida] = []
                        competencia_comida[comida].append(bacteria)

                    # Verificar colisiones en la posición final
                    for posicion_comida in posiciones_comida:
                        if bacteria.verificar_colision(posicion_comida, config):
                            if posicion_comida not in competencia_comida:
                                competencia_comida[posicion_comida] = []
                            competencia_comida[posicion_comida].append(bacteria)

                # Segunda pasada: resolver competencias y eliminar comida
                comidas_para_eliminar = []
                for posicion_comida, bacterias_competidoras in competencia_comida.items():
                    if bacterias_competidoras:
                        # Seleccionar una bacteria ganadora
                        bacteria_ganadora = resolver_competencia_comida(bacterias_competidoras)

                        # Marcar solo la bacteria ganadora como alimentada
                        for bacteria in bacterias_competidoras:
                            if bacteria == bacteria_ganadora:
                                bacteria.comio_comida = True
                                bacteria.comidas_este_ciclo += 1
                                print(f"Bacteria {bacteria.id} comió en posición {posicion_comida}")
                                print(f"  - Comidas en este ciclo: {bacteria.comidas_este_ciclo}")
                                print(f"  - Velocidad actual: {bacteria.velocidad}")

                        comidas_para_eliminar.append(posicion_comida)

                # Eliminar las comidas consumidas mediante .discard() que es O(1) para sets
                for comida in comidas_para_eliminar:
                    posiciones_comida.discard(comida)

            pantalla.fill(config.colors.FONDO)
            dibujar_cuadricula(pantalla, config)
            dibujar_comida(pantalla, posiciones_comida)
            dibujar_bacteria_con_numeros(pantalla, bacterias, config)
            
            # Dibujar los cuadros de información siempre (en modo debug y no debug)
            bacterias_vivas = [b for b in bacterias if b.vida > 0]
            dibujar_info_boxes(pantalla, ciclo, config, bacterias_vivas, 
                             len(posiciones_comida), resource_manager)
            btn_salir.draw(pantalla)

            if config.debug:
                for bacteria in bacterias:
                    for punto, cuenta in bacteria.trazas.items():
                        color = config.colors.SUPERPOSICION_TRAZA if cuenta > 1 else config.colors.TRAZA
                        pygame.draw.circle(pantalla, color, punto, 3)
                dibujar_info_debug(pantalla, ciclo, bacterias, posiciones_comida, config)
                for bacteria in bacterias:
                    pygame.draw.circle(pantalla, (100, 100, 100), bacteria.posicion, 
                                     bacteria.campo_repulsion, 1)
            pygame.display.flip()

        # Al final de cada ciclo, antes de crear nuevas bacterias
        bacterias_sobrevivientes = []
        for bacteria in bacterias:
            if bacteria.comio_comida:
                velocidad_anterior = bacteria.velocidad
                bacteria.actualizar_velocidad()
                print(f"\nBacteria {bacteria.id} al final del ciclo:")
                print(f"  - Comió {bacteria.comidas_este_ciclo} veces")
                print(f"  - Velocidad anterior: {velocidad_anterior}")
                print(f"  - Velocidad siguiente ciclo: {bacteria.velocidad_siguiente_ciclo}")
                bacterias_sobrevivientes.append(bacteria)

        # Modificar esta sección para mantener los IDs originales
        bacterias = []
        for bacteria_anterior in bacterias_sobrevivientes:
            nueva_bacteria = Bacteria(
                bacteria_anterior.id,  # Mantener el ID original
                generar_inicio_bacteria(config.display.ANCHO, config.display.ALTO, config.display.TAMANO_CELDA, config.display.MARGEN_HORIZONTAL, config.display.MARGEN_VERTICAL),
                config.simulation.vida_inicial
            )
            nueva_bacteria.velocidad = bacteria_anterior.velocidad_siguiente_ciclo
            nueva_bacteria.velocidad_siguiente_ciclo = bacteria_anterior.velocidad_siguiente_ciclo
            nueva_bacteria.cargar_imagen(int(config.display.TAMANO_CELDA * 0.75))
            bacterias.append(nueva_bacteria)

        pygame.time.delay(500)

    # End-game display logic (Modal style rather than wiping the screen)
    fuente_grande = pygame.font.SysFont("Courier New", 32, bold=True)
    fuente_pequena = pygame.font.SysFont("Courier New", 20)
    
    # Pre-render statistics
    mensaje_estado = "AGOTAMIENTO DE RECURSOS" if len(bacterias) == 0 else "CICLO DE SIMULACION COMPLETADO"
    estadisticas = [
        mensaje_estado,
        "",
        f"Ciclos ejecutados: {config.simulation.num_ciclos - ciclos_restantes}",
        f"Poblacion inicial: {bacterias_iniciales}",
        f"Poblacion final: {len(bacterias)}",
        f"Nutrientes iniciales: {comida_inicial}",
        f"Nutrientes restantes: {len(posiciones_comida)}",
        "",
        "[PRESIONA ESC PARA SALIR]"
    ]
    
    # Calculate Modal dimensions
    modal_ancho = 500
    modal_alto = 400
    modal_x = config.display.ANCHO_VENTANA // 2 - modal_ancho // 2
    modal_y = config.display.ALTO_VENTANA // 2 - modal_alto // 2
    modal_rect = pygame.Rect(modal_x, modal_y, modal_ancho, modal_alto)

    # Creating a semi-transparent surface for the frosted glass effect
    overlay = pygame.Surface((config.display.ANCHO_VENTANA, config.display.ALTO_VENTANA))
    overlay.set_alpha(180) # Darken background
    overlay.fill((10, 10, 15))

    # Add Return Button
    from gui import LabButton
    btn_font = pygame.font.SysFont("Courier New", 24, bold=True)
    btn_rect = pygame.Rect(modal_x + modal_ancho // 2 - 120, modal_y + modal_alto - 70, 240, 40)
    btn_volver = LabButton(btn_rect, "Volver al Menu", btn_font, config)

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return "menu"
                    
            if btn_volver.handle_event(evento):
                return "menu"

        # We DO NOT call pantalla.fill(0,0,0) here, we want the frozen petri-dish underneath!
        pantalla.blit(overlay, (0, 0))
        
        # Modal Background (Terminal Style)
        pygame.draw.rect(pantalla, (25, 25, 30), modal_rect)
        pygame.draw.rect(pantalla, (100, 200, 100), modal_rect, 2) # Accent border
        
        # Internal Padding Modal Line
        inner_rect = modal_rect.inflate(-20, -20)
        pygame.draw.rect(pantalla, (50, 50, 60), inner_rect, 1)

        # Draw Statistics
        start_text_y = modal_y + 40
        for i, linea in enumerate(estadisticas):
            if i == 0: # Header
                texto = fuente_grande.render(linea, True, (150, 220, 150))
            elif i == len(estadisticas) - 1: # Footer
                texto = fuente_pequena.render(linea, True, (120, 120, 140))
            else: # Body
                texto = fuente_pequena.render(linea, True, (200, 220, 200))
                
            rect_texto = texto.get_rect(center=(config.display.ANCHO_VENTANA // 2, start_text_y + i * 30))
            pantalla.blit(texto, rect_texto)

        btn_volver.draw(pantalla)

        pygame.display.flip()
        reloj.tick(60)

