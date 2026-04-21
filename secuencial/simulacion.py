import numpy as np
import time
import os

# Constantes de los estados SIR
S, I, R = 0, 1, 2

def contar_vecinos_infectados(grid):
    n, m = grid.shape
    infectados = (grid == I).astype(np.int8)
    vecinos = np.zeros((n, m), dtype=np.int8)
    
    # Sumar vecinos usando slices de numpy (Vecindad de Moore, 8 vecinos)
    vecinos[:-1, :] += infectados[1:, :]    # arriba
    vecinos[1:, :]  += infectados[:-1, :]   # abajo
    vecinos[:, :-1] += infectados[:, 1:]    # izquierda
    vecinos[:, 1:]  += infectados[:, :-1]   # derecha
    
    vecinos[:-1, :-1] += infectados[1:, 1:]   # diagonal arriba-izquierda
    vecinos[1:, :-1]  += infectados[:-1, 1:]  # diagonal abajo-izquierda
    vecinos[:-1, 1:]  += infectados[1:, :-1]  # diagonal arriba-derecha
    vecinos[1:, 1:]   += infectados[:-1, :-1] # diagonal abajo-derecha
    
    return vecinos

def simular_secuencial(filas=1000, columnas=1000, dias=365, beta=0.2, gamma=0.1, semilla=None, guardar_frames=False):
    """
    Simulación Monte-Carlo secuencial del modelo SIR sobre una grilla espacial.
    """
    if semilla is not None:
        np.random.seed(semilla)
        
    grid = np.full((filas, columnas), S, dtype=np.int8)
    
    # Paciente inicial (brote en el centro)
    grid[filas//2, columnas//2] = I
    # Si la grilla es muy grande, sumamos un pequeño cluster para iniciar más rápido
    if filas >= 100:
        grid[filas//2-2:filas//2+3, columnas//2-2:columnas//2+3] = I
    
    historial_estadisticas = []
    frames = []
    
    print(f"[Secuencial] Iniciando simulación en grilla de {filas}x{columnas} por {dias} días...")
    inicio = time.time()
    
    for dia in range(dias):
        count_S = np.sum(grid == S)
        count_I = np.sum(grid == I)
        count_R = np.sum(grid == R)
        historial_estadisticas.append((count_S, count_I, count_R))
        
        if guardar_frames:
            frames.append(grid.copy())
            
        if count_I == 0:
            # Epidemia terminada anticipadamente
            for _ in range(dia, dias):
                historial_estadisticas.append((count_S, 0, count_R))
                if guardar_frames: frames.append(grid.copy())
            break
            
        # Generar matrices aleatorias de la etapa de Monte-Carlo
        rand_recup = np.random.rand(filas, columnas)
        rand_contagio = np.random.rand(filas, columnas)
        
        nuevos_estados = grid.copy()
        
        # 1. Recuperación: Infectados -> Recuperados
        mascara_I = (grid == I)
        se_recuperan = mascara_I & (rand_recup < gamma)
        nuevos_estados[se_recuperan] = R
        
        # 2. Contagio: Susceptibles -> Infectados basado en vecinos
        mascara_S = (grid == S)
        vecinos_I = contar_vecinos_infectados(grid)
        
        # Probabilidad combinada = 1 - (1 - beta)^n
        prob_contagio = 1.0 - (1.0 - beta)**vecinos_I
        se_contagian = mascara_S & (rand_contagio < prob_contagio)
        nuevos_estados[se_contagian] = I
        
        grid = nuevos_estados

    fin = time.time()
    tiempo_total = fin - inicio
    print(f"[Secuencial] Simulación finalizada en {tiempo_total:.4f} segundos.")
    
    if guardar_frames:
        return historial_estadisticas, tiempo_total, frames
    return historial_estadisticas, tiempo_total

if __name__ == '__main__':
    # Prueba del código en una grilla de tamaño pequeño para verificar coherencia
    stats, t = simular_secuencial(filas=200, columnas=200, dias=50)
    print("Estadísticas finales (Día 50):", stats[-1])
