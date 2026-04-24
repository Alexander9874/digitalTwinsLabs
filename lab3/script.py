import numpy as np
import matplotlib.pyplot as plt

L = 8000.0
H = 2000.0
X0 = 300.0
V = 300.0
theta_deg = 0.0
T1 = 0.25
T2 = 0.25
delta_deg = 2.0

theta = np.radians(theta_deg)
delta = np.radians(delta_deg)


y0 = np.sqrt(L**2 - H**2)

t_end = y0 / (V * np.cos(theta))

dt = 0.1
t = np.arange(0, t_end + dt, dt)
n_steps = len(t)

y = y0 - V * t * np.cos(theta)

phi_true = np.arctan(y / X0)
psi_true = np.arctan((H + V * t * np.sin(theta)) / np.sqrt(X0**2 + y**2))

phi_deg = np.degrees(phi_true)
psi_deg = np.degrees(psi_true)

plt.plot(t, phi_deg, 'b-', label='Азимут φ')    
plt.plot(t, psi_deg, 'r-', label='Возвышение ψ')
plt.xlabel('Время, с')  
plt.ylabel('Угол, град')
plt.title('Истинные углы визирования')
plt.grid(True)
plt.legend()
plt.show()


phi_c = np.zeros(n_steps)
psi_c = np.zeros(n_steps)

phi_c[0] = phi_true[0]
psi_c[0] = psi_true[0]

for i in range(n_steps - 1):
    phi_c[i+1] = phi_c[i] + (phi_true[i] - phi_c[i]) / T1 * dt
    psi_c[i+1] = psi_c[i] + (psi_true[i] - psi_c[i]) / T2 * dt

delta_phi = phi_true - phi_c
delta_psi = psi_true - psi_c

delta_phi_deg = np.degrees(delta_phi)
delta_psi_deg = np.degrees(delta_psi)

plt.plot(t, delta_phi_deg, 'b-', alpha=0.7, label='Δφ без шума')
plt.plot(t, delta_psi_deg, 'r-', alpha=0.7, label='Δψ без шума')
plt.xlabel('Время, с')
plt.ylabel('Ошибка, град')
plt.title('Ошибки без помех')
plt.grid(True)
plt.legend()
plt.show()


np.random.seed(67)

phi_c = np.zeros(n_steps)
psi_c = np.zeros(n_steps)

phi_c[0] = phi_true[0]
psi_c[0] = psi_true[0]

noise_phi = np.random.uniform(-delta/2, delta/2, size=n_steps)
noise_psi = np.random.uniform(-delta/2, delta/2, size=n_steps)

for i in range(n_steps - 1):
    err_phi = phi_true[i] - phi_c[i]
    err_psi = psi_true[i] - psi_c[i]

    dphi_c = (err_phi / T1) * dt + noise_phi[i] * dt
    dpsi_c = (err_psi / T2) * dt + noise_psi[i] * dt

    phi_c[i+1] = phi_c[i] + dphi_c
    psi_c[i+1] = psi_c[i] + dpsi_c

delta_phi = phi_true - phi_c
delta_psi = psi_true - psi_c

delta_phi_deg = np.degrees(delta_phi)
delta_psi_deg = np.degrees(delta_psi)

plt.plot(t, delta_phi_deg, 'b-', label='Δφ с шумом')
plt.plot(t, delta_psi_deg, 'r-', label='Δψ с шумом')
plt.xlabel('Время, с')
plt.ylabel('Ошибка, град')
plt.title('Ошибки при наличии помех')
plt.grid(True)
plt.legend()
plt.show()


print(f"Время наблюдения: {t_end:.3f} с")
