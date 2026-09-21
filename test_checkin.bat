@echo off
chcp 65001 >nul
rem ============================================================
rem Test Check-in Functionality
rem ============================================================

echo ============================================================
echo Test Check-in Functionality
echo ============================================================
echo.

rem Check if Python is available
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python and add to PATH.
    pause >nul
    exit /b 1
)

rem Check if Node.js is available
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js and add to PATH.
    pause >nul
    exit /b 1
)

echo [1/3] Test path validation...
python scripts\test_paths.py
if errorlevel 1 (
    echo [ERROR] Path validation failed. Please check configuration.
    pause >nul
    exit /b 1
)

echo.
echo [2/3] Test Trae check-in (test only, no actual check-in)...
echo Note: This will try to connect to Trae and perform check-in
echo.
pause

rem Run Trae check-in test
node trae-daily-checkin\src\auto-checkin.mjs --force
if errorlevel 1 (
    echo [WARN] Trae check-in test failed or already signed today
) else (
    echo [OK] Trae check-in test completed
)

echo.
echo [3/3] Test WorkBuddy check-in (test only, no actual check-in)...
echo Note: This will try to operate WorkBuddy window
echo.
pause

rem Run WorkBuddy check-in test
python workbuddy-checkin\scripts\checkin_py.py
if errorlevel 1 (
    echo [WARN] WorkBuddy check-in test failed
) else (
    echo [OK] WorkBuddy check-in test completed
)

echo.
echo ============================================================
echo Test completed!
echo ============================================================
echo.
pause >nul
