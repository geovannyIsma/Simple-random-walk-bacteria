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
        movimiento = random.choice(["arriba", "abajo", "izquierda", "derecha"])
        if movimiento == "arriba":
            y -= TAMANO_CELDA
        elif movimiento == "abajo":
            y += TAMANO_CELDA
        elif movimiento == "derecha":
            x += TAMANO_CELDA
        else:
            x -= TAMANO_CELDA

        nueva_posicion = (x, y)
        if MARGEN <= x < ANCHO + MARGEN and MARGEN <= y < ALTO + MARGEN:
            self.posicion = nueva_posicion
            self.vida -= 1
            if nueva_posicion in self.trazas:
                self.trazas[nueva_posicion] += 1
            else:
                self.trazas[nueva_posicion] = 1

    def verificar_colision(self, posicion_comida, DISTANCIA_COLISION):
        bx, by = self.posicion
        fx, fy = posicion_comida
        distancia = ((bx - fx) ** 2 + (by - fy) ** 2) ** 0.5
        if distancia <= DISTANCIA_COLISION:
            self.comio_comida = True
            return True
        return False