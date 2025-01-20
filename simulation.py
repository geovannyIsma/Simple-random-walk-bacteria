import pygame
import random
import sys

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

def dibujar_info_debug(pantalla, ciclo, posiciones_bacteria, pasos_movidos, comio_comida, trazas, posiciones_comida, num_ciclos,
                    vida_inicial, num_comida, num_particulas, ALTURA_VENTANA):
    fuente = pygame.font.SysFont("Courier New", 16)
    info_debug = [
        f"Ciclo: {ciclo + 1}/{num_ciclos}",
        f"Partículas: {len(posiciones_bacteria)}",
        f"Comida restante: {len(posiciones_comida)}"
    ]
    for i, (pos, pasos, comio) in enumerate(zip(posiciones_bacteria, pasos_movidos, comio_comida)):
        cuenta_trazas = trazas[i].get(pos, 0)
        info_debug.append(
            f"Bacteria {i + 1}: Vida {pasos}/{vida_inicial}, {'Comió' if comio else 'No comió'}, Trazas: {cuenta_trazas}")

    for i, linea in enumerate(info_debug):
        texto = fuente.render(linea, True, (255, 255, 255))
        pantalla.blit(texto, (10, 10 + i * 20))

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

def dibujar_bacteria_con_numeros(pantalla, posiciones_bacteria, numeros_bacteria, COLOR_BACTERIA, RADIO_BACTERIA):
    fuente = pygame.font.SysFont("Courier New", 16)
    for i, posicion_bacteria in enumerate(posiciones_bacteria):
        pygame.draw.circle(pantalla, COLOR_BACTERIA, posicion_bacteria, RADIO_BACTERIA)
        texto = fuente.render(str(numeros_bacteria[i]), True, (255, 255, 255))
        pantalla.blit(texto, (posicion_bacteria[0] + RADIO_BACTERIA, posicion_bacteria[1] - RADIO_BACTERIA))

def ejecutar_simulacion(pantalla, reloj, ANCHO, ALTO, TAMANO_CELDA, MARGEN, MARGEN_HORIZONTAL, MARGEN_VERTICAL,
                   COLOR_FONDO, COLOR_BACTERIA, COLOR_TRAZA, COLOR_SUPERPOSICION_TRAZA, COLOR_COMIDA,
                   RADIO_COMIDA, RADIO_BACTERIA, DISTANCIA_COLISION, INTERVALO_MOVIMIENTO,
                   num_ciclos, vida_inicial, num_comida, num_particulas, ALTURA_VENTANA, debug):
    posiciones_bacteria = [generar_inicio_bacteria(ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL) for _ in
                          range(num_particulas)]
    numeros_bacteria = list(range(1, num_particulas + 1))
    trazas = [{pos: 1} for pos in posiciones_bacteria]
    bacterias_sobrevivientes = [True] * num_particulas

    posiciones_comida = generar_comida(num_comida, ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL)
    
    ciclos_restantes = num_ciclos

    for ciclo in range(num_ciclos):
        ultimo_tiempo_movimiento = pygame.time.get_ticks()
        pasos_movidos = [0] * len(posiciones_bacteria)
        comio_comida = [False] * len(posiciones_bacteria)

        if len(posiciones_bacteria) == 0:
            ciclos_restantes = num_ciclos - ciclo
            break

        while any(pasos < vida_inicial for pasos in pasos_movidos):
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
                for traza in trazas:
                    for punto, cuenta in traza.items():
                        color = COLOR_SUPERPOSICION_TRAZA if cuenta > 1 else COLOR_TRAZA
                        pygame.draw.circle(pantalla, color, punto, 3)

            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - ultimo_tiempo_movimiento >= INTERVALO_MOVIMIENTO:
                ultimo_tiempo_movimiento = tiempo_actual

                for i, posicion_bacteria in enumerate(posiciones_bacteria):
                    if pasos_movidos[i] >= vida_inicial or not bacterias_sobrevivientes[i]:
                        continue

                    x, y = posicion_bacteria
                    movimiento = caminar()

                    if movimiento == "arriba":
                        y -= TAMANO_CELDA
                    elif movimiento == "abajo":
                        y += TAMANO_CELDA
                    elif movimiento == "derecha":
                        x += TAMANO_CELDA
                    else:
                        x -= TAMANO_CELDA

                    nueva_posicion = (x, y)

                    if esta_dentro_pantalla(*nueva_posicion, MARGEN, ANCHO, ALTO):
                        posiciones_bacteria[i] = nueva_posicion
                        pasos_movidos[i] += 1

                        if debug:
                            print(f"Bacteria {i} posición: {posiciones_bacteria[i]}")

                        if nueva_posicion in trazas[i]:
                            trazas[i][nueva_posicion] += 1
                        else:
                            trazas[i][nueva_posicion] = 1

                    for posicion_comida in posiciones_comida:
                        if hay_colision(posiciones_bacteria[i], posicion_comida, DISTANCIA_COLISION):
                            comio_comida[i] = True
                            posiciones_comida.remove(posicion_comida)
                            break

            pantalla.fill(COLOR_FONDO)
            dibujar_cuadricula(pantalla, ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL)
            for posicion_comida in posiciones_comida:
                pygame.draw.circle(pantalla, COLOR_COMIDA, posicion_comida, RADIO_COMIDA)
            dibujar_bacteria_con_numeros(pantalla, posiciones_bacteria, numeros_bacteria, COLOR_BACTERIA, RADIO_BACTERIA)
            if debug:
                for traza in trazas:
                    for punto, cuenta in traza.items():
                        color = COLOR_SUPERPOSICION_TRAZA if cuenta > 1 else COLOR_TRAZA
                        pygame.draw.circle(pantalla, color, punto, 3)
                dibujar_info_debug(pantalla, ciclo, posiciones_bacteria, pasos_movidos, comio_comida, trazas, posiciones_comida,
                                num_ciclos, vida_inicial, num_comida, num_particulas, ALTURA_VENTANA)
            pygame.display.flip()
            reloj.tick(60)

        for i in range(len(posiciones_bacteria)):
            if not comio_comida[i]:
                bacterias_sobrevivientes[i] = False

        posiciones_bacteria = [generar_inicio_bacteria(ANCHO, ALTO, TAMANO_CELDA, MARGEN_HORIZONTAL, MARGEN_VERTICAL) for
                              i, pos in enumerate(posiciones_bacteria) if bacterias_sobrevivientes[i]]
        numeros_bacteria = [num for i, num in enumerate(numeros_bacteria) if bacterias_sobrevivientes[i]]
        trazas = [{pos: 1} for pos in posiciones_bacteria]
        bacterias_sobrevivientes = [True] * len(posiciones_bacteria)

        pygame.time.delay(500)

    if len(posiciones_bacteria) == 0:
        fuente = pygame.font.SysFont("Courier New", 36)
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pantalla.fill((0, 0, 0))
            mensaje = f"No hay bacterias vivas. {ciclos_restantes} ciclos no se ejecutaron."
            texto = fuente.render(mensaje, True, (255, 255, 255))
            pantalla.blit(texto, (50, ALTURA_VENTANA // 2))
            pygame.display.flip()
            reloj.tick(60)

    pygame.quit()
    