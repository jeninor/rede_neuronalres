from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time
import math
import numpy as np
import matplotlib.pyplot as plt

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

def generate_workspace(sim, axes, tcp_handle):
    print('[INFO] Iniciando varredura da área de trabalho...')

    theta1_range = np.radians(np.linspace(-180, 180, 10))  # junta
    theta2_range = np.radians(np.linspace(0, 90, 10))  # junta
    d3_range = np.linspace(0.0, 0.5, 10)               # linear

    points = []

    total = len(theta1_range) * len(theta2_range) * len(d3_range)
    count = 0

    for t1 in theta1_range:
        for t2 in theta2_range:
            for d3 in d3_range:
                # Comando de posição
                sim.setJointTargetPosition(axes['axis1'], t1)
                sim.setJointTargetPosition(axes['axis2'], t2)
                sim.setJointTargetPosition(axes['axis3'], d3)
                time.sleep(0.01)

                # Leitura real da posição do TCP
                pose = sim.getObjectPose(tcp_handle, -1)
                position = pose[:3]
                points.append(position)

                count += 1
                if count % 100 == 0:
                    print(f'  - {count}/{total} pontos coletados...')

    return np.array(points)

def plot_workspace(points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=1, alpha=0.5, c='blue')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title('Área de Trabalho - Leitura Real do TCP')
    plt.tight_layout()
    plt.show()

def main():
    sim = connect_to_coppeliasim()
    scene_path = '/home/usuario/compartilhado/Robotica/Esferico.ttt'
    result = sim.loadScene(scene_path)
    if result == 0:
        raise RuntimeError("Erro ao carregar a cena.")
    print("[SUCCESS] Manipulador carregado com sucesso.")

    sim.startSimulation()
    time.sleep(0.5)

    axes = get_esferico_axes(sim)
    tcp_handle = sim.getObject('/Manipulador/axis4')

    points = generate_workspace(sim, axes, tcp_handle)
    plot_workspace(points)

    sim.stopSimulation()
    print('[DONE] Simulação finalizada.')

if __name__ == "__main__":
    main()
