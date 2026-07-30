import streamlit as st
import pandas as pd
import math

# ---------- CROP DATABASE (SIMPLE RULES) ----------
crop_data = {
    'Rice': {
        'optimal': {'N': 80, 'P': 40, 'K': 40, 'pH': 6.5},
        'base_yield': 3.5,
        'price_per_ton': 22000,
        'cost_per_hectare': 22000
    },
    'Wheat': {
        'optimal': {'N': 120, 'P': 60, 'K': 60, 'pH': 7.0},
        'base_yield': 3.0,
        'price_per_ton': 24000,
        'cost_per_hectare': 24000
    },
    'Maize': {
        'optimal': {'N': 150, 'P': 70, 'K': 50, 'pH': 6.8},
        'base_yield': 4.0,
        'price_per_ton': 20000,
        'cost_per_hectare': 20000
    },
    'Sugarcane': {
        'optimal': {'N': 200, 'P': 100, 'K': 100, 'pH': 7.2},
        'base_yield': 8.0,
        'price_per_ton': 3500,
        'cost_per_hectare': 40000
    },
    'Cotton': {
        'optimal': {'N': 100, 'P': 50, 'K': 70, 'pH': 7.0},
        'base_yield': 2.5,
        'price_per_ton': 60000,
        'cost_per_hectare': 28000
    }
}

# ---------- APP UI ----------
st.set_page_config(page_title="Smart Agri Advisor", page_icon="🌾", layout="centered")

st.title("🌾 Smart Agri Advisor (Lite)")
st.markdown("**No AI training required! Instant recommendations based on soil science.**")
st.markdown("---")

# Inputs
col1, col2 = st.columns(2)
with col1:
    crop = st.selectbox("🌱 Select Crop", list(crop_data.keys()))
    land_area = st.number_input("📏 Land Area (Hectares)", min_value=0.5, max_value=100.0, value=1.0, step=0.5)
    nitrogen = st.slider("🌱 Nitrogen (N)", 0, 250, 80)
    phosphorus = st.slider("💧 Phosphorus (P)", 0, 150, 50)

with col2:
    potassium = st.slider("🥔 Potassium (K)", 0, 150, 50)
    ph = st.slider("🧪 Soil pH", 4.0, 9.0, 6.8, 0.1)
    temperature = st.slider("🌡️ Temperature (°C)", 10, 40, 25)
    rainfall = st.slider("☔ Rainfall (mm)", 50, 400, 150)

# ---------- LOGIC (No ML, Pure Math) ----------
def get_recommendations(crop, N, P, K, pH):
    opt = crop_data[crop]['optimal']
    recs = []
    
    # N Recommendation
    if N < opt['N'] * 0.8:
        recs.append(f"🌱 **Nitrogen**: Low! Add Urea or DAP (Need ~{opt['N'] - N} kg/ha more)")
    elif N > opt['N'] * 1.3:
        recs.append(f"⚠️ **Nitrogen**: High! Reduce application to avoid burning")
    else:
        recs.append(f"✅ **Nitrogen**: Optimal! Current level is perfect")
    
    # P Recommendation
    if P < opt['P'] * 0.8:
        recs.append(f"💧 **Phosphorus**: Low! Add SSP or DAP (Need ~{opt['P'] - P} kg/ha more)")
    elif P > opt['P'] * 1.3:
        recs.append(f"⚠️ **Phosphorus**: High! Reduce application")
    else:
        recs.append(f"✅ **Phosphorus**: Optimal! Current level is perfect")
    
    # K Recommendation
    if K < opt['K'] * 0.8:
        recs.append(f"🥔 **Potassium**: Low! Add MOP (Need ~{opt['K'] - K} kg/ha more)")
    elif K > opt['K'] * 1.3:
        recs.append(f"⚠️ **Potassium**: High! Reduce application")
    else:
        recs.append(f"✅ **Potassium**: Optimal! Current level is perfect")
    
    # pH Recommendation
    if pH < 5.5:
        recs.append(f"⚖️ **Soil pH**: Too Acidic! Add Lime (Recommended: {opt['pH']:.1f})")
    elif pH > 7.5:
        recs.append(f"⚖️ **Soil pH**: Too Alkaline! Add Gypsum (Recommended: {opt['pH']:.1f})")
    else:
        recs.append(f"✅ **Soil pH**: Optimal! Current level is perfect")
    
    return recs

def calculate_yield(crop, N, P, K, pH):
    opt = crop_data[crop]['optimal']
    
    # Calculate deviation (0 = perfect, higher = worse)
    deviation = (
        abs(N - opt['N']) / opt['N'] * 0.4 +
        abs(P - opt['P']) / opt['P'] * 0.3 +
        abs(K - opt['K']) / opt['K'] * 0.2 +
        abs(pH - opt['pH']) / opt['pH'] * 0.1
    )
    
    # Yield drops by max 70% if everything is wrong
    penalty = min(deviation * 0.5, 0.7) 
    predicted_yield = crop_data[crop]['base_yield'] * (1 - penalty)
    
    # Add some randomness effect of temp and rain (simplified bonus/penalty)
    if 20 <= temperature <= 30:
        predicted_yield *= 1.05  # 5% bonus for good temp
    else:
        predicted_yield *= 0.95  # 5% penalty
    
    if 100 <= rainfall <= 200:
        predicted_yield *= 1.05
    else:
        predicted_yield *= 0.95
        
    return round(max(0.5, predicted_yield), 2)

# ---------- SHOW RESULTS ----------
if st.button("🚀 Get Advice", type="primary"):
    
    # 1. Yield Prediction
    yield_tons = calculate_yield(crop, nitrogen, phosphorus, potassium, ph)
    total_yield = yield_tons * land_area
    
    # 2. Profit Calculation
    data = crop_data[crop]
    revenue = total_yield * data['price_per_ton']
    cost = data['cost_per_hectare'] * land_area
    profit = revenue - cost
    roi = (profit / cost) * 100 if cost > 0 else 0
    
    # Display Metrics
    st.markdown("---")
    st.subheader("📊 Results")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("🌾 Predicted Yield", f"{yield_tons} tons/ha")
    col_b.metric("💰 Total Revenue", f"₹{revenue:,.0f}")
    col_c.metric("💸 Total Cost", f"₹{cost:,.0f}")
    col_d.metric("📈 Net Profit", f"₹{profit:,.0f}", delta=f"{roi:.1f}% ROI")
    
    # 3. Fertilizer Recommendations
    st.markdown("---")
    st.subheader("🧪 Soil Health & Fertilizer Recommendations")
    
    recs = get_recommendations(crop, nitrogen, phosphorus, potassium, ph)
    for rec in recs:
        st.write(rec)
    
    # 4. Summary Table
    st.markdown("---")
    st.subheader("📋 Quick Summary")
    summary_df = pd.DataFrame({
        "Parameter": ["Crop", "Area", "N", "P", "K", "pH", "Yield"],
        "Value": [crop, f"{land_area} ha", nitrogen, phosphorus, potassium, ph, f"{yield_tons} tons/ha"]
    })
    st.dataframe(summary_df, hide_index=True, use_container_width=True)

else:
    st.info("👆 Adjust the sliders and click **'Get Advice'** to see instant recommendations!")

st.markdown("---")
st.caption("🌱 Smart Agri Advisor Lite - No ML, 100% Transparent Rules | Hackathon Ready 🏆")
