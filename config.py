from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class Colors:
    FONDO: Tuple[int, int, int] = (0, 0, 0)
    BACTERIA: Tuple[int, int, int] = (0, 255, 0)
    TRAZA: Tuple[int, int, int] = (255, 255, 0)
    SUPERPOSICION_TRAZA: Tuple[int, int, int] = (255, 0, 0)
    COMIDA: Tuple[int, int, int] = (255, 0, 255)

@dataclass
class PhysicsConfig:
    RADIO_COMIDA: int = 5
    RADIO_BACTERIA: int = 6
    DISTANCIA_COLISION: int = 11  # RADIO_COMIDA + RADIO_BACTERIA
    INTERVALO_MOVIMIENTO: int = 500  # En milisegundos

@dataclass
class DisplayConfig:
    ANCHO_VENTANA: int = 1280
    ALTO_VENTANA: int = 720
    MARGEN: int = 120
    TAMANO_CELDA: int = 40

    @property
    def ANCHO(self) -> int:
        return (self.ANCHO_VENTANA - 2 * self.MARGEN) // self.TAMANO_CELDA * self.TAMANO_CELDA

    @property
    def ALTO(self) -> int:
        return (self.ALTO_VENTANA - 2 * self.MARGEN) // self.TAMANO_CELDA * self.TAMANO_CELDA

    @property
    def MARGEN_HORIZONTAL(self) -> int:
        return (self.ANCHO_VENTANA - self.ANCHO) // 2

    @property
    def MARGEN_VERTICAL(self) -> int:
        return (self.ALTO_VENTANA - self.ALTO) // 2

@dataclass
class SimulationConfig:
    num_ciclos: int = 500
    vida_inicial: int = 500
    num_comida: int = 100
    num_particulas: int = 5 

@dataclass
class GameConfig:
    display: DisplayConfig = field(default_factory=DisplayConfig)
    colors: Colors = field(default_factory=Colors)
    physics: PhysicsConfig = field(default_factory=PhysicsConfig)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    debug: bool = False
