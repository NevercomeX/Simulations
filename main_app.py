# -*- coding: utf-8 -*-
"""
Aplicación Principal / Hub de Simuladores de Reactores
Autor: Antigravity AI
"""

import streamlit as st
import sys
import os

# Configuración de la página principal (obligatorio al inicio)
st.set_page_config(
    page_title="Simulador de Reactores Químicos",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados para el panel de control lateral
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 20px;">
    <h2 style="color: #FF4B4B; margin-bottom: 0;">🧪 Reactores</h2>
    <small style="color: #7d7d7d;">Hub de Simulaciones</small>
</div>
""", unsafe_allow_html=True)

# Menú de navegación
sim_option = st.sidebar.radio(
    "Selecciona la simulación a cargar:",
    [
        "Problema 1: Esterificación (Batch)",
        "Problema 2: Hidrogenación (CSTR/Isotérmico/Adiabático)",
        "Problema 3: Hidrodesalquilación (PFR/EDO)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Simulador de Reactores Químicos**
*   Usa propiedades reales (Peng-Robinson).
*   Resuelve balances cinéticos y térmicos de forma acoplada.
""")

def run_app(folder_name):
    """
    Carga y ejecuta dinámicamente el archivo app.py del problema seleccionado,
    evitando colisiones de configuración de Streamlit y resolviendo imports relativos.
    """
    folder_path = os.path.abspath(folder_name)
    
    # 1. Agregar la carpeta al path para imports locales (como model.py)
    sys.path.insert(0, folder_path)
    
    # 2. Cambiar temporalmente el directorio de trabajo
    old_cwd = os.getcwd()
    os.chdir(folder_path)
    
    # 3. Mockear st.set_page_config para evitar StreamlitAPIException (solo se permite una vez)
    orig_set_page_config = st.set_page_config
    st.set_page_config = lambda *args, **kwargs: None
    
    try:
        app_path = os.path.join(folder_path, "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Ejecutar el código del sub-app en el contexto global
        exec(code, globals())
    finally:
        # 4. Restaurar estado original del sistema y Streamlit
        st.set_page_config = orig_set_page_config
        sys.path.pop(0)
        os.chdir(old_cwd)

# Enrutamiento de páginas
if sim_option == "Problema 1: Esterificación (Batch)":
    run_app("Problema 1")
elif sim_option == "Problema 2: Hidrogenación (CSTR/Isotérmico/Adiabático)":
    run_app("Problema 2")
elif sim_option == "Problema 3: Hidrodesalquilación (PFR/EDO)":
    run_app("Problema 3")
