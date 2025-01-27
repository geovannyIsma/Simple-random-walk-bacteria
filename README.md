# Simulación de Caminata Aleatoria de Bacterias

Este proyecto simula la caminata aleatoria de bacterias en un entorno de cuadrícula utilizando Pygame para la visualización y PyQt5 para la configuración de entrada.

## Características

- Simulación de caminata aleatoria de bacterias con comportamiento adaptativo.
- Sistema de velocidad variable basado en el éxito de alimentación.
- Detección inteligente de comida en líneas horizontales y verticales.
- Competencia entre bacterias por recursos alimenticios.
- Parámetros configurables:
  - Número de ciclos
  - Vida inicial de las bacterias
  - Número de partículas de comida
  - Número de bacterias
- Visualización detallada:
  - Movimiento de bacterias numeradas
  - Partículas de comida
  - Rastros dejados por las bacterias
  - Información de depuración (toggle con Ctrl+D)
  - Estadísticas en tiempo real de cada bacteria

## Mecánicas Principales

- Las bacterias aumentan su velocidad si consumen 2 o más comidas en un ciclo
- Sistema de detección de comida en línea recta
- Resolución de competencia por comida entre múltiples bacterias
- Seguimiento de trazas y superposición de caminos
- Sistema de vida y regeneración entre ciclos

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

2. Configura los parámetros en la ventana de entrada:
   - Número de ciclos de simulación
   - Vida inicial de cada bacteria
   - Cantidad de partículas de comida
   - Número de bacterias

3. Controles durante la simulación:
   - Ctrl+D: Activa/desactiva la información de depuración
   - ESC: Salir (cuando no hay bacterias vivas)

## Archivos

- `main.py`: Script principal para ejecutar la simulación
- `simulation.py`: Contiene la lógica principal de la simulación
- `bacteria.py`: Define la clase Bacteria y su comportamiento
- `input_window.py`: Interfaz de configuración inicial con PyQt5

## Interfaz

- Ventana principal de simulación con cuadrícula
- Panel de depuración con información en tiempo real
- Ventana de configuración inicial estilizada
- Indicadores visuales de estado de las bacterias
