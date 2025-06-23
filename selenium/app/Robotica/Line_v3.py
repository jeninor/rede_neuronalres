from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time
import math
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # o 'Qt5Agg'
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def setup_plot():
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('X [m]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y [m]', fontsize=12, fontweight='bold')
    ax.set_zlabel('Z [m]', fontsize=12, fontweight='bold')
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([0, 1.5])
    ax.grid(True)
    return fig, ax

def connect_to_coppeliasim():
    client = RemoteAPIClient()
    sim = client.getObject('sim')
    print('[SUCCESS] Conectado ao CoppeliaSim')
    return sim

def get_esferico_axes(sim):
    axes = {
        'axis1': sim.getObject('/Manipulador/axis1'),  # Rotativo base
        'axis2': sim.getObject('/Manipulador/axis2'),  # Rotativo plano vertical
        'axis3': sim.getObject('/Manipulador/axis3'),  # Linear (alongamento)
    }
    return axes

def cinem_inversa(x, y, z, L1 = 0.7):
    r = np.sqrt(x**2 + y**2 + z**2)

    # Evitar divisões por zero
    if r < 1e-6:
        raise ValueError("Raio muito pequeno, posição inválida.")

    theta1 = np.arctan2(y, x)
    theta2 = np.arccos(z / r)
    d3 = r - L1
    return theta1, theta2, d3


matricula = "98225"
matricula = matricula.zfill(6)
R, S, T, X, Y, Z = map(int, matricula)

# Estratégia
if Z % 2 == 0:
    estrategia = "bang-bang"
else:
    estrategia = "polinomial"

partida = [-0.5, -0.5, 0.5]
chegada = [0.5, 0.5, 1.5]

ajuste_A = [0.25 if d % 2 == 0 else -0.25 for d in [R, S, T]]
ajuste_B = [0.25 if d % 2 == 0 else -0.25 for d in [X, Y, Z]]

ponto_A = [p + a for p, a in zip(partida, ajuste_A)]
ponto_B = [p + b for p, b in zip(chegada, ajuste_B)]

# Tempo total
tf = R + S + T + X + Y + Z

# Conectar com o simulador
sim = connect_to_coppeliasim()
sim.startSimulation()
time.sleep(0.5)

axes = get_esferico_axes(sim)
tcp_handle = sim.getObject('/Manipulador/axis4')

L1 = 0.7  # comprimento fixo

  # Configuração inicial
fig, ax = setup_plot()
trajectory_line, = ax.plot([], [], [], 'k-', linewidth=2)
visited_x, visited_y, visited_z = [], [], []
current_pos_marker = ax.scatter([], [], [], 'r--', linewidth=2)

# Levar ao ponto inicial
x0, y0, z0 = ponto_A
xf, yf, zf = ponto_B

# Mover para posição inicial
print('[INFO] Levadando o manipulador para a posição inicial: ', ponto_A)
   

theta1, theta2, d3 = cinem_inversa(x0, y0, z0, L1)
sim.setJointTargetPosition(axes['axis1'], theta1)
sim.setJointTargetPosition(axes['axis2'], theta2)
sim.setJointTargetPosition(axes['axis3'], d3)
time.sleep(2)

# Preparar dados
print('[INFO] Estratégia %s configurada para um tempo total de %d segundos.' %(estrategia, tf))
print('[INFO] Iniciando reta no espaço até a posição final: ', ponto_B)

def update(frame):
        alpha = 3*(frame/tf)**2 - 2*(frame/tf)**3  # Interpolação polinomial
        
        # Calcular posição desejada
        x = x0 + alpha*(xf - x0)
        y = y0 + alpha*(yf - y0)
        z = z0 + alpha*(zf - z0)
        
        try:
            # Cinemática inversa e controle
            theta1, theta2, d3 = cinem_inversa(x, y, z)
            sim.setJointTargetPosition(axes['axis1'], theta1)
            sim.setJointTargetPosition(axes['axis2'], theta2)
            sim.setJointTargetPosition(axes['axis3'], d3)
            
            # Obter posição atual
            pose = sim.getObjectPose(tcp_handle, -1)
            current_pos = pose[:3]
            
            # Atualizar plot
            trajectory_line.set_data([x0, x], [y0, y])
            trajectory_line.set_3d_properties([z0, z])
            
            visited_x.append(current_pos[0])
            visited_y.append(current_pos[1])
            visited_z.append(current_pos[2])
            print(f"{current_pos[0]}, {current_pos[1]}, {current_pos[2]}")
            
            current_pos_marker._offsets3d = ([current_pos[0]], [current_pos[1]], [current_pos[2]])
            
            # current_pos_marker.set_data(visited_x, visited_y)
            # current_pos_marker.set_3d_properties(visited_z)


        except Exception as e:
            print(f"Erro: {e}")
        
        return trajectory_line, current_pos_marker
    
# Criar animação
ani = FuncAnimation(fig, update, frames=np.linspace(0, tf, 100),
                    interval=50, blit=False, repeat=False)

plt.tight_layout()
plt.show()
  

sim.stopSimulation()
print("[INFO] Simulação finalizada.")


