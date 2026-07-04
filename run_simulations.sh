#!/bin/bash

echo "====================================================================="
echo "   Simulador de Reactores Químicos - Instalador y Ejecutor (Linux/macOS)"
echo "====================================================================="
echo

# 1. Detectar Python
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python no está instalado o no se encuentra en el PATH del sistema."
    echo "Por favor, instale Python 3 antes de ejecutar este script."
    echo
    exit 1
fi

echo "Python detectado correctamente ($PYTHON_CMD)."
echo

# 2. Instalar dependencias
echo "Instalando dependencias necesarias (esto puede tomar un momento la primera vez)..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo
    echo "[WARNING] Hubo un problema al instalar las dependencias con requirements.txt."
    echo "Intentando instalación manual de paquetes principales..."
    $PYTHON_CMD -m pip install streamlit numpy pandas matplotlib scipy thermo
fi

echo
echo "Dependencias listas. Iniciando las 3 simulaciones en paralelo..."
echo

# 3. Lanzar las simulaciones en segundo plano (&)
echo "- Iniciando Problema 1 en el puerto 8501..."
$PYTHON_CMD -m streamlit run "Problema 1/app.py" --server.port 8501 &

echo "- Iniciando Problema 2 en el puerto 8502... "
$PYTHON_CMD -m streamlit run "Problema 2/app.py" --server.port 8502 &

echo "- Iniciando Problema 3 en el puerto 8503..."
$PYTHON_CMD -m streamlit run "Problema 3/app.py" --server.port 8503 &

echo
echo "Las simulaciones se han iniciado en segundo plano."
echo "Si no se abren automáticamente en su navegador, visite:"
echo "  - Problema 1: http://localhost:8501"
echo "  - Problema 2: http://localhost:8502"
echo "  - Problema 3: http://localhost:8503"
echo
echo "Presione Ctrl+C para detener todos los servidores de Streamlit."

# Limpiar procesos en segundo plano al salir
trap "kill 0" EXIT
wait
