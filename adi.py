import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import subprocess
import platform
import speedtest
from datetime import datetime
import time
import re

# -----------------------------------
# Helper Functions
# -----------------------------------

def get_wifi_info():
    system_platform = platform.system()

    wifi_info = {
        'SSID': 'Unknown',
        'BSSID': 'Unknown',
        'Signal': None,
        'Frequency': 'Unknown',
        'Channel': 'Unknown'
    }

    try:
        if system_platform == 'Linux':
            result = subprocess.check_output(["iwconfig"], universal_newlines=True)
            ssid_match = re.search(r'ESSID:"(.+?)"', result)
            freq_match = re.search(r'Frequency:(\d+\.\d+)', result)
            signal_match = re.search(r'Signal level=(-?\d+) dBm', result)

            if ssid_match:
                wifi_info['SSID'] = ssid_match.group(1)
            if freq_match:
                wifi_info['Frequency'] = f"{freq_match.group(1)} GHz"
            if signal_match:
                wifi_info['Signal'] = int(signal_match.group(1))

        elif system_platform == 'Windows':
            result = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], universal_newlines=True)
            ssid_match = re.search(r'SSID\s+:\s(.*)', result)
            bssid_match = re.search(r'BSSID\s+:\s(.*)', result)
            signal_match = re.search(r'Signal\s+:\s(\d+)%', result)
            freq_match = re.search(r'Radio type\s+:\s(.*)', result)

            if ssid_match:
                wifi_info['SSID'] = ssid_match.group(1).strip()
            if bssid_match:
                wifi_info['BSSID'] = bssid_match.group(1).strip()
            if signal_match:
                wifi_info['Signal'] = int(signal_match.group(1).strip())
            if freq_match:
                wifi_info['Frequency'] = freq_match.group(1).strip()

    except Exception as e:
        st.error(f"Error fetching Wi-Fi info: {e}")

    return wifi_info

def get_latency(host="8.8.8.8"):
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', host]
        result = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True)
        output = result.stdout

        if platform.system().lower() == 'windows':
            latency_line = [line for line in output.splitlines() if "Average" in line]
            latency = latency_line[0].split('=')[-1].replace('ms', '').strip()
        else:
            latency_line = [line for line in output.splitlines() if "time=" in line]
            latency = latency_line[0].split('time=')[1].split(' ')[0]

        return float(latency)
    except Exception as e:
        st.warning(f"Latency check failed: {e}")
        return None

def run_speedtest():
    try:
        stest = speedtest.Speedtest()
        download_speed = round(stest.download() / 1_000_000, 2)  # Mbps
        upload_speed = round(stest.upload() / 1_000_000, 2)      # Mbps
        return download_speed, upload_speed
    except Exception as e:
        st.warning(f"Speedtest failed: {e}")
        return None, None

# -----------------------------------
# Streamlit App Layout
# -----------------------------------

st.set_page_config(page_title="Wi-Fi Signal Tracker & Optimizer", layout="wide")

st.title("📡 TarangWifi")
st.caption("Move around and find the best Wi-Fi spots in real time!")

# Initialize session state
if 'tracking' not in st.session_state:
    st.session_state.tracking = False
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Time', 'Location', 'SSID', 'BSSID', 'Signal', 'Latency', 'Download', 'Upload'])

# Sidebar Controls
with st.sidebar:
    st.header("Controls")
    location = st.text_input("🏷️ Enter Current Location", "Unknown")

    if st.button("🚀 Start Real-Time Tracking"):
        st.session_state.tracking = True
        st.session_state.last_update = 0  # Reset timer

    if st.button("🛑 Stop Tracking"):
        st.session_state.tracking = False

    st.markdown("---")

    if st.button("⚡ Run Speedtest"):
        st.info("Running speedtest...")
        d_speed, u_speed = run_speedtest()
        if d_speed and u_speed:
            st.success(f"Download: {d_speed} Mbps | Upload: {u_speed} Mbps")

    if st.button("⏱️ Check Latency"):
        st.info("Checking latency...")
        ping_latency = get_latency()
        if ping_latency:
            st.success(f"Latency: {ping_latency} ms")

# ------------------------
# Tracking Functionality
# ------------------------

