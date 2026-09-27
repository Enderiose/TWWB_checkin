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
rem
rem Every run writes a diagnostic log to  logs\install_task.log
rem so that a failed install is never silent again.
rem ============================================================

rem ---- Settings (edit here if needed) ------------------------
set "TASK_NAME=AutoCheckinOnStartup"
rem Delay after logon before the check-in starts, format MINUTES:SECONDS
set "STARTUP_DELAY=0002:00"
rem Default check-in target when nothing is chosen: all | trae | workbuddy
set "DEFAULT_TARGET=all"
rem ------------------------------------------------------------

rem Keep our own path BEFORE any SHIFT (shift also moves %0)
set "SELF=%~f0"

rem ---- Project paths + install log ---------------------------
set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
set "SCRIPT_PATH=%PROJECT_DIR%\scripts\auto_checkin.py"
set "LOG_DIR=%PROJECT_DIR%\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>nul
set "LOG=%LOG_DIR%\install_task.log"

rem ---- Command line arguments --------------------------------
rem   quiet     : never wait for a key press (unattended / elevated use)
rem   elevated  : internal flag set by the re-launch after UAC elevation (ignored)
rem   trae      : install a task that only checks in Trae
rem   workbuddy : install a task that only checks in WorkBuddy
rem   all|both  : install a task that checks in both (default)
rem   1|2|3     : same as the interactive menu choices
set "TARGET="
set "QUIET="
:parse_args
if "%~1"=="" goto args_done
if /i "%~1"=="quiet" set "QUIET=1"
if /i "%~1"=="trae" set "TARGET=trae"
if /i "%~1"=="workbuddy" set "TARGET=workbuddy"
if /i "%~1"=="all" set "TARGET=all"
if /i "%~1"=="both" set "TARGET=all"
if "%~1"=="1" set "TARGET=trae"
if "%~1"=="2" set "TARGET=workbuddy"
if "%~1"=="3" set "TARGET=all"
shift
goto parse_args
:args_done
call :log "==== start : args=[%*]"

rem ---- Target selection (interactive when not given) --------
if defined TARGET goto target_done
if defined QUIET (
    set "TARGET=%DEFAULT_TARGET%"
    goto target_done
)
echo ============================================================
echo Select what the scheduled task should check in
echo ============================================================
echo   [1] Trae only
echo   [2] WorkBuddy only
echo   [3] Both (default)
echo.
choice /c 123 /n /t 15 /d 3 /m "Choice [1/2/3] (default 3 after 15s): "
if errorlevel 3 (
    set "TARGET=all"
) else if errorlevel 2 (
    set "TARGET=workbuddy"
) else (
    set "TARGET=trae"
)
echo.
:target_done
call :log "target=%TARGET% quiet=%QUIET%"

rem ---- Elevation ---------------------------------------------
rem Only pass "quiet" on to the elevated window when the caller asked for it,
rem so that a double-click keeps the elevated window (and its errors) visible.
set "ELEV_ARGS=elevated"
if defined QUIET set "ELEV_ARGS=elevated quiet"

net session >nul 2>nul
if %errorlevel% neq 0 (
    call :log "not elevated : requesting UAC"
    echo [INFO] Requesting administrator privileges...
    echo [INFO] Please click [Yes] on the UAC window.
    powershell -NoProfile -Command "try { Start-Process -FilePath '%SELF%' -Verb RunAs -ArgumentList '%ELEV_ARGS% %TARGET%' -ErrorAction Stop; exit 0 } catch { Write-Host '[ERROR] Could not elevate:' $_.Exception.Message; exit 1 }"
    if errorlevel 1 (
        call :log "UAC request FAILED - cancelled or blocked"
        echo.
        echo ============================================================
        echo [ERROR] Elevation failed or was cancelled.
        echo [ERROR] The scheduled task was NOT installed - nothing changed.
        echo [ERROR] Diagnostics: %LOG%
        echo ============================================================
        call :wait
        exit /b 1
    )
    call :log "UAC accepted : elevated window launched, original window exits"
    exit /b 0
)
call :log "running elevated"

rem ---- Paths / runtimes --------------------------------------
set "PYTHON_EXE=python"

where python >nul 2>nul
if errorlevel 1 (
    call :log "ERROR python not found on PATH"
    echo [ERROR] Python not found. Please install Python and add to PATH.
    call :wait
    exit /b 1
)
for /f "delims=" %%p in ('where python') do call :log "python = %%p"

