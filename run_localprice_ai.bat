@echo off

echo ==========================================
echo        LOCALPRICE AI
echo ==========================================

echo.
echo Installing requirements...
python -m pip install -r requirements.txt

echo.
echo Starting LocalPrice AI...
python -m streamlit run app.py

pause
