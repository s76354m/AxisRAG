@echo off
setlocal enabledelayedexpansion

:menu
cls
echo ===================================
echo Axis RAG Analysis Tool
echo ===================================
echo.
echo 1. Run Full Analysis
echo 2. Launch Web Interface
echo 3. Run Analysis + Launch Interface
echo 4. Install/Update Dependencies
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto run_analysis
if "%choice%"=="2" goto launch_interface
if "%choice%"=="3" goto run_both
if "%choice%"=="4" goto install_deps
if "%choice%"=="5" goto end
goto menu

:install_deps
echo.
echo Installing/Updating Dependencies...
pip install streamlit plotly pandas openai anthropic chromadb langchain
if errorlevel 1 (
    echo Error installing dependencies
    pause
    goto menu
)
echo Dependencies installed successfully
timeout /t 2
goto menu

:run_analysis
echo.
echo Starting Analysis at %date% %time%...
python notebooks/AxisRAG.py --pdf_path "notebooks/data/Axis Program Management_Unformatted detailed.pdf"
if errorlevel 1 (
    echo Error during analysis
    pause
    goto menu
)
echo Analysis completed
choice /c YN /m "Would you like to launch the interface now? (Y/N)"
if errorlevel 2 goto menu
if errorlevel 1 goto launch_interface
goto menu

:launch_interface
echo.
echo Launching Web Interface...
start "Axis RAG Interface" streamlit run notebooks/app.py
if errorlevel 1 (
    echo Error launching interface
    pause
    goto menu
)
goto menu

:run_both
echo.
echo Running Analysis and Interface...
start "Axis RAG Analysis" python notebooks/AxisRAG.py --pdf_path "notebooks/data/Axis Program Management_Unformatted detailed.pdf"
timeout /t 5
start "Axis RAG Interface" streamlit run notebooks/app.py
if errorlevel 1 (
    echo Error in execution
    pause
    goto menu
)
goto menu

:end
echo.
echo Thank you for using Axis RAG Analysis Tool
timeout /t 2
exit 