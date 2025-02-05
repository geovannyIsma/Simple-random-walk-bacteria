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

    # Convertir el set a lista antes de retornar
    return list(posiciones_comida)


def esta_dentro_pantalla(x, y, MARGEN, ANCHO, ALTO, TAMANO_CELDA):
    return (MARGEN <= x <= ANCHO + MARGEN - TAMANO_CELDA and
            MARGEN <= y <= ALTO + MARGEN - TAMANO_CELDA)


def hay_colision(posicion_bacteria, posicion_comida, DISTANCIA_COLISION, MARGEN, ANCHO, ALTO, TAMANO_CELDA):
    bx, by = posicion_bacteria
    fx, fy = posicion_comida
    # Verificar que la comida está dentro del área jugable antes de detectar colisión
    if not esta_dentro_pantalla(fx, fy, MARGEN, ANCHO, ALTO, TAMANO_CELDA):
        return False
    distancia = ((bx - fx) ** 2 + (by - fy) ** 2) ** 0.5
    return distancia <= DISTANCIA_COLISION


def dibujar_cuadricula(pantalla, ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL):
    for x in range(MARGEN_HORIZONTAL, ANCHO + MARGEN_HORIZONTAL + 1, TAMANO_CELDA):
        pygame.draw.line(pantalla, (50, 50, 50), (x, MARGEN_VERTICAL), (x, ALTO + MARGEN_VERTICAL))
    for y in range(MARGEN_VERTICAL, ALTO + MARGEN_VERTICAL + 1, TAMANO_CELDA):
        pygame.draw.line(pantalla, (50, 50, 50), (MARGEN_HORIZONTAL, y), (ANCHO + MARGEN_HORIZONTAL, y))


def caminar():
    orientacion = random.choice([1, -1])
    direccion = random.choice([1, -1])
    if orientacion == 1:
        return "arriba" if direccion == 1 else "abajo"
    else:
        return "derecha" if direccion == 1 else "izquierda"


def dibujar_info_debug(pantalla, ciclo, bacterias, posiciones_comida, num_ciclos,
                       vida_inicial, num_comida, num_particulas, ALTURA_VENTANA):
    fuente = pygame.font.SysFont("Courier New", 16)
    info_debug = [
        f"Ciclo: {ciclo + 1}/{num_ciclos}",
        f"Partículas: {len(bacterias)}",
        f"Comida restante: {len(posiciones_comida)}"
    ]
    for i, linea in enumerate(info_debug):
        texto = fuente.render(linea, True, (255, 255, 255))
        pantalla.blit(texto, (10, 10 + i * 20))

    # Información de bacterias en blanco
    for i, bacteria in enumerate(bacterias):
        cuenta_trazas = bacteria.trazas.get(bacteria.posicion, 0)
        info_bacteria = f"Bacteria {bacteria.id}: Vida {bacteria.vida}/{vida_inicial}, {'Comió' if bacteria.comio_comida else 'No comió'}, Trazas: {cuenta_trazas}"
        texto = fuente.render(info_bacteria, True, (255, 255, 255))
        pantalla.blit(texto, (10, 70 + i * 40))

        # Agregar contador de comidas y velocidad en azul
        info_stats = f"Comidas en este ciclo: {bacteria.comidas_este_ciclo} | Velocidad actual: {bacteria.velocidad}x"
        texto_stats = fuente.render(info_stats, True, (0, 191, 255))  # Azul claro
        pantalla.blit(texto_stats, (30, 90 + i * 40))

    info_parametros = [
        f"Parámetros:",
        f"Número de ciclos: {num_ciclos}",
        f"Vida inicial de la bacteria: {vida_inicial}",
        f"Número de comidas: {num_comida}",
        f"Número de partículas: {num_particulas}"
    ]
    for i, linea in enumerate(info_parametros):
        texto = fuente.render(linea, True, (255, 255, 255))
        pantalla.blit(texto, (10, ALTURA_VENTANA - (len(info_parametros) - i) * 20 - 10))


def dibujar_bacteria_con_numeros(pantalla, bacterias, COLOR_BACTERIA, RADIO_BACTERIA):
    fuente = pygame.font.SysFont("Courier New", 16)
    for bacteria in bacterias:
        if bacteria.imagen:
            bacteria.actualizar_rect()
            pantalla.blit(bacteria.imagen, bacteria.rect)
        else:
            # Fallback al círculo si no hay imagen
            pygame.draw.circle(pantalla, COLOR_BACTERIA, bacteria.posicion, RADIO_BACTERIA)
        
        # Dibujar el ID de la bacteria
        texto = fuente.render(str(bacteria.id), True, (255, 255, 255))
        pantalla.blit(texto, (bacteria.posicion[0] + RADIO_BACTERIA, bacteria.posicion[1] - RADIO_BACTERIA))


