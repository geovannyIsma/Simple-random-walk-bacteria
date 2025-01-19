# Simulación de Caminata Aleatoria de Bacterias

Este proyecto simula la caminata aleatoria de bacterias en un entorno de cuadrícula utilizando Pygame para la visualización y PyQt5 para la configuración de entrada.

## Características

- Simulación de caminata aleatoria de bacterias.
- Parámetros configurables como número de ciclos, vida inicial de las bacterias, número de partículas de comida y número de bacterias.
- Visualización del movimiento de las bacterias, partículas de comida y rastros dejados por las bacterias.
- Visualización de información de depuración.

## Requisitos

- Python 3.x
- Pygame
- PyQt5

## Instalación

1. Clona el repositorio:
    ```sh
    git clone https://github.com/yourusername/Simple-random-walk-bacteria.git
    cd Simple-random-walk-bacteria
    ```

2. Instala los paquetes requeridos:
    ```sh
    pip install -r requirements.txt
    ```

## Uso

1. Ejecuta el script principal:
    ```sh
    python main.py
    ```

2. Aparecerá una ventana de configuración. Ingresa los parámetros deseados y comienza la simulación.

## Archivos

- `main.py`: Script principal para ejecutar la simulación.
- `simulation.py`: Contiene la lógica para la simulación de las bacterias.
- `input_window.py`: Contiene el código de PyQt5 para la ventana de configuración de entrada.
