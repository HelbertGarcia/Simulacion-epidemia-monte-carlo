import time
import os
import sys
import pandas as pd
import multiprocessing as mp

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from secuencial.simulacion import simular_secuencial
from paralelo.simulacion_paralela import simular_paralelo

def run_benchmarks():
    # Parámetros del experimento ajustados para ejecución más rápida (500x500 = 250k celdas, 100 días)
    filas = 500
    columnas = 500
    dias = 100
    
    resultados = []
    
    print("=== INICIANDO EXPERIMENTOS DE STRONG SCALING ===")
    print(f"Grilla: {filas}x{columnas} ({filas*columnas} celdas), Días: {dias}")
    
    # 1. Secuencial (Baseline)
    print("\nCorriendo versión Secuencial...")
    _, t_sec = simular_secuencial(filas, columnas, dias, semilla=42)
    resultados.append({'Mode': 'Secuencial', 'Cores': 1, 'Tiempo (s)': t_sec, 'Speed-up': 1.0})
    print(f"Secuencial tardó: {t_sec:.2f}s")
    
    # 2. Paralelo con scaling
    cores_list = [1, 2, 4, 8]
    max_cores = min(8, mp.cpu_count())
    cores_list = [c for c in cores_list if c <= max_cores]
    
    for cores in cores_list:
        print(f"\nCorriendo versión Paralela con {cores} cores...")
        _, t_par = simular_paralelo(num_workers=cores, filas=filas, columnas=columnas, dias=dias, semilla=42)
        speedup = t_sec / t_par
        resultados.append({'Mode': 'Paralelo', 'Cores': cores, 'Tiempo (s)': t_par, 'Speed-up': speedup})
        print(f"Paralelo ({cores} cores) tardó: {t_par:.2f}s | Speed-up: {speedup:.2f}x")
        
    df = pd.DataFrame(resultados)
    df.to_csv("tiempos.csv", index=False)
    print("\n=== Resultados guardados en tiempos.csv ===")
    print(df)

if __name__ == '__main__':
    mp.freeze_support()
    run_benchmarks()
