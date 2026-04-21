import multiprocessing as mp
import numpy as np
import time
import sys

S, I, R = 0, 1, 2

def contar_vecinos_infectados(grid):
    n, m = grid.shape
    infectados = (grid == I).astype(np.int8)
    vecinos = np.zeros((n, m), dtype=np.int8)
    
    vecinos[:-1, :] += infectados[1:, :]
    vecinos[1:, :]  += infectados[:-1, :]
    vecinos[:, :-1] += infectados[:, 1:]
    vecinos[:, 1:]  += infectados[:, :-1]
    
    vecinos[:-1, :-1] += infectados[1:, 1:]
    vecinos[1:, :-1]  += infectados[:-1, 1:]
    vecinos[:-1, 1:]  += infectados[1:, :-1]
    vecinos[1:, 1:]   += infectados[:-1, :-1]
    
    return vecinos

def worker_simulation(worker_id, num_workers, filas, columnas, dias, beta, gamma, pipe_top, pipe_bottom, result_queue, worker_seed, guardar_frames):
    np.random.seed(worker_seed)
    
    filas_locales = filas // num_workers
    inicio_fila = worker_id * filas_locales
    fin_fila = (worker_id + 1) * filas_locales
    
    # Matriz local más 2 filas fantasma (arriba y abajo)
    grid = np.full((filas_locales + 2, columnas), S, dtype=np.int8)
    
    # Inicializar brote central (cluster de 5x5)
    cluster_r, cluster_c = filas // 2, columnas // 2
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            r = cluster_r + dr
            c = cluster_c + dc
            if inicio_fila <= r < fin_fila:
                local_r = r - inicio_fila + 1 # +1 por el ghost cell superior
                if 0 <= c < columnas:
                    grid[local_r, c] = I
                    
    historial_estadisticas = []
    frames = []
    
    for dia in range(dias):
        if guardar_frames:
            frames.append(grid[1:-1, :].copy())
            
        # 1. COMUNICACIÓN DE GHOST-CELLS (Intercambio de fronteras)
        # Enviar primero
        if pipe_top is not None:
            pipe_top.send(grid[1, :].copy())
        if pipe_bottom is not None:
            pipe_bottom.send(grid[-2, :].copy())
            
        # Recibir después
        if pipe_top is not None:
            grid[0, :] = pipe_top.recv()
        if pipe_bottom is not None:
            grid[-1, :] = pipe_bottom.recv()
            
        # 2. ESTADÍSTICAS LOCALES
        real_grid = grid[1:-1, :] # Ignorar ghost cells para estadísticas
        count_S = np.sum(real_grid == S)
        count_I = np.sum(real_grid == I)
        count_R = np.sum(real_grid == R)
        historial_estadisticas.append((count_S, count_I, count_R))
        
        # 3. ACTUALIZACIÓN (Transiciones SIR)
        rand_recup = np.random.rand(filas_locales, columnas)
        rand_contagio = np.random.rand(filas_locales, columnas)
        
        nuevos_estados = grid.copy()
        
        mascara_I = (real_grid == I)
        se_recuperan = mascara_I & (rand_recup < gamma)
        nuevos_estados[1:-1][se_recuperan] = R
        
        vecinos_I = contar_vecinos_infectados(grid)[1:-1] # El conteo usa ghost cells
        mascara_S = (real_grid == S)
        prob_contagio = 1.0 - (1.0 - beta)**vecinos_I
        se_contagian = mascara_S & (rand_contagio < prob_contagio)
        nuevos_estados[1:-1][se_contagian] = I
        
        grid = nuevos_estados
        
    # Enviar estadísticas y (opcionalmente) frames locales
    if guardar_frames:
        result_queue.put((worker_id, historial_estadisticas, frames))
    else:
        result_queue.put((worker_id, historial_estadisticas, None))

def simular_paralelo(num_workers, filas=1000, columnas=1000, dias=365, beta=0.2, gamma=0.1, semilla=42, guardar_frames=False):
    print(f"[Paralelo] Iniciando simulación con {num_workers} workers en grilla {filas}x{columnas} por {dias} días...")
    inicio = time.time()
    
    # Crear pipes para comunicación entre workers adyacentes
    pipes = [mp.Pipe() for _ in range(num_workers - 1)]
    result_queue = mp.Queue()
    
    procesos = []
    
    for i in range(num_workers):
        pipe_top = pipes[i-1][1] if i > 0 else None
        pipe_bottom = pipes[i][0] if i < num_workers - 1 else None
        worker_seed = semilla + i if semilla else None
        
        p = mp.Process(target=worker_simulation, 
                       args=(i, num_workers, filas, columnas, dias, beta, gamma, pipe_top, pipe_bottom, result_queue, worker_seed, guardar_frames))
        procesos.append(p)
        p.start()
        
    # Recolectar resultados
    resultados_locales = {}
    frames_locales = {}
    for _ in range(num_workers):
        w_id, hist, w_frames = result_queue.get()
        resultados_locales[w_id] = hist
        frames_locales[w_id] = w_frames
        
    for p in procesos:
        p.join()
        
    # Reducción paralela: sumar estadísticas de todos los workers por cada día
    historial_global = []
    for dia in range(dias):
        tot_S = sum(resultados_locales[w][dia][0] for w in range(num_workers))
        tot_I = sum(resultados_locales[w][dia][1] for w in range(num_workers))
        tot_R = sum(resultados_locales[w][dia][2] for w in range(num_workers))
        historial_global.append((tot_S, tot_I, tot_R))
        
    # Reconstruir frames globales si se solicitaron
    frames_globales = []
    if guardar_frames:
        for dia in range(dias):
            dia_chunks = [frames_locales[w][dia] for w in range(num_workers)]
            frame_global = np.vstack(dia_chunks)
            frames_globales.append(frame_global)
            
    fin = time.time()
    tiempo_total = fin - inicio
    print(f"[Paralelo] Simulación finalizada en {tiempo_total:.4f} segundos.")
    
    if guardar_frames:
        return historial_global, tiempo_total, frames_globales
    return historial_global, tiempo_total

if __name__ == '__main__':
    mp.freeze_support()
    stats, t = simular_paralelo(num_workers=4, filas=200, columnas=200, dias=50)
    print("Estadísticas finales global (Día 50):", stats[-1])
