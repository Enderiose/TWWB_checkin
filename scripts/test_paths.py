#!/usr/bin/env python3
"""
Test Script - Validate application and script paths
"""

import os

# Application path configuration
TRAE_EXE = r"C:\Users\Administrator\AppData\Local\Programs\TRAE SOLO CN\TRAE SOLO CN.exe"
WORKBUDDY_EXE = r"C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\WorkBuddy.exe"

# Trae check-in script path
TRAE_CHECKIN_SCRIPT = r"D:\agents_project\auto_sign\trae-daily-checkin\src\auto-checkin.mjs"

# WorkBuddy check-in script path
WORKBUDDY_CHECKIN_SCRIPT = r"D:\agents_project\auto_sign\workbuddy-checkin\scripts\checkin_py.py"

def test_path(path, name):
    """Test if path exists"""
    if os.path.exists(path):
        print(f"[OK] {name}: {path}")
        return True
    else:
        print(f"[ERROR] {name}: {path} not found")
        return False

def main():
    print("=" * 60)
    print("Path Validation Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Test application paths
    print("Application Paths:")
    results.append(test_path(TRAE_EXE, "Trae SOLO CN"))
    results.append(test_path(WORKBUDDY_EXE, "WorkBuddy"))
    
    print()
    
    # Test script paths
    print("Check-in Script Paths:")
    results.append(test_path(TRAE_CHECKIN_SCRIPT, "Trae Check-in Script"))
    results.append(test_path(WORKBUDDY_CHECKIN_SCRIPT, "WorkBuddy Check-in Script"))
    
    print()
    print("=" * 60)
    
    # Count results
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print("All paths validated successfully!")
    else:
        print(f"Path validation failed: {total_count - success_count} path(s) have issues")
    
    print("=" * 60)
    
    return 0 if success_count == total_count else 1

if __name__ == "__main__":
    exit(main())
