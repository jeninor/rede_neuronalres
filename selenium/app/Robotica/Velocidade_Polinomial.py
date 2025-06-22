import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import Polynomial

# Lendo os dados do arquivo
data = np.loadtxt("posicao_tempo.txt", skiprows=1)  # Pula o cabeçalho
tempos = data[:, 0]
posicoes = data[:, 1:4]  # X, Y, Z

# Normalizando o tempo para intervalo [0, 1]
tempo_normalizado = (tempos - tempos.min()) / (tempos.max() - tempos.min())

# Calculando a norma da posição
norma_posicao = np.linalg.norm(posicoes, axis=1)

# ==============================================
# Cálculo das velocidades no tempo ORIGINAL
# ==============================================
velocidades_original = np.zeros_like(posicoes)
for i in range(1, len(tempos)):
    dt = tempos[i] - tempos[i-1]
    if dt > 0:
        velocidades_original[i, :] = (posicoes[i, :] - posicoes[i-1, :]) / dt

velocidade_resultante_original = np.linalg.norm(velocidades_original, axis=1)

# ==============================================
# Cálculo das velocidades no tempo NORMALIZADO
# ==============================================
velocidades_normalizado = np.zeros_like(posicoes)
for i in range(1, len(tempo_normalizado)):
    dt_norm = tempo_normalizado[i] - tempo_normalizado[i-1]
    if dt_norm > 0:
        # Usamos a mesma diferença de posição, mas dividimos pelo delta do tempo normalizado
        velocidades_normalizado[i, :] = (posicoes[i, :] - posicoes[i-1, :]) / dt_norm

velocidade_resultante_norm = np.linalg.norm(velocidades_normalizado, axis=1)

# ==============================================
# Cálculo das curvas de tendência
# ==============================================

# Para tempo normalizado
coef_norm = Polynomial.fit(tempo_normalizado, velocidade_resultante_norm, 2).convert().coef
tendencia_norm = np.polyval(coef_norm[::-1], tempo_normalizado)

# ==============================================
# Plotagem dos resultados
# ==============================================
plt.figure(figsize=(12, 18))

# Gráfico 1: Posições originais
plt.subplot(3, 1, 1)
plt.plot(tempos, posicoes[:, 0], 'r-', label='X', alpha=0.6)
plt.plot(tempos, posicoes[:, 1], 'g-', label='Y', alpha=0.6)
plt.plot(tempos, posicoes[:, 2], 'b-', label='Z', alpha=0.6)
plt.xlabel('Tempo (s)')
plt.ylabel('Posição (m)')
plt.legend()
plt.grid(True)

# Gráfico 2: Velocidade no tempo original
plt.subplot(3, 1, 2)
plt.plot(tempos, velocidade_resultante_original, 'k-', linewidth=1.5, label='Velocidade Resultante', alpha=0.6)
plt.xlabel('Tempo (s)')
plt.ylabel('Velocidade (m/s)')
plt.legend()
plt.grid(True)

# Gráfico 3: Velocidade no tempo normalizado
plt.subplot(3, 1, 3)
plt.plot(tempo_normalizado, velocidade_resultante_norm, 'b-', linewidth=1.5, label='Velocidade Resultante', alpha=0.6)
plt.plot(tempo_normalizado, tendencia_norm, 'r--', linewidth=2, label='Tendência (normalizada)')
plt.xlabel('Tempo Normalizado [0,1]')
plt.ylabel('Velocidade (m/s)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

print("\nEquação da tendência:")
print(f"v(t_norm) = {coef_norm[2]:.2f}t² + {coef_norm[1]:.2f}t + {coef_norm[0]:.2f}")