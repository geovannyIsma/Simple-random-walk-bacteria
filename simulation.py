import pygame
import random
import sys
from bacteria import Bacteria


def generar_inicio_bacteria(ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL):
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
    posiciones_comida = []
    while len(posiciones_comida) < num_comida:
        x = random.randint(0, ANCHO // TAMANO_CELDA - 1) * TAMANO_CELDA + MARGEN_HORIZONTAL
        y = random.randint(0, ALTO // TAMANO_CELDA - 1) * TAMANO_CELDA + MARGEN_VERTICAL
        posiciones_comida.append((x, y))
    return posiciones_comida


def esta_dentro_pantalla(x, y, MARGEN, ANCHO, ALTO):
    return MARGEN <= x < ANCHO + MARGEN and MARGEN <= y < ALTO + MARGEN


def hay_colision(posicion_bacteria, posicion_comida, DISTANCIA_COLISION):
    bx, by = posicion_bacteria
    fx, fy = posicion_comida
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
        pygame.draw.circle(pantalla, COLOR_BACTERIA, bacteria.posicion, RADIO_BACTERIA)
        texto = fuente.render(str(bacteria.id), True, (255, 255, 255))
        pantalla.blit(texto, (bacteria.posicion[0] + RADIO_BACTERIA, bacteria.posicion[1] - RADIO_BACTERIA))


def resolver_competencia_comida(bacterias_competidoras):
    """Selecciona aleatoriamente una bacteria ganadora entre las competidoras"""
    return random.choice(bacterias_competidoras)


def ejecutar_simulacion(pantalla, reloj, ANCHO, ALTO, TAMANO_CELDA, MARGEN, MARGEN_HORIZONTAL, MARGEN_VERTICAL,
                        COLOR_FONDO, COLOR_BACTERIA, COLOR_TRAZA, COLOR_SUPERPOSICION_TRAZA, COLOR_COMIDA,
                        RADIO_COMIDA, RADIO_BACTERIA, DISTANCIA_COLISION, INTERVALO_MOVIMIENTO,
                        num_ciclos, vida_inicial, num_comida, num_particulas, ALTURA_VENTANA, debug):
    bacterias = [Bacteria(i + 1, generar_inicio_bacteria(ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL),
                          vida_inicial) for i in range(num_particulas)]
    posiciones_comida = generar_comida(num_comida, ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL)

    ciclos_restantes = num_ciclos

    for ciclo in range(num_ciclos):
        print(f"\n=== CICLO {ciclo + 1} ===")
        # Imprimir velocidades iniciales
        for bacteria in bacterias:
            print(f"Bacteria {bacteria.id} inicia ciclo con velocidad: {bacteria.velocidad}")

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
            for posicion_comida in posiciones_comida:
                pygame.draw.circle(pantalla, COLOR_COMIDA, posicion_comida, RADIO_COMIDA)

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

                    # El método mover ahora devuelve las comidas encontradas en el camino
                    comidas_encontradas = bacteria.mover(TAMANO_CELDA, MARGEN, ANCHO, ALTO, posiciones_comida)
                    
                    if debug:
                        print(f"Bacteria {bacteria.id} posición: {bacteria.posicion}")

                    # Registrar las comidas encontradas en el camino
                    for comida in comidas_encontradas:
                        if comida not in competencia_comida:
                            competencia_comida[comida] = []
                        competencia_comida[comida].append(bacteria)

                    # Verificar colisiones en la posición final
                    for posicion_comida in posiciones_comida:
                        if bacteria.verificar_colision(posicion_comida, DISTANCIA_COLISION):
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
            for posicion_comida in posiciones_comida:
                pygame.draw.circle(pantalla, COLOR_COMIDA, posicion_comida, RADIO_COMIDA)
            dibujar_bacteria_con_numeros(pantalla, bacterias, COLOR_BACTERIA, RADIO_BACTERIA)
            if debug:
                for bacteria in bacterias:
                    for punto, cuenta in bacteria.trazas.items():
                        color = COLOR_SUPERPOSICION_TRAZA if cuenta > 1 else COLOR_TRAZA
                        pygame.draw.circle(pantalla, color, punto, 3)
                dibujar_info_debug(pantalla, ciclo, bacterias, posiciones_comida,
                                   num_ciclos, vida_inicial, num_comida, num_particulas, ALTURA_VENTANA)
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

        # Crear nuevas bacterias manteniendo las propiedades de las sobrevivientes
        bacterias = []
        for i, bacteria_anterior in enumerate(bacterias_sobrevivientes):
            nueva_bacteria = Bacteria(i + 1, 
                generar_inicio_bacteria(ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL),
                vida_inicial)
            nueva_bacteria.velocidad = bacteria_anterior.velocidad_siguiente_ciclo  # Usar la velocidad siguiente
            nueva_bacteria.velocidad_siguiente_ciclo = bacteria_anterior.velocidad_siguiente_ciclo
            bacterias.append(nueva_bacteria)

        pygame.time.delay(500)

    if len(bacterias) == 0:
        fuente_grande = pygame.font.SysFont("Courier New", 36)
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
            
            # Mensaje principal
            mensaje = f"No hay bacterias vivas. {ciclos_restantes} ciclos no se ejecutaron."
            texto = fuente_grande.render(mensaje, True, (255, 255, 255))
            rect_texto = texto.get_rect(center=(1280 // 2, 800 // 2))
            pantalla.blit(texto, rect_texto)
            
            # Mensaje ESC
            mensaje_esc = "ESC: Salir"
            texto_esc = fuente_pequena.render(mensaje_esc, True, (255, 255, 255))
            rect_esc = texto_esc.get_rect(bottomright=(1280 - 20, 800 - 20))
            pantalla.blit(texto_esc, rect_esc)
            
            pygame.display.flip()
            reloj.tick(60)

    pygame.quit()
