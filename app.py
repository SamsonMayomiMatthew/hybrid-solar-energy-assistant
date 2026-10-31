import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="AI Hybrid Solar Mini-Grid Assistant",
    page_icon="⚡",
    layout="wide"
)

# Title and Overview
st.title("⚡ AI-Driven Hybrid Solar Mini-Grid Energy Assistant")
st.markdown("""
This application simulates real-time time-series telemetry from a hybrid solar photovoltaic (PV) 
mini-grid installation. It applies rule-based AI logic and automated evaluation to optimize load distribution, 
manage battery state-of-charge (SoC), and prevent power outages.
""")

# Data Simulation Function
@st.cache_data
def generate_solar_data():
    np.random.seed(42)
    hours = pd.date_range(start="2026-10-31 00:00:00", periods=24, freq="h")
    
    # Simulate solar generation (peaks at midday 12 PM, zero at night)
    solar_gen = [max(0, 1.5 * np.sin((h - 6) * np.pi / 12)) if 6 <= h <= 18 else 0 for h in hours.hour]
    # Simulate variable load demand
    load_demand = np.random.uniform(0.4, 1.1, size=24)
    # Simulate battery state of charge (%) based on net generation vs demand
    net_power = np.array(solar_gen) - load_demand
    battery_soc = np.clip(80 + np.cumsum(net_power * 15), 15, 100)
    
    df = pd.DataFrame({
        "Timestamp": hours,
        "Solar_Gen_kW": [round(val, 2) for val in solar_gen],
        "Load_Demand_kW": [round(val, 2) for val in load_demand],
        "Battery_SoC_%": [round(val, 1) for val in battery_soc]
    })
    return df

# AI Logic / Recommendation Engine
def analyze_energy_status(row):
    if row["Battery_SoC_%"] < 30:
        return "🔴 CRITICAL: Low Battery SoC. Automatically shed non-essential administrative loads."
    elif row["Solar_Gen_kW"] > row["Load_Demand_kW"] + 0.3:
        return "🟢 OPTIMAL: Surplus solar power available. Ideal window to run high-load appliances or charge aux storage."
    else:
        return "🟡 STABLE: Balanced system operation utilizing grid and solar mix."

# Load data
df = generate_solar_data()
df["AI_Recommendation"] = df.apply(lambda row: analyze_energy_status(row), axis=1)

# Dashboard Metrics layout
latest = df.iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric("Current Solar Generation", f"{latest['Solar_Gen_kW']} kW", delta="+0.2 kW vs avg")
col2.metric("Current Load Demand", f"{latest['Load_Demand_kW']} kW", delta="-0.1 kW")
col3.metric("Battery State of Charge", f"{latest['Battery_SoC_%']}%", delta="Stable" if latest['Battery_SoC_%'] > 30 else "Low Warning")

st.divider()

# Charts Section
st.subheader("📊 24-Hour Solar Generation vs. Load Demand")
chart_data = df.set_index("Timestamp")[["Solar_Gen_kW", "Load_Demand_kW"]]
st.line_chart(chart_data)

# AI Insights Table Section
st.subheader("💡 Automated AI Recommendations & Telemetry Log")
st.dataframe(df[["Timestamp", "Solar_Gen_kW", "Load_Demand_kW", "Battery_SoC_%", "AI_Recommendation"]], use_container_width=True)

# Footer info
st.markdown("---")
st.markdown("**Capstone Project** | Built for 3MTT & Meta AI Skills Development Programme")
