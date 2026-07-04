# 🧪 Simulador Interactivo de Reactores Químicos

Este repositorio contiene tres simuladores termodinámicos y cinéticos interactivos desarrollados en **Python** y **Streamlit**. Están diseñados para modelar diferentes tipos de reactores y reacciones químicas, comparando modelos ideales frente a reales (Peng-Robinson) y visualizando perfiles cinéticos y balances de energía en tiempo real.

---

## 📂 Estructura del Proyecto

El repositorio está organizado de la siguiente manera:

*   **`Problema 1/`** - **Esterificación de Acetato de Etilo**
    *   Simula la reacción reversible en fase líquida $\text{AcOH} + \text{EtOH} \rightleftharpoons \text{EtOAc} + \text{H}_2\text{O}$.
    *   Cálculo interactivo de constantes de equilibrio, balances de materia y perfiles de conversión en reactores discontinuos (Batch).
*   **`Problema 2/`** - **Hidrogenación de Nitrobenceno**
    *   Simula la hidrogenación altamente exotérmica de Nitrobenceno a Anilina: $\text{C}_6\text{H}_5\text{NO}_2 + 3\text{H}_2 \rightarrow \text{C}_6\text{H}_5\text{NH}_2 + 2\text{H}_2\text{O}$.
    *   Modela el comportamiento isotérmico y adiabático comparando **Gas Ideal** frente a **Gas Real** (utilizando la ecuación de estado de **Peng-Robinson**).
*   **`Problema 3/`** - **Hidrodesalquilación de Tolueno (Reactor Tubular PFR)**
    *   Simula la reacción reversible en fase gaseosa $\text{Tolueno} + \text{H}_2 \rightleftharpoons \text{Benceno} + \text{Metano}$ en un reactor tubular PFR.
    *   Resuelve el sistema acoplado de ecuaciones diferenciales ordinarias (EDO) para obtener los perfiles de flujo molar de cada especie, conversión y temperatura a lo largo del volumen del reactor.

---

## 🚀 Cómo Ejecutar el Proyecto

### Opción Rápida (Windows, Linux y macOS)
Si deseas arrancar todo de forma automática sin configurar entornos de forma manual:

*   **En Windows:**
    1.  Asegúrate de tener instalado **Python 3.8+** en tu sistema y haber marcado la casilla **"Add Python to PATH"** durante la instalación.
    2.  Haz doble clic en el archivo **`run_simulations.bat`** en la carpeta raíz.
*   **En Linux / macOS:**
    1.  Abre una terminal en la carpeta raíz del proyecto.
    2.  Otorga permisos de ejecución al script:
        ```bash
        chmod +x run_simulations.sh
        ```
    3.  Ejecuta el script:
        ```bash
        ./run_simulations.sh
        ```

Cualquiera de los dos scripts instalará automáticamente todas las dependencias necesarias (`requirements.txt`) y levantará las 3 simulaciones de forma simultánea en tu navegador en los siguientes puertos:
    *   **Problema 1:** [http://localhost:8501](http://localhost:8501)
    *   **Problema 2:** [http://localhost:8502](http://localhost:8502)
    *   **Problema 3:** [http://localhost:8503](http://localhost:8503)

---

### Opción Manual (Cualquier Sistema Operativo)
Si prefieres iniciar las simulaciones de forma manual desde la terminal:

1.  **Clonar el repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd Simulations
    ```
2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Ejecutar la simulación deseada:**
    *   Para el **Problema 1**:
        ```bash
        streamlit run "Problema 1/app.py"
        ```
    *   Para el **Problema 2**:
        ```bash
        streamlit run "Problema 2/app.py"
        ```
    *   Para el **Problema 3**:
        ```bash
        streamlit run "Problema 3/app.py"
        ```

---

## 🛠️ Tecnologías Utilizadas

*   **Python 3.8+**
*   **Streamlit** - Interfaz de usuario interactiva y dashboard.
*   **Thermo** & **Chemicals** - Propiedades termodinámicas avanzadas y estimación de fases por Peng-Robinson.
*   **SciPy** - Resolución de balances y sistemas de ecuaciones diferenciales ordinarias (integradores numéricos).
*   **NumPy** & **Pandas** - Procesamiento de datos y operaciones vectorizadas.
*   **Matplotlib** - Generación y visualización de gráficos termodinámicos y cinéticos.
