# Simulación Monte-Carlo de epidemias paralela (SIR)

Este proyecto implementa una simulación estocástica del modelo epidemiológico SIR sobre una grilla espacial 2D de 1000x1000. Cuenta con versiones secuencial y paralela utilizando la técnica de descomposición de dominio y paso de *ghost-cells* (celdas fantasma).

## Contenido del Proyecto

- `secuencial/`: Contiene `simulacion.py`. Modelo ejecutado en un solo núcleo.
- `paralelo/`: Contiene `simulacion_paralela.py`. Modelo optimizado dividiendo la carga de trabajo usando `multiprocessing`.
- `scripts/`: Herramientas auxiliares:
  - `benchmarks.py`: Ejecuta la simulación con 1, 2, 4 y 8 núcleos para la evaluación _strong scaling_. Genera resultados en `tiempos.csv`.
  - `plot_scaling.py`: Grafica el *Speed-up* a partir de los tiempos medidos (revisar imagen `speedup_plot.png`).
  - `animate.py`: Extrae las matrices diarias de la simulación y genera una animación `.gif` del brote.
- `informe/explicacion.md`: Documento con explicación didáctica y sencilla del funcionamiento y paralelización.

## Requisitos
Para ejecutar este programa requieres Python 3.8+ y las siguientes librerías:
```bash
pip install numpy pandas matplotlib
```

## Instrucciones de Uso

Para probar y evaluar el desempeño:

1. **Generar Tiempos (Benchmark Escalado Fuerte)**:
   ```bash
   python scripts/benchmarks.py
   ```
   *Nota: Por defecto, este análisis corre 1 millón de células y evalúa hasta 8 cores. Puede durar algunos minutos en finalizar. Para acelerarlo, ajusta los valores de la `grilla` y los `días` en este script.*

2. **Generar Gráfica de Speed-Up**:
   Posterior a la ejecución del paso previo, ejecuta:
   ```bash
   python scripts/plot_scaling.py
   ```
   Esto guardará un archivo de imagen en la carpeta principal.

3. **Ver la Animación del Brote**:
   ```bash
   python scripts/animate.py
   ```
   Esto correrá una demo rápida a pequeña escala (200x200) y exportará un GIF que puedes abrir con tu navegador web o visor de fotos.
