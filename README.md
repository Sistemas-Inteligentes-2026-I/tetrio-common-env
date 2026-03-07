# TETR.IO Common Environment

Ambiente común para experimentar con agentes que interactúan con una sala privada de TETR.IO usando únicamente:

- procesamiento visual de pantalla
- simulación de teclado

## Objetivo

Este repositorio proporciona una base compartida para que múltiples equipos construyan y prueben agentes sobre un mismo entorno técnico, sin depender de internals del juego.

El repositorio común incluye:

- captura de pantalla
- calibración de la región del juego
- extracción visual del estado
- interfaz estándar para agentes
- simulación de teclado
- logging y herramientas de depuración

El repositorio común **no** incluye lógica competitiva avanzada ni la estrategia particular de cada equipo.

## Alcance y restricciones

Este proyecto está diseñado para pruebas en salas privadas y bajo las reglas específicas de la competencia o entorno autorizado.

Restricciones de diseño:

- no usar hacks
- no leer memoria del proceso
- no manipular DOM del juego para extraer estado
- no usar APIs privadas o internas del juego para jugar
- solo lectura visual de pantalla y emisión de teclado

Cada equipo es responsable de verificar que su uso esté permitido por la organización de la competencia.

## Plataforma objetivo

- Sistema operativo: Windows
- Runtime principal: Python 3.11+
- Cliente objetivo: TETR.IO en navegador
- Navegador soportado inicialmente: Chrome / Edge
- Resolución base recomendada: 1920x1080
- Zoom del navegador: 100%

## Arquitectura

El pipeline general es:

1. capturar frame de la región del juego
2. detectar tablero, pieza activa, next queue y hold
3. construir una observación estándar
4. pasar la observación al agente
5. traducir la acción del agente a eventos de teclado
6. registrar telemetría para depuración

## Estructura del repositorio

- `src/tetrio_env/capture/`: captura de pantalla y sincronización
- `src/tetrio_env/calibration/`: calibración y perfiles
- `src/tetrio_env/vision/`: extracción visual del estado
- `src/tetrio_env/control/`: simulación de teclado y seguridad
- `src/tetrio_env/agents/`: agentes de ejemplo
- `src/tetrio_env/telemetry/`: logging, grabación y exportación
- `tools/`: scripts operativos
- `configs/`: perfiles de navegador, resolución y teclas
- `docs/`: documentación del proyecto

## Interfaz del agente

Todo agente debe implementar una interfaz compatible con el ambiente común.

Ejemplo conceptual:

```python
class Agent:
    def reset(self) -> None:
        ...

    def act(self, observation) -> str:
        # retorna una acción lógica:
        # "left", "right", "rotate_cw", "rotate_ccw",
        # "soft_drop", "hard_drop", "hold", "noop"
        ...
