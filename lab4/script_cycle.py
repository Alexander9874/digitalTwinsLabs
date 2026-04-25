#! /usr/bin/python3

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

D_0 = 8000
H_0 = 2000
psi = 0.0
V = 600
U = 300
phi_max = 0.6

x_a0 = 0.0
y_a0 = 0.0
x_b0 = float(D_0)
y_b0 = float(H_0)
theta0 = np.arctan2(y_b0 - y_a0, x_b0 - x_a0)
phi0 = theta0

state0 = [x_a0, y_a0, x_b0, y_b0, phi0]

def ode_system(t, s):
    x_a, y_a, x_b, y_b, phi = s

    dx = x_b - x_a
    dy = y_b - y_a
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

fig1, ax1 = plt.subplots(figsize=(11, 7))
fig2, ax2 = plt.subplots(figsize=(10, 5))

for K in [1.0, 2.0, 2.5, 3.0]:
    sol = solve_ivp(
        ode_system,
        t_span=(0, 1000),
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

    label = 'Траектория A при K = ' + str(K)
    if K == 1:
        ax1.plot(x_b, y_b, lw=1, color='black', label='Траектория B')
    ax1.plot(x_a, y_a, lw=1, label=label)

    lable = 'Перегрузка при K = ' + str(K) +' , рад/с'

    ax2.plot(t, dphi_dt, lw=1, label=lable)

ax1.set_xlabel('x, м', fontsize=12)
ax1.set_ylabel('y, м', fontsize=12)
ax1.set_title('Траектории движения объектов A и B', fontsize=13)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.4)
ax1.set_aspect('equal', adjustable='datalim')
fig1.tight_layout()

ax2.set_xlabel('t, с', fontsize=12)
ax2.set_ylabel('Перегрузка, рад/с', fontsize=12)
ax2.set_title('Перегрузки от времени', fontsize=13)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.4)
fig2.tight_layout()

plt.show()