def resolver_competencia_comida(bacterias_competidoras):
    """Selecciona aleatoriamente una bacteria ganadora entre las competidoras"""
    return random.choice(bacterias_competidoras)


def dibujar_info_boxes(pantalla, ciclo, num_ciclos, bacterias_vivas, num_comida_actual, vida_inicial, resource_manager, MARGEN_VERTICAL):
    """Dibuja los cuadros de información en la parte superior"""
    box_width = 150
    box_height = 40
    box_margin = 20
    icon_size = 30
    start_x = 300  # Posición inicial X ajustada
    y = MARGEN_VERTICAL // 2 - box_height // 2  # Centrado verticalmente en el margen superior
    
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
        ("cicle-icon", f"{ciclo + 1}/{num_ciclos}"),
        ("bacteria-icon", str(len(bacterias_vivas))),
        ("food-icon", str(num_comida_actual)),
        ("hp-icon", str(vida_inicial))
    ]
    
    for i, (icon_name, value) in enumerate(boxes):
        # Posición del cuadro
        box_x = start_x + (box_width + box_margin) * i
        
        # Dibujar el borde del cuadro
        pygame.draw.rect(pantalla, (255, 255, 255), (box_x, y, box_width, box_height), 1)
        
        # Cargar y dibujar el icono
        icon = resource_manager.get_scaled_image(icon_name, (icon_size, icon_size))
        if icon:
            icon_x = box_x + 5
            icon_y = y + (box_height - icon_size) // 2
            pantalla.blit(icon, (icon_x, icon_y))
        
        # Dibujar el texto
        texto = fuente.render(value, True, (255, 255, 255))
        text_x = box_x + icon_size + 10
        text_y = y + (box_height - texto.get_height()) // 2
        pantalla.blit(texto, (text_x, text_y))


