import numpy as np
import matplotlib.pyplot as plt
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

# ======= Conectar ao CoppeliaSim =======
client = RemoteAPIClient()
sim = client.getObject('sim')
print("[INFO] Conectado ao CoppeliaSim com sucesso.")

# ======= Handles das juntas =======
handles = {
    'j1': sim.getObject('/Manipulador/axis1'),
    'j2': sim.getObject('/Manipulador/axis2'),
    'j3': sim.getObject('/Manipulador/axis3'),
    'tcp': sim.getObject('/Manipulador/axis4'),
}

# ======= Cinemática Inversa =======
def cinem_inversa(x, y, z, L1=0.7):
    r = np.sqrt(x**2 + y**2 + z**2)
    theta1 = np.arctan2(y, x)
    theta2 = np.arccos(z / r)
    d3 = r - L1
    return theta1, theta2, d3


# ======= Parâmetros da trajetória =======
ponto_A = [-0.25, -0.75, 0.75]
ponto_B =  [0.75, 0.75, 1.25]
x0, y0, z0 = ponto_A
xf, yf, zf = ponto_B
L1 = 0.7
tf = 26  # tempo total (s)
fps = 50
n_frames = tf * fps

# ======= Iniciar simulação e ir para ponto inicial =======
sim.startSimulation()
time.sleep(1)

theta1, theta2, d3 = cinem_inversa(x0, y0, z0, L1)
sim.setJointTargetPosition(handles['j1'], theta1)
sim.setJointTargetPosition(handles['j2'], theta2)
sim.setJointTargetPosition(handles['j3'], d3)
time.sleep(2)

# ======= Coleta de dados =======
tempos = []
posicoes = []
juntas = []

print("[INFO] Iniciando execução da trajetória...")
start = time.time()
for i in range(n_frames):
    t = i / fps
    alpha = 3*(t/tf)**2 - 2*(t/tf)**3

    # Ponto atual da interpolação
    x = x0 + alpha * (xf - x0)
    y = y0 + alpha * (yf - y0)
    z = z0 + alpha * (zf - z0)

    # Inversa + envio
    theta1, theta2, d3 = cinem_inversa(x, y, z, L1)
    sim.setJointTargetPosition(handles['j1'], theta1)
    sim.setJointTargetPosition(handles['j2'], theta2)
    sim.setJointTargetPosition(handles['j3'], d3)

    # Espera para simular tempo real
    time.sleep(1/fps)
    #time.sleep(0.2)
    # Coletar dados
    tcp_pos = sim.getObjectPosition(handles['tcp'], -1)
    joint1 = sim.getJointPosition(handles['j1'])
    joint2 = sim.getJointPosition(handles['j2'])
    joint3 = sim.getJointPosition(handles['j3'])

    tempos.append(t)
    posicoes.append(tcp_pos)
    juntas.append([joint1, joint2, joint3])

sim.stopSimulation()
print("[INFO] Simulação finalizada.")

# ======= Processamento =======
tempos = np.array(tempos)
posicoes = np.array(posicoes)
juntas = np.array(juntas)

# Calcular velocidades por diferenças finitas
velocidades = np.zeros_like(posicoes)
for i in range(1, len(tempos)):
    dt = tempos[i] - tempos[i-1]
    velocidades[i] = (posicoes[i] - posicoes[i-1]) / dt

v_resultante = np.linalg.norm(velocidades, axis=1)

# ======= Plot 1: Posição do efetuador =======
plt.figure(figsize=(12, 8))
plt.subplot(3, 1, 1)
plt.plot(tempos, posicoes[:, 0], label='X [m]', color='r')
plt.plot(tempos, posicoes[:, 1], label='Y [m]', color='g')
plt.plot(tempos, posicoes[:, 2], label='Z [m]', color='b')
plt.title('Posição do Efetuador no Tempo')
plt.ylabel('Posição [m]')
plt.grid(True)
plt.legend()

# ======= Plot 2: Velocidade do efetuador =======
plt.subplot(3, 1, 2)
plt.plot(tempos, v_resultante, label='Velocidade Resultante', color='black')
plt.title('Velocidade do Efetuador no Tempo')
plt.ylabel('Velocidade [m/s]')
plt.grid(True)
plt.legend()

# ======= Plot 3: Juntas =======
plt.subplot(3, 1, 3)
plt.plot(tempos, np.degrees(juntas[:, 0]), label='θ₁ [°]', linestyle='--', color='orange')
plt.plot(tempos, np.degrees(juntas[:, 1]), label='θ₂ [°]', linestyle='--', color='purple')
plt.plot(tempos, juntas[:, 2], label='d₃ [m]', linestyle='-', color='blue')
plt.title('Posições das Juntas')
plt.xlabel('Tempo [s]')
plt.ylabel('Valor')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