rem Check if Node.js is available (needed for the Trae check-in only)
if /i "%TARGET%"=="workbuddy" goto node_check_done
where node >nul 2>nul
if errorlevel 1 (
    call :log "ERROR node not found on PATH"
    echo [ERROR] Node.js not found. Please install Node.js and add to PATH.
    rem NOTE: keep round brackets out of any echo/rem line inside an if block -
    rem cmd miscounts them and lines after the block then run unconditionally.
    echo [ERROR] Only needed for the Trae check-in - pick WorkBuddy only to skip it.
    call :wait
    exit /b 1
)
for /f "delims=" %%p in ('where node') do call :log "node = %%p"
:node_check_done

if not exist "%SCRIPT_PATH%" (
    call :log "ERROR check-in script missing: %SCRIPT_PATH%"
    echo [ERROR] Check-in script not found: %SCRIPT_PATH%
    call :wait
    exit /b 1
)

echo ============================================================
echo Install Auto Check-in Task
echo ============================================================
echo.
echo Task Name : %TASK_NAME%
echo Trigger   : At user logon + %STARTUP_DELAY% delay
echo Target    : %TARGET%
echo Command   : python "%SCRIPT_PATH%" --startup --target %TARGET%
echo Log files : %PROJECT_DIR%\logs\auto_checkin_YYYY-MM-DD.log
echo Install log: %LOG%
echo.

rem NOTE: no explicit /Delete here - schtasks /Create /F overwrites the task,
rem so a failed create can never leave the machine without a working task.
echo Creating task (logon trigger, %STARTUP_DELAY% delay, target %TARGET%)...
call :log "create: schtasks /Create /TN %TASK_NAME% /SC ONLOGON /DELAY %STARTUP_DELAY% /RL HIGHEST /F /TR [%PYTHON_EXE%] [%SCRIPT_PATH%] --startup --target %TARGET%"
schtasks /Create /TN "%TASK_NAME%" ^
    /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --startup --target %TARGET%" ^
    /SC ONLOGON /DELAY %STARTUP_DELAY% /RL HIGHEST /F >>"%LOG%" 2>&1
call :log "create (with delay) errorlevel=%errorlevel%"
if errorlevel 1 goto create_retry
goto create_done

:create_retry
echo.
echo [WARN] Could not create the task with the %STARTUP_DELAY% delay.
echo [WARN] Retrying without the delay (the script still waits for the desktop)...
call :log "retry create without delay"
schtasks /Create /TN "%TASK_NAME%" ^
    /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --startup --target %TARGET%" ^
    /SC ONLOGON /RL HIGHEST /F >>"%LOG%" 2>&1
call :log "create (no delay) errorlevel=%errorlevel%"
if errorlevel 1 (
    echo.
    echo ============================================================
    echo [ERROR] Task creation failed.
    echo [ERROR] Full output: %LOG%
    echo ============================================================
    call :wait
    exit /b 1
)
:create_done

echo.
echo [OK] Task created. Current definition:
echo ------------------------------------------------------------
schtasks /Query /TN "%TASK_NAME%" /V /FO LIST
echo ------------------------------------------------------------
call :log "query errorlevel=%errorlevel%"

echo.
echo ============================================================
echo Task installed successfully!
echo ============================================================
echo.
echo Notes:
echo   - Selected target: %TARGET%
echo   - Check-in starts about %STARTUP_DELAY:~-5% after logon, not during logon.
echo   - It only fires AT LOGON: reboot or sign out/in to arm it.
echo   - The script also waits for the Windows desktop shell to be ready.
echo   - Failed runs, crashes and every sub-process exit code are written to:
echo       %PROJECT_DIR%\logs\auto_checkin_YYYY-MM-DD.log
echo   - Install diagnostics are written to:
echo       %LOG%
echo   - Change STARTUP_DELAY at the top of this file to adjust the delay.
echo.
echo Useful commands:
echo   View task  : schtasks /Query /TN "%TASK_NAME%" /V
echo   Run now    : schtasks /Run /TN "%TASK_NAME%"
echo   Remove task: uninstall_startup_task.bat
echo   Change the target: install_startup_task.bat [trae|workbuddy|all]
echo.
call :wait
exit /b 0

rem ============================================================
:log
rem Append one timestamped line to the install log.
rem The message is re-quoted on purpose: the caller's quotes are stripped by the
rem first argument, so a redirection character in the message would otherwise
rem overwrite a file instead of being logged.
rem Keep log messages free of double quotes as well.
>>"%LOG%" echo [%date% %time%] "%~1"
goto :eof

:wait
rem Wait for a key press unless running in quiet mode
if not defined QUIET pause >nul
goto :eof
