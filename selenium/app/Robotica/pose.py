from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time

client = RemoteAPIClient()
sim = client.getObject('sim')

# Iniciar simulação, se necessário
if sim.getSimulationState() == sim.simulation_stopped:
    sim.startSimulation()
    time.sleep(0.5)

# Obter o handle do efetuador final (TCP)
tcp_handle = sim.getObject('/UR10/link7_visible')  # ou o nome do seu último link

# Referência: usar o referencial global (mundo)
world_frame = -1  # padrão para referencial absoluto

# Ler a pose [x, y, z, qx, qy, qz, qw]
pose = sim.getObjectPose(tcp_handle, world_frame)

position = pose[:3]
quaternion = pose[3:]

print(f'[INFO] Posição (x, y, z): {position}')
print(f'[INFO] Orientação (quaternion): {quaternion}')
