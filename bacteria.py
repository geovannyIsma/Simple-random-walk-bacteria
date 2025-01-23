import random
import math

class Bacteria:
    def __init__(self, id, posicion, vida_inicial):
        self.id = id
        self.posicion = posicion
        self.vida = vida_inicial
        self.trazas = {posicion: 1}
        self.comio_comida = False
        self.comidas_este_ciclo = 0  # Contador de comidas en el ciclo actual
        self.velocidad = 1  # Multiplicador de velocidad
        self.intentos_fallidos = {}  # Diccionario para rastrear intentos fallidos por comida
        self.max_intentos = 1  # Máximo número de intentos antes de ignorar una comida
        self.comidas_alcanzables = set()  # Nuevo conjunto para almacenar comidas alcanzables
        self.comidas_imposibles = set()   # Nuevo conjunto para almacenar comidas imposibles

    def es_comida_alcanzable(self, posicion_comida, TAMANO_CELDA):
        """Verifica si la comida es alcanzable dado el tamaño del movimiento de la bacteria"""
        # Si ya hemos intentado demasiadas veces alcanzar esta comida, la ignoramos
        if self.intentos_fallidos.get(posicion_comida, 0) >= self.max_intentos:
            return False

        x, y = self.posicion
        fx, fy = posicion_comida
        distancia = math.sqrt((x - fx) ** 2 + (y - fy) ** 2)
        
        # Calcula la distancia mínima que la bacteria puede moverse
        distancia_minima = TAMANO_CELDA * self.velocidad
        
        # Verifica si la comida está a una distancia que la bacteria puede alcanzar
        # Consideramos que es alcanzable si está a una distancia que es múltiplo
        # (con cierta tolerancia) del movimiento de la bacteria
        tolerancia = TAMANO_CELDA / 2
        return abs(distancia % distancia_minima) < tolerancia

    def calcular_comidas_alcanzables(self, posiciones_comida, TAMANO_CELDA):
        """Precalcula qué comidas son alcanzables basándose en la posición actual"""
        self.comidas_alcanzables.clear()
        self.comidas_imposibles.clear()
        
        x, y = self.posicion
        for comida in posiciones_comida:
            fx, fy = comida
            dx = abs(x - fx)
            dy = abs(y - fy)
            
            # Una comida es alcanzable si:
            # 1. La distancia en X e Y son múltiplos del tamaño de celda
            # 2. O si está a una distancia que permite movimiento diagonal
            es_multiplo_x = dx % (TAMANO_CELDA * self.velocidad) < TAMANO_CELDA/2
            es_multiplo_y = dy % (TAMANO_CELDA * self.velocidad) < TAMANO_CELDA/2
            
            if es_multiplo_x or es_multiplo_y:
                self.comidas_alcanzables.add(comida)
            else:
                self.comidas_imposibles.add(comida)

    def detectar_comida_cercana(self, posiciones_comida, rango_deteccion):
        comida_cercana = []
        x, y = self.posicion
        for pos_comida in posiciones_comida:
            fx, fy = pos_comida
            distancia = math.sqrt((x - fx) ** 2 + (y - fy) ** 2)
            # Solo añadir comida que esté dentro del rango y sea alcanzable
            if distancia <= rango_deteccion and self.es_comida_alcanzable(pos_comida, rango_deteccion/7):
                comida_cercana.append((pos_comida, distancia))
        return min(comida_cercana, key=lambda x: x[1])[0] if comida_cercana else None

    def detectar_comida_cercana(self, posiciones_comida, rango_deteccion):
        """Detecta la comida alcanzable más cercana dentro del rango"""
        comida_mas_cercana = None
        distancia_minima = float('inf')
        x, y = self.posicion
        
        # Filtrar solo las comidas que están en el conjunto de alcanzables
        for comida in self.comidas_alcanzables:
            if comida not in posiciones_comida:
                continue
                
            fx, fy = comida
            distancia = math.sqrt((x - fx) ** 2 + (y - fy) ** 2)
            
            if distancia <= rango_deteccion and distancia < distancia_minima:
                distancia_minima = distancia
                comida_mas_cercana = comida
        
        return comida_mas_cercana

    def verificar_comida_en_trayectoria(self, inicio, fin, posiciones_comida, DISTANCIA_COLISION):
        x1, y1 = inicio
        x2, y2 = fin
        comidas_encontradas = []
        
        # Calcular cuántos pasos intermedios verificar basado en la velocidad
        pasos = self.velocidad
        for i in range(pasos + 1):
            # Calcular punto intermedio
            x = x1 + (x2 - x1) * i / pasos
            y = y1 + (y2 - y1) * i / pasos
            
            # Verificar colisión con comida en este punto
            for comida in posiciones_comida:
                if ((x - comida[0]) ** 2 + (y - comida[1]) ** 2) ** 0.5 <= DISTANCIA_COLISION:
                    comidas_encontradas.append(comida)
        
        return comidas_encontradas

    def mover(self, TAMANO_CELDA, MARGEN, ANCHO, ALTO, posiciones_comida=None):
        x, y = self.posicion
        comida_objetivo = None
        
        if posiciones_comida:
            # Limpiar intentos fallidos para comidas que ya no existen
            self.intentos_fallidos = {k: v for k, v in self.intentos_fallidos.items() 
                                    if k in posiciones_comida}
            
            # Filtrar solo las comidas alcanzables
            comidas_alcanzables = [comida for comida in posiciones_comida 
                                 if self.es_comida_alcanzable(comida, TAMANO_CELDA)]
            
            if comidas_alcanzables:
                comida_objetivo = self.detectar_comida_cercana(comidas_alcanzables, TAMANO_CELDA * 7)
                if comida_objetivo:
                    # Verificar si el movimiento fue exitoso
                    posicion_anterior = self.posicion

            if comida_objetivo:
                # ...resto del código de movimiento hacia la comida...
                fx, fy = comida_objetivo
                dx = fx - x
                dy = fy - y
                
                if abs(dx) > abs(dy):
                    movimientos = ["derecha" if dx > 0 else "izquierda",
                                 "arriba" if dy < 0 else "abajo"]
                else:
                    movimientos = ["arriba" if dy < 0 else "abajo",
                                 "derecha" if dx > 0 else "izquierda"]
                movimientos.extend(["arriba", "abajo", "izquierda", "derecha"])
            else:
                movimientos = ["arriba", "abajo", "izquierda", "derecha"]
                random.shuffle(movimientos)
        else:
            movimientos = ["arriba", "abajo", "izquierda", "derecha"]
            random.shuffle(movimientos)

        if posiciones_comida:
            # Actualizar comidas alcanzables al inicio del movimiento
            self.calcular_comidas_alcanzables(posiciones_comida, TAMANO_CELDA)
            comida_objetivo = self.detectar_comida_cercana(posiciones_comida, TAMANO_CELDA * 7)
            
            if comida_objetivo:
                # Calcular el movimiento óptimo hacia la comida
                x, y = self.posicion
                fx, fy = comida_objetivo
                dx = fx - x
                dy = fy - y
                
                # Priorizar el movimiento en la dirección con mayor diferencia
                if abs(dx) > abs(dy):
                    movimientos = ["derecha" if dx > 0 else "izquierda",
                                 "arriba" if dy < 0 else "abajo"]
                else:
                    movimientos = ["arriba" if dy < 0 else "abajo",
                                 "derecha" if dx > 0 else "izquierda"]
            else:
                movimientos = ["arriba", "abajo", "izquierda", "derecha"]
                random.shuffle(movimientos)
        else:
            movimientos = ["arriba", "abajo", "izquierda", "derecha"]
            random.shuffle(movimientos)

        # Intentar mover la bacteria según su velocidad
        distancia_movimiento = TAMANO_CELDA * self.velocidad
        while movimientos:
            movimiento = movimientos.pop(0)
            if movimiento == "arriba":
                nueva_posicion = (x, y - distancia_movimiento)
            elif movimiento == "abajo":
                nueva_posicion = (x, y + distancia_movimiento)
            elif movimiento == "derecha":
                nueva_posicion = (x + distancia_movimiento, y)
            else:
                nueva_posicion = (x - distancia_movimiento, y)

            if MARGEN <= nueva_posicion[0] < ANCHO + MARGEN and MARGEN <= nueva_posicion[1] < ALTO + MARGEN:
                # Verificar comida en la trayectoria antes de moverse
                comidas_en_camino = self.verificar_comida_en_trayectoria(
                    self.posicion, nueva_posicion, posiciones_comida, TAMANO_CELDA/2)
                
                # Actualizar la posición
                self.posicion = nueva_posicion
                self.vida -= 1
                
                # Si había un objetivo y no lo alcanzamos, incrementar contador de intentos
                if comida_objetivo and not comidas_en_camino and comida_objetivo not in comidas_en_camino:
                    self.intentos_fallidos[comida_objetivo] = self.intentos_fallidos.get(comida_objetivo, 0) + 1
                
                # Si alcanzamos alguna comida, resetear sus intentos fallidos
                for comida in comidas_en_camino:
                    if comida in self.intentos_fallidos:
                        del self.intentos_fallidos[comida]
                
                # Registrar la nueva posición en las trazas
                if nueva_posicion in self.trazas:
                    self.trazas[nueva_posicion] += 1
                else:
                    self.trazas[nueva_posicion] = 1
                
                return comidas_en_camino
                
        return []

    def verificar_colision(self, posicion_comida, DISTANCIA_COLISION):
        bx, by = self.posicion
        fx, fy = posicion_comida
        distancia = ((bx - fx) ** 2 + (by - fy) ** 2) ** 0.5
        if distancia <= DISTANCIA_COLISION:
            self.comidas_este_ciclo += 1
            return True
        return False

    
    def actualizar_velocidad(self):
        if self.comidas_este_ciclo >= 2:
            self.velocidad += 1
        self.comidas_este_ciclo = 0  # Reiniciar contador para el siguiente ciclo