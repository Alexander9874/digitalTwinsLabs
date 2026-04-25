#! /usr/bin/python3

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

D_0 = 8000
H_0 = 2000
psi = 0.0
V = 600
U = 300
K = 3
phi_max = 0.6

x_a0, y_a0 = 0.0, 0.0
x_b0, y_b0 = float(D_0), float(H_0)
theta0 = np.arctan2(y_b0 - y_a0, x_b0 - x_a0)
phi0 = theta0

state0 = [x_a0, y_a0, x_b0, y_b0, phi0]

def ode_system(t, s):
    x_a, y_a, x_b, y_b, phi = s

    dx, dy = x_b - x_a, y_b - y_a
    R  = np.sqrt(dx**2 + dy**2)

    theta = np.arctan2(dy, dx)

    if R > 1e-6:
        dtheta_dt = (-V * np.sin(phi - theta) + U * np.sin(psi + theta)) / R
    else:
        dtheta_dt = 0.0

    dphi_dt = np.clip(K * dtheta_dt, -phi_max, phi_max)

    dx_a = V * np.cos(phi)
    dy_a = V * np.sin(phi)
    dx_b = -U * np.cos(psi)
    dy_b = U * np.sin(psi)

    return [dx_a, dy_a, dx_b, dy_b, dphi_dt]

def event_close(t, s):
    x_a, y_a, x_b, y_b, _ = s
    return np.sqrt((x_b - x_a)**2 + (y_b - y_a)**2) - 60.0

event_close.terminal = True
event_close.direction = -1

sol = solve_ivp(
    ode_system,
    t_span=(0, 10000),
    y0=state0,
    events=event_close,
    max_step=0.05,
    rtol=1e-9,
    atol=1e-11,
)

if sol.status != 1:
    raise RuntimeError("t_span")

t = sol.t
x_a = sol.y[0]
y_a = sol.y[1]
x_b = sol.y[2]
y_b = sol.y[3]
phi = sol.y[4]

dphi_dt = np.array([ode_system(t[i], sol.y[:, i])[4] for i in range(len(t))])


print(f"x = {x_a[-1]:.4f}\ny = {y_a[-1]:.4f}\nt = {t[-1]:.4f}")


fig1, ax1 = plt.subplots(figsize=(11, 7))

ax1.plot(x_a, y_a, color='blue', lw=2, label='Траектория A')
ax1.plot(x_b, y_b, color='red', lw=2, label='Траектория B')
ax1.plot(x_a[0], y_a[0], 'o', color='blue', ms=8, zorder=5)
ax1.plot(x_b[0], y_b[0], 'o', color='red', ms=8, zorder=5)

los_idx = np.linspace(0, len(t) - 1, 10, dtype=int)
for k, i in enumerate(los_idx):
    label = 'Линия визирования' if k == 0 else None
    ax1.plot([x_a[i], x_b[i]], [y_a[i], y_b[i]], color='seagreen', lw=1, ls='--', alpha=0.7, label=label)
    ax1.plot(x_a[i], y_a[i], '.', color='blue', ms=6, zorder=4)
    ax1.plot(x_b[i], y_b[i], '.', color='red', ms=6, zorder=4)

ax1.set_xlabel('x, м', fontsize=12)
ax1.set_ylabel('y, м', fontsize=12)
ax1.set_title('Траектории движения объектов A и B', fontsize=13)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.4)
ax1.set_aspect('equal', adjustable='datalim')
fig1.tight_layout()

fig2, ax2 = plt.subplots(figsize=(10, 5))

ax2.plot(t, dphi_dt, lw=2, label='Перегрузка')
ax2.set_xlabel('t, с', fontsize=12)
ax2.set_ylabel('Перегрузка, рад/с', fontsize=12)
ax2.set_title('Перегрузка от времени', fontsize=13)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.4)
fig2.tight_layout()

plt.show()
