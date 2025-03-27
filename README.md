# 

# 📡 TarangWifi – Wi-Fi Signal Tracker & Optimizer  

**Move around and find the best Wi-Fi spots in real time! 🚀**  

## 📌 Features  
✅ Real-time Wi-Fi signal tracking 📶  
✅ Internet speed & latency measurement ⚡  
✅ Interactive dashboards & data visualization 📊  
✅ Generate a CSV report for analysis 📥  

---

## 📂 Installation  

### **1️⃣ Install Dependencies**  
Run the following command:  
```sh
pip install streamlit pandas plotly speedtest-cli
```

### **2️⃣ Run the App**  
```sh
streamlit run app.py
```

---

## ⚙️ How It Works  

### **1. Get Wi-Fi Info (`get_wifi_info()`)**  
Extracts details like:  
- **SSID** (Network Name)  
- **BSSID** (MAC Address)  
- **Signal Strength** (**dBm**)  
- **Frequency** (**GHz**)  

#### **Signal Strength Conversion (Windows Only)**  
Wi-Fi signal percentage **(0-100%)** is converted to **dBm** using:  
\[
\text{Signal Strength (dBm)} = -30 + \left( \frac{\text{Signal Percentage} \times (-60)}{100} \right)
\]

Example: If signal is **80%**, then:  
\[
-30 + \left( \frac{80 \times (-60)}{100} \right) = -78 dBm
\]

---

### **2. Measure Network Latency (`get_latency()`)**  
Latency (**ping time**) is calculated using:  
\[
\text{Latency} = \frac{\text{Total Round Trip Time}}{\text{Number of Packets Sent}}
\]

For Linux: Extracts `time=X ms` from:  
```sh
64 bytes from 8.8.8.8: icmp_seq=1 ttl=57 time=12.3 ms
```

For Windows: Extracts `Average = X ms` from the output.

---

### **3. Run Speed Test (`run_speedtest()`)**  
Measures **Download** & **Upload speeds** using:  
\[
\text{Speed (Mbps)} = \frac{\text{Total Data Transferred (Megabits)}}{\text{Total Time (Seconds)}}
\]
- Converts bits/second to **Mbps** by dividing by **1,000,000**.  

---

## 📊 Real-Time Visualization  

### **📶 Signal Strength Over Time**
![Signal Strength Graph](https://via.placeholder.com/600x300?text=Signal+Graph)  

### **⏱️ Latency Over Time**
![Latency Graph](https://via.placeholder.com/600x300?text=Latency+Graph)  

### **⚡ Download & Upload Speeds**
![Speed Graph](https://via.placeholder.com/600x300?text=Speed+Graph)  

---

## 📋 Summary & CSV Report  

🏆 **Best Wi-Fi Spot** ➡️ *Based on max signal strength*  
🚨 **Worst Wi-Fi Spot** ➡️ *Based on weakest signal*  

### **Averages**  
📶 **Signal**: `X dBm`  
⏱️ **Latency**: `Y ms`  
⚡ **Download Speed**: `Z Mbps`  
⚡ **Upload Speed**: `W Mbps`  

📥 **Download Report as CSV**  

```sh
st.download_button("📥 Download Report as CSV", data=csv, file_name='wifi_report.csv', mime='text/csv')
```

---

## 📜 License  
MIT License © 2025 Aditya Kumar Jha  

