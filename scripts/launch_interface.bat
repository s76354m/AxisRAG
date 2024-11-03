@echo off
echo Launching RAG Web Interface at %date% %time%...
streamlit run notebooks/app.py
pause > nul 