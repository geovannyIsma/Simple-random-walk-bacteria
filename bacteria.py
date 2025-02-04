import random
import math
import pygame  # Importar pygame para manejar imágenes


class Bacteria:
    def __init__(self, id, posicion, vida_inicial):
        self.id = id
        self.posicion = posicion
        self.vida = vida_inicial
        self.trazas = {posicion: 1}
        self.comio_comida = False
        self.comidas_este_ciclo = 0
        self.velocidad = 1
        self.velocidad_siguiente_ciclo = 1  # Nueva variable para controlar el aumento
        self.comidas_registradas = set()  # Nuevo: para evitar contar la misma comida múltiples veces
        self.tiempo_espera = 0  # Nuevo: contador de tiempo de espera
        self.direccion_inicial = None  # Nueva variable para recordar la dirección inicial
        self.campo_repulsion = 30  # Radio del campo de repulsión
        self.fuerza_repulsion = 1.5  # Factor de fuerza de repulsión
        self.ultima_celda = None  # Para tracking de cuadrícula
        self.imagen = None  # Nueva propiedad para la imagen
        self.rect = None    # Nueva propiedad para el rectángulo de la imagen

    def cargar_imagen(self, ruta_imagen, tamano):
        """Carga y escala la imagen de la bacteria"""
        try:
            imagen_original = pygame.image.load(ruta_imagen).convert_alpha()
            self.imagen = pygame.transform.scale(imagen_original, (tamano, tamano))
            self.rect = self.imagen.get_rect(center=self.posicion)
        except pygame.error as e:
            print(f"No se pudo cargar la imagen: {e}")
            self.imagen = None

    def actualizar_rect(self):
        """Actualiza la posición del rectángulo de la imagen"""
        if self.rect:
            self.rect.center = self.posicion

    def detectar_comida_en_linea(self, posiciones_comida, rango_deteccion):
        """Detecta comida en líneas horizontales y verticales"""
        x, y = self.posicion
        comida_mas_cercana = None
        distancia_minima = float('inf')

        for comida in posiciones_comida:
            fx, fy = comida
            # Verifica si la comida está alineada horizontal o verticalmente
            if x == fx or y == fy:
                distancia = abs(x - fx) + abs(y - fy)  # Distancia Manhattan
                if distancia <= rango_deteccion and distancia < distancia_minima:
                    distancia_minima = distancia
                    comida_mas_cercana = comida

        return comida_mas_cercana

    def verificar_comida_en_trayectoria(self, inicio, fin, posiciones_comida, DISTANCIA_COLISION, MARGEN, ANCHO, ALTO,
                                        TAMANO_CELDA):
        x1, y1 = inicio
        x2, y2 = fin
        comidas_encontradas = []

        # Verificar todas las posiciones intermedias en el camino
        if x1 == x2:  # Movimiento vertical
            paso = TAMANO_CELDA if y2 > y1 else -TAMANO_CELDA
            for y in range(int(y1), int(y2) + (1 if y2 > y1 else -1), paso):
                for comida in posiciones_comida:
                    fx, fy = comida
                    if abs(x1 - fx) <= DISTANCIA_COLISION and abs(y - fy) <= DISTANCIA_COLISION:
                        if comida not in comidas_encontradas:
                            comidas_encontradas.append(comida)
        elif y1 == y2:  # Movimiento horizontal
            paso = TAMANO_CELDA if x2 > x1 else -TAMANO_CELDA
            for x in range(int(x1), int(x2) + (1 if x2 > x1 else -1), paso):
                for comida in posiciones_comida:
                    fx, fy = comida
                    if abs(x - fx) <= DISTANCIA_COLISION and abs(y1 - fy) <= DISTANCIA_COLISION:
                        if comida not in comidas_encontradas:
                            comidas_encontradas.append(comida)

        return comidas_encontradas

    def predecir_colision_con_bacterias(self, nueva_posicion, otras_bacterias):
        """Verifica si alguna otra bacteria se encuentra o se moverá a la nueva posición"""
        if not otras_bacterias:
            return False
            
        x, y = nueva_posicion
        margen_seguridad = 20 + (self.tiempo_espera * 5)  # Reducido el factor de incremento
        
        for otra in otras_bacterias:
            ox, oy = otra.posicion
            distancia = ((x - ox) ** 2 + (y - oy) ** 2) ** 0.5
            if distancia < margen_seguridad:
                return True
        return False

    def obtener_direccion_opuesta(self, direccion):
        """Retorna la dirección opuesta a la dada"""
        opuestos = {
            "arriba": "abajo",
            "abajo": "arriba",
            "izquierda": "derecha",
            "derecha": "izquierda"
        }
        return opuestos.get(direccion)

    def calcular_fuerzas_repulsion(self, otras_bacterias, TAMANO_CELDA):
        """Calcula las fuerzas de repulsión de otras bacterias"""
        fx = fy = 0
        x, y = self.posicion
        
        for otra in otras_bacterias:
            if otra.id == self.id:
                continue
                
            ox, oy = otra.posicion
            dx = x - ox
            dy = y - oy
            distancia = math.sqrt(dx*dx + dy*dy)
            
            if distancia < self.campo_repulsion:
                # Fuerza inversamente proporcional al cuadrado de la distancia
                fuerza = (self.campo_repulsion - distancia) * self.fuerza_repulsion
                # Evitar división por cero
                if distancia > 0:
                    fx += (dx/distancia) * fuerza
                    fy += (dy/distancia) * fuerza
        
        return fx, fy

    def obtener_celda_actual(self, TAMANO_CELDA):
        """Retorna la celda de la cuadrícula en la que está la bacteria"""
        x, y = self.posicion
        celda_x = x // TAMANO_CELDA
        celda_y = y // TAMANO_CELDA
        return (celda_x, celda_y)

    def mover(self, TAMANO_CELDA, MARGEN, ANCHO, ALTO, posiciones_comida=None, otras_bacterias=None):
        x, y = self.posicion
        comidas_encontradas = []
        
        # Asegurar dirección inicial correcta
        if self.direccion_inicial is None:
            # Asignar dirección inicial basada en la posición de aparición
            if y == MARGEN:  # Apareció arriba
                self.direccion_inicial = "abajo"
            elif y >= ALTO + MARGEN:  # Apareció abajo
                self.direccion_inicial = "arriba"
            elif x == MARGEN:  # Apareció a la izquierda
                self.direccion_inicial = "derecha"
            else:  # Apareció a la derecha
                self.direccion_inicial = "izquierda"
            
            # Realizar el primer movimiento en la dirección inicial
            dx = dy = 0
            if self.direccion_inicial in ["izquierda", "derecha"]:
                dx = 1 if self.direccion_inicial == "derecha" else -1
            else:
                dy = 1 if self.direccion_inicial == "abajo" else -1
                
        else:
            # Comportamiento normal después del primer movimiento
            direcciones_posibles = ["horizontal", "vertical"]
            direccion_principal = random.choice(direcciones_posibles)
            
            dx = dy = 0
            
            # Detectar comida cercana
            if posiciones_comida:
                comida_objetivo = self.detectar_comida_en_linea(posiciones_comida, TAMANO_CELDA * 7)
                if comida_objetivo:
                    fx, fy = comida_objetivo
                    if abs(x - fx) > abs(y - fy):
                        direccion_principal = "horizontal"
                        dx = 1 if fx > x else -1
                    else:
                        direccion_principal = "vertical"
                        dy = 1 if fy > y else -1
            
            # Si no hay comida o no se decidió dirección, mover aleatoriamente
            if dx == 0 and dy == 0:
                if direccion_principal == "horizontal":
                    dx = random.choice([-1, 1])
                else:
                    dy = random.choice([-1, 1])

        # Calcular nueva posición
        velocidad_efectiva = TAMANO_CELDA * self.velocidad
        nueva_x = x + dx * velocidad_efectiva
        nueva_y = y + dy * velocidad_efectiva

        # Limitar al área de juego
        nueva_x = max(MARGEN, min(ANCHO + MARGEN - TAMANO_CELDA, nueva_x))
        nueva_y = max(MARGEN, min(ALTO + MARGEN - TAMANO_CELDA, nueva_y))

        # Verificar colisiones con otras bacterias
        puede_moverse = True
        if otras_bacterias:
            for otra in otras_bacterias:
                if otra.id != self.id:
                    dist = math.sqrt((nueva_x - otra.posicion[0])**2 + (nueva_y - otra.posicion[1])**2)
                    if dist < TAMANO_CELDA:
                        puede_moverse = False
                        break

        if puede_moverse:
            # Verificar comida en el camino
            if posiciones_comida:
                comidas_en_camino = self.verificar_comida_en_trayectoria(
                    self.posicion, (nueva_x, nueva_y), posiciones_comida,
                    TAMANO_CELDA / 2, MARGEN, ANCHO, ALTO, TAMANO_CELDA)
                
                for comida in comidas_en_camino:
                    if comida not in self.comidas_registradas:
                        self.comidas_registradas.add(comida)
                        comidas_encontradas.append(comida)

            self.posicion = (nueva_x, nueva_y)
            
            if self.posicion in self.trazas:
                self.trazas[self.posicion] += 1
            else:
                self.trazas[self.posicion] = 1

        self.vida -= 1
        self.actualizar_rect()  # Actualizar la posición del rectángulo de la imagen
        return comidas_encontradas

    def mover_en_direccion(self, direccion, TAMANO_CELDA, MARGEN, ANCHO, ALTO):
        x, y = self.posicion
        distancia_movimiento = TAMANO_CELDA * self.velocidad

        if direccion == "arriba":
            nueva_y = max(MARGEN, y - distancia_movimiento)
            self.posicion = (x, nueva_y)
        elif direccion == "abajo":
            nueva_y = min(ALTO + MARGEN, y + distancia_movimiento)
            self.posicion = (x, nueva_y)
        elif direccion == "derecha":
            nueva_x = min(ANCHO + MARGEN, x + distancia_movimiento)
            self.posicion = (nueva_x, y)
        else:  # izquierda
            nueva_x = max(MARGEN, x - distancia_movimiento)
            self.posicion = (nueva_x, y)

        self.vida -= 1
        self.actualizar_rect()  # Actualizar la posición del rectángulo de la imagen
        return []

    def verificar_colision(self, posicion_comida, DISTANCIA_COLISION, MARGEN, ANCHO, ALTO, TAMANO_CELDA):
        fx, fy = posicion_comida
        # Verificar que la comida está dentro del área jugable
        if not (MARGEN <= fx <= ANCHO + MARGEN - TAMANO_CELDA and
                MARGEN <= fy <= ALTO + MARGEN - TAMANO_CELDA):
            return False

        bx, by = self.posicion
        distancia = ((bx - fx) ** 2 + (by - fy) ** 2) ** 0.5
        if distancia <= DISTANCIA_COLISION:
            if posicion_comida not in self.comidas_registradas:
                self.comidas_registradas.add(posicion_comida)
                self.comidas_este_ciclo += 1
                return True
        return False

    def actualizar_velocidad(self):
        velocidad_anterior = self.velocidad
        # Imprimir el conteo real de comidas únicas
        print(f"  - Comidas únicas en este ciclo: {len(self.comidas_registradas)}")

        if len(self.comidas_registradas) >= 2:  # Usar el número de comidas únicas
            self.velocidad_siguiente_ciclo = self.velocidad + 1
            print(f"  - Ganó velocidad: {velocidad_anterior} -> {self.velocidad_siguiente_ciclo}")
        else:
            self.velocidad_siguiente_ciclo = self.velocidad
            print(f"  - Mantiene velocidad: {velocidad_anterior}")

        # Limpiar el registro de comidas para el siguiente ciclo
        self.comidas_registradas.clear()
        self.comidas_este_ciclo = 0
        self.velocidad = self.velocidad_siguiente_ciclo