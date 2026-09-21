@echo off
chcp 65001 >nul
rem ============================================================
rem Show Project Information
rem ============================================================

echo ============================================================
echo Auto Check-in Tool
echo ============================================================
echo.
echo Project Directory: %~dp0
echo.
echo Files:
echo   config.py                - Configuration file
echo   scripts\auto_checkin.py  - Main check-in script
echo   scripts\test_paths.py    - Path test script
echo   install_startup_task.bat - Install auto check-in task
echo   uninstall_startup_task.bat - Uninstall auto check-in task
echo   test_checkin.bat         - Test check-in functionality
echo   info.bat                 - Show project information
echo.
echo Documentation:
echo   README.md                - Project documentation
echo   QUICKSTART.md            - Quick start guide
echo   USAGE.md                 - Usage instructions
echo   SUMMARY.md               - Project summary
echo.
echo Reference Libraries:
echo   trae-daily-checkin\      - Trae check-in library
echo   workbuddy-checkin\       - WorkBuddy check-in library
echo.
echo ============================================================
echo Quick Start:
echo   1. Run python scripts\test_paths.py to validate paths
echo   2. Double-click install_startup_task.bat to install
echo   3. Run python scripts\auto_checkin.py to test
echo ============================================================
echo.
pause >nul
