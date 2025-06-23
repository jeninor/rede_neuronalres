from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time
import math
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # o 'Qt5Agg'
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def connect_to_coppeliasim():
    client = RemoteAPIClient()
    sim = client.getObject('sim')
    print('[SUCCESS] Conectado ao CoppeliaSim')
    return sim

def get_mtb_axes(sim):
    return {
        'axis1': sim.getObject('/MTB/axis1'),
        'axis2': sim.getObject('/MTB/axis2'),
        'axis3': sim.getObject('/MTB/axis3'),
        'tcp': sim.getObject('/MTB/axis4')
    }

def ik(x, y, z, L1=0.467, a3=0.3, d2=0.4):
    r = math.sqrt(x**2 + y**2)
    if r < L1 or r > L1 + d2:
        raise ValueError(f"Ponto fora do alcance: r={r:.3f}m")
    d3 = a3 - z
    theta2 = math.acos((x**2 + y**2 - L1**2 - d2**2) / (2 * L1 * d2))
    theta1 = math.atan2(y, x) - math.atan2(d2 * math.sin(theta2), L1 + d2 * math.cos(theta2))
    return theta1, theta2, d3

def setup_plot():
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X [m]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y [m]', fontsize=12, fontweight='bold')
    ax.set_zlabel('Z [m]', fontsize=12, fontweight='bold')
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([0, 0.5])
    ax.grid(True)
    return fig, ax

def trajectory_control():
    sim = connect_to_coppeliasim()
    sim.startSimulation()
    time.sleep(0.5)
    
    axes = get_mtb_axes(sim)
    tcp_handle = axes['tcp']
    
    # Configuração inicial
    fig, ax = setup_plot()
    trajectory_line, = ax.plot([], [], [], 'k-', linewidth=2)
    current_pos_marker = ax.scatter([], [], [], c='r', s=50)
    
    # Parâmetros da trajetória
    tf = 10.0  # Tempo total
    x0, y0, z0 = 0.0, 0.75, 0.1  # Posição inicial
    xf, yf, zf = 0.75, 0.0, 0.2  # Posição final
    
    # Mover para posição inicial
    theta1, theta2, d3 = ik(x0, y0, z0)
    sim.setJointTargetPosition(axes['axis1'], theta1)
    sim.setJointTargetPosition(axes['axis2'], theta2)
    sim.setJointTargetPosition(axes['axis3'], d3)
    time.sleep(2)  # Esperar chegar na posição inicial
    
    # Preparar animação
    def update(frame):
        alpha = 3*(frame/tf)**2 - 2*(frame/tf)**3  # Interpolação polinomial
        
        # Calcular posição desejada
        x = x0 + alpha*(xf - x0)
        y = y0 + alpha*(yf - y0)
        z = z0 + alpha*(zf - z0)
        
        try:
            # Cinemática inversa e controle
            theta1, theta2, d3 = ik(x, y, z)
            sim.setJointTargetPosition(axes['axis1'], theta1)
            sim.setJointTargetPosition(axes['axis2'], theta2)
            sim.setJointTargetPosition(axes['axis3'], d3)
            
            # Obter posição atual
            pose = sim.getObjectPosition(tcp_handle, -1)
            current_pos = pose[:3]
            
            # Atualizar plot
            trajectory_line.set_data([x0, x], [y0, y])
            trajectory_line.set_3d_properties([z0, z])
            current_pos_marker._offsets3d = ([current_pos[0]], [current_pos[1]], [current_pos[2]])
            
        except Exception as e:
            print(f"Erro: {e}")
        
        return trajectory_line, current_pos_marker
    
    # Criar animação
    ani = FuncAnimation(fig, update, frames=np.linspace(0, tf, 100),
                        interval=50, blit=False, repeat=False)
    
    plt.tight_layout()
    plt.show()
    
    sim.stopSimulation()
    print('[DONE] Simulação finalizada.')

if __name__ == "__main__":
    trajectory_control()