import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
from io import StringIO

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="FarmIQ Pro - Smart Agri Advisor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card { background: #1e2229; border-radius: 12px; padding: 15px; border: 1px solid #2d333b; text-align: center; }
    .rec-card { background: #161b22; border-radius: 8px; padding: 12px 16px; border-left: 4px solid; margin-bottom: 8px; }
    .rec-good { border-left-color: #2ea043; }
    .rec-warning { border-left-color: #d29922; }
    .rec-danger { border-left-color: #f85149; }
    .custom-divider { height: 1px; background: linear-gradient(90deg, #2d333b, #58a6ff, #2d333b); margin: 20px 0; }
    .risk-card { padding: 15px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
    .conclusion-box {
        background: #161b22;
        border-radius: 12px;
        padding: 25px 30px;
        border: 1px solid #2d333b;
        border-left: 6px solid #58a6ff;
    }
</style>
""", unsafe_allow_html=True)

# ---------- CROP DATABASE ----------
crop_data = {
    'Rice': {
        'optimal': {'N': 80, 'P': 40, 'K': 40, 'pH': 6.5, 'temp': 28, 'humidity': 80, 'rainfall': 200},
        'base_yield': 3.5, 'price_per_ton': 22000, 'cost_per_hectare': 22000, 'emoji': '🍚'
    },
    'Wheat': {
        'optimal': {'N': 120, 'P': 60, 'K': 60, 'pH': 7.0, 'temp': 20, 'humidity': 60, 'rainfall': 150},
        'base_yield': 3.0, 'price_per_ton': 24000, 'cost_per_hectare': 24000, 'emoji': '🌾'
    },
    'Maize': {
        'optimal': {'N': 150, 'P': 70, 'K': 50, 'pH': 6.8, 'temp': 25, 'humidity': 65, 'rainfall': 180},
        'base_yield': 4.0, 'price_per_ton': 20000, 'cost_per_hectare': 20000, 'emoji': '🌽'
    },
    'Sugarcane': {
        'optimal': {'N': 200, 'P': 100, 'K': 100, 'pH': 7.2, 'temp': 30, 'humidity': 75, 'rainfall': 250},
        'base_yield': 8.0, 'price_per_ton': 3500, 'cost_per_hectare': 40000, 'emoji': '🎋'
    },
    'Cotton': {
        'optimal': {'N': 100, 'P': 50, 'K': 70, 'pH': 7.0, 'temp': 28, 'humidity': 55, 'rainfall': 120},
        'base_yield': 2.5, 'price_per_ton': 60000, 'cost_per_hectare': 28000, 'emoji': '🧵'
    },
    'Tomato': {
        'optimal': {'N': 120, 'P': 60, 'K': 80, 'pH': 6.5, 'temp': 24, 'humidity': 70, 'rainfall': 120},
        'base_yield': 3.0, 'price_per_ton': 12000, 'cost_per_hectare': 25000, 'emoji': '🍅'
    }
}

# ---------- CORE ENGINE ----------
def calculate_yield(crop, N, P, K, pH, temp, humidity, rainfall):
    opt = crop_data[crop]['optimal']
    deviation = (
        abs(N - opt['N']) / max(opt['N'], 1) * 0.30 +
        abs(P - opt['P']) / max(opt['P'], 1) * 0.20 +
        abs(K - opt['K']) / max(opt['K'], 1) * 0.15 +
        abs(pH - opt['pH']) / max(opt['pH'], 1) * 0.10 +
        abs(temp - opt['temp']) / max(opt['temp'], 1) * 0.10 +
        abs(humidity - opt['humidity']) / max(opt['humidity'], 1) * 0.05 +
        abs(rainfall - opt['rainfall']) / max(opt['rainfall'], 1) * 0.10
    )
    penalty = min(deviation * 0.65, 0.75)
    yield_tons = crop_data[crop]['base_yield'] * (1 - penalty)
    noise = np.random.normal(0, 0.05)
    return round(max(0.2, yield_tons + noise), 2)

def get_recommendations(crop, N, P, K, pH):
    opt = crop_data[crop]['optimal']
    recs = []
    if N < opt['N'] * 0.8: recs.append(("🌱 Nitrogen", f"Low! Add Urea/DAP (Need ~{opt['N'] - N} kg/ha)", "danger"))
    elif N > opt['N'] * 1.3: recs.append(("🌱 Nitrogen", "High! Reduce application", "warning"))
    else: recs.append(("🌱 Nitrogen", "Optimal! Perfect balance", "good"))
    if P < opt['P'] * 0.8: recs.append(("💧 Phosphorus", f"Low! Add SSP/DAP (Need ~{opt['P'] - P} kg/ha)", "danger"))
    elif P > opt['P'] * 1.3: recs.append(("💧 Phosphorus", "High! Reduce application", "warning"))
    else: recs.append(("💧 Phosphorus", "Optimal! Great level", "good"))
    if K < opt['K'] * 0.8: recs.append(("🥔 Potassium", f"Low! Add MOP (Need ~{opt['K'] - K} kg/ha)", "danger"))
    elif K > opt['K'] * 1.3: recs.append(("🥔 Potassium", "High! Reduce application", "warning"))
    else: recs.append(("🥔 Potassium", "Optimal! Well balanced", "good"))
    if pH < 5.5: recs.append(("🧪 Soil pH", "Acidic! Apply Lime to raise pH", "danger"))
    elif pH > 7.5: recs.append(("🧪 Soil pH", "Alkaline! Apply Gypsum to lower pH", "danger"))
    else: recs.append(("🧪 Soil pH", "Optimal! Ideal for this crop", "good"))
    return recs

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("# 🌾 FarmIQ Pro")
    st.caption("Smart Agri Advisor v2.0 (Hackathon Edition)")
    st.markdown("---")
    with st.expander("🧑‍🌾 Field Settings", expanded=True):
        crop = st.selectbox("Select Crop", list(crop_data.keys()), format_func=lambda x: f"{crop_data[x]['emoji']} {x}")
        land_area = st.number_input("Land Area (Hectares)", 0.5, 100.0, 1.0, 0.5)
    with st.expander("🌱 Soil Parameters", expanded=True):
        N = st.slider("Nitrogen (N)", 0, 250, 80)
        P = st.slider("Phosphorus (P)", 0, 150, 50)
        K = st.slider("Potassium (K)", 0, 150, 50)
        pH = st.slider("Soil pH", 4.0, 9.0, 6.8, 0.1)
    with st.expander("🌦️ Climate Conditions", expanded=True):
        temp = st.slider("Temperature (°C)", 10, 40, 25)
        humidity = st.slider("Humidity (%)", 20, 90, 70)
        rainfall = st.slider("Rainfall (mm)", 50, 400, 150)
    st.markdown("---")
    analyze_btn = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

# ---------- MAIN DASHBOARD ----------
st.title("🌾 Smart Agri Advisor Pro")
st.markdown("**Precision agriculture insights — powered by expert systems**")
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

if analyze_btn or 'last_run' in st.session_state:
    st.session_state['last_run'] = True
    
    yield_tons = calculate_yield(crop, N, P, K, pH, temp, humidity, rainfall)
    total_yield = yield_tons * land_area
    data = crop_data[crop]
    revenue = total_yield * data['price_per_ton']
    cost = data['cost_per_hectare'] * land_area
    profit = revenue - cost
    roi = (profit / cost) * 100 if cost > 0 else 0

    # ----------------------------------------------------------------
    # SECTION 1: GAUGE + METRICS
    # ----------------------------------------------------------------
    col_gauge, col_metrics = st.columns([1.2, 2])
    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=yield_tons,
            title={'text': f"Predicted Yield<br><span style='font-size:12px;color:gray'>{crop}</span>", 'font': {'size': 18}},
            delta={'reference': crop_data[crop]['base_yield'], 'increasing': {'color': "#2ea043"}},
            gauge={
                'axis': {'range': [0, crop_data[crop]['base_yield'] * 1.5], 'tickwidth': 1},
                'bar': {'color': "#58a6ff"},
                'steps': [
                    {'range': [0, crop_data[crop]['base_yield'] * 0.5], 'color': "#21262d"},
                    {'range': [crop_data[crop]['base_yield'] * 0.5, crop_data[crop]['base_yield'] * 1.0], 'color': "#30363d"},
                    {'range': [crop_data[crop]['base_yield'] * 1.0, crop_data[crop]['base_yield'] * 1.5], 'color': "#21262d"}
                ],
                'threshold': {'line': {'color': "#f85149", 'width': 4}, 'thickness': 0.75, 'value': crop_data[crop]['base_yield']}
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

    with col_metrics:
        st.markdown("### 📊 Financial Overview")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("💰 Revenue", f"₹{revenue:,.0f}")
        m_col2.metric("💸 Total Cost", f"₹{cost:,.0f}")
        m_col3.metric("📈 Net Profit", f"₹{profit:,.0f}", delta=f"{roi:.1f}% ROI", delta_color="normal")
        m_col4.metric("🌾 Total Yield", f"{total_yield:.2f} tons")
        if roi > 30: st.success(f"✅ Excellent! This crop yields a {roi:.1f}% ROI. Highly recommended.")
        elif roi > 10: st.info(f"ℹ️ Moderate ROI of {roi:.1f}%. Consider optimizing inputs.")
        else: st.warning(f"⚠️ Low ROI ({roi:.1f}%). Review parameters or consider a different crop.")

    # ----------------------------------------------------------------
    # SECTION 2: RECOMMENDATIONS
    # ----------------------------------------------------------------
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.subheader("🧪 Soil Health & Fertilizer Recommendations")
    recs = get_recommendations(crop, N, P, K, pH)
    cols = st.columns(len(recs))
    for idx, (label, msg, status) in enumerate(recs):
        color = "#2ea043" if status == "good" else "#d29922" if status == "warning" else "#f85149"
        with cols[idx]:
            st.markdown(f"""
            <div style="background:#161b22; border-radius:10px; padding:15px; border-top:4px solid {color}; height:100%;">
                <div style="font-size:14px; color:#8b949e;">{label}</div>
                <div style="font-size:14px; color:#f0f6fc; margin-top:8px;">{msg}</div>
            </div>
            """, unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # SECTION 3: PEST & DISEASE RISK
    # ----------------------------------------------------------------
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.subheader("🐛 Pest & Disease Risk Assessment")
    
    risk_level = "Low"
    risk_color = "#2ea043"
    risk_emoji = "🟢"
    risk_details = "No immediate threats detected."
    
    if crop == "Rice":
        if temp > 28 and humidity > 80:
            risk_level, risk_color, risk_emoji = "High", "#f85149", "🔴"
            risk_details = "⚠️ Blast Disease Risk: High temp + humidity. Apply fungicide (e.g., Tricyclazole)."
        elif temp > 25 and humidity > 70:
            risk_level, risk_color, risk_emoji = "Medium", "#d29922", "🟡"
            risk_details = "⚠️ Sheath Blight Risk: Conditions favorable. Monitor fields closely."
    elif crop == "Wheat":
        if humidity > 70 and rainfall > 150:
            risk_level, risk_color, risk_emoji = "High", "#f85149", "🔴"
            risk_details = "⚠️ Rust Disease Risk: High humidity + rainfall. Scout for orange pustules."
    elif crop == "Cotton":
        if temp > 30 and humidity < 50:
            risk_level, risk_color, risk_emoji = "High", "#f85149", "🔴"
            risk_details = "⚠️ Aphid/Whitefly Risk: Hot & dry conditions favor pests. Apply neem oil."
    else:
        if temp > 30 and humidity > 75:
            risk_level, risk_color, risk_emoji = "Medium", "#d29922", "🟡"
            risk_details = "⚠️ High temp & humidity may encourage fungal growth. Consider preventive spray."
    
    col_risk1, col_risk2 = st.columns([1, 3])
    with col_risk1:
        st.markdown(f"""
        <div class="risk-card" style="background:#161b22; border-radius:10px; padding:20px; border: 1px solid {risk_color};">
            <div style="font-size:40px;">{risk_emoji}</div>
            <div style="font-size:24px; font-weight:bold; color:{risk_color};">{risk_level}</div>
            <div style="font-size:12px; color:#8b949e;">Risk Level</div>
        </div>
        """, unsafe_allow_html=True)
    with col_risk2:
        st.markdown(f"""
        <div style="background:#161b22; border-radius:10px; padding:20px; height:100%; display:flex; align-items:center;">
            <div>
                <div style="font-size:16px; color:#f0f6fc;">{risk_details}</div>
                <div style="font-size:12px; color:#8b949e; margin-top:10px;">
                    💡 <i>Recommendation: Based on current weather and crop type.</i>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # SECTION 4: SOIL HEALTH RADAR
    # ----------------------------------------------------------------
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.subheader("📊 Soil Health Scorecard (Radar Chart)")
    st.caption("How close are your current soil parameters to the crop's optimal requirements?")
    
    opt = crop_data[crop]['optimal']
    categories = ['N', 'P', 'K', 'pH']
    current_vals = [N, P, K, pH]
    optimal_vals = [opt['N'], opt['P'], opt['K'], opt['pH']]
    norm_vals = []
    for c, o in zip(current_vals, optimal_vals):
        if o == 0: norm_vals.append(0)
        else: norm_vals.append(min(c / o, 1.0))
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=norm_vals,
        theta=categories,
        fill='toself',
        name='Current Soil Health',
        line_color='#58a6ff',
        fillcolor='rgba(88, 166, 255, 0.3)'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[1, 1, 1, 1],
        theta=categories,
        fill='toself',
        name='Optimal Target',
        line_color='#2ea043',
        fillcolor='rgba(46, 160, 67, 0.1)',
        line_dash='dash'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1.2], tickformat=',.0%'), bgcolor='rgba(0,0,0,0)'),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#8b949e',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ----------------------------------------------------------------
    # SECTION 5: MULTI-CROP COMPARISON
    # ----------------------------------------------------------------
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.subheader("🤝 Multi-Crop Profit Comparison")
    st.caption("Compare which crop gives the best ROI for your current land & climate.")
    
    compare_crops = st.multiselect(
        "Select crops to compare (Max 4)", 
        list(crop_data.keys()), 
        default=[crop, 'Wheat', 'Maize'] if crop not in ['Wheat', 'Maize'] else [crop, 'Rice', 'Cotton']
    )
    
    if compare_crops:
        comp_data = []
        for c in compare_crops:
            y = calculate_yield(c, N, P, K, pH, temp, humidity, rainfall)
            tot = y * land_area
            rev = tot * crop_data[c]['price_per_ton']
            cst = crop_data[c]['cost_per_hectare'] * land_area
            prof = rev - cst
            roi_calc = (prof / cst) * 100 if cst > 0 else 0
            comp_data.append({
                'Crop': f"{crop_data[c]['emoji']} {c}",
                'Yield (tons)': round(y, 2),
                'Revenue (₹)': round(rev, 0),
                'Cost (₹)': round(cst, 0),
                'Profit (₹)': round(prof, 0),
                'ROI (%)': round(roi_calc, 1)
            })
        
        df_comp = pd.DataFrame(comp_data)
        st.dataframe(df_comp.style.format({
            'Revenue (₹)': '₹{:.0f}',
            'Cost (₹)': '₹{:.0f}',
            'Profit (₹)': '₹{:.0f}',
            'ROI (%)': '{:.1f}%'
        }).background_gradient(subset=['ROI (%)'], cmap='RdYlGn', vmin=0, vmax=50), use_container_width=True)
        
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=df_comp['Crop'],
            y=df_comp['Profit (₹)'],
            name='Profit',
            marker_color=['#2ea043' if p > 0 else '#f85149' for p in df_comp['Profit (₹)']],
            text=df_comp['Profit (₹)'].apply(lambda x: f'₹{x:,.0f}'),
            textposition='outside'
        ))
        fig_comp.update_layout(
            height=350,
            xaxis_title="Crop",
            yaxis_title="Net Profit (₹)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#8b949e',
            xaxis=dict(gridcolor='#2d333b'),
            yaxis=dict(gridcolor='#2d333b')
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    # ----------------------------------------------------------------
    # SECTION 6: DOWNLOAD REPORT
    # ----------------------------------------------------------------
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.subheader("📄 Export Report")
    
    report_text = f"""
    ========================================
    FARM IQ PRO - AGRI ADVISORY REPORT
    ========================================
    Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
    
    -------------------- FARM DETAILS --------------------
    Crop Selected: {crop}
    Land Area: {land_area} Hectares
    
    -------------------- SOIL & WEATHER --------------------
    Nitrogen (N): {N} kg/ha
    Phosphorus (P): {P} kg/ha
    Potassium (K): {K} kg/ha
    Soil pH: {pH}
    Temperature: {temp} °C
    Humidity: {humidity} %
    Rainfall: {rainfall} mm
    
    -------------------- PREDICTIONS --------------------
    Predicted Yield: {yield_tons} tons/ha
    Total Yield: {total_yield} tons
    Total Revenue: ₹{revenue:,.2f}
    Total Cost: ₹{cost:,.2f}
    Net Profit: ₹{profit:,.2f}
    ROI: {roi:.2f}%
    
    -------------------- RECOMMENDATIONS --------------------
    """
    for label, msg, status in recs:
        report_text += f"{label}: {msg}\n"
    
    report_text += f"""
    
    -------------------- RISK ASSESSMENT --------------------
    Risk Level: {risk_level}
    Details: {risk_details}
    
    ========================================
    Report generated by FarmIQ Pro v2.0
    ========================================
    """
    
    st.download_button(
        label="📥 Download Full Report (TXT)",
        data=report_text,
        file_name=f"FarmIQ_Report_{crop}_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
        mime="text/plain",
        use_container_width=True
    )

    # ----------------------------------------------------------------
    # SECTION 7: CHARTS (Sensitivity, Importance, Future)
    # ----------------------------------------------------------------
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📈 Sensitivity Analysis", "📊 Feature Drivers", "🔮 Future Projection"])

    with tab1:
        st.markdown("#### Yield Sensitivity to Environmental Factors")
        opt = crop_data[crop]['optimal']
        factors = ['Rainfall', 'Temperature', 'Humidity']
        fig = make_subplots(rows=1, cols=3, subplot_titles=factors, shared_yaxes=True)
        for i, factor in enumerate(factors):
            if factor == 'Rainfall':
                x_vals = np.linspace(50, 400, 30)
                y_vals = [calculate_yield(crop, N, P, K, pH, temp, humidity, r) for r in x_vals]
                opt_val = opt['rainfall']
            elif factor == 'Temperature':
                x_vals = np.linspace(10, 40, 30)
                y_vals = [calculate_yield(crop, N, P, K, pH, t, humidity, rainfall) for t in x_vals]
                opt_val = opt['temp']
            else:
                x_vals = np.linspace(20, 90, 30)
                y_vals = [calculate_yield(crop, N, P, K, pH, temp, h, rainfall) for h in x_vals]
                opt_val = opt['humidity']
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines+markers', name=factor, line=dict(color='#58a6ff', width=3)), row=1, col=i+1)
            fig.add_vline(x=opt_val, line_dash="dash", line_color="#2ea043", row=1, col=i+1)
        fig.update_layout(height=350, showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#8b949e')
        fig.update_xaxes(gridcolor='#2d333b', zerolinecolor='#2d333b')
        fig.update_yaxes(gridcolor='#2d333b', zerolinecolor='#2d333b')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("#### Global Feature Importance (Sensitivity Analysis)")
        base_y = calculate_yield(crop, N, P, K, pH, temp, humidity, rainfall)
        params = {'N': N, 'P': P, 'K': K, 'pH': pH, 'Temp': temp, 'Humidity': humidity, 'Rainfall': rainfall}
        importance = {}
        for name, val in params.items():
            delta = max(val * 0.2, 1)
            temp_dict = {'N': N, 'P': P, 'K': K, 'pH': pH, 'Temp': temp, 'Humidity': humidity, 'Rainfall': rainfall}
            temp_dict[name] = val + delta
            y_up = calculate_yield(crop, temp_dict['N'], temp_dict['P'], temp_dict['K'], temp_dict['pH'], temp_dict['Temp'], temp_dict['Humidity'], temp_dict['Rainfall'])
            temp_dict[name] = val - delta
            y_down = calculate_yield(crop, temp_dict['N'], temp_dict['P'], temp_dict['K'], temp_dict['pH'], temp_dict['Temp'], temp_dict['Humidity'], temp_dict['Rainfall'])
            importance[name] = (abs(y_up - base_y) + abs(y_down - base_y)) / 2
        max_imp = max(importance.values()) if max(importance.values()) > 0 else 1
        df_imp = pd.DataFrame(list(importance.items()), columns=['Feature', 'Importance'])
        df_imp['Importance'] = df_imp['Importance'] / max_imp
        df_imp = df_imp.sort_values('Importance', ascending=True)
        fig_imp = go.Figure(go.Bar(x=df_imp['Importance'], y=df_imp['Feature'], orientation='h', marker=dict(color=df_imp['Importance'], colorscale='Blues'), text=df_imp['Importance'].apply(lambda x: f'{x:.1%}'), textposition='outside'))
        fig_imp.update_layout(height=350, xaxis_title="Relative Impact", yaxis_title="", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#8b949e', xaxis=dict(gridcolor='#2d333b'), yaxis=dict(gridcolor='#2d333b'))
        st.plotly_chart(fig_imp, use_container_width=True)

    with tab3:
        st.markdown("#### Climate Impact Projection (Temperature Scenario)")
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            future_year = st.slider("Projection Year", 2025, 2040, 2030)
            future_temp_shift = st.slider("Expected Temp Rise (°C)", 0.0, 3.0, 1.5, 0.1)
        years = list(range(2024, 2041))
        temp_scenario = [temp + (future_temp_shift * ((y - 2024) / 16)) for y in years]
        proj_yields = [calculate_yield(crop, N, P, K, pH, t, humidity, rainfall) for t in temp_scenario]
        current_yield = calculate_yield(crop, N, P, K, pH, temp, humidity, rainfall)
        fig_future = go.Figure()
        fig_future.add_trace(go.Scatter(x=years, y=proj_yields, mode='lines+markers', name='Projected Yield', line=dict(color='#f0883e', width=3)))
        fig_future.add_hline(y=current_yield, line_dash="dash", line_color="#2ea043", annotation_text=f"Current Yield ({current_yield:.2f} t/ha)")
        fig_future.add_trace(go.Scatter(x=years + years[::-1], y=[y + 0.15 for y in proj_yields] + [y - 0.15 for y in proj_yields[::-1]], fill='toself', fillcolor='rgba(255, 165, 0, 0.15)', line=dict(color='rgba(255,255,255,0)'), name='Confidence Band'))
        fig_future.update_layout(height=350, xaxis_title="Year", yaxis_title="Yield (tons/ha)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#8b949e', xaxis=dict(gridcolor='#2d333b'), yaxis=dict(gridcolor='#2d333b'), hovermode='x unified')
        st.plotly_chart(fig_future, use_container_width=True)

    # ----------------------------------------------------------------
    # SECTION 8: EXECUTIVE SUMMARY & CONCLUSION (NEW)
    # ----------------------------------------------------------------
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.subheader("📋 Executive Summary & Conclusion")
    
    # Determine best crop suggestion
    best_crop = crop
    best_roi = roi
    best_profit = profit
    for c in crop_data.keys():
        if c == crop: continue
        y = calculate_yield(c, N, P, K, pH, temp, humidity, rainfall)
        prof = (y * land_area * crop_data[c]['price_per_ton']) - (crop_data[c]['cost_per_hectare'] * land_area)
        r = (prof / (crop_data[c]['cost_per_hectare'] * land_area)) * 100 if (crop_data[c]['cost_per_hectare'] * land_area) > 0 else 0
        if prof > best_profit:
            best_profit = prof
            best_crop = c
            best_roi = r
    
    # Health status
    total_health = sum(norm_vals) / len(norm_vals) * 100
    
    st.markdown(f"""
    <div class="conclusion-box">
        <p style="color: #f0f6fc; font-size: 16px; line-height: 1.6;">
        <strong>🔍 Key Findings:</strong><br>
        • Based on your current soil (N={N}, P={P}, K={K}, pH={pH}) and climate (Temp={temp}°C, Humidity={humidity}%, Rainfall={rainfall}mm), 
        your selected crop <strong>{crop}</strong> is projected to yield <strong>{yield_tons} tons/ha</strong>, 
        generating a net profit of <strong>₹{profit:,.0f}</strong> with an ROI of <strong>{roi:.1f}%</strong>.
        </p>
        
        <p style="color: #f0f6fc; font-size: 16px; line-height: 1.6;">
        <strong>🌱 Soil Health Score:</strong> Your soil is at <strong>{total_health:.0f}%</strong> of the ideal composition for {crop}.
        {'✅ Your soil is well-balanced and ready for planting!' if total_health > 70 else '⚠️ Consider adjusting your fertilizer levels based on the recommendations above.'}
        </p>
        
        <p style="color: #f0f6fc; font-size: 16px; line-height: 1.6;">
        <strong>🐛 Risk Assessment:</strong> {risk_details}
        </p>
        
        <p style="color: #f0f6fc; font-size: 16px; line-height: 1.6;">
        <strong>💡 Recommendation:</strong><br>
        {'👉 ' + best_crop + ' appears to be a more profitable option for your land, with an estimated ROI of ' + str(round(best_roi, 1)) + '%.' if best_crop != crop else '✅ Your current crop selection is the best match for your land and climate.'}
        </p>
        
        <p style="color: #8b949e; font-size: 14px; line-height: 1.6; border-top: 1px solid #2d333b; padding-top: 15px; margin-top: 10px;">
        <strong>🎯 Final Verdict:</strong> 
        This analysis provides a data-driven advisory for your farm. Use the recommended fertilizer adjustments and keep an eye on the weather forecast to maximize your yield and profits.
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    # Welcome screen
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 0;">
        <div style="font-size: 80px;">🌾</div>
        <h2 style="color: #f0f6fc;">Welcome to FarmIQ Pro</h2>
        <p style="color: #8b949e; max-width: 600px; text-align: center;">
            Get professional-grade agricultural insights instantly. Adjust your farm parameters 
            in the sidebar and hit <strong>"Run Analysis"</strong> to unlock yield predictions, 
            financial forecasts, and soil health recommendations.
        </p>
        <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 20px; justify-content: center;">
            <div style="background: #161b22; border-radius: 10px; padding: 12px 20px; border: 1px solid #2d333b;"><span style="color: #58a6ff;">📈</span> Sensitivity</div>
            <div style="background: #161b22; border-radius: 10px; padding: 12px 20px; border: 1px solid #2d333b;"><span style="color: #2ea043;">🧪</span> Soil Health Radar</div>
            <div style="background: #161b22; border-radius: 10px; padding: 12px 20px; border: 1px solid #2d333b;"><span style="color: #f0883e;">🔮</span> Climate Projections</div>
            <div style="background: #161b22; border-radius: 10px; padding: 12px 20px; border: 1px solid #2d333b;"><span style="color: #f85149;">🐛</span> Pest Risk Alerts</div>
            <div style="background: #161b22; border-radius: 10px; padding: 12px 20px; border: 1px solid #2d333b;"><span style="color: #d29922;">🤝</span> Crop Comparison</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("🌱 FarmIQ Pro | Anshu Sharma VIT Bhopal")
