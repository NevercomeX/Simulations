# -*- coding: utf-8 -*-
"""
Dashboard Interactivo para el Reactor de Esterificación de Acetato de Etilo
Autor: Antigravity AI
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from model import EsterificationSimulator

# Configuración de la página
st.set_page_config(
    page_title="Simulador de Esterificación: Acetato de Etilo",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Premium (Glassmorphism & Gradient Headers)
st.markdown("""
<style>
    /* Estilo del título principal */
    .main-title {
        background: linear-gradient(135deg, #4A90E2 0%, #bd10e0 100%);
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
        color: #bd10e0;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 500;
        color: #555555;
    }
    /* Tarjetas personalizadas */
</style>
""", unsafe_allow_html=True)

# Título del Dashboard
st.markdown('<div class="main-title">Esterificación de Acetato de Etilo</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Simulador del reactor continuo CSTR en fase líquida con análisis termodinámico y de sensibilidad</div>', unsafe_allow_html=True)

# Inicializar Simulador
@st.cache_resource
def get_simulator():
    return EsterificationSimulator()

sim = get_simulator()

# ---------------------------------------------------------
# Barra Lateral (Controles del Reactor)
# ---------------------------------------------------------
st.sidebar.markdown("### Configuración del CSTR")

T_reactor_C = st.sidebar.slider(
    "Temperatura del Reactor (ºC)",
    min_value=50.0,
    max_value=130.0,
    value=70.0,
    step=1.0,
    help="Temperatura de operación del reactor continuo."
)

T_feed_C = st.sidebar.slider(
    "Temperatura de Alimentación (ºC)",
    min_value=20.0,
    max_value=100.0,
    value=70.0,
    step=1.0,
    help="Temperatura a la que ingresan los reactivos al reactor."
)

F_A0 = st.sidebar.slider(
    "Alimentación de Ácido Acético (kmol/h)",
    min_value=10.0,
    max_value=200.0,
    value=50.0,
    step=5.0,
    help="Flujo molar de entrada del ácido acético (reactivo limitante)."
)

feed_ratio = st.sidebar.slider(
    "Relación Molar Etanol / Ácido Acético",
    min_value=0.5,
    max_value=3.0,
    value=1.0,
    step=0.1,
    help="Relación molar de alimentación (EtOH/AcOH). Una relación de 1.0 significa alimentación equimolar."
)

W_kg = st.sidebar.slider(
    "Masa del Catalizador (kg)",
    min_value=0.1,
    max_value=2000.0,
    value=1.0,
    step=1.0,
    help="Masa total de catalizador sólido dentro del reactor. Al aumentar este valor, se aumenta la velocidad de reacción efectiva (residencia química)."
)

# ---------------------------------------------------------
# Cálculos Principales
# ---------------------------------------------------------
# Resolver el balance de materia en el CSTR
X, F_out, rates = sim.solve_cstr(T_reactor_C, F_A0, W_kg, feed_ratio)
r_f, r_b, r_net = rates
kf, kb = sim.get_k(T_reactor_C + 273.15)

# Flujos de entrada
F_in = np.array([F_A0, F_A0 * feed_ratio, 0.0, 0.0])
F_total_in = np.sum(F_in)
F_total_out = np.sum(F_out)

# Fracciones molares de salida
y_out = F_out / F_total_out if F_total_out > 0 else np.zeros(4)
y_EtOAc_pct = y_out[2] * 100.0

# Calcular Cargas Térmicas (Heat Duties)
dH_rxn, Q_rxn, Q_sensible, Q_total = sim.calculate_heat_duties(
    T_reactor_C, T_feed_C, F_A0, W_kg, X, feed_ratio
)

# Ejecutar Análisis de Sensibilidad
df_sens, T_opt, max_y = sim.run_sensitivity(F_A0, W_kg, feed_ratio)

# ---------------------------------------------------------
# Panel Principal: KPIs y Métricas clave
# ---------------------------------------------------------
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    with st.container(border=True):
        st.metric(
            label="Frac. Molar Acetato de Etilo",
            value=f"{y_EtOAc_pct:.3f} %",
            help="Porcentaje molar de acetato de etilo en la corriente de salida del reactor."
        )

with col_kpi2:
    with st.container(border=True):
        st.metric(
            label="Conversión del Ácido Acético",
            value=f"{X*100.0:.3f} %",
            help="Fracción del ácido acético alimentado que reacciona para formar producto."
        )

with col_kpi3:
    with st.container(border=True):
        st.metric(
            label="Calor de Reacción (Q_rxn)",
            value=f"{Q_rxn:.3f} kW",
            help="Calor liberado por la reacción química. Un valor negativo indica reacción exotérmica."
        )

with col_kpi4:
    with st.container(border=True):
        st.metric(
            label="Temperatura Óptima del Reactor",
            value=f"{T_opt:.1f} ºC",
            help="Temperatura dentro del rango 50-130ºC que proporciona la máxima fracción molar de Acetato de Etilo."
        )

# ---------------------------------------------------------
# Pestañas de Análisis (Tabs)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Balance de Materia",
    "🔥 Cinética y Termodinámica",
    "📈 Análisis de Sensibilidad",
    "📖 Fundamentos Teóricos"
])

# ---------------------------------------------------------
# Tab 1: Balance de Materia
# ---------------------------------------------------------
with tab1:
    st.write("### Corrientes de Entrada y Salida del CSTR")
    
    # Crear DataFrame de Balance
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
    
    st.write("### Comparación Gráfica de Flujos Molares")
    fig_flow, ax_flow = plt.subplots(figsize=(10, 4.5))
    x_indices = np.arange(len(sim.names))
    width = 0.35
    
    rects1 = ax_flow.bar(x_indices - width/2, F_in, width, label='Entrada', color='#4A90E2', edgecolor='black', alpha=0.85)
    rects2 = ax_flow.bar(x_indices + width/2, F_out, width, label='Salida', color='#bd10e0', edgecolor='black', alpha=0.85)
    
    ax_flow.set_ylabel('Flujo Molar (kmol/h)')
    ax_flow.set_title('Balance de Materia en el Reactor')
    ax_flow.set_xticks(x_indices)
    ax_flow.set_xticklabels(sim.names)
    ax_flow.legend()
    ax_flow.grid(True, linestyle='--', alpha=0.5, axis='y')
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 0:
                ax_flow.annotate(f'{height:.2f}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9)
            
    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    st.pyplot(fig_flow)

# ---------------------------------------------------------
# Tab 2: Cinética y Termodinámica
# ---------------------------------------------------------
with tab2:
    st.write("### Parámetros de Transferencia de Energía e Enfoque Cinético")
    
    col_term1, col_term2 = st.columns(2)
    
    with col_term1:
        st.info("#### Cargas Térmicas del Reactor (Heat Duties)")
        st.write(f"**Calor de Reacción a {T_reactor_C:.1f} ºC ($\\Delta_r H$):** `{dH_rxn:.4f} kJ/mol` (exotérmica)")
        st.write(f"**Potencia de Reacción ($Q_{{rxn}}$):** `{Q_rxn:.4f} kW` (calor liberado)")
        st.write(f"**Potencia Sensible ($Q_{{sensible}}$):** `{Q_sensible:.4f} kW` (calor necesario para calentar la alimentación de {T_feed_C:.1f}ºC a {T_reactor_C:.1f}ºC)")
        
        # Resaltar la potencia neta requerida por el reactor
        if Q_total < 0:
            st.success(f"**Potencia Térmica Total a RETIRAR ($Q_{{total}}$):** `{abs(Q_total):.4f} kW` (enfriamiento necesario)")
        else:
            st.warning(f"**Potencia Térmica Total a SUMINISTRAR ($Q_{{total}}$):** `{Q_total:.4f} kW` (calentamiento necesario)")
            
    with col_term2:
        st.success("#### Constantes Cinéticas y Velocidades de Reacción")
        st.write(f"**Constante Directa ($k_f$):** `{kf:.4e} kmol/s` (Ea = 48.3 kJ/mol)")
        st.write(f"**Constante Inversa ($k_b$):** `{kb:.4e} kmol/s` (Ea = 66.2 kJ/mol)")
        st.write("---")
        st.write(f"**Velocidad de Reacción Directa ($r_f$):** `{r_f:.6e} kmol/s` (efectiva)")
        st.write(f"**Velocidad de Reacción Reversa ($r_b$):** `{r_b:.6e} kmol/s` (efectiva)")
        st.write(f"**Velocidad Neta de Reacción ($r_{{net}}$):** `{r_net:.6e} kmol/s` (efectiva)")

# ---------------------------------------------------------
# Tab 3: Análisis de Sensibilidad
# ---------------------------------------------------------
with tab3:
    st.write("### Variación de la Fracción Molar de Acetato de Etilo con la Temperatura")
    st.write(
        f"Al realizar un barrido de temperatura entre **50 ºC** y **130 ºC** (con paso de **5 ºC**), "
        f"se puede analizar el efecto del balance termodinámico y cinético. La temperatura óptima obtenida es "
        f"**{T_opt:.1f} ºC**, proporcionando una fracción molar máxima de **{max_y:.4f} %** de Acetato de Etilo en los productos."
    )
    
    # Graficar sensibilidad
    fig_sens, ax_sens = plt.subplots(figsize=(10, 5))
    ax_sens.plot(df_sens['Temperature_C'], df_sens['y_EtOAc'], marker='o', color='#bd10e0', linewidth=2.5, label='Fracción EtOAc (%)')
    
    # Resaltar la temperatura óptima
    ax_sens.axvline(x=T_opt, color='green', linestyle='--', alpha=0.7, label=f'T Óptima: {T_opt}ºC')
    ax_sens.plot(T_opt, max_y, marker='*', markersize=15, color='gold', markeredgecolor='black')
    
    # Resaltar la temperatura actual de operación
    y_current = df_sens.loc[df_sens['Temperature_C'] == T_reactor_C, 'y_EtOAc'].values[0]
    ax_sens.plot(T_reactor_C, y_current, marker='o', markersize=10, color='red', label=f'Operación Actual: {T_reactor_C}ºC')
    
    ax_sens.set_xlabel('Temperatura (ºC)', fontsize=11)
    ax_sens.set_ylabel('Fracción Molar de EtOAc (%)', fontsize=11)
    ax_sens.set_title('Prueba de Sensibilidad: Efecto de la Temperatura', fontsize=13, fontweight='bold')
    ax_sens.grid(True, linestyle='--', alpha=0.5)
    ax_sens.legend(fontsize=10)
    
    plt.tight_layout()
    st.pyplot(fig_sens)
    
    # Mostrar tabla de datos de sensibilidad
    with st.expander("Ver tabla completa de datos de sensibilidad"):
        st.dataframe(df_sens.style.format({
            'Conversion': '{:.6f}',
            'Conversion_pct': '{:.3f}%',
            'y_EtOAc': '{:.4f}%',
            'kf': '{:.4e}',
            'kb': '{:.4e}',
            'dH_rxn': '{:.4f} kJ/mol',
            'Q_rxn': '{:.4f} kW'
        }), width='stretch')

# ---------------------------------------------------------
# Tab 4: Fundamentos Teóricos
# ---------------------------------------------------------
with tab4:
    st.write("### 📖 Sustento Físico-Químico y Análisis del Reactor")
    
    col_doc1, col_doc2 = st.columns(2)
    
    with col_doc1:
        st.info("""
        **1. Cinética de la Reacción Reversible**
        La esterificación se modela como una reacción elemental reversible en fase líquida homogénea:
        
        $$ \\text{CH}_3\\text{COOH} + \\text{CH}_3\\text{CH}_2\\text{OH} \\rightleftharpoons \\text{CH}_3\\text{COOC}_2\\text{H}_5 + \\text{H}_2\\text{O} $$
        
        Las velocidades de reacción directa ($r_f$) y reversa ($r_b$) se expresan como:
        
        $$ r_f = k_f x_{\\text{EtOH}} x_{\\text{AcOH}}^{1.5} $$
        $$ r_b = k_b x_{\\text{EtOAc}} x_{\\text{H}_2\\text{O}} $$
        
        Donde las constantes cinéticas de Arrhenius siguen el comportamiento de activación térmica:
        
        $$ k_f = 4.24 \\times 10^3 \\exp\\left(\\frac{-48300\\text{ J/mol}}{RT}\\right) \\text{ kmol/s} $$
        $$ k_b = 4.55 \\times 10^5 \\exp\\left(\\frac{-66200\\text{ J/mol}}{RT}\\right) \\text{ kmol/s} $$
        """)
        
        st.markdown("""
        **2. Ecuación de Diseño del CSTR**
        Para un reactor CSTR que opera en estado estacionario con catalizador sólido, el balance molar para el reactivo limitante (Ácido Acético, component A) se define como:
        
        $$ F_{A0} - F_A = W \\cdot r_{\\text{net}} $$
        
        Donde $W$ es la masa de catalizador, y $r_{\\text{net}} = r_f - r_b$. Al definir la conversión $X$:
        
        $$ F_{A0} \\cdot X = W \\cdot (r_f - r_b) $$
        
        Esta ecuación es resuelta numéricamente para encontrar el valor de $X \\in [0, 1)$ a cada temperatura.
        """)
        
    with col_doc2:
        st.success("""
        **3. Control Cinético vs. Control Termodinámico**
        Dado que la energía de activación directa ($E_{a,f} = 48.3 \\text{ kJ/mol}$) es **menor** que la inversa ($E_{a,b} = 66.2 \\text{ kJ/mol}$), la reacción es **exotérmica**:
        
        * A temperaturas bajas, la reacción es lenta debido a limitaciones cinéticas (valores de $k_f$ y $k_b$ pequeños), por lo que la conversión es baja.
        * A temperaturas altas, la velocidad de reacción aumenta exponencialmente, pero la constante de equilibrio ($K_{eq} = k_f/k_b$) disminuye, lo que limita la conversión termodinámica máxima.
        
        **Efecto de la Masa de Catalizador ($W$):**
        * Si el reactor posee **baja cantidad de catalizador ($W = 1.0\\text{ kg}$)**, el reactor opera bajo fuerte **control cinético** en todo el rango analizado, lo que hace que la conversión aumente de manera continua hasta los 130ºC (la tasa de equilibrio inversa no llega a limitar el proceso).
        * Si se **incrementa la masa de catalizador (por ejemplo a $1000\\text{ kg}$)**, las tasas de reacción se incrementan permitiendo que el reactor alcance el equilibrio químico. En este escenario, la conversión termodinámica limita el rendimiento a altas temperaturas, mostrando un **óptimo claro (por ejemplo, a 105 ºC)**, donde se maximiza el equilibrio sin sacrificar la velocidad cinética de aproximación.
        """)
        
        st.warning("""
        ⚠️ **Conclusión de Diseño:**
        El comportamiento óptimo del reactor de esterificación es una función conjunta del tiempo de residencia química (definido por el catalizador $W$ y los flujos) y la termodinámica de la mezcla líquida. Un dimensionado riguroso requiere operar en la ventana de temperatura óptima para evitar excesos de catalizador o temperaturas excesivamente elevadas que aumenten la presión de vapor de la mezcla y requieran equipos de alta presión.
        """)

    st.info("""
    **📚 Librerías Utilizadas y Justificación del Paquete Termodinámico:**
    * **Librerías de Python:** `streamlit` (interfaz interactiva), `thermo` (base de datos fisicoquímicos), `scipy.optimize.brentq` (cálculo numérico de la conversión del CSTR), `numpy` (operaciones de matrices y balances), `matplotlib.pyplot` (gráficas del balance y de sensibilidad) y `pandas` (administración de flujos molares).
    * **Justificación de la Elección Termodinámica (Fase Líquida):**
      Dado que la esterificación de ácido acético y etanol ocurre en fase líquida a presiones bajas (1 atm) y temperaturas entre 50 y 130 ºC, los reactivos y productos se comportan como una mezcla líquida homogénea subenfriada o saturada (bajo presión).
      Se justifica el uso del paquete de propiedades de fase líquida estable de la librería `thermo`. El calor de reacción y los balances de energía se resuelven utilizando las entalpías molares líquidas (`c.Hm`) y entalpías estándar de formación (`c.Hfm`), obtenidas mediante las correlaciones de capacidad calorífica de líquidos (DIPPR) de `thermo`. Esto permite estimar rigurosamente los cambios térmicos de calentamiento y reacción, fundamentales para dimensionar las necesidades de refrigeración/calefacción en la esterificación.
    """)
