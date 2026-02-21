import random
import math
import pygame  # Importar pygame para manejar imágenes
from resource_manager import ResourceManager

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
        self.campo_repulsion = 40  # Aumentado de 30 a 40
        self.fuerza_repulsion = 2.0  # Aumentado de 1.5 a 2.0
        self.ultima_celda = None  # Para tracking de cuadrícula
        self.resource_manager = ResourceManager()
        self.imagen = None
        self.rect = None
        self.tamano = None
        self.tamano_original = None  # Nueva propiedad para recordar el tamaño original

    def cargar_imagen(self, tamano):
        """Carga la imagen de la bacteria usando el ResourceManager"""
        self.tamano_original = tamano
        self.tamano = tamano
        if self.imagen is None:  # Solo cargar si no hay imagen
            # Centrar la imagen más pequeña en la celda
            self.imagen = self.resource_manager.get_scaled_image('bacteria', (tamano, tamano))
            if self.imagen:
                self.rect = self.imagen.get_rect()
                self.rect.center = self.posicion
            else:
                print(f"No se pudo cargar la imagen para la bacteria {self.id}")

    def actualizar_rect(self):
        """Actualiza la posición del rectángulo de la imagen"""
        if self.rect and self.imagen:
            self.rect.center = self.posicion
            
    def __copy__(self):
        """Implementar método de copia para mantener las propiedades importantes"""
        nueva_bacteria = Bacteria(self.id, self.posicion, self.vida)
        nueva_bacteria.velocidad = self.velocidad
        nueva_bacteria.velocidad_siguiente_ciclo = self.velocidad_siguiente_ciclo
        if self.tamano:
            nueva_bacteria.cargar_imagen(self.tamano)
        return nueva_bacteria

    def detectar_comida_en_linea(self, posiciones_comida, rango_deteccion, config):
        """Detecta comida en líneas horizontales y verticales (optimizado O(1) con sets)"""
        x, y = self.posicion
        pasos = int(rango_deteccion // config.display.TAMANO_CELDA)

        for p in range(1, pasos + 1):
            dist = p * config.display.TAMANO_CELDA
            
            direcciones = [
                (x + dist, y), # Derecha
                (x - dist, y), # Izquierda
                (x, y + dist), # Abajo
                (x, y - dist)  # Arriba
            ]
            
            for pos in direcciones:
                if pos in posiciones_comida:
                    return pos

        return None

    def verificar_comida_en_trayectoria(self, inicio, fin, posiciones_comida, config):
        x1, y1 = inicio
        x2, y2 = fin
        comidas_encontradas = []

        # Usar la naturaleza de Set O(1) para buscar la coordenada exacta directamente
        if x1 == x2:  # Movimiento vertical
            paso = config.display.TAMANO_CELDA if y2 > y1 else -config.display.TAMANO_CELDA
            for y in range(int(y1), int(y2) + (1 if y2 > y1 else -1), paso):
                pos = (int(x1), int(y))
                if pos in posiciones_comida and pos not in comidas_encontradas:
                    comidas_encontradas.append(pos)
        elif y1 == y2:  # Movimiento horizontal
            paso = config.display.TAMANO_CELDA if x2 > x1 else -config.display.TAMANO_CELDA
            for x in range(int(x1), int(x2) + (1 if x2 > x1 else -1), paso):
                pos = (int(x), int(y1))
                if pos in posiciones_comida and pos not in comidas_encontradas:
                    comidas_encontradas.append(pos)

        return comidas_encontradas

    def predecir_colision_con_bacterias(self, nueva_posicion, otras_bacterias):
        """Verifica si alguna otra bacteria se encuentra o se moverá a la nueva posición"""
        if not otras_bacterias:
            return False
            
        x, y = nueva_posicion
        margen_seguridad_cuadrado = (25 + (self.tiempo_espera * 5)) ** 2
        
        for otra in otras_bacterias:
            if otra.id == self.id:
                continue
            ox, oy = otra.posicion
            dist_cuadrada = (x - ox) ** 2 + (y - oy) ** 2
            if dist_cuadrada < margen_seguridad_cuadrado:
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

    def calcular_fuerzas_repulsion(self, otras_bacterias, config):
        """Calcula las fuerzas de repulsión de otras bacterias"""
        fx = fy = 0
        x, y = self.posicion
        campo_cuadrado = self.campo_repulsion ** 2
        
        for otra in otras_bacterias:
            if otra.id == self.id:
                continue
                
            ox, oy = otra.posicion
            dx = x - ox
            dy = y - oy
            dist_cuadrada = dx*dx + dy*dy
            
            if dist_cuadrada < campo_cuadrado and dist_cuadrada > 0:
                # Calculamos sqrt solo si están dentro del rango de repulsión
                distancia = math.sqrt(dist_cuadrada)
                fuerza = (self.campo_repulsion - distancia) * self.fuerza_repulsion
                fx += (dx/distancia) * fuerza
                fy += (dy/distancia) * fuerza
        
        return fx, fy

    def obtener_celda_actual(self, config):
        """Retorna la celda de la cuadrícula en la que está la bacteria"""
        x, y = self.posicion
        celda_x = x // config.display.TAMANO_CELDA
        celda_y = y // config.display.TAMANO_CELDA
        return (celda_x, celda_y)

    def mover(self, config, posiciones_comida=None, otras_bacterias=None):
        x, y = self.posicion
        comidas_encontradas = []
        
        # Asegurar dirección inicial correcta
        if self.direccion_inicial is None:
            # Asignar dirección inicial basada en la posición de aparición
            if y == config.display.MARGEN:  # Apareció arriba
                self.direccion_inicial = "abajo"
            elif y >= config.display.ALTO + config.display.MARGEN:  # Apareció abajo
                self.direccion_inicial = "arriba"
            elif x == config.display.MARGEN:  # Apareció a la izquierda
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
                comida_objetivo = self.detectar_comida_en_linea(posiciones_comida, config.display.TAMANO_CELDA * 7, config)
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
        velocidad_efectiva = config.display.TAMANO_CELDA * self.velocidad
        nueva_x = x + dx * velocidad_efectiva
        nueva_y = y + dy * velocidad_efectiva

        # Limitar al área de juego
        nueva_x = max(config.display.MARGEN, min(config.display.ANCHO + config.display.MARGEN - config.display.TAMANO_CELDA, nueva_x))
        nueva_y = max(config.display.MARGEN, min(config.display.ALTO + config.display.MARGEN - config.display.TAMANO_CELDA, nueva_y))

        # Verificar colisiones con otras bacterias de manera optimizada
        puede_moverse = True
        if otras_bacterias:
            tamano_celda_cuadrado = config.display.TAMANO_CELDA ** 2
            for otra in otras_bacterias:
                if otra.id != self.id:
                    dist_cuadrada = (nueva_x - otra.posicion[0])**2 + (nueva_y - otra.posicion[1])**2
                    if dist_cuadrada < tamano_celda_cuadrado:
                        puede_moverse = False
                        break

        if puede_moverse:
            # Verificar comida en el camino
            if posiciones_comida:
                comidas_en_camino = self.verificar_comida_en_trayectoria(
                    self.posicion, (nueva_x, nueva_y), posiciones_comida, config)
                
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

    def mover_en_direccion(self, direccion, config):
        x, y = self.posicion
        distancia_movimiento = config.display.TAMANO_CELDA * self.velocidad

        if direccion == "arriba":
            nueva_y = max(config.display.MARGEN, y - distancia_movimiento)
            self.posicion = (x, nueva_y)
        elif direccion == "abajo":
            nueva_y = min(config.display.ALTO + config.display.MARGEN, y + distancia_movimiento)
            self.posicion = (x, nueva_y)
        elif direccion == "derecha":
            nueva_x = min(config.display.ANCHO + config.display.MARGEN, x + distancia_movimiento)
            self.posicion = (nueva_x, y)
        else:  # izquierda
            nueva_x = max(config.display.MARGEN, x - distancia_movimiento)
            self.posicion = (nueva_x, y)

        self.vida -= 1
        self.actualizar_rect()  # Actualizar la posición del rectángulo de la imagen
        return []

    def verificar_colision(self, posicion_comida, config):
        fx, fy = posicion_comida
        # Verificar que la comida está dentro del área jugable
        if not (config.display.MARGEN <= fx <= config.display.ANCHO + config.display.MARGEN - config.display.TAMANO_CELDA and
                config.display.MARGEN <= fy <= config.display.ALTO + config.display.MARGEN - config.display.TAMANO_CELDA):
            return False

        bx, by = self.posicion
        dist_cuadrada = (bx - fx) ** 2 + (by - fy) ** 2
        if dist_cuadrada <= (config.physics.DISTANCIA_COLISION ** 2):
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