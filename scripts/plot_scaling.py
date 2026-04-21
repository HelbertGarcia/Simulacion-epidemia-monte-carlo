import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_speedup():
    path_tiempos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tiempos.csv")
    if not os.path.exists(path_tiempos):
        print(f"El archivo {path_tiempos} no existe. Ejecuta benchmarks.py primero.")
        return
        
    df = pd.read_csv(path_tiempos)
    df_paralelo = df[df['Mode'] == 'Paralelo'].copy()
    
    plt.figure(figsize=(12, 5))
    
    # Gráfica 1: Tiempo vs Cores
    plt.subplot(1, 2, 1)
    
    # Extraer el tiempo del secuencial como línea de referencia
    tiempo_sec = df[df['Mode']=='Secuencial']['Tiempo (s)'].values[0]
    
    plt.plot(df_paralelo['Cores'], df_paralelo['Tiempo (s)'], marker='o', linestyle='-', color='b', label='Paralelo')
    plt.axhline(y=tiempo_sec, color='r', linestyle='--', label='Secuencial')
    
    plt.title('Tiempo de Ejecución vs Cores')
    plt.xlabel('Número de Cores')
    plt.ylabel('Tiempo Total (s)')
    plt.legend()
    plt.grid(True)
    plt.xticks(df_paralelo['Cores'])
    
    # Gráfica 2: Speed-up vs Cores
    plt.subplot(1, 2, 2)
    plt.plot(df_paralelo['Cores'], df_paralelo['Speed-up'], marker='s', linestyle='-', color='g', label='Speed-up Obtenido')
    plt.plot(df_paralelo['Cores'], df_paralelo['Cores'], linestyle='--', color='gray', label='Speed-up Ideal')
    
    plt.title('Strong Scaling: Speed-up')
    plt.xlabel('Número de Cores')
    plt.ylabel('Speed-up (x)')
    plt.legend()
    plt.grid(True)
    plt.xticks(df_paralelo['Cores'])
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "speedup_plot.png")
    plt.savefig(output_path)
    print(f"Gráfica de rendimiento guardada como {output_path}")

if __name__ == '__main__':
    plot_speedup()
