#!/usr/bin/env python3
"""
Auto Check-in Script - Handle Trae SOLO CN and WorkBuddy daily check-in
Usage: python scripts/auto_checkin.py
"""

import subprocess
import time
import os
import sys
from datetime import datetime

# Try to import config file
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import (
        TRAE_EXE, WORKBUDDY_EXE, TRAE_CHECKIN_SCRIPT, WORKBUDDY_CHECKIN_SCRIPT,
        TRAE_TIMEOUT, WORKBUDDY_TIMEOUT, WAIT_BETWEEN_TASKS
    )
except ImportError:
    # Use default values if config file not found
    TRAE_EXE = r"C:\Users\Administrator\AppData\Local\Programs\TRAE SOLO CN\TRAE SOLO CN.exe"
    WORKBUDDY_EXE = r"C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\WorkBuddy.exe"
    TRAE_CHECKIN_SCRIPT = r"D:\agents_project\auto_sign\trae-daily-checkin\src\auto-checkin.mjs"
    WORKBUDDY_CHECKIN_SCRIPT = r"D:\agents_project\auto_sign\workbuddy-checkin\scripts\checkin_py.py"
    TRAE_TIMEOUT = 120
    WORKBUDDY_TIMEOUT = 60
    WAIT_BETWEEN_TASKS = 5

def log(message, level="INFO"):
    """Print log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def run_trae_checkin():
    """Execute Trae SOLO CN check-in"""
    log("Starting Trae SOLO CN check-in...")
    
    try:
        cmd = ["node", TRAE_CHECKIN_SCRIPT, "--force", "--close"]
        log(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TRAE_TIMEOUT
        )
        
        log(f"Trae script exit code: {result.returncode}")
        
        if result.stdout:
            log(f"Trae output:\n{result.stdout}")
        
        if result.stderr:
            log(f"Trae error output:\n{result.stderr}", "WARN")
        
        if result.returncode == 0:
            log("Trae check-in successful!", "SUCCESS")
            return True
        elif result.returncode == 2:
            log("Trae already signed today", "INFO")
            return True
        else:
            log(f"Trae check-in failed, exit code: {result.returncode}", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        log("Trae check-in script timeout", "ERROR")
        return False
    except Exception as e:
        log(f"Trae check-in exception: {str(e)}", "ERROR")
        return False

def run_workbuddy_checkin():
    """Execute WorkBuddy check-in"""
    log("Starting WorkBuddy check-in...")
    
    try:
        cmd = ["python", WORKBUDDY_CHECKIN_SCRIPT]
        log(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=WORKBUDDY_TIMEOUT
        )
        
        log(f"WorkBuddy script exit code: {result.returncode}")
        
        if result.stdout:
            log(f"WorkBuddy output:\n{result.stdout}")
        
        if result.stderr:
            log(f"WorkBuddy error output:\n{result.stderr}", "WARN")
        
        if result.returncode == 0:
            log("WorkBuddy check-in successful!", "SUCCESS")
            return True
        else:
            log(f"WorkBuddy check-in failed, exit code: {result.returncode}", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        log("WorkBuddy check-in script timeout", "ERROR")
        return False
    except Exception as e:
        log(f"WorkBuddy check-in exception: {str(e)}", "ERROR")
        return False

def check_application_exists(exe_path, app_name):
    """Check if application exists"""
    if not os.path.exists(exe_path):
        log(f"{app_name} not found: {exe_path}", "ERROR")
        return False
    log(f"{app_name} path verified: {exe_path}")
    return True

def main():
    """Main function"""
    log("=" * 60)
    log("Auto Check-in Script Started")
    log("=" * 60)
    
    # Check if applications exist
    trae_exists = check_application_exists(TRAE_EXE, "Trae SOLO CN")
    workbuddy_exists = check_application_exists(WORKBUDDY_EXE, "WorkBuddy")
    
    if not trae_exists and not workbuddy_exists:
        log("Both applications not found, cannot proceed", "ERROR")
        sys.exit(1)
    
    # Record results
    results = {
        "trae": False,
        "workbuddy": False
    }
    
    # Execute Trae check-in
    if trae_exists:
        results["trae"] = run_trae_checkin()
        # Wait before next task
        time.sleep(WAIT_BETWEEN_TASKS)
    
    # Execute WorkBuddy check-in
    if workbuddy_exists:
        results["workbuddy"] = run_workbuddy_checkin()
    
    # Output summary
    log("=" * 60)
    log("Check-in Results Summary:")
    log(f"  Trae SOLO CN: {'Success' if results['trae'] else 'Failed' if trae_exists else 'Not found'}")
    log(f"  WorkBuddy: {'Success' if results['workbuddy'] else 'Failed' if workbuddy_exists else 'Not found'}")
    
    # Determine overall result
    success_count = sum(results.values())
    total_apps = sum([trae_exists, workbuddy_exists])
    
    if success_count == total_apps:
        log("All check-in tasks completed!", "SUCCESS")
        sys.exit(0)
    elif success_count > 0:
        log(f"Partial check-in tasks completed ({success_count}/{total_apps})", "WARN")
        sys.exit(0)
    else:
        log("All check-in tasks failed", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
