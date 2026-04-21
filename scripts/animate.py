import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from secuencial.simulacion import simular_secuencial
from paralelo.simulacion_paralela import simular_paralelo

def create_animation():
    filas, columnas = 200, 200
    dias = 365
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "animacion_brote")
    
    print(f"Generando frames de la simulación ({filas}x{columnas}) para {dias} días...")
    
    # Extraer frames
    print("Corriendo versión secuencial...")
    _, _, frames_sec = simular_secuencial(filas, columnas, dias, semilla=42, guardar_frames=True)
    
    print("Corriendo versión paralela (4 cores)...")
    _, _, frames_par = simular_paralelo(num_workers=4, filas=filas, columnas=columnas, dias=dias, semilla=42, guardar_frames=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(['#E0E0E0', '#FF3333', '#33CC33']) # S=Gris, I=Rojo, R=Verde
    
    mat1 = ax1.matshow(frames_sec[0], cmap=cmap, vmin=0, vmax=2)
    ax1.set_title("Secuencial")
    ax1.axis('off')
    
    mat2 = ax2.matshow(frames_par[0], cmap=cmap, vmin=0, vmax=2)
    ax2.set_title("Paralelo (Domain Decomp)")
    ax2.axis('off')
    
    # Título principal
    fig.suptitle(f"Simulación SIR (Día 0)", fontsize=16)
    
    def update(frame_idx):
        mat1.set_data(frames_sec[frame_idx])
        mat2.set_data(frames_par[frame_idx])
        fig.suptitle(f"Simulación SIR - Día {frame_idx}", fontsize=16)
        return mat1, mat2
        
    print("Renderizando animación side-by-side...")
    total_frames = min(len(frames_sec), len(frames_par))
    ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=100, blit=False)
    
    gif_path = f"{output_path}.gif"
    try:
        ani.save(gif_path, writer='pillow', fps=10)
        print(f"¡Animación guardada con éxito en {gif_path}!")
    except Exception as e:
        print(f"Error al guardar la animación: {e}")

if __name__ == '__main__':
    create_animation()
