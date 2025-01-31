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
        self.velocidad_siguiente_ciclo = 1
        self.comidas_registradas = set()

    def mover(self, TAMANO_CELDA, MARGEN, ANCHO, ALTO, posiciones_comida=None, otras_bacterias=None):
        x, y = self.posicion
        comida_objetivo = None
        comidas_encontradas = []
        velocidad_original = self.velocidad  # Guardar la velocidad original

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
        while movimientos:
            movimiento = movimientos.pop(0)
            nueva_x, nueva_y = x, y

            if movimiento == "arriba":
                nueva_y = y - distancia_movimiento
                if nueva_y < MARGEN:
                    nueva_y = MARGEN
            elif movimiento == "abajo":
                nueva_y = y + distancia_movimiento
                if nueva_y > ALTO + MARGEN:
                    nueva_y = ALTO + MARGEN
            elif movimiento == "derecha":
                nueva_x = x + distancia_movimiento
                if nueva_x > ANCHO + MARGEN:
                    nueva_x = ANCHO + MARGEN
            else:
                nueva_x = x - distancia_movimiento
                if nueva_x < MARGEN:
                    nueva_x = MARGEN

            nueva_posicion = (nueva_x, nueva_y)
            if otras_bacterias and any(b.posicion == nueva_posicion for b in otras_bacterias):
                if random.choice([True, False]):
                    continue  # Esta bacteria no se mueve, intenta otro movimiento
                else:
                    # La otra bacteria no se mueve, esta bacteria se mueve
                    break

            comidas_en_camino = self.verificar_comida_en_trayectoria(self.posicion, nueva_posicion, posiciones_comida,
                                                                     TAMANO_CELDA / 2)
            for comida in comidas_en_camino:
                if comida not in self.comidas_registradas:
                    self.comidas_registradas.add(comida)
                    comidas_encontradas.append(comida)

            # Si la comida está en una posición inaccesible con el paso actual, reducir el paso a 1
            if comida_objetivo and self.velocidad > 1:
                fx, fy = comida_objetivo
                if (x != fx and y != fy) and (abs(x - fx) < TAMANO_CELDA or abs(y - fy) < TAMANO_CELDA):
                    self.velocidad = 1
                    distancia_movimiento = TAMANO_CELDA * self.velocidad
                    continue  # Reintentar el movimiento con la nueva velocidad

            self.posicion = nueva_posicion
            self.vida -= 1

            if nueva_posicion in self.trazas:
                self.trazas[nueva_posicion] += 1
            else:
                self.trazas[nueva_posicion] = 1

            # Restaurar la velocidad original después de comer
            if comidas_encontradas:
                self.velocidad = velocidad_original

            return comidas_encontradas

        return []

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

    def verificar_comida_en_trayectoria(self, inicio, fin, posiciones_comida, DISTANCIA_COLISION, MARGEN, ANCHO, ALTO, TAMANO_CELDA):
        x1, y1 = inicio
        x2, y2 = fin
        comidas_encontradas = []
        
        # Solo verifica colisiones en movimientos rectos y dentro del área jugable
        if x1 == x2 or y1 == y2:  # Movimiento horizontal o vertical
            for comida in posiciones_comida:
                fx, fy = comida
                # Verificar que la comida está dentro del área jugable
                if not (MARGEN <= fx <= ANCHO + MARGEN - TAMANO_CELDA and 
                       MARGEN <= fy <= ALTO + MARGEN - TAMANO_CELDA):
                    continue
                
                # Para movimiento horizontal
                if y1 == y2 and y1 == fy and min(x1, x2) <= fx <= max(x1, x2):
                    comidas_encontradas.append(comida)
                # Para movimiento vertical
                elif x1 == x2 and x1 == fx and min(y1, y2) <= fy <= max(y1, y2):
                    comidas_encontradas.append(comida)
        
        return comidas_encontradas

<<<<<<< HEAD
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
            
            # Verificar si hay colisión con otras bacterias
            if otras_bacterias and self.predecir_colision_con_bacterias(nueva_posicion, otras_bacterias):
                # Si hay colisión, intentar la dirección opuesta
                direccion_opuesta = self.obtener_direccion_opuesta(movimiento)
                if direccion_opuesta and direccion_opuesta not in direcciones_intentadas:
                    movimientos.insert(0, direccion_opuesta)
                continue

            # Si no hay colisión, realizar el movimiento
            if nueva_x != x or nueva_y != y:
                if posiciones_comida:
                    comidas_en_camino = self.verificar_comida_en_trayectoria(
                        self.posicion, nueva_posicion, posiciones_comida, 
                        TAMANO_CELDA/2, MARGEN, ANCHO, ALTO, TAMANO_CELDA)
                    for comida in comidas_en_camino:
                        if comida not in self.comidas_registradas:
                            self.comidas_registradas.add(comida)
                            comidas_encontradas.append(comida)

                self.posicion = nueva_posicion
                self.vida -= 1
                
                if nueva_posicion in self.trazas:
                    self.trazas[nueva_posicion] += 1
                else:
                    self.trazas[nueva_posicion] = 1
                
                return comidas_encontradas
        
        return []

    def verificar_colision(self, posicion_comida, DISTANCIA_COLISION, MARGEN, ANCHO, ALTO, TAMANO_CELDA):
=======
    def verificar_colision(self, posicion_comida, DISTANCIA_COLISION):
        bx, by = self.posicion
>>>>>>> 463cfec6b3333ff89e4d5443d72a5f18fa00c0fe
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