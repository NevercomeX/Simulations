# -*- coding: utf-8 -*-
"""
Dashboard Interactivo para el Reactor de Hidrogenación de Nitrobenceno
Autor: Antigravity AI
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from model import NitrobenzeneSimulator
from thermo import Chemical

# Configuración de la página
st.set_page_config(
    page_title="Simulador de Reactores: Hidrogenación",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Premium (Glassmorphism & Gradient Headers)
st.markdown("""
<style>
    /* Estilo del título principal */
    .main-title {
        background: linear-gradient(135deg, #FF4B4B 0%, #FF8F8F 100%);
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
        font-size: 2.2rem;
        font-weight: 700;
        color: #FF4B4B;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 500;
        color: #555555;
    }
</style>
""", unsafe_allow_html=True)

# Título y encabezado
st.markdown('<div class="main-title">Reactor de Hidrogenación de Nitrobenceno</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Simulador termodinámico interactivo: Gas Ideal vs Gas Real (Peng-Robinson)</div>', unsafe_allow_html=True)

# Inicializar Simulador
@st.cache_resource
def get_simulator():
    return NitrobenzeneSimulator()

sim = get_simulator()

# ---------------------------------------------------------
# Barra Lateral (Controles)
# ---------------------------------------------------------
st.sidebar.markdown("### Configuración del Reactor")

T_in_C = st.sidebar.slider(
    "Temperatura de Entrada (ºC)",
    min_value=100.0,
    max_value=400.0,
    value=300.0,
    step=10.0,
    help="Temperatura a la que ingresa la alimentación al reactor."
)

P_react_kPa = st.sidebar.slider(
    "Presión del Reactor (kPa)",
    min_value=100.0,
    max_value=2000.0,
    value=500.0,
    step=50.0,
    help="Presión total de operación del reactor."
)

F_NB0 = st.sidebar.slider(
    "Alimentación de Nitrobenceno (kmol/h)",
    min_value=10.0,
    max_value=500.0,
    value=100.0,
    step=10.0,
    help="Flujo molar de nitrobenceno alimentado."
)

H2_ratio = st.sidebar.slider(
    "Relación Molar H₂ / Nitrobenceno",
    min_value=3.0,
    max_value=20.0,
    value=10.0,
    step=0.5,
    help="Relación molar de hidrógeno a nitrobenceno en la alimentación."
)

X_pct = st.sidebar.slider(
    "Conversión de Nitrobenceno (%)",
    min_value=50.0,
    max_value=100.0,
    value=99.0,
    step=0.5,
    help="Porcentaje de nitrobenceno que reacciona."
)
X = X_pct / 100.0

# ---------------------------------------------------------
# Cálculos Termodinámicos y Balances
# ---------------------------------------------------------
# Balance de materia
F0, F, y = sim.calculate_balance(F_NB0, H2_ratio, X)

# Termodinámica
dH_rxn_ideal_Tin, dH_rxn_real_Tin, Q_isothermal_ideal, Q_isothermal_real, chems_in = sim.calculate_thermodynamics(
    T_in_C, P_react_kPa, F_NB0, H2_ratio, X
)

# Adiabático
T_out_ideal, T_out_real = sim.solve_adiabatic(T_in_C, P_react_kPa, F_NB0, H2_ratio, X, chems_in)

# ---------------------------------------------------------
# Interfaz de Usuario: Métricas Principales (KPIs)
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("MODELO GAS IDEAL")
        st.metric(
            label="Calor de Reacción (a T_in)",
            value=f"{dH_rxn_ideal_Tin/1e3:.2f} kJ/mol"
        )
        st.metric(
            label="Potencia Térmica Isoterma (Heat Duty)",
            value=f"{Q_isothermal_ideal/1000.0:.3f} MW",
            help="Calor que se debe retirar del reactor para mantenerlo isotérmico."
        )
        st.metric(
            label="Temp. Salida Reactor Adiabático",
            value=f"{T_out_ideal - 273.15:.2f} ºC",
            help="Temperatura de la corriente de salida si no hay transferencia de calor."
        )

with col2:
    with st.container(border=True):
        st.subheader("MODELO GAS REAL (PR)")
        st.metric(
            label="Calor de Reacción (a T_in)",
            value=f"{dH_rxn_real_Tin/1e3:.2f} kJ/mol",
            delta=f"{(dH_rxn_real_Tin - dH_rxn_ideal_Tin)/1e3:.2f} kJ/mol (Dep.)",
            delta_color="inverse"
        )
        st.metric(
            label="Potencia Térmica Isoterma (Heat Duty)",
            value=f"{Q_isothermal_real/1000.0:.3f} MW",
            delta=f"{(Q_isothermal_real - Q_isothermal_ideal)/1000.0:.3f} MW",
            delta_color="inverse",
            help="Calor que se debe retirar del reactor en el modelo real."
        )
        st.metric(
            label="Temp. Salida Reactor Adiabático",
            value=f"{T_out_real - 273.15:.2f} ºC",
            delta=f"{(T_out_real - T_out_ideal):.2f} ºC",
            delta_color="inverse",
            help="Temperatura del reactor adiabático real en comparación con el gas ideal."
        )

# ---------------------------------------------------------
# Pestañas de Análisis (Tabs)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Balance de Materia",
    "🔥 Termodinámica del Reactor",
    "📈 Comportamiento Termofísico (Cp & dH)",
    "📖 Explicación y Justificación"
])

# ---------------------------------------------------------
# Tab 1: Balance de Materia
# ---------------------------------------------------------
with tab1:
    st.write("### Flujos de Entrada y Salida del Reactor")
    
    # Crear DataFrame
    df_balance = pd.DataFrame({
        "Componente": sim.names,
        "Fórmula": sim.formulas,
        "Flujo Entrada (kmol/h)": F0,
        "Flujo Salida (kmol/h)": F,
        "Fracción Molar Salida (%)": y * 100.0
    })
    
    st.dataframe(df_balance.style.format({
        "Flujo Entrada (kmol/h)": "{:.2f}",
        "Flujo Salida (kmol/h)": "{:.2f}",
        "Fracción Molar Salida (%)": "{:.3f}%"
    }), width='stretch')
    
    # Gráfico de barras de comparación
    st.write("### Comparación de Flujos Molares")
    fig_flow, ax_flow = plt.subplots(figsize=(10, 4.5))
    x_indices = np.arange(len(sim.names))
    width = 0.35
    
    rects1 = ax_flow.bar(x_indices - width/2, F0, width, label='Entrada', color='#4A90E2', edgecolor='black', alpha=0.85)
    rects2 = ax_flow.bar(x_indices + width/2, F, width, label='Salida', color='#F5A623', edgecolor='black', alpha=0.85)
    
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
# Tab 2: Termodinámica del Reactor
# ---------------------------------------------------------
with tab2:
    st.write("### Análisis de la Elevación de Temperatura (Adiabático)")
    st.write(
        f"El reactor ingresa a **{T_in_C:.1f} ºC** y, al no haber remoción de calor, "
        f"la energía de reacción liberada eleva la temperatura del flujo de productos hasta "
        f"**{T_out_real - 273.15:.1f} ºC** (Modelo Real) o **{T_out_ideal - 273.15:.1f} ºC** (Modelo Ideal)."
    )
    
    # Diagrama de elevación de temperatura
    fig_temp, ax_temp = plt.subplots(figsize=(8, 4))
    modelos = ['Entrada', 'Salida (Gas Ideal)', 'Salida (Gas Real)']
    temps = [T_in_C, T_out_ideal - 273.15, T_out_real - 273.15]
    colors_temp = ['#4A90E2', '#FF4B4B', '#bd10e0']
    
    bars_t = ax_temp.barh(modelos, temps, color=colors_temp, height=0.5, edgecolor='black', alpha=0.85)
    ax_temp.set_xlabel('Temperatura (ºC)')
    ax_temp.grid(True, linestyle='--', alpha=0.5, axis='x')
    
    for bar in bars_t:
        width = bar.get_width()
        ax_temp.text(width + 15, bar.get_y() + bar.get_height()/2.0, f'{width:.1f} ºC',
                    ha='left', va='center', fontweight='bold', fontsize=10)
        
    ax_temp.set_xlim(0, max(temps) * 1.15)
    plt.tight_layout()
    st.pyplot(fig_temp)

# ---------------------------------------------------------
# Tab 3: Comportamiento Termofísico (Cp & dH)
# ---------------------------------------------------------
with tab3:
    st.write("### Variación de Propiedades con la Temperatura")
    
    col_plot1, col_plot2 = st.columns(2)
    
    with col_plot1:
        st.write("#### Capacidad Calorífica Gas Ideal ($C_{p,g}$)")
        T_range = np.linspace(300.0, 1500.0, 200)
        fig_cp, ax_cp = plt.subplots(figsize=(6, 4))
        colors_cp = ['#d62728', '#1f77b4', '#2ca02c', '#ff7f0e']
        
        for idx, (name, c) in enumerate(zip(sim.names, sim.species)):
            cpg_vals = [c.HeatCapacityGas.calculate(t, c.HeatCapacityGas.method) for t in T_range]
            ax_cp.plot(T_range - 273.15, cpg_vals, label=name, color=colors_cp[idx], linewidth=2.0)
            
        ax_cp.set_xlabel("Temperatura (ºC)")
        ax_cp.set_ylabel("$C_{p,g}$ (J / mol·K)")
        ax_cp.grid(True, linestyle='--', alpha=0.5)
        ax_cp.legend(fontsize=9)
        plt.tight_layout()
        st.pyplot(fig_cp)
        
    with col_plot2:
        st.write(r"#### Entalpía de Reacción ($\Delta_r H$) vs Temperatura")
        T_range_rxn = np.linspace(298.15, 1000.0, 100)
        
        # Calcular dH en función de T para ambos modelos
        dH_ideal_range = []
        dH_real_range = []
        P_react = P_react_kPa * 1000.0
        
        for t in T_range_rxn:
            # Ideal Gas
            dh_id = sim.dH_rxn_std_gas + np.sum(
                sim.nu * np.array([c.HeatCapacityGas.T_dependent_property_integral(298.15, t) for c in sim.species])
            )
            dH_ideal_range.append(dh_id / 1e3) # kJ/mol
            
            # Real Gas
            try:
                chems_t = [Chemical(c.CAS, T=t, P=P_react) for c in sim.species]
                dh_re = sim.dH_rxn_std_stable + np.sum(sim.nu * np.array([c.Hm for c in chems_t]))
                dH_real_range.append(dh_re / 1e3)
            except Exception:
                dH_real_range.append(dh_id / 1e3)
                
        fig_dh, ax_dh = plt.subplots(figsize=(6, 4))
        ax_dh.plot(T_range_rxn - 273.15, dH_ideal_range, label='Gas Ideal', color='#4A90E2', linewidth=2.5)
        ax_dh.plot(T_range_rxn - 273.15, dH_real_range, label=f'Gas Real ({P_react_kPa/100:.1f} bar)', color='#bd10e0', linestyle='--', linewidth=2.0)
        ax_dh.set_xlabel("Temperatura (ºC)")
        ax_dh.set_ylabel(r"$\Delta_r H$ (kJ / mol)")
        ax_dh.grid(True, linestyle='--', alpha=0.5)
        ax_dh.legend(fontsize=9)
        plt.tight_layout()
        st.pyplot(fig_dh)

# ---------------------------------------------------------
# Tab 4: Explicación y Justificación
# ---------------------------------------------------------
with tab4:
    st.write("### 📖 Fundamentos Termodinámicos y Justificación del Modelo")
    
    st.markdown("""
    En esta sección se detalla el sustento físico-químico del simulador y se analizan críticamente los resultados obtenidos al comparar el comportamiento de **Gas Ideal** frente a **Gas Real** (utilizando la ecuación de estado de **Peng-Robinson**).
    """)
    
    col_just1, col_just2 = st.columns(2)
    
    with col_just1:
        st.info("""
        **1. Naturaleza de la Reacción Química**
        La hidrogenación catalítica de nitrobenceno a anilina es una reacción de vital importancia en la industria química (por ejemplo, en la síntesis de poliuretanos, colorantes y fármacos).
        
        $$ \\text{C}_6\\text{H}_5\\text{NO}_2\\text{ (g)} + 3\\text{H}_2\\text{ (g)} \\rightarrow \\text{C}_6\\text{H}_5\\text{NH}_2\\text{ (g)} + 2\\text{H}_2\\text{O (g)} $$
        
        * **Altamente Exotérmica:** La reacción libera una gran cantidad de calor (alrededor de $-443 \\text{ kJ/mol}$ a condiciones estándar). Esta enorme liberación de energía hace que el control de temperatura sea el desafío de diseño más crítico en el reactor.
        * **Variación Molar:** Pasa de 4 moles de reactivo a 3 moles de producto (reducción de volumen molar a presión constante), lo que hace que la presión de operación influya directamente en el equilibrio y en el comportamiento volumétrico de la mezcla.
        """)
        
        st.markdown("""
        **2. Limitaciones del Modelo de Gas Ideal**
        El modelo de **Gas Ideal** asume que:
        1. Las moléculas de gas no tienen volumen propio (son puntos de masa infinitamente pequeños).
        2. No existen fuerzas de atracción o repulsión intermoleculares.
        
        Bajo estas suposiciones, la entalpía de la mezcla depende **exclusivamente** de la temperatura ($H = H(T)$). No obstante, para presiones moderadas a altas (donde la densidad del gas aumenta y las moléculas se encuentran más próximas) estas suposiciones fallan significativamente.
        """)
        
    with col_just2:
        st.success("""
        **3. Ventajas del Modelo de Gas Real (Peng-Robinson)**
        La ecuación de estado de **Peng-Robinson (PR)** describe de manera más precisa el comportamiento del sistema real al incorporar dos parámetros críticos:
        * **Parámetro $a(T)$:** Mide las fuerzas de atracción intermolecular.
        * **Parámetro $b$ (covolumen):** Representa el volumen propio ocupado por las moléculas de gas.
        
        $$ P = \\frac{RT}{v-b} - \\frac{a(T)}{v(v+b) + b(v-b)} $$
        
        La entalpía del gas real se calcula sumando la entalpía del gas ideal y la **entalpía de desviación (departure enthalpy, $H^{dep}$)**:
        
        $$ H(T, P) = H^{id}(T) + H^{dep}(T, P) $$
        
        La entalpía de desviación representa el trabajo neto realizado contra las fuerzas de atracción moleculares al expandir el gas real desde su volumen actual hasta un volumen infinito (estado de gas ideal).
        """)
        
    st.write("---")
    st.write("### 🔍 Análisis de Desviación y su Impacto en el Diseño")
    
    col_just3, col_just4 = st.columns(2)
    
    with col_just3:
        st.markdown(f"""
        **¿Por qué difieren los calores de reacción ($\\Delta_r H$)?**
        La entalpía de reacción en el modelo real se define como:
        
        $$ \\Delta_r H_{{real}}(T, P) = \\sum \\nu_i H_i(T, P) $$
        
        Dado que cada componente tiene una entalpía de desviación diferente (debido a diferencias en polaridad, tamaño molecular y factores acéntricos), la suma ponderada del calor de reacción difiere del caso ideal.
        
        * Con la configuración actual (Presión = **{P_react_kPa:.1f} kPa** y Temp. Entrada = **{T_in_C:.1f} ºC**):
          * $\\Delta_r H^{{ideal}}$ = **{dH_rxn_ideal_Tin/1e3:.2f} kJ/mol**
          * $\\Delta_r H^{{real}}$ = **{dH_rxn_real_Tin/1e3:.2f} kJ/mol**
          * Desviación absoluta = **{abs(dH_rxn_real_Tin - dH_rxn_ideal_Tin)/1e3:.2f} kJ/mol** ({abs(dH_rxn_real_Tin - dH_rxn_ideal_Tin)/dH_rxn_ideal_Tin*100:.2f}% de error relativo).
        """)
    
    with col_just4:
        st.markdown(f"""
        **Impacto en la Operación Adiabática e Isoterma:**
        1. **Caso Isotérmico (Heat Duty):**
           Para mantener el reactor a la temperatura de entrada (**{T_in_C:.1f} ºC**), se requiere retirar calor.
           * Calor a retirar (Gas Ideal): **{Q_isothermal_ideal/1000.0:.3f} MW**
           * Calor a retirar (Gas Real): **{Q_isothermal_real/1000.0:.3f} MW**
           * Si se diseña el sistema de refrigeración usando gas ideal, se cometería un desfase de **{abs(Q_isothermal_real - Q_isothermal_ideal)/1000.0:.3f} MW** en la capacidad de transferencia de calor.
        
        2. **Caso Adiabático (Temperatura de Salida):**
           * Temp. Salida (Gas Ideal): **{T_out_ideal - 273.15:.1f} ºC**
           * Temp. Salida (Gas Real): **{T_out_real - 273.15:.1f} ºC**
           * La diferencia de temperatura de **{abs(T_out_real - T_out_ideal):.2f} ºC** es clave. Temperaturas más altas pueden provocar desactivación térmica del catalizador, reacciones secundarias no deseadas o riesgos de embalamiento térmico (*runaway*).
        """)
        
    st.warning("""
    ⚠️ **Conclusión de Ingeniería:**
    Utilizar el modelo de **Gas Ideal** para el diseño de reactores de hidrogenación bajo condiciones de presión industrial (típicamente > 5 bar) introduce desviaciones no despreciables en los balances de energía. Para asegurar un diseño seguro, evitar puntos calientes (*hotspots*) y dimensionar correctamente los cambiadores de calor, es mandatorio emplear ecuaciones de estado consistentes como **Peng-Robinson**, especialmente al tratar con mezclas gaseosas complejas que involucran moléculas polares como la anilina y el agua junto con gases altamente supercríticos como el hidrógeno.
    """)

    st.info("""
    **📚 Librerías Utilizadas y Justificación del Paquete Termodinámico:**
    * **Librerías de Python:** `streamlit` (interfaz y visualización), `thermo` (propiedades y equilibrio de fases), `scipy.optimize.brentq` (búsqueda de raíces para balances térmicos adiabáticos), `numpy` (operaciones numéricas matriciales), `matplotlib.pyplot` (gráficas del comportamiento de Cp y entalpía) y `pandas` (tablas de balance de materia).
    * **Justificación de la Elección Termodinámica (Peng-Robinson):**
      El simulador opera en condiciones de presión moderada a alta (hasta 2000 kPa / 20 bar) y maneja una mezcla reactiva con hidrógeno (un gas supercrítico) y compuestos condensables pesados y polares (nitrobenceno, anilina y agua). El modelo de gas ideal no representa adecuadamente las interacciones moleculares bajo estas condiciones. 
      Se ha seleccionado la ecuación de estado de **Peng-Robinson (PR)** en la librería `thermo` debido a su versatilidad para predecir coeficientes de fugacidad y entalpías de desviación (departure enthalpy) para mezclas gaseosas de hidrocarburos y gases disueltos. Esto nos permite cuantificar la no-idealidad termodinámica a nivel de desviación de entalpía de la mezcla, garantizando cálculos térmicos (heat duties) y de temperatura de salida adiabática exactos y seguros para el diseño del reactor.
    """)
