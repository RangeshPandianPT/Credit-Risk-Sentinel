@echo off
echo Starting Risk API...
REM Set environment variable for simulation and start uvicorn from root, pointing to src module
start "Risk API" cmd /k "call .venv\Scripts\activate.bat && set SNS_TOPIC_ARN=arn:aws:sns:local:simulation && uvicorn src.phase3_risk_api:app --reload"

echo Starting Dashboard...
start "Dashboard" cmd /k "call .venv\Scripts\activate.bat && streamlit run src/dashboard.py"

echo Demo environment started.
