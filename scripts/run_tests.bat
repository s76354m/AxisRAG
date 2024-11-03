@echo off
echo Running Axis RAG Tests...
python notebooks/tests/test_axis_rag.py
if errorlevel 1 (
    echo Tests failed! Check the report for details.
) else (
    echo All tests passed successfully!
)
pause 