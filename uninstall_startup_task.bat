@echo off
chcp 65001 >nul
rem ============================================================
rem Uninstall Auto Check-in Task
rem ============================================================

set "TASK_NAME=AutoCheckinOnStartup"

echo ============================================================
echo Uninstall Auto Check-in Task
echo ============================================================
echo.

rem Check if task exists
schtasks /Query /TN "%TASK_NAME%" >nul 2>nul
if errorlevel 1 (
    echo [INFO] Task "%TASK_NAME%" does not exist.
    pause >nul
    exit /b 0
)

rem Delete task
schtasks /Delete /TN "%TASK_NAME%" /F

if errorlevel 1 (
    echo [ERROR] Failed to delete task.
    pause >nul
    exit /b 1
)

echo [OK] Task deleted successfully: %TASK_NAME%
echo.
echo ============================================================
echo Task uninstalled successfully!
echo ============================================================
echo.
pause >nul
