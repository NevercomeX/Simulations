# -*- coding: utf-8 -*-
"""
Dashboard Interactivo para el Reactor PFR de Hidrodesalquilación de Tolueno
Autor: Antigravity AI
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from model import HydrodealkylationSimulator

# Constante de los gases ideales (J / (mol*K))
R = 8.3144

# Configuración de la página
st.set_page_config(
    page_title="Simulador de Reactor PFR: Hidrodesalquilación",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Premium (Glassmorphism & Gradient Headers)
st.markdown("""
<style>
    /* Estilo del título principal */
    .main-title {
        background: linear-gradient(135deg, #FF9F00 0%, #bd10e0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-align: left;
    }
    .subtitle {
        color: #7d7d7d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    /* Estilo para las tarjetas de métricas */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
        color: #FF9F00;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: 500;
        color: #555555;
    }
    /* Evitar truncamiento en métricas */
    div[data-testid="stMetricValue"] > div,
    div[data-testid="stMetricLabel"] > div,
    div[data-testid="stMetricLabel"] {
        white-space: normal !important;
        word-break: break-word !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
</style>
""", unsafe_allow_html=True)

# Título y encabezado
st.markdown('<div class="main-title">Hidrodesalquilación de Tolueno a Benceno</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Simulador de reactor de flujo continuo (PFR) de múltiples tubos con balances de materia, energía y perfiles longitudinales</div>', unsafe_allow_html=True)

# Inicializar Simulador
@st.cache_resource
def get_p3_simulator():
    return HydrodealkylationSimulator()

sim = get_p3_simulator()

# ---------------------------------------------------------
# Barra Lateral (Controles)
# ---------------------------------------------------------
st.sidebar.markdown("### Configuración de Operación")

T_reactor_C = st.sidebar.slider(
    "Temperatura del Reactor (ºC)",
    min_value=700.0,
    max_value=900.0,
    value=815.0,
    step=5.0,
    help="Temperatura a la que opera isotérmicamente el reactor."
)

T_feed_C = st.sidebar.slider(
    "Temperatura de Entrada (ºC)",
    min_value=700.0,
    max_value=900.0,
    value=750.0,
    step=5.0,
    help="Temperatura a la que ingresa la corriente de alimentación al reactor."
)

P_bar = st.sidebar.slider(
    "Presión de Operación (bar)",
    min_value=10.0,
    max_value=50.0,
    value=26.0,
    step=1.0,
    help="Presión total del gas en el reactor."
)

st.sidebar.markdown("### Flujos de Alimentación (kmol/h)")

F_Tol0 = st.sidebar.slider("Tolueno", min_value=10.0, max_value=200.0, value=70.0, step=5.0)
F_H20 = st.sidebar.slider("Hidrógeno (H₂)", min_value=100.0, max_value=1000.0, value=370.0, step=10.0)
F_CH40 = st.sidebar.slider("Metano (CH₄)", min_value=0.0, max_value=500.0, value=160.0, step=10.0)
F_B0 = st.sidebar.slider("Benceno", min_value=0.0, max_value=100.0, value=4.0, step=1.0)

st.sidebar.markdown("### Geometría del Reactor PFR")

tube_length_m = st.sidebar.slider(
    "Longitud de los Tubos (m)",
    min_value=1.0,
    max_value=30.0,
    value=10.0,
    step=0.5,
    help="Longitud longitudinal de cada uno de los tubos del PFR."
)

num_tubes = st.sidebar.slider(
    "Número de Tubos",
    min_value=100,
    max_value=1000,
    value=500,
    step=50,
    help="Número total de tubos paralelos que conforman el reactor."
)

internal_diam_m = st.sidebar.slider(
    "Diámetro Interno del Tubo (m)",
    min_value=0.01,
    max_value=0.1,
    value=0.02,
    step=0.005,
    help="Diámetro interior de cada tubo del reactor."
)

# ---------------------------------------------------------
# Cálculos de Simulación
# ---------------------------------------------------------
# Integrar el perfil a lo largo del PFR
F_feed_kmol_h = [F_Tol0, F_H20, F_CH40, F_B0]
df_profile, tau, v0 = sim.solve_pfr(
    T_reactor_C, P_bar, F_feed_kmol_h, tube_length_m, num_tubes, internal_diam_m
)

# Resultados finales a la salida del PFR (última fila del perfil)
last_row = df_profile.iloc[-1]
X_final = last_row['Conversion']
F_out = np.array([last_row['F_Toluene'], last_row['F_Hydrogen'], last_row['F_Benzene'], last_row['F_Methane']])

# Caudales volumétricos y flujos
F_in = np.array(F_feed_kmol_h)
F_total_in = np.sum(F_in)
F_total_out = np.sum(F_out)
y_out = F_out / F_total_out if F_total_out > 0 else np.zeros(4)

# Calcular Cargas Térmicas (Heat Duties)
dH_rxn, Q_rxn, Q_sensible, Q_total = sim.calculate_heat_duties(
    T_reactor_C, T_feed_C, P_bar, F_feed_kmol_h, X_final
)

# Constante de velocidad
k_val = sim.get_k(T_reactor_C + 273.15)

# ---------------------------------------------------------
# KPIs Principales
# ---------------------------------------------------------
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    with st.container(border=True):
        st.metric(
            label="Conversión Tolueno",
            value=f"{X_final*100.0:.3f} %",
            help="Conversión acumulada del reactivo limitante (Tolueno) a la salida del PFR."
        )

with col_kpi2:
    with st.container(border=True):
        st.metric(
            label="Tiempo de Residencia",
            value=f"{tau:.4f} s",
            help="Tiempo promedio que tarda la mezcla gaseosa en cruzar la longitud del reactor."
        )

with col_kpi3:
    with st.container(border=True):
        st.metric(
            label="Calor Neto Requerido",
            value=f"{Q_total/1000.0:.3f} MW" if abs(Q_total) >= 1000.0 else f"{Q_total:.3f} kW",
            help="Calor neto que se debe intercambiar. Si es negativo, indica que se debe REMOVER calor para mantener la temperatura isotérmica."
        )

with col_kpi4:
    with st.container(border=True):
        st.metric(
            label="Flujo Benceno Salida",
            value=f"{F_out[2]:.3f} kmol/h",
            help="Flujo molar de benceno en la corriente de salida del reactor."
        )

# ---------------------------------------------------------
# Pestañas de Análisis (Tabs)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Balance de Materia",
    "📈 Perfiles del Reactor PFR",
    "🔥 Termodinámica y Cinética",
    "📖 Fundamentos Teóricos"
])

# ---------------------------------------------------------
# Tab 1: Balance de Materia
# ---------------------------------------------------------
with tab1:
    st.write("### Tabla de Balance de Materia Global")
    
    # Crear DataFrame
    df_balance = pd.DataFrame({
        "Componente": sim.names,
        "Fórmula": sim.formulas,
        "Entrada (kmol/h)": F_in,
        "Salida (kmol/h)": F_out,
        "Fracción Molar Salida (%)": y_out * 100.0
    })
    
    st.dataframe(df_balance.style.format({
        "Entrada (kmol/h)": "{:.3f}",
        "Salida (kmol/h)": "{:.3f}",
        "Fracción Molar Salida (%)": "{:.3f}%"
    }), width='stretch')
    
    st.write("### Comparación de Flujos de Entrada y Salida")
    fig_flow, ax_flow = plt.subplots(figsize=(10, 4.5))
    x_indices = np.arange(len(sim.names))
    width = 0.35
    
    rects1 = ax_flow.bar(x_indices - width/2, F_in, width, label='Entrada', color='#FF9F00', edgecolor='black', alpha=0.85)
    rects2 = ax_flow.bar(x_indices + width/2, F_out, width, label='Salida', color='#bd10e0', edgecolor='black', alpha=0.85)
    
    ax_flow.set_ylabel('Flujo Molar (kmol/h)')
    ax_flow.set_xticks(x_indices)
    ax_flow.set_xticklabels(sim.names)
    ax_flow.legend()
    ax_flow.grid(True, linestyle='--', alpha=0.5, axis='y')
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 0:
                ax_flow.annotate(f'{height:.1f}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9)
            
    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    st.pyplot(fig_flow)

# ---------------------------------------------------------
# Tab 2: Perfiles del Reactor PFR
# ---------------------------------------------------------
with tab2:
    st.write("### Evolución de Variables a lo Largo de la Longitud del Reactor")
    st.write(
        f"El reactor consta de **{num_tubes} tubos** con una longitud total de **{tube_length_m:.1f} m** y "
        f"un volumen total de **{num_tubes * (np.pi / 4.0) * (internal_diam_m**2) * tube_length_m:.4f} m³**."
    )
    
    col_plot1, col_plot2 = st.columns(2)
    
    with col_plot1:
        st.write("#### Perfil de Conversión de Tolueno")
        fig_conv, ax_conv = plt.subplots(figsize=(6, 4))
        ax_conv.plot(df_profile['Length_m'], df_profile['Conversion_pct'], color='#FF9F00', linewidth=2.5, label='Conversión (%)')
        ax_conv.set_xlabel('Posición en el Tubo (m)')
        ax_conv.set_ylabel('Conversión (%)')
        ax_conv.set_ylim(-5, 105)
        ax_conv.grid(True, linestyle='--', alpha=0.5)
        ax_conv.legend()
        plt.tight_layout()
        st.pyplot(fig_conv)
        
    with col_plot2:
        st.write("#### Perfil de Flujos Molares de Componentes")
        fig_prof, ax_prof = plt.subplots(figsize=(6, 4))
        colors_prof = ['#d62728', '#1f77b4', '#2ca02c', '#ff7f0e']
        
        ax_prof.plot(df_profile['Length_m'], df_profile['F_Toluene'], color=colors_prof[0], linewidth=2.0, label='Tolueno')
        ax_prof.plot(df_profile['Length_m'], df_profile['F_Hydrogen'], color=colors_prof[1], linewidth=2.0, label='H₂')
        ax_prof.plot(df_profile['Length_m'], df_profile['F_Benzene'], color=colors_prof[2], linewidth=2.0, label='Benceno')
        ax_prof.plot(df_profile['Length_m'], df_profile['F_Methane'], color=colors_prof[3], linewidth=2.0, label='Metano')
        
        ax_prof.set_xlabel('Posición en el Tubo (m)')
        ax_prof.set_ylabel('Flujo Molar (kmol/h)')
        ax_prof.grid(True, linestyle='--', alpha=0.5)
        ax_prof.legend(fontsize=9)
        plt.tight_layout()
        st.pyplot(fig_prof)

# ---------------------------------------------------------
# Tab 3: Termodinámica y Cinética
# ---------------------------------------------------------
with tab3:
    st.write("### Parámetros Energéticos y Cinéticos de la Reacción")
    
    col_term1, col_term2 = st.columns(2)
    
    with col_term1:
        st.info("#### Cargas Térmicas del PFR (Heat Duties)")
        st.write(f"**Calor de Reacción a {T_reactor_C:.1f} ºC ($\\Delta_r H$):** `{dH_rxn:.4f} kJ/mol` (exotérmica)")
        st.write(f"**Potencia de Reacción ($Q_{{rxn}}$):** `{Q_rxn:.4f} kW` (calor liberado por la reacción)")
        st.write(f"**Potencia Sensible ($Q_{{sensible}}$):** `{Q_sensible:.4f} kW` (calor necesario para calentar el gas de entrada de {T_feed_C:.1f}ºC a {T_reactor_C:.1f}ºC)")
        
        # Potencia neta
        if Q_total < 0:
            st.success(f"**Carga Térmica Neta a RETIRAR ($Q_{{total}}$):** `{abs(Q_total):.4f} kW` (refrigeración necesaria)")
        else:
            st.warning(f"**Carga Térmica Neta a SUMINISTRAR ($Q_{{total}}$):** `{Q_total:.4f} kW` (calentamiento necesario)")
            
    with col_term2:
        st.success("#### Parámetros Cinéticos a la Temperatura de Reacción")
        st.write(f"**Constante de Velocidad ($k$):** `{k_val:.6f} m^1.5 / (mol^0.5 · s)`")
        st.write(f"**Energía de Activación ($E_a$):** `209.213 kJ/mol`")
        st.write(f"**Factor Pre-exponencial ($k_0$):** `3.00e10 m^1.5 / (mol^0.5 · s)`")
        st.write("---")
        st.write(f"**Velocidad de Entrada al Reactor ($v_0$):** `{v0:.4f} m³/s` (Caudal volumétrico)")
        st.write(f"**Concentración Molar de Gas Total ($C_{{total}}$):** `{P_bar * 100000.0 / (R * (T_reactor_C + 273.15)):.4f} mol/m³` (Gas Ideal)")

# ---------------------------------------------------------
# Tab 4: Fundamentos Teóricos
# ---------------------------------------------------------
with tab4:
    st.write("### 📖 Sustento Físico-Químico y Ecuaciones del PFR")
    
    col_doc1, col_doc2 = st.columns(2)
    
    with col_doc1:
        st.info("""
        **1. Cinética de la Hidrodesalquilación**
        La reacción de hidrodesalquilación térmica de tolueno a benceno es de tipo irreversible y se lleva a cabo típicamente en fase gas a altas temperaturas:
        
        $$ \\text{C}_6\\text{H}_5\\text{CH}_3\\text{ (g)} + \\text{H}_2\\text{ (g)} \\rightarrow \\text{C}_6\\text{H}_6\\text{ (g)} + \\text{CH}_4\\text{ (g)} $$
        
        La velocidad de reacción se modela utilizando una base de concentración molar ($C_i$ en $\\text{mol/m}^3$):
        
        $$ r = k C_{\\text{Tol}} C_{\\text{H}_2}^{0.5} $$
        
        Donde la constante cinética de velocidad ($k$) sigue la ley de Arrhenius:
        
        $$ k = 3 \\times 10^{10} \\exp\\left(\\frac{-209213\\text{ J/mol}}{RT}\\right) \\text{ } \\frac{\\text{m}^{1.5}}{\\text{mol}^{0.5}\\cdot\\text{s}} $$
        """)
        
        st.markdown("""
        **2. Ecuación de Diseño del Reactor de Flujo Pistón (PFR)**
        Para un reactor PFR que opera en estado estacionario bajo comportamiento de flujo pistón, el balance molar para el Tolueno (componente A, limitante) a lo largo de un diferencial de volumen se define como:
        
        $$ \\frac{dF_{\\text{Tol}}}{dV} = -r $$
        
        Al definir la conversión de tolueno $X$ ($F_{\\text{Tol}} = F_{\\text{Tol},0}(1-X)$):
        
        $$ \\frac{dX}{dV} = \\frac{r(X)}{F_{\\text{Tol},0}} $$
        
        Esta ecuación diferencial ordinaria (EDO) se integra numéricamente a lo largo de la coordenada del volumen del reactor $V \\in [0, V_{\\text{total}}]$ con la condición inicial $X(0) = 0$.
        """)
        
    with col_doc2:
        st.success("""
        **3. Relación de Concentración en Fase Gas**
        Dado que la presión $P$ y la temperatura $T$ son constantes a lo largo del reactor (isobárico e isotérmico), y la reacción no altera el número total de moles ($\\sum \\nu_i = 0$), el caudal volumétrico del gas es constante e igual al de entrada:
        
        $$ v(V) = v_0 = \\frac{F_{\\text{total},0}}{C_{\\text{total}}} = \\frac{F_{\\text{total},0} R T}{P} $$
        
        Las concentraciones instantáneas de las especies en cualquier punto del reactor se expresan en función de la conversión $X$:
        
        $$ C_{\\text{Tol}} = \\frac{F_{\\text{Tol},0}(1-X)}{F_{\\text{total},0}} C_{\\text{total}} $$
        $$ C_{\\text{H}_2} = \\frac{F_{\\text{H}_2,0} - F_{\\text{Tol},0}X}{F_{\\text{total},0}} C_{\\text{total}} $$
        """)
        
        st.warning("""
        ⚠️ **Conclusión de Ingeniería y Tiempo de Residencia:**
        El tiempo de residencia de la mezcla gaseosa dentro del reactor se calcula directamente a partir de la relación entre el volumen total y el caudal volumétrico:
        
        $$ \\tau = \\frac{V_{\\text{total}}}{v_0} $$
        
        Bajo las condiciones dadas, el tiempo de residencia es de **2.69 segundos**, lo cual es suficiente para lograr una conversión prácticamente del **100%** del tolueno a 815 ºC, indicando que el reactor se encuentra sobredimensionado para esta temperatura o que existe un margen térmico amplio para operar a menor temperatura (lo que reduciría la tasa de coquización y aumentaría la vida útil del reactor).
        """)

    st.info("""
    **📚 Librerías Utilizadas y Justificación del Paquete Termodinámico:**
    * **Librerías de Python:** `streamlit` (interfaz interactiva), `thermo` (base de datos fisicoquímicos), `numpy` (operaciones matemáticas y el método RK4), `matplotlib.pyplot` (gráficas de flujos y perfiles a lo largo del reactor), y `pandas` (tablas de balance de materia).
    * **Justificación de la Elección Termodinámica (Fase Gas a Alta Temperatura):**
      Dado que la hidrodesalquilación de tolueno se realiza a temperaturas extremadamente altas (700 a 900 ºC) y presiones de 10 a 50 bar, todos los componentes (tolueno, hidrógeno, benceno y metano) se encuentran en fase gaseosa supercalentada (muy por encima de sus puntos de ebullición).
      Se justifica el uso del paquete de propiedades en fase gas de la librería `thermo` para calcular las entalpías de formación estándar en fase gas y la integral de capacidades caloríficas de gases ideales ($C_{p,g}$) dependiente de la temperatura. A estas elevadas temperaturas, los gases se comportan casi de manera ideal (el factor de compresibilidad $Z \\approx 1$), pero sus capacidades caloríficas varían drásticamente. El uso de la base de datos de `thermo` permite una predicción exacta del calor de reacción ($\\Delta_r H$) y de la energía de precalentamiento (sensible) a 815 ºC.
    """)
