import random


class Bacteria:
    def __init__(self, id, posicion, vida_inicial):
        self.id = id
        self.posicion = posicion
        self.vida = vida_inicial
        self.trazas = {posicion: 1}
        self.comio_comida = False

    def mover(self, TAMANO_CELDA, MARGEN, ANCHO, ALTO):
        x, y = self.posicion
        movimientos = ["arriba", "abajo", "izquierda", "derecha"]
        while movimientos:
            movimiento = random.choice(movimientos)
            if movimiento == "arriba":
                nueva_posicion = (x, y - TAMANO_CELDA)
            elif movimiento == "abajo":
                nueva_posicion = (x, y + TAMANO_CELDA)
            elif movimiento == "derecha":
                nueva_posicion = (x + TAMANO_CELDA, y)
            else:
                nueva_posicion = (x - TAMANO_CELDA, y)

            if MARGEN <= nueva_posicion[0] < ANCHO + MARGEN and MARGEN <= nueva_posicion[1] < ALTO + MARGEN:
                self.posicion = nueva_posicion
                self.vida -= 1
                if nueva_posicion in self.trazas:
                    self.trazas[nueva_posicion] += 1
                else:
                    self.trazas[nueva_posicion] = 1
                break
            else:
                movimientos.remove(movimiento)

    def verificar_colision(self, posicion_comida, DISTANCIA_COLISION):
        bx, by = self.posicion
        fx, fy = posicion_comida
        distancia = ((bx - fx) ** 2 + (by - fy) ** 2) ** 0.5
        if distancia <= DISTANCIA_COLISION:
            self.comio_comida = True
            return True
        return False