# Explicación del Programa: Simulación SIR en Paralelo

Este proyecto simula la propagación de una enfermedad utilizando el modelo epidemiológico **SIR** (Susceptible, Infectado, Recuperado) aplicando el método de simulación de Monte-Carlo, el cual consiste en usar probabilidades aleatorias repetidamente para modelar sistemas complejos.

¡Aquí te explicamos de forma sencilla cómo funciona bajo el capó!

## 1. El Mundo (La Grilla)
Imagina la simulación como un enorme tablero de ajedrez gigante de 1000x1000 casillas. 
Cada casilla representa a una persona que puede estar en uno de tres estados:
- **(S) Susceptible (0):** Persona sana que puede contagiarse.
- **(I) Infectada (1):** Persona enferma que puede contagiar a sus vecinos.
- **(R) Recuperada (2):** Persona que ya superó la enfermedad (o falleció) y no se puede contagiar de nuevo.

El programa arranca (Día 0) poniendo a casi todo el mundo en estado **S**, y colocando a un "paciente cero" (un pequeño grupo de infectados) justo en el centro del tablero.

## 2. El Paso del Tiempo (Los Días)
Cada iteración del bucle principal del código representa **1 día**. 
Durante un día, el programa evalúa a todas las personas al mismo tiempo para ver qué les ocurre al día siguiente usando dos reglas aleatorias (Monte-Carlo):

1. **Recuperación:** Si la persona estaba Infectada (I), tiramos unos dados (probabilidad `gamma`). Si gana, al día siguiente estará Recuperada (R).
2. **Contagio:** Si la persona es Susceptible (S), miramos cuántos de sus 8 vecinos directos están infectados. Entre más vecinos enfermos tenga, mayor será la "probabilidad combinada" de contagiarse. Luego, tiramos los dados frente a esa probabilidad; si el contagio ocurre, pasará a estar Infectada (I).

Esto se repite durante 365 días para ver cómo avanza y se apaga el brote.

## 3. ¿Por qué Paralelismo?
Tirar dados para 1 millón de personas durante 365 días toma muchísimo tiempo para el procesador. Para acelerarlo, creamos la **versión Paralela**.

En lugar de que una sola persona (un hilo/core del computador) revise las 1,000,000 de celdas, contratamos a **varios trabajadores** (cores) y les repartimos el tablero.
- Si tenemos 4 cores, cortamos el tablero "como un pastel, en 4 porciones horizontales" de 250x1000 cada una.
- Cada procesador se encarga exclusivamente de simular las personas en su porción.

### El Reto de la Frontera (Ghost Cells)
Si el Procesador 1 y el Procesador 2 están simulando pedazos adyacentes del tablero, surge un problema: **Las personas que están en el borde del pedazo 1 necesitan saber si sus vecinos en el borde del pedazo 2 están enfermos para contagiarse.**

Para solucionarlo usamos **Ghost-Cells (Celdas Fantasma)**:
Cada procesador guarda "una copia falsa" de la última fila de su vecino. 
Al final de cada día simulado, antes de calcular los contagios, los procesadores se llaman por teléfono (se envían mensajes por memoria/Pipes) para decirse: *"Toma, estos son mis infectados del borde hoy"*. Así, cada máquina actualiza su *Ghost-Cell* y calcula correctamente la probabilidad de infección sin invadir el territorio del otro procesador.

## 4. Estructura del Código
- **`secuencial/simulacion.py`**: El programa básico sin trabajadores extra. Muy útil para tener una línea base y validar que las matemáticas del contagio estén bien implementadas.
- **`paralelo/simulacion_paralela.py`**: La versión avanzada. Usa la librería `multiprocessing` de Python. Aquí puedes ver explícitamente cómo asignamos los "pedazos" del tablero, y cómo se pasan la información de los bordes (`pipe_top.send()`, `pipe_bottom.recv()`).
- **`scripts/`**: Herramientas que preparamos para ti. Una mide automáticamente el "Speed-Up" (qué tan rápido corren 4 cores unidos frente a 1 solo), y otra genera una animación en video para visualizar toda la simulación.

## 5. El Speed-Up (Ganancia de tiempo)
Teóricamente, 4 trabajadores deberían demorar 1/4 del tiempo. Pero en la realidad, la ganancia ("Speed-up") nunca es del 100% perfecto porque:
- Crear trabajadores toma tiempo.
- Tienen que pausar para intercambiar sus bordes (ghost-cells).
- Tienen que sincronizarse al final para enviar las estadísticas al "jefe".
Esto podrás verlo claramente en la gráfica generada por el benchmark.
