import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="FR2 Beam Spoiling Simulator", layout="wide")

st.title("📡 FR2 Antenna Beam Broadening Tool")
st.markdown("""
This tool simulates an **8-channel beamformer** driving a **4x8 patch array**. 
The system is modeled as a **2 (Horizontal) x 4 (Vertical)** grid of 2x2 sub-arrays.
""")

# --- Sidebar Controls ---
st.sidebar.header("System Parameters")
freq_ghz = st.sidebar.slider("Frequency (GHz)", 24.0, 40.0, 31.0, 0.1)
phase_delta_deg = st.sidebar.slider("Azimuth Phase Offset (Degrees)", 0, 180, 88)

# Physical Constants
c = 3e8
freq = freq_ghz * 1e9
lam = c / freq
k = 2 * np.pi / lam

# Assume lambda/2 spacing for the sub-array centers
d_h = lam / 2 # Horizontal spacing (between Column A and B)
d_v = lam / 2 # Vertical spacing (between the 4 rows)

# --- Calculation Logic ---
def get_patterns():
    theta = np.linspace(-90, 90, 500)
    theta_rad = np.radians(theta)
    
    # Symmetric Phase: -phi/2 on left, +phi/2 on right
    half_phase = np.radians(phase_delta_deg) / 2
    
    # E1 = exp(-j * half_phase), E2 = exp(j * (k*d*sin(theta) + half_phase))
    # This keeps the phase center at the physical center of the array
    term1 = np.exp(-1j * half_phase)
    term2 = np.exp(1j * (k * d_h * np.sin(theta_rad) + half_phase))
    
    af_az = np.abs(term1 + term2) / 2
    
    # Elevation remains the same (Symmetric by default if no tilt applied)
    psi_el = k * d_v * np.sin(theta_rad) 
    with np.errstate(divide='ignore', invalid='ignore'):
        af_el = np.abs(np.sin(4 * psi_el / 2) / (4 * np.sin(psi_el / 2)))
        af_el = np.nan_to_num(af_el, nan=1.0)

    return theta, 20 * np.log10(af_az + 1e-6), 20 * np.log10(af_el + 1e-6)


theta, mag_az, mag_el = get_patterns()

# --- GUI Layout ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Azimuth Plot (Beam Broadening)")
    fig_az, ax_az = plt.subplots()
    ax_az.plot(theta, mag_az, color='#FF4B4B', lw=2, label=f"Phase Delta: {phase_delta_deg}°")
    ax_az.axhline(-3, color='black', linestyle='--', alpha=0.5, label="-3dB BW")
    ax_az.set_ylim([-30, 0])
    ax_az.set_xlim([-90, 90])
    ax_az.set_xlabel("Angle (Deg)")
    ax_az.set_ylabel("Normalized Gain (dB)")
    ax_az.grid(True, alpha=0.3)
    ax_az.legend()
    st.pyplot(fig_az)

with col2:
    st.subheader("Elevation Plot (Fixed)")
    fig_el, ax_el = plt.subplots()
    ax_el.plot(theta, mag_el, color='#1C83E1', lw=2)
    ax_el.axhline(-3, color='black', linestyle='--', alpha=0.5)
    ax_el.set_ylim([-30, 0])
    ax_el.set_xlim([-90, 90])
    ax_el.set_xlabel("Angle (Deg)")
    ax_el.set_ylabel("Normalized Gain (dB)")
    ax_el.grid(True, alpha=0.3)
    st.pyplot(fig_el)

# --- Array Visualization ---
st.divider()
st.subheader("Logical Array Configuration (8 Channels)")
st.write("Each block represents a **2x2 sub-array** controlled by one beamformer channel.")

# Visualizing the 2x4 grid
grid_html = f"""
<div style="display: flex; justify-content: center;">
    <table style="border: 2px solid white; text-align: center;">
        <tr>
            <th style="padding: 10px; border: 1px solid gray;">Left Column (0°)</th>
            <th style="padding: 10px; border: 1px solid gray;">Right Column ({phase_delta_deg}°)</th>
        </tr>
        {" ".join([f'<tr><td style="padding: 20px; border: 1px solid gray; background-color: #262730;">CH {i}</td><td style="padding: 20px; border: 1px solid gray; background-color: #262730;">CH {i+4}</td></tr>' for i in range(1, 5)])}
    </table>
</div>
"""
st.markdown(grid_html, unsafe_allow_html=True)

# --- Analysis Text ---
bw_idx = np.where(mag_az >= -3)[0]
estimated_bw = theta[bw_idx[-1]] - theta[bw_idx[0]] if len(bw_idx) > 0 else 0

st.info(f"""
**Technical Analysis:**
- **Estimated Azimuth Beamwidth:** ~{estimated_bw:.1f}°
- **Frequency:** {freq_ghz} GHz (λ ≈ {lam*1000:.2f} mm)
- **Observation:** At ~90° phase delta, you will see the beam 'flatten.' Beyond 100°, the boresight gain drops significantly as the beam bifurcates.
""")
