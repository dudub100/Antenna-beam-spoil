import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="FR2 Beam Analysis", layout="wide")

st.title("📡 31 GHz Antenna Array: Full Pattern Analysis")
st.markdown("""
This simulation combines the **Symmetric Array Factor** (from your 8-channel beamformer) 
with a **Rectangular Patch Element Pattern**.
""")

# --- Sidebar Controls ---
st.sidebar.header("1. Calibration (Baseline)")
freq_ghz = st.sidebar.slider("Frequency (GHz)", 24.0, 40.0, 31.0)
# Adjust this until Phase Delta 0 matches your native +/- 15 deg beamwidth
d_over_lambda = st.sidebar.slider("Column Spacing (d/λ)", 0.5, 1.5, 1.15, 0.05)

st.sidebar.header("2. Element Characteristics")
# n=1 is a standard patch, n=1.5 to 2 is more directive
n_factor = st.sidebar.slider("Patch Directivity (cos^n)", 1.0, 3.0, 1.5, 0.1)

st.sidebar.header("3. Beam Control")
phase_delta_deg = st.sidebar.slider("Total Phase Delta (Degrees)", 0, 180, 85)

# --- Constants & Calculations ---
c = 3e8
freq = freq_ghz * 1e9
lam = c / freq
k = 2 * np.pi / lam
d_h = d_over_lambda * lam

theta = np.linspace(-90, 90, 1000)
theta_rad = np.radians(theta)

# A. ELEMENT PATTERN (EP)
# Standard patch approximation: cos^n(theta)
# We mask negative values to 0 to simulate the ground plane (no back radiation)
ep = np.where(np.cos(theta_rad) > 0, np.cos(theta_rad)**n_factor, 0)

# B. ARRAY FACTOR (AF)
# Symmetric phase to keep boresight centered
phi_rad = np.radians(phase_delta_deg)
# AF for two points: |exp(-j*psi) + exp(j*psi)| / 2 = cos(psi)
psi = (k * d_h * np.sin(theta_rad) + phi_rad) / 2
af = np.abs(np.cos(psi))

# C. TOTAL PATTERN
total_pattern_linear = af * ep
total_pattern_db = 20 * np.log10(total_pattern_linear + 1e-6)

# --- Find Beamwidth ---
# Find indices where gain is above -3dB
indices = np.where(total_pattern_db >= -3)[0]
if len(indices) > 1:
    bw_low = theta[indices[0]]
    bw_high = theta[indices[-1]]
    total_bw = bw_high - bw_low
else:
    bw_low = bw_high = total_bw = 0

# --- Plotting ---
fig, ax = plt.subplots(figsize=(12, 6))

# Plot Total Pattern
ax.plot(theta, total_pattern_db, color='#FF4B4B', lw=3, label="Total Pattern (AF * EP)")
# Plot Element Pattern for reference
ax.plot(theta, 20 * np.log10(ep + 1e-6), color='gray', linestyle='--', alpha=0.5, label="Single Element Pattern")

# Formatting
ax.axhline(-3, color='black', linestyle=':', label="-3dB Threshold")
ax.axvline(22.5, color='green', linestyle='--', alpha=0.6, label="Target ±22.5°")
ax.axvline(-22.5, color='green', linestyle='--', alpha=0.6)

ax.set_ylim([-30, 5])
ax.set_xlim([-90, 90])
ax.set_xlabel("Angle (Degrees)")
ax.set_ylabel("Normalized Gain (dB)")
ax.set_title(f"Radiation Pattern at {freq_ghz} GHz")
ax.legend(loc='upper right')
ax.grid(True, alpha=0.2)

st.pyplot(fig)

# --- Metric Dashboard ---
m1, m2, m3 = st.columns(3)
m1.metric("Calculated Total BW", f"{total_bw:.1f}°")
m2.metric("Left -3dB Point", f"{bw_low:.1f}°")
m3.metric("Right -3dB Point", f"{bw_high:.1f}°")

st.divider()
st.subheader("Implementation Steps for 45° Beam")
st.write(f"""
1. **Calibrate:** Set Phase to 0 and adjust **Column Spacing** until BW is 30°.
2. **Broaden:** Increase **Phase Delta** until Total BW hits 45°.
3. **Register Settings:**
    * **Channels 1-4:** Apply Phase **{-phase_delta_deg/2:.1f}°**
    * **Channels 5-8:** Apply Phase **{phase_delta_deg/2:.1f}°**
""")
