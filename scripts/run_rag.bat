@echo off
echo Starting RAG application at %date% %time%...

REM Check if --interface flag is provided
if "%1"=="--interface" (
    echo Launching web interface...
    streamlit run notebooks/app.py
) else (
    echo Running analysis...
    python notebooks/AxisRAG.py --pdf_path "notebooks/data/Axis Program Management_Unformatted detailed.pdf"
)

echo Application finished. Press any key to exit.
pause > nul