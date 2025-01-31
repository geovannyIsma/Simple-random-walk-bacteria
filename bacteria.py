import random
import math


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
        for otra in otras_bacterias:
            if otra.id != self.id and otra.posicion == nueva_posicion:
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

    def mover(self, TAMANO_CELDA, MARGEN, ANCHO, ALTO, posiciones_comida=None, otras_bacterias=None):
        x, y = self.posicion
        comidas_encontradas = []

        # Si está en la misma posición que otras bacterias al inicio
        if otras_bacterias and any(otra.id != self.id and otra.posicion == self.posicion for otra in otras_bacterias):
            # Asignar dirección inicial basada en el ID para evitar que vayan en la misma dirección
            direcciones = ["arriba", "derecha", "abajo", "izquierda"]
            movimientos = [direcciones[self.id % 4]]  # Usar el ID para determinar la dirección inicial
        else:
            # Comportamiento normal de detección de comida
            if posiciones_comida:
                comida_objetivo = self.detectar_comida_en_linea(posiciones_comida, TAMANO_CELDA * 7)
                if comida_objetivo:
                    fx, fy = comida_objetivo
                    if x == fx:
                        movimientos = ["arriba"] if fy < y else ["abajo"]
                    elif y == fy:
                        movimientos = ["izquierda"] if fx < x else ["derecha"]
                else:
                    movimientos = ["arriba", "abajo", "izquierda", "derecha"]
                    random.shuffle(movimientos)
            else:
                movimientos = ["arriba", "abajo", "izquierda", "derecha"]
                random.shuffle(movimientos)

        distancia_movimiento = TAMANO_CELDA * self.velocidad
        direcciones_intentadas = set()

        while movimientos and len(direcciones_intentadas) < 4:
            movimiento = movimientos.pop(0)
            if movimiento in direcciones_intentadas:
                continue

            direcciones_intentadas.add(movimiento)
            nueva_x, nueva_y = x, y

            if movimiento == "arriba":
                nueva_y = max(MARGEN, y - distancia_movimiento)
            elif movimiento == "abajo":
                nueva_y = min(ALTO + MARGEN, y + distancia_movimiento)
            elif movimiento == "derecha":
                nueva_x = min(ANCHO + MARGEN, x + distancia_movimiento)
            else:  # izquierda
                nueva_x = max(MARGEN, x - distancia_movimiento)

            nueva_posicion = (nueva_x, nueva_y)

            # Verificar colisiones con otras bacterias
            if otras_bacterias and self.predecir_colision_con_bacterias(nueva_posicion, otras_bacterias):
                direccion_opuesta = self.obtener_direccion_opuesta(movimiento)
                if direccion_opuesta and direccion_opuesta not in direcciones_intentadas:
                    movimientos.insert(0, direccion_opuesta)
                continue

            # Verificar comidas en el camino antes de moverse
            if posiciones_comida:
                comidas_en_camino = self.verificar_comida_en_trayectoria(
                    self.posicion, nueva_posicion, posiciones_comida,
                    TAMANO_CELDA / 2, MARGEN, ANCHO, ALTO, TAMANO_CELDA)
                
                # Procesar inmediatamente las comidas encontradas
                for comida in comidas_en_camino:
                    if comida not in self.comidas_registradas:
                        self.comidas_registradas.add(comida)
                        comidas_encontradas.append(comida)

            # Realizar el movimiento
            self.posicion = nueva_posicion
            self.vida -= 1

            if nueva_posicion in self.trazas:
                self.trazas[nueva_posicion] += 1
            else:
                self.trazas[nueva_posicion] = 1

            return comidas_encontradas

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