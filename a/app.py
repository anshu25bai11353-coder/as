import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="FarmIQ Pro - Smart Agri Advisor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CUSTOM CSS (Professional Look) ----------
st.markdown("""
<style>
    /* Main background */
    .main {
        background-color: #0e1117;
    }
    /* Metric Cards */
    .metric-card {
        background: #1e2229;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #2d333b;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5);
        text-align: center;
    }
    .metric-label {
        font-size: 14px;
        color: #8b949e;
        font-weight: 400;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        margin-top: 5px;
    }
    .metric-delta {
        font-size: 14px;
        margin-top: 2px;
    }
    /* Recommendation Cards */
    .rec-card {
        background: #161b22;
        border-radius: 8px;
        padding: 12px 16px;
        border-left: 4px solid;
        margin-bottom: 8px;
    }
    .rec-good { border-left-color: #2ea043; }
    .rec-warning { border-left-color: #d29922; }
    .rec-danger { border-left-color: #f85149; }
    /* Sidebar styling */
    .css-1d391kg { background-color: #0d1117; }
    h1, h2, h3, h4 {
        color: #f0f6fc;
    }
    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, #2d333b, #58a6ff, #2d333b);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------- CROP DATABASE (RULES) ----------
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
    # Nitrogen
    if N < opt['N'] * 0.8:
        recs.append(("🌱 Nitrogen", f"Low! Add Urea/DAP (Need ~{opt['N'] - N} kg/ha)", "danger"))
    elif N > opt['N'] * 1.3:
        recs.append(("🌱 Nitrogen", "High! Reduce application to prevent burning", "warning"))
    else:
        recs.append(("🌱 Nitrogen", "Optimal! Perfect balance", "good"))
    
    # Phosphorus
    if P < opt['P'] * 0.8:
        recs.append(("💧 Phosphorus", f"Low! Add SSP/DAP (Need ~{opt['P'] - P} kg/ha)", "danger"))
    elif P > opt['P'] * 1.3:
        recs.append(("💧 Phosphorus", "High! Reduce application", "warning"))
    else:
        recs.append(("💧 Phosphorus", "Optimal! Great level", "good"))
    
    # Potassium
    if K < opt['K'] * 0.8:
        recs.append(("🥔 Potassium", f"Low! Add MOP (Need ~{opt['K'] - K} kg/ha)", "danger"))
    elif K > opt['K'] * 1.3:
        recs.append(("🥔 Potassium", "High! Reduce application", "warning"))
    else:
        recs.append(("🥔 Potassium", "Optimal! Well balanced", "good"))
    
    # pH
    if pH < 5.5:
        recs.append(("🧪 Soil pH", "Acidic! Apply Lime to raise pH", "danger"))
    elif pH > 7.5:
        recs.append(("🧪 Soil pH", "Alkaline! Apply Gypsum to lower pH", "danger"))
    else:
        recs.append(("🧪 Soil pH", "Optimal! Ideal for this crop", "good"))
    return recs

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("# 🌾 FarmIQ Pro")
    st.caption("Smart Agri Advisor v2.0")
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
st.markdown("**Precision agriculture insights — powered by rule-based expert systems**")
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

if analyze_btn or 'last_run' in st.session_state:
    # Store in session state to persist after reruns
    st.session_state['last_run'] = True
    
    # 1. PREDICT
    yield_tons = calculate_yield(crop, N, P, K, pH, temp, humidity, rainfall)
    total_yield = yield_tons * land_area
    data = crop_data[crop]
    revenue = total_yield * data['price_per_ton']
    cost = data['cost_per_hectare'] * land_area
    profit = revenue - cost
    roi = (profit / cost) * 100 if cost > 0 else 0

    # ----- TOP ROW: GAUGE + KEY METRICS -----
    col_gauge, col_metrics = st.columns([1.2, 2])
    
    with col_gauge:
        # Professional Gauge Chart
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
                'threshold': {
                    'line': {'color': "#f85149", 'width': 4},
                    'thickness': 0.75,
                    'value': crop_data[crop]['base_yield']
                }
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
        
        st.markdown("---")
        # Status bar
        if roi > 30:
            st.success(f"✅ Excellent! This crop is projected to yield a {roi:.1f}% ROI. Highly recommended.")
        elif roi > 10:
            st.info(f"ℹ️ Moderate ROI of {roi:.1f}%. Consider optimizing inputs for better margins.")
        else:
            st.warning(f"⚠️ Low ROI ({roi:.1f}%). Review soil parameters or consider a different crop.")

    # ----- MIDDLE SECTION: RECOMMENDATIONS -----
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

    # ----- BOTTOM SECTION: ADVANCED CHARTS (TABS) -----
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📈 Sensitivity Analysis", "📊 Feature Drivers", "🔮 Future Projection"])

    # --- TAB 1: Sensitivity ---
    with tab1:
        st.markdown("#### Yield Sensitivity to Environmental Factors")
        opt = crop_data[crop]['optimal']
        
        # Generate data for 3 factors
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
            else: # Humidity
                x_vals = np.linspace(20, 90, 30)
                y_vals = [calculate_yield(crop, N, P, K, pH, temp, h, rainfall) for h in x_vals]
                opt_val = opt['humidity']
            
            fig.add_trace(
                go.Scatter(x=x_vals, y=y_vals, mode='lines+markers', name=factor,
                           line=dict(color='#58a6ff', width=3),
                           marker=dict(size=4, color='#1f6feb')),
                row=1, col=i+1
            )
            # Add optimal line
            fig.add_vline(x=opt_val, line_dash="dash", line_color="#2ea043", 
                         annotation_text="Optimal", row=1, col=i+1)
        
        fig.update_layout(height=350, showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)', font_color='#8b949e')
        fig.update_xaxes(gridcolor='#2d333b', zerolinecolor='#2d333b')
        fig.update_yaxes(gridcolor='#2d333b', zerolinecolor='#2d333b')
        st.plotly_chart(fig, use_container_width=True)

    # --- TAB 2: Feature Importance (Perturbation-based) ---
    with tab2:
        st.markdown("#### Global Feature Importance (Sensitivity Analysis)")
        base_y = calculate_yield(crop, N, P, K, pH, temp, humidity, rainfall)
        params = {'N': N, 'P': P, 'K': K, 'pH': pH, 'Temp': temp, 'Humidity': humidity, 'Rainfall': rainfall}
        importance = {}
        
        for name, val in params.items():
            delta = max(val * 0.2, 1)
            # Make perturbation
            temp_dict = {'N': N, 'P': P, 'K': K, 'pH': pH, 'Temp': temp, 'Humidity': humidity, 'Rainfall': rainfall}
            temp_dict[name] = val + delta
            y_up = calculate_yield(crop, temp_dict['N'], temp_dict['P'], temp_dict['K'], 
                                   temp_dict['pH'], temp_dict['Temp'], temp_dict['Humidity'], temp_dict['Rainfall'])
            temp_dict[name] = val - delta
            y_down = calculate_yield(crop, temp_dict['N'], temp_dict['P'], temp_dict['K'],
                                     temp_dict['pH'], temp_dict['Temp'], temp_dict['Humidity'], temp_dict['Rainfall'])
            importance[name] = (abs(y_up - base_y) + abs(y_down - base_y)) / 2
        
        # Normalize
        max_imp = max(importance.values()) if max(importance.values()) > 0 else 1
        df_imp = pd.DataFrame(list(importance.items()), columns=['Feature', 'Importance'])
        df_imp['Importance'] = df_imp['Importance'] / max_imp
        df_imp = df_imp.sort_values('Importance', ascending=True)
        
        fig_imp = go.Figure(go.Bar(
            x=df_imp['Importance'],
            y=df_imp['Feature'],
            orientation='h',
            marker=dict(color=df_imp['Importance'], colorscale='Blues', showscale=True),
            text=df_imp['Importance'].apply(lambda x: f'{x:.1%}'),
            textposition='outside'
        ))
        fig_imp.update_layout(
            height=350,
            xaxis_title="Relative Impact",
            yaxis_title="",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#8b949e',
            xaxis=dict(gridcolor='#2d333b'),
            yaxis=dict(gridcolor='#2d333b')
        )
        st.plotly_chart(fig_imp, use_container_width=True)

    # --- TAB 3: Future Projection ---
    with tab3:
        st.markdown("#### Climate Impact Projection (Temperature Scenario)")
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            future_year = st.slider("Projection Year", 2025, 2040, 2030)
            future_temp_shift = st.slider("Expected Temp Rise (°C)", 0.0, 3.0, 1.5, 0.1)
        
        # Generate projection
        years = list(range(2024, 2041))
        temp_scenario = [temp + (future_temp_shift * ((y - 2024) / 16)) for y in years]
        proj_yields = []
        for i, y in enumerate(years):
            t = temp_scenario[i]
            yld = calculate_yield(crop, N, P, K, pH, t, humidity, rainfall)
            proj_yields.append(yld)
        
        # Current yield for reference
        current_yield = calculate_yield(crop, N, P, K, pH, temp, humidity, rainfall)
        
        fig_future = go.Figure()
        fig_future.add_trace(go.Scatter(
            x=years, y=proj_yields,
            mode='lines+markers',
            name='Projected Yield',
            line=dict(color='#f0883e', width=3),
            marker=dict(size=6, color='#d29922')
        ))
        fig_future.add_hline(y=current_yield, line_dash="dash", line_color="#2ea043", 
                             annotation_text=f"Current Yield ({current_yield:.2f} t/ha)")
        
        # Add confidence ribbon (simple deviation)
        fig_future.add_trace(go.Scatter(
            x=years + years[::-1],
            y=[y + 0.15 for y in proj_yields] + [y - 0.15 for y in proj_yields[::-1]],
            fill='toself',
            fillcolor='rgba(255, 165, 0, 0.15)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Band',
            showlegend=True
        ))
        
        fig_future.update_layout(
            height=350,
            xaxis_title="Year",
            yaxis_title="Yield (tons/ha)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#8b949e',
            xaxis=dict(gridcolor='#2d333b'),
            yaxis=dict(gridcolor='#2d333b'),
            hovermode='x unified'
        )
        st.plotly_chart(fig_future, use_container_width=True)
        
        # Show projected metric
        proj_yield_2030 = proj_yields[6] # 2030 index
        col_a, col_b = st.columns(2)
        col_a.metric("🌡️ Projected Temp (2030)", f"{temp_scenario[6]:.1f}°C", delta=f"{temp_scenario[6] - temp:.1f}°C")
        col_b.metric("🌾 Projected Yield (2030)", f"{proj_yield_2030:.2f} t/ha", 
                     delta=f"{proj_yield_2030 - current_yield:.2f} t/ha", 
                     delta_color="inverse")

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
        <div style="display: flex; gap: 20px; margin-top: 20px;">
            <div style="background: #161b22; border-radius: 10px; padding: 15px 25px; border: 1px solid #2d333b;">
                <span style="color: #58a6ff;">📈</span> Sensitivity Analysis
            </div>
            <div style="background: #161b22; border-radius: 10px; padding: 15px 25px; border: 1px solid #2d333b;">
                <span style="color: #2ea043;">🧪</span> Fertilizer Recommendations
            </div>
            <div style="background: #161b22; border-radius: 10px; padding: 15px 25px; border: 1px solid #2d333b;">
                <span style="color: #f0883e;">🔮</span> Climate Projections
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("🌱 FarmIQ Pro | Built for Hackathon | 0 ML Models, 100% Transparency")
