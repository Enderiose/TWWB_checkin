@echo off
chcp 65001 >nul
setlocal
rem ============================================================
rem Uninstall Auto Check-in Task
rem ============================================================
rem This removes everything that the install script / check-in
rem relies on:
rem   1) the Windows scheduled task (AutoCheckinOnStartup)
rem   2) the WorkBuddy "start at logon" entry
rem
rem Why (2): WorkBuddy registers its own autostart in the
rem HKCU ...\CurrentVersion\Run key. While the scheduled task
rem existed it launched WorkBuddy, checked in and closed it
rem again. After uninstalling the task, WorkBuddy would still
rem start at logon and nothing would close it - so the
rem autostart entry is removed here as well.
rem ============================================================

rem ---- Settings ----------------------------------------------
set "TASK_NAME=AutoCheckinOnStartup"
set "WORKBUDDY_RUN_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
set "WORKBUDDY_RUN_VALUE=WorkBuddy.WorkBuddy"
rem ------------------------------------------------------------

echo ============================================================
echo Uninstall Auto Check-in Task
echo ============================================================
echo.

set "EXITCODE=0"

rem ---- 1. Delete the scheduled task --------------------------
echo [1/2] Removing scheduled task "%TASK_NAME%"...
schtasks /Query /TN "%TASK_NAME%" >nul 2>nul
if errorlevel 1 (
    echo       [INFO] Task "%TASK_NAME%" does not exist, nothing to delete.
) else (
    schtasks /Delete /TN "%TASK_NAME%" /F
    if errorlevel 1 (
        echo       [ERROR] Failed to delete task "%TASK_NAME%".
        set "EXITCODE=1"
    ) else (
        echo       [OK] Task deleted successfully: %TASK_NAME%
    )
)
echo.

rem ---- 2. Remove WorkBuddy autostart -------------------------
echo [2/2] Removing WorkBuddy autostart entry...
reg query "%WORKBUDDY_RUN_KEY%" /v "%WORKBUDDY_RUN_VALUE%" >nul 2>nul
if errorlevel 1 (
    echo       [INFO] WorkBuddy autostart entry not found, nothing to delete.
) else (
    reg delete "%WORKBUDDY_RUN_KEY%" /v "%WORKBUDDY_RUN_VALUE%" /f >nul
    if errorlevel 1 (
        echo       [ERROR] Failed to remove WorkBuddy autostart entry.
        set "EXITCODE=1"
    ) else (
        echo       [OK] WorkBuddy autostart entry removed.
    )
)
echo.

echo ============================================================
if "%EXITCODE%"=="0" (
    echo Task uninstalled successfully!
) else (
    echo Uninstall finished with errors, see the messages above.
)
echo ============================================================
echo.
echo Notes:
echo   - WorkBuddy may write the autostart entry back the next time
echo     it starts. To make this permanent, turn off the "start at
echo     logon" option inside WorkBuddy's own settings.
echo   - To restore the autostart entry manually, run:
echo       reg add "%WORKBUDDY_RUN_KEY%" /v "%WORKBUDDY_RUN_VALUE%" /t REG_SZ /d "%%LOCALAPPDATA%%\Programs\WorkBuddy\WorkBuddy.exe" /f
echo.
pause >nul
exit /b %EXITCODE%
