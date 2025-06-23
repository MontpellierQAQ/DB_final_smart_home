@echo off
setlocal

:: =================================================================
:: Smart Home System - Start Script (Global Python)
:: =================================================================
:: This script uses the system's global Python environment.
:: Make sure all dependencies from requirements.txt are installed globally.
:: (e.g., pip install -r requirements.txt)
:: =================================================================

echo [INFO] Using system's global Python to launch services...
echo.

:: Start FastAPI backend service in a new window
echo [LAUNCH] Starting Backend Service...
start "Backend_Service" cmd /k "python run_server.py"

:: Wait for a few seconds to ensure the server has time to start
echo [INFO] Waiting for 3 seconds for the server to initialize...
timeout /t 3 /nobreak > nul

:: Start Python CLI client in another new window
echo [LAUNCH] Starting Client CLI...
start "Client_CLI" cmd /k "python client_cli.py"

echo.
echo [SUCCESS] Both services launched. This window will close in 3 seconds...
timeout /t 3 /nobreak > nul

endlocal 