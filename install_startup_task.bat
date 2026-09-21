@echo off
chcp 65001 >nul
rem ============================================================
rem Install Auto Check-in Task on Windows Startup
rem ============================================================

rem Check for admin privileges
net session >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Requesting administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs -ArgumentList 'elevated'"
    exit /b
)

rem If launched with elevation, continue below

set "TASK_NAME=AutoCheckinOnStartup"
set "PROJECT_DIR=%~dp0"
set "PYTHON_EXE=python"

rem Check if Python is available
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python and add to PATH.
    pause >nul
    exit /b 1
)

rem Check if Node.js is available (needed for Trae check-in)
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js and add to PATH.
    pause >nul
    exit /b 1
)

echo ============================================================
echo Install Auto Check-in Task
echo ============================================================
echo.
echo Task Name: %TASK_NAME%
echo Trigger: On user logon
echo Command: python "%PROJECT_DIR%scripts\auto_checkin.py"
echo.

rem Delete existing task if exists
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>nul

rem Create task: execute on user logon
schtasks /Create /TN "%TASK_NAME%" /TR "\"%PYTHON_EXE%\" \"%PROJECT_DIR%scripts\auto_checkin.py\"" /SC ONLOGON /RL HIGHEST /F

if errorlevel 1 (
    echo [ERROR] Task creation failed.
    pause >nul
    exit /b 1
)

echo [OK] Auto check-in task created successfully:
echo   Task Name: %TASK_NAME%
echo   Trigger: On user logon
echo   Command: python scripts\auto_checkin.py
echo.
echo ============================================================
echo Task installed successfully!
echo ============================================================
echo.
echo Notes:
echo   - System will auto check-in after user logon
echo   - First run may need admin privileges
echo   - Check task status in Task Scheduler
echo.
echo Useful commands:
echo   View task: schtasks /Query /TN "%TASK_NAME%" /V
echo   Remove task: uninstall_startup_task.bat
echo.
pause >nul
