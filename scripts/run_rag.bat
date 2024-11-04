@echo off
echo Starting RAG application at %date% %time%...

REM Set the root directory
set ROOT_DIR=%~dp0..

REM Check if --interface flag is provided
if "%1"=="--interface" (
    echo Launching web interface...
    streamlit run "%ROOT_DIR%\notebooks\app.py"
) else (
    echo Running analysis...
    python "%ROOT_DIR%\src\AxisRAG.py" --pdf_path "%ROOT_DIR%\data\raw\Axis Program Management_Unformatted detailed.pdf"
)

echo Application finished. Press any key to exit.
pause > nul