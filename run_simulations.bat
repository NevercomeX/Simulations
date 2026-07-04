@echo off
chcp 65001 > nul
echo =====================================================================
echo    Simulador de Reactores Químicos - Instalador y Ejecutor
echo =====================================================================
echo.

:: Detectar Python o el launcher 'py'
set PYTHON_CMD=python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo [ERROR] Python no está instalado o no se encuentra en el PATH del sistema.
        echo Por favor, instale Python desde python.org y asegúrese de marcar
        echo la casilla "Add Python to PATH" durante la instalación.
        echo.
        pause
        exit /b
    )
)

echo Python detectado correctamente (%PYTHON_CMD%).
echo.
echo Instalando dependencias necesarias (esto puede tomar un momento la primera vez)...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Hubo un problema al instalar las dependencias con requirements.txt.
    echo Intentando instalación manual de paquetes principales...
    %PYTHON_CMD% -m pip install streamlit numpy pandas matplotlib scipy thermo
)

echo.
echo Dependencias listas. Iniciando las 3 simulaciones en paralelo...
echo.
echo - Iniciando Problema 1 en el puerto 8501...
start "Simulación Problema 1" cmd /k %PYTHON_CMD% -m streamlit run "Problema 1\app.py" --server.port 8501

echo - Iniciando Problema 2 en el puerto 8502...
start "Simulación Problema 2" cmd /k %PYTHON_CMD% -m streamlit run "Problema 2\app.py" --server.port 8502

echo - Iniciando Problema 3 en el puerto 8503...
start "Simulación Problema 3" cmd /k %PYTHON_CMD% -m streamlit run "Problema 3\app.py" --server.port 8503

echo.
echo Las simulaciones se han iniciado en pestañas independientes de su navegador.
echo Si no se abren automáticamente, visite:
echo   - Problema 1: http://localhost:8501
echo   - Problema 2: http://localhost:8502
echo   - Problema 3: http://localhost:8503
echo.
echo Presione cualquier tecla para finalizar este instalador.
pause
