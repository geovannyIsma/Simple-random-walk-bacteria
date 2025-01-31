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
        self.tiempo_espera = 0  # Nuevo: contador de tiempo de espera
        self.direccion_inicial = None  # Nueva variable para recordar la dirección inicial

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

    def mover(self, TAMANO_CELDA, MARGEN, ANCHO, ALTO, posiciones_comida=None, otras_bacterias=None):
        x, y = self.posicion
        comidas_encontradas = []

        # Si es el primer movimiento, asignar una dirección inicial basada en el ID
        if self.direccion_inicial is None:
            direcciones = ["arriba", "derecha", "abajo", "izquierda"]
            self.direccion_inicial = direcciones[self.id % 4]
            return self.mover_en_direccion(self.direccion_inicial, TAMANO_CELDA, MARGEN, ANCHO, ALTO)

        # Si hay otras bacterias demasiado cerca, incrementar espera y quedarse quieto
        if otras_bacterias and self.predecir_colision_con_bacterias(self.posicion, otras_bacterias):
            self.tiempo_espera += 1
            self.vida -= 1
            print(f"Bacteria {self.id} esperando por colisión (tiempo: {self.tiempo_espera})")
            return []

        # Resetear tiempo de espera al moverse
        self.tiempo_espera = 0

        # Resto de la lógica de movimiento
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

            # Si hay colisión predicha, no moverse y continuar con otra dirección
            if otras_bacterias and self.predecir_colision_con_bacterias(nueva_posicion, otras_bacterias):
                continue

            # Si llegamos aquí, es seguro moverse
            self.tiempo_espera = 0  # Reiniciar tiempo de espera al moverse exitosamente
            
            if posiciones_comida:
                comidas_en_camino = self.verificar_comida_en_trayectoria(
                    self.posicion, nueva_posicion, posiciones_comida,
                    TAMANO_CELDA / 2, MARGEN, ANCHO, ALTO, TAMANO_CELDA)
                
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

        # Si no se pudo mover en ninguna dirección, perder vida
        self.tiempo_espera += 1  # Incrementar tiempo de espera
        self.vida -= 1
        return []

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