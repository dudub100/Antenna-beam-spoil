import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="FR2 Beam Widening", layout="wide")

st.title("📡 FR2 Azimuth Widening Tool (31 GHz)")

# --- Sidebar ---
st.sidebar.header("1. Calibration")
# Adjust d_lambda until Phase 0 shows your 30° baseline
d_lambda = st.sidebar.slider("Column Spacing (d/λ)", 0.5, 2.0, 1.15, 0.01)

st.sidebar.header("2. Beam Widening")
# This is the "Divergence Phase"
phase_div_deg = st.sidebar.slider("Divergence Phase (Deg)", 0, 180, 90)

# --- Physics ---
freq = 31e9
c = 3e8
lam = c / freq
k = 2 * np.pi / lam
d = d_lambda * lam

theta = np.linspace(-90, 90, 1000)
theta_rad = np.radians(theta)

# 1. Element Pattern (Standard Patch)
ep = np.cos(theta_rad)**1.5 

# 2. Array Factor (Symmetric)
# Applying -phi/2 to left and +phi/2 to right
phi_rad = np.radians(phase_div_deg)
# Resulting AF = |exp(-j*phi/2) + exp(j*(k*d*sin(theta) + phi/2))|
# Normalized: cos((k*d*sin(theta) + phi) / 2)
psi = (k * d * np.sin(theta_rad) + phi_rad) / 2
af = np.abs(np.cos(psi))

# 3. Total Pattern
total_lin = af * ep
total_db = 20 * np.log10(total_lin + 1e-6)

# --- Analysis ---
indices = np.where(total_db >= -3)[0]
bw = theta[indices[-1]] - theta[indices[0]] if len(indices) > 0 else 0

# --- Plot ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(theta, total_db, color='red', lw=2, label="Resulting Beam")
ax.axhline(-3, color='black', linestyle='--', alpha=0.5)
ax.axvline(22.5, color='green', linestyle=':', label="Target ±22.5°")
ax.axvline(-22.5, color='green', linestyle=':')
ax.set_ylim([-25, 0])
ax.set_xlim([-90, 90])
ax.set_ylabel("Gain (dB)")
ax.set_xlabel("Angle (Deg)")
ax.legend()
st.pyplot(fig)

st.metric("Measured Beamwidth", f"{bw:.1f}°")

st.info(f"""
**Action Plan:**
1. Keep **CH 1-4** at phase $0^\circ$.
2. Set **CH 5-8** to phase ${phase_div_deg}^\circ$.
3. This creates the divergence needed to hit {bw:.1f}°.
""")