if st.session_state.tracking:
    now = time.time()

    # Get Wi-Fi info and latency every 3 seconds
    wifi_info = get_wifi_info()
    latency = get_latency()

    # Optional: uncomment to run speed tests during tracking (could slow things down!)
    # download, upload = run_speedtest()
    download, upload = None, None

    current_time = datetime.now().strftime("%H:%M:%S")
    new_row = {
        'Time': current_time,
        'Location': location,
        'SSID': wifi_info['SSID'],
        'BSSID': wifi_info['BSSID'],
        'Signal': wifi_info['Signal'],
        'Latency': latency,
        'Download': download,
        'Upload': upload
    }

    # Append new data row
    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new_row])],
        ignore_index=True
    )

    st.session_state.last_update = now
    st.toast(f"Updated {current_time}")

    # Add live metrics display
    col1, col2, col3 = st.columns(3)
    wifi_col1, wifi_col2, wifi_col3 = st.columns(3)

    wifi_col1.metric("SSID", wifi_info.get('SSID', 'Unknown'))
    wifi_col2.metric("BSSID", wifi_info.get('BSSID', 'Unknown'))
    wifi_col3.metric("Frequency", wifi_info.get('Frequency', 'Unknown'))

    col1.metric("📶 Signal Strength", f"{wifi_info.get('Signal', 'N/A')} dBm")
    col2.metric("⏱️ Latency", f"{latency} ms" if latency is not None else "N/A")
    col3.metric("⚡ Download/Upload", f"{download} / {upload} Mbps" if download else "Not Tested")

    # Wait 3 seconds and rerun the app
    time.sleep(3)
    st.rerun()

# ------------------------
# Data & Graphs
# ------------------------

df = st.session_state.data

if not df.empty:
    st.subheader("📊 Real-Time Tracking Data")

    # Graph: Signal Strength
    fig_signal = go.Figure()
    fig_signal.add_trace(go.Scatter(
        x=df['Time'],
        y=df['Signal'],
        mode='lines+markers',
        name='Signal Strength (dBm)',
        line=dict(color='blue')
    ))
    fig_signal.update_layout(title="📶 Signal Strength Over Time", yaxis_title="dBm", xaxis_title="Time")
    st.plotly_chart(fig_signal, use_container_width=True)

    # Graph: Latency
    fig_latency = go.Figure()
    fig_latency.add_trace(go.Scatter(
        x=df['Time'],
        y=df['Latency'],
        mode='lines+markers',
        name='Latency (ms)',
        line=dict(color='orange')
    ))
    fig_latency.update_layout(title="⏱️ Latency Over Time", yaxis_title="ms", xaxis_title="Time")
    st.plotly_chart(fig_latency, use_container_width=True)

    # Graph: Speed
    fig_speed = go.Figure()
    fig_speed.add_trace(go.Scatter(
        x=df['Time'],
        y=df['Download'],
        mode='lines+markers',
        name='Download (Mbps)',
        line=dict(color='green')
    ))
    fig_speed.add_trace(go.Scatter(
        x=df['Time'],
        y=df['Upload'],
        mode='lines+markers',
        name='Upload (Mbps)',
        line=dict(color='purple')
    ))
    fig_speed.update_layout(title="⚡ Download / Upload Speeds Over Time", yaxis_title="Mbps", xaxis_title="Time")
    st.plotly_chart(fig_speed, use_container_width=True)

    # ------------------------
    # Summary Report
    # ------------------------
    if not st.session_state.tracking:
        st.subheader("📋 Summary Report")

        best_row = df.loc[df['Signal'].idxmax()]
        worst_row = df.loc[df['Signal'].idxmin()]

        st.markdown(f"**Best Spot** ➡️ `{best_row['Location']}` with **Signal** `{best_row['Signal']} dBm`")
        st.markdown(f"**Worst Spot** ➡️ `{worst_row['Location']}` with **Signal** `{worst_row['Signal']} dBm`")

        st.write("### Averages")
        st.write(f"📶 **Signal**: {df['Signal'].mean():.2f} dBm")
        st.write(f"⏱️ **Latency**: {df['Latency'].mean():.2f} ms")
        st.write(f"⚡ **Download Speed**: {df['Download'].mean():.2f} Mbps")
        st.write(f"⚡ **Upload Speed**: {df['Upload'].mean():.2f} Mbps")

        # Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Report as CSV", data=csv, file_name='wifi_report.csv', mime='text/csv')
# -----------------------------------
# Footer
# -----------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Made with ❤️ by <strong>Aditya Kumar Jha</strong>"
    "</div>",
    unsafe_allow_html=True
)
