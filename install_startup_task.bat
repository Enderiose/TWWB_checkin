@echo off
chcp 65001 >nul
setlocal
rem ============================================================
rem Install Auto Check-in Task on Windows Startup
rem ============================================================
rem The task runs AFTER USER LOGON, delayed by STARTUP_DELAY minutes.
rem Reason: running the check-in during the first seconds of a logon makes the
rem GUI automation (Trae launch / WorkBuddy clicks) fail, because the desktop
rem shell and the background services are not ready yet.
rem ============================================================

rem ---- Settings (edit here if needed) ------------------------
set "TASK_NAME=AutoCheckinOnStartup"
rem Delay after logon before the check-in starts, format MINUTES:SECONDS
set "STARTUP_DELAY=0002:00"
rem ------------------------------------------------------------

rem "quiet" (1st or 2nd argument) = never wait for a key press, for unattended use
set "QUIET="
if /i "%~1"=="quiet" set "QUIET=1"
if /i "%~2"=="quiet" set "QUIET=1"

rem Check for admin privileges
net session >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Requesting administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs -ArgumentList 'elevated quiet'"
    exit /b
)

rem ---- Paths -------------------------------------------------
set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
set "SCRIPT_PATH=%PROJECT_DIR%\scripts\auto_checkin.py"
set "PYTHON_EXE=python"

rem Check if Python is available
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python and add to PATH.
    call :wait
    exit /b 1
)

rem Check if Node.js is available (needed for Trae check-in)
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js and add to PATH.
    call :wait
    exit /b 1
)

echo ============================================================
echo Install Auto Check-in Task
echo ============================================================
echo.
echo Task Name : %TASK_NAME%
echo Trigger   : At user logon + %STARTUP_DELAY% delay
echo Command   : python "%SCRIPT_PATH%" --startup
echo Log files : %PROJECT_DIR%\logs\auto_checkin_YYYY-MM-DD.log
echo.

rem Delete existing task if exists
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>nul

echo Creating task (logon trigger, %STARTUP_DELAY% delay)...
schtasks /Create /TN "%TASK_NAME%" ^
    /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --startup" ^
    /SC ONLOGON /DELAY %STARTUP_DELAY% /RL HIGHEST /F

if errorlevel 1 (
    echo.
    echo [WARN] Could not create the task with the %STARTUP_DELAY% delay.
    echo [WARN] Retrying without the delay (the script still waits for the desktop)...
    schtasks /Create /TN "%TASK_NAME%" ^
        /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --startup" ^
        /SC ONLOGON /RL HIGHEST /F
    if errorlevel 1 (
        echo [ERROR] Task creation failed.
        call :wait
        exit /b 1
    )
)

echo.
echo [OK] Task created. Current definition:
echo ------------------------------------------------------------
schtasks /Query /TN "%TASK_NAME%" /V /FO LIST
echo ------------------------------------------------------------
echo.
echo ============================================================
echo Task installed successfully!
echo ============================================================
echo.
echo Notes:
echo   - Check-in starts about %STARTUP_DELAY:~-5% after logon, not during logon.
echo   - The script also waits for the Windows desktop shell to be ready.
echo   - Failed runs, crashes and every sub-process exit code are written to:
echo       %PROJECT_DIR%\logs\auto_checkin_YYYY-MM-DD.log
echo   - Change STARTUP_DELAY at the top of this file to adjust the delay.
echo.
echo Useful commands:
echo   View task  : schtasks /Query /TN "%TASK_NAME%" /V
echo   Run now    : schtasks /Run /TN "%TASK_NAME%"
echo   Remove task: uninstall_startup_task.bat
echo.
call :wait
exit /b 0

:wait
rem Wait for a key press unless running in quiet mode
if not defined QUIET pause >nul
goto :eof