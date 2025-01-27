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

    def verificar_comida_en_trayectoria(self, inicio, fin, posiciones_comida, DISTANCIA_COLISION):
        x1, y1 = inicio
        x2, y2 = fin
        comidas_encontradas = []
        
        # Solo verifica colisiones en movimientos rectos
        if x1 == x2 or y1 == y2:  # Movimiento horizontal o vertical
            for comida in posiciones_comida:
                fx, fy = comida
                # Para movimiento horizontal
                if y1 == y2 and y1 == fy and min(x1, x2) <= fx <= max(x1, x2):
                    comidas_encontradas.append(comida)
                # Para movimiento vertical
                elif x1 == x2 and x1 == fx and min(y1, y2) <= fy <= max(y1, y2):
                    comidas_encontradas.append(comida)
        
        return comidas_encontradas

    def mover(self, TAMANO_CELDA, MARGEN, ANCHO, ALTO, posiciones_comida=None):
        x, y = self.posicion
        comida_objetivo = None
        comidas_encontradas = []  # Lista para rastrear las comidas encontradas en este movimiento
        
        if posiciones_comida:
            comida_objetivo = self.detectar_comida_en_linea(posiciones_comida, TAMANO_CELDA * 7)
            
            if comida_objetivo:
                fx, fy = comida_objetivo
                if x == fx:  # Mismo eje X, mover verticalmente
                    movimientos = ["arriba"] if fy < y else ["abajo"]
                elif y == fy:  # Mismo eje Y, mover horizontalmente
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
                # Ajustar al borde si se excede
                if nueva_y < MARGEN:
                    nueva_y = MARGEN
            elif movimiento == "abajo":
                nueva_y = y + distancia_movimiento
                # Ajustar al borde si se excede
                if nueva_y > ALTO + MARGEN:
                    nueva_y = ALTO + MARGEN
            elif movimiento == "derecha":
                nueva_x = x + distancia_movimiento
                # Ajustar al borde si se excede
                if nueva_x > ANCHO + MARGEN:
                    nueva_x = ANCHO + MARGEN
            else:  # izquierda
                nueva_x = x - distancia_movimiento
                # Ajustar al borde si se excede
                if nueva_x < MARGEN:
                    nueva_x = MARGEN

            # Si hubo algún movimiento (aunque sea parcial)
            if nueva_x != x or nueva_y != y:
                nueva_posicion = (nueva_x, nueva_y)
                comidas_en_camino = self.verificar_comida_en_trayectoria(
                    self.posicion, nueva_posicion, posiciones_comida, TAMANO_CELDA/2)
                
                # Agregar solo las comidas que no han sido registradas antes
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

    def verificar_colision(self, posicion_comida, DISTANCIA_COLISION):
        bx, by = self.posicion
        fx, fy = posicion_comida
        distancia = ((bx - fx) ** 2 + (by - fy) ** 2) ** 0.5
        if distancia <= DISTANCIA_COLISION:
            # Solo incrementar si esta comida no ha sido registrada antes
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