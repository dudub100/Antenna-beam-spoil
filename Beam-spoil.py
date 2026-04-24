import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📡 FR2 Symmetric Beam Broadening (31 GHz)")

# --- Sidebar ---
st.sidebar.header("1. Physical Setup")
freq_ghz = st.sidebar.number_input("Frequency (GHz)", value=31.0)
# Adjust this to get your 30° baseline (typically 1.0 to 1.2)
d_lam = st.sidebar.slider("Sub-array Spacing (d/λ)", 0.5, 2.0, 1.15, 0.01)

st.sidebar.header("2. Element Pattern (Patch)")
n_pow = st.sidebar.slider("Patch Directivity (cos^n)", 1.0, 3.0, 1.5)

st.sidebar.header("3. Broadening Control")
# This is the total phase DIFFERENCE between the two columns
delta_phi = st.sidebar.slider("Phase Delta (Degrees)", 0, 180, 0)

# --- Calculations ---
c = 3e8
lam = c / (freq_ghz * 1e9)
k = 2 * np.pi / lam
d = d_lam * lam

theta = np.linspace(-90, 90, 1000)
theta_rad = np.radians(theta)

# A. ELEMENT PATTERN (EP)
# The "envelope" of a single patch element
ep_lin = np.where(np.cos(theta_rad) > 0, np.cos(theta_rad)**n_pow, 0)
ep_db = 20 * np.log10(ep_lin + 1e-6)

# B. SYMMETRIC ARRAY FACTOR (AF)
# We apply phase symmetrically to prevent steering
phi_rad = np.radians(delta_phi)
# AF = | exp(-j*(kd/2*sin(theta) + phi/2)) + exp(j*(kd/2*sin(theta) + phi/2)) | / 2
# Simplifies to: cos( (k*d*sin(theta) + phi) / 2 )
psi = (k * d * np.sin(theta_rad) + phi_rad) / 2
af_lin = np.abs(np.cos(psi))
af_db = 20 * np.log10(af_lin + 1e-6)

# C. TOTAL PATTERN
total_lin = af_lin * ep_lin
total_db = 20 * np.log10(total_lin + 1e-6)

# --- Beamwidth Calculation ---
try:
    # Find -3dB points relative to the PEAK of the total pattern
    peak_val = np.max(total_db)
    idx = np.where(total_db >= (peak_val - 3))[0]
    bw = theta[idx[-1]] - theta[idx[0]]
except:
    bw = 0

# --- Plotting ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(theta, total_db, color='red', lw=3, label="Total Pattern (Array)")
ax.plot(theta, ep_db, color='blue', lw=1, ls='--', label="Single Element Pattern")

ax.axhline(np.max(total_db) - 3, color='black', ls=':', label="-3dB level")
ax.axvline(22.5, color='green', ls='--', alpha=0.5, label="Target ±22.5°")
ax.axvline(-22.5, color='green', ls='--', alpha=0.5)

ax.set_ylim([-30, 5])
ax.set_xlim([-90, 90])
ax.set_title(f"Symmetric Beam at {freq_ghz} GHz | BW: {bw:.1f}°")
ax.set_xlabel("Azimuth Angle (Degrees)")
ax.set_ylabel("Gain (dB)")
ax.legend()
ax.grid(True, alpha=0.2)

st.pyplot(fig)

# --- Results ---
st.write(f"**Current Beamwidth:** {bw:.1f}°")
st.info(f"To achieve this, set Channels 1-4 to **{-delta_phi/2}°** and Channels 5-8 to **{delta_phi/2}°**.")