def ejecutar_simulacion(pantalla, reloj, ANCHO, ALTO, TAMANO_CELDA, MARGEN, MARGEN_HORIZONTAL, MARGEN_VERTICAL,
                        COLOR_FONDO, COLOR_BACTERIA, COLOR_TRAZA, COLOR_SUPERPOSICION_TRAZA, COLOR_COMIDA,
                        RADIO_COMIDA, RADIO_BACTERIA, DISTANCIA_COLISION, INTERVALO_MOVIMIENTO,
                        num_ciclos, vida_inicial, num_comida, num_particulas, ALTURA_VENTANA, ANCHO_VENTANA, debug):
    
    resource_manager = ResourceManager()
    # Aumentar el tamaño de la comida (multiplicar RADIO_COMIDA por 3 en lugar de 2)
    food_image = resource_manager.get_scaled_image('food', (RADIO_COMIDA * 8, RADIO_COMIDA * 8))
    
    # Crear bacterias sin verificar posiciones ocupadas
    bacterias = [
        Bacteria(
            i + 1,
            generar_inicio_bacteria(ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL),
            vida_inicial
        ) for i in range(num_particulas)
    ]
    
    # Cargar imagen para cada bacteria con tamaño reducido
    for bacteria in bacterias:
        bacteria.cargar_imagen(int(TAMANO_CELDA * 0.75))  # Reducir el tamaño al 75%

    # Modificar la función para dibujar comida
    def dibujar_comida(pantalla, posiciones_comida):
        if food_image:
            for pos in posiciones_comida:
                rect = food_image.get_rect(center=pos)
                pantalla.blit(food_image, rect)
        else:
            for pos in posiciones_comida:
                pygame.draw.circle(pantalla, COLOR_COMIDA, pos, RADIO_COMIDA)

    posiciones_comida = generar_comida(num_comida, ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL)

    ciclos_restantes = 0  # Inicializar en 0 en lugar de num_ciclos
    bacterias_iniciales = num_particulas
    comida_inicial = num_comida

    for ciclo in range(num_ciclos):
        print(f"\n=== CICLO {ciclo + 1} ===")
        # Imprimir posiciones y velocidades iniciales
        print("\nPosiciones de las bacterias:")
        for bacteria in bacterias:
            print(f"Bacteria {bacteria.id}: Posición {bacteria.posicion}, Velocidad: {bacteria.velocidad}")

        ultimo_tiempo_movimiento = pygame.time.get_ticks()

        if len(bacterias) == 0:
            ciclos_restantes = num_ciclos - ciclo
            break

        while any(bacteria.vida > 0 for bacteria in bacterias):
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.mod & pygame.KMOD_CTRL and evento.key == pygame.K_d:
                        debug = not debug

            pantalla.fill(COLOR_FONDO)
            dibujar_cuadricula(pantalla, ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL)
            dibujar_comida(pantalla, posiciones_comida)

            if debug:
                for bacteria in bacterias:
                    for punto, cuenta in bacteria.trazas.items():
                        color = COLOR_SUPERPOSICION_TRAZA if cuenta > 1 else COLOR_TRAZA
                        pygame.draw.circle(pantalla, color, punto, 3)

            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - ultimo_tiempo_movimiento >= INTERVALO_MOVIMIENTO:
                ultimo_tiempo_movimiento = tiempo_actual

                # Diccionario para rastrear qué bacterias intentan comer cada comida
                competencia_comida = {}

                # Primera pasada: registrar todas las bacterias que intentan comer
                for bacteria in bacterias:
                    if bacteria.vida <= 0:
                        continue

                    posicion_anterior = bacteria.posicion
                    # Pasar todas las bacterias excepto la actual como otras_bacterias
                    otras_bacterias = [b for b in bacterias if b.id != bacteria.id]
                    comidas_encontradas = bacteria.mover(TAMANO_CELDA, MARGEN, ANCHO, ALTO, posiciones_comida, otras_bacterias)
                    
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
                        if bacteria.verificar_colision(posicion_comida, DISTANCIA_COLISION, MARGEN, ANCHO, ALTO,
                                                       TAMANO_CELDA):
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

                # Eliminar las comidas consumidas
                for comida in comidas_para_eliminar:
                    if comida in posiciones_comida:
                        posiciones_comida.remove(comida)

            pantalla.fill(COLOR_FONDO)
            dibujar_cuadricula(pantalla, ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL)
            dibujar_comida(pantalla, posiciones_comida)
            dibujar_bacteria_con_numeros(pantalla, bacterias, COLOR_BACTERIA, RADIO_BACTERIA)
            
            # Dibujar los cuadros de información siempre (en modo debug y no debug)
            bacterias_vivas = [b for b in bacterias if b.vida > 0]
            dibujar_info_boxes(pantalla, ciclo, num_ciclos, bacterias_vivas, 
                             len(posiciones_comida), vida_inicial, resource_manager, 
                             MARGEN_VERTICAL)

            if debug:
                for bacteria in bacterias:
                    for punto, cuenta in bacteria.trazas.items():
                        color = COLOR_SUPERPOSICION_TRAZA if cuenta > 1 else COLOR_TRAZA
                        pygame.draw.circle(pantalla, color, punto, 3)
                dibujar_info_debug(pantalla, ciclo, bacterias, posiciones_comida,
                                   num_ciclos, vida_inicial, num_comida, num_particulas, ALTURA_VENTANA)
                for bacteria in bacterias:
                    pygame.draw.circle(pantalla, (100, 100, 100), bacteria.posicion, 
                                     bacteria.campo_repulsion, 1)
            pygame.display.flip()
            reloj.tick(60)

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
                generar_inicio_bacteria(ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL),
                vida_inicial
            )
            nueva_bacteria.velocidad = bacteria_anterior.velocidad_siguiente_ciclo
            nueva_bacteria.velocidad_siguiente_ciclo = bacteria_anterior.velocidad_siguiente_ciclo
            nueva_bacteria.cargar_imagen(TAMANO_CELDA)  # Cargar la imagen para la nueva bacteria
            bacterias.append(nueva_bacteria)

        pygame.time.delay(500)

    # Modificar la condición para mostrar la pantalla final
    fuente_grande = pygame.font.SysFont("Courier New", 32)
    fuente_pequena = pygame.font.SysFont("Courier New", 24)
    
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pantalla.fill((0, 0, 0))

        # Estadísticas finales
        mensaje_estado = "No hay bacterias vivas." if len(bacterias) == 0 else "Simulación completada."
        estadisticas = [
            mensaje_estado,
            f"Ciclos ejecutados: {num_ciclos - ciclos_restantes}",
            f"Ciclos no ejecutados: {ciclos_restantes}",
            f"Bacterias iniciales: {bacterias_iniciales}",
            f"Bacterias finales: {len(bacterias)}",
            f"Comida inicial: {comida_inicial}",
            f"Comida restante: {len(posiciones_comida)}",
            "",
            "Presiona ESC para salir"
        ]

        # Mostrar cada línea de estadísticas
        for i, linea in enumerate(estadisticas):
            texto = fuente_grande.render(linea, True, (255, 255, 255))
            rect_texto = texto.get_rect(center=(ANCHO_VENTANA // 2, 200 + i * 50))
            pantalla.blit(texto, rect_texto)

        pygame.display.flip()
        reloj.tick(60)

