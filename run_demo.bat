@echo off
echo Starting Risk API...
start "Risk API" cmd /k "uvicorn phase3_risk_api:app --reload"

echo Starting Dashboard...
start "Dashboard" cmd /k "streamlit run dashboard.py"

echo Demo environment started.
