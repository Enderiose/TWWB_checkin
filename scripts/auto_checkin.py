#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Check-in Script - Handle Trae SOLO CN and WorkBuddy daily check-in

Usage:
    python scripts/auto_checkin.py              # manual / test run
    python scripts/auto_checkin.py --startup    # run by the Windows scheduled task

Logs (always written, even if the script crashes):
    logs/auto_checkin_YYYY-MM-DD.log

Exit codes:
    0 = success  (all tasks done, or at least one task done)
    1 = all check-in tasks failed / required applications not found
    3 = unexpected crash (full traceback written to the log file)
"""

import argparse
import atexit
import ctypes
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from ctypes import wintypes
from datetime import datetime

# ============================================================
# Paths / configuration
# ============================================================

SCRIPT_PATH = os.path.abspath(__file__)
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_PATH))

CONFIG_SOURCE = "config.py"
CONFIG_ERROR = None

try:
    if PROJECT_DIR not in sys.path:
        sys.path.insert(0, PROJECT_DIR)
    from config import (  # noqa: E402
        TRAE_EXE, WORKBUDDY_EXE,
        TRAE_CHECKIN_SCRIPT, WORKBUDDY_CHECKIN_SCRIPT,
        TRAE_TIMEOUT, WORKBUDDY_TIMEOUT, WAIT_BETWEEN_TASKS,
        LOG_DIR, LOG_KEEP_DAYS, LOG_CONSOLE,
        WAIT_FOR_DESKTOP, DESKTOP_READY_TIMEOUT,
        DESKTOP_POLL_INTERVAL, DESKTOP_SETTLE_SECONDS,
        WORKBUDDY_COORD_BASELINE,
        WORKBUDDY_MENU_X, WORKBUDDY_MENU_Y,
        WORKBUDDY_CHECKIN_X, WORKBUDDY_CHECKIN_Y,
        WORKBUDDY_SKIP_MENU,
        WORKBUDDY_VERIFY, WORKBUDDY_READY_TIMEOUT,
        WORKBUDDY_MAX_TRIES, WORKBUDDY_CLOSE_DELAY,
    )
    try:
        from config import PYTHON_EXE, NODE_EXE
    except ImportError:
        PYTHON_EXE = sys.executable or "python"
        NODE_EXE = "node"
except Exception as _exc:                                      # noqa: BLE001
    CONFIG_SOURCE = "built-in defaults"
    CONFIG_ERROR = "%s: %s" % (type(_exc).__name__, _exc)
    TRAE_EXE = r"C:\Users\Administrator\AppData\Local\Programs\TRAE SOLO CN\TRAE SOLO CN.exe"
    WORKBUDDY_EXE = r"C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\WorkBuddy.exe"
    TRAE_CHECKIN_SCRIPT = os.path.join(PROJECT_DIR, "trae-daily-checkin", "src", "auto-checkin.mjs")
    WORKBUDDY_CHECKIN_SCRIPT = os.path.join(PROJECT_DIR, "workbuddy-checkin", "scripts", "checkin_py.py")
    PYTHON_EXE = sys.executable or "python"
    NODE_EXE = "node"
    TRAE_TIMEOUT = 120
    WORKBUDDY_TIMEOUT = 60
    WAIT_BETWEEN_TASKS = 5
    LOG_DIR = os.path.join(PROJECT_DIR, "logs")
    LOG_KEEP_DAYS = 30
    LOG_CONSOLE = True
    WAIT_FOR_DESKTOP = True
    DESKTOP_READY_TIMEOUT = 300
    DESKTOP_POLL_INTERVAL = 3
    DESKTOP_SETTLE_SECONDS = 5
    WORKBUDDY_COORD_BASELINE = (1920, 1080)
    WORKBUDDY_MENU_X = 207
    WORKBUDDY_MENU_Y = 983
    WORKBUDDY_CHECKIN_X = 112
    WORKBUDDY_CHECKIN_Y = 487
    WORKBUDDY_SKIP_MENU = False
    WORKBUDDY_VERIFY = True
    WORKBUDDY_READY_TIMEOUT = 20
    WORKBUDDY_MAX_TRIES = 3
    WORKBUDDY_CLOSE_DELAY = 3

# ============================================================
# Logging (file + console), crash-safe
# ============================================================

_log_path = None
_log_stream = None
CONSOLE = bool(LOG_CONSOLE)
LOG_FILE_PREFIX = "auto_checkin_"


def _open_log_file():
    """Open (or create) today's log file. Falls back to %TEMP% if needed."""
    global _log_path, _log_stream
    today = datetime.now().strftime("%Y-%m-%d")
    candidates = [LOG_DIR, os.path.join(tempfile.gettempdir(), "TWWB_checkin_logs")]
    for directory in candidates:
        try:
            os.makedirs(directory, exist_ok=True)
            path = os.path.join(directory, "%s%s.log" % (LOG_FILE_PREFIX, today))
            _log_stream = open(path, "a", encoding="utf-8", errors="replace")
            _log_path = path
            return
        except Exception:                                      # noqa: BLE001
            continue
    _log_stream = None
    _log_path = None


def _emit(line):
    """Write one line to console + log file. Never raises."""
    if CONSOLE:
        try:
            print(line, flush=True)
        except Exception:                                      # noqa: BLE001
            pass
    if _log_stream is not None:
        try:
            _log_stream.write(line + "\n")
            _log_stream.flush()
        except Exception:                                      # noqa: BLE001
            pass


def log(message, level="INFO"):
    """Log a single line with timestamp."""
    _emit("[%s] [%s] %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), level, message))


def log_block(text, indent="      | "):
    """Log multi-line text (sub-process output, tracebacks) line by line."""
    for line in str(text).replace("\r\n", "\n").replace("\r", "\n").rstrip("\n").split("\n"):
        _emit(indent + line)


def log_separator(char="=", level="INFO"):
    log(char * 70, level)


def _log_crash(exc_type, exc_value, exc_tb, origin="unhandled exception"):
    """Write a complete crash report (this is what was missing before)."""
    log_separator("!", "CRASH")
    log("SCRIPT ABORTED - %s" % origin, "CRASH")
    log("Reason  : %s: %s" % (getattr(exc_type, "__name__", exc_type), exc_value), "CRASH")
    log("Time    : %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "CRASH")
    log("Python  : %s (%s)" % (sys.version.split()[0], sys.executable), "CRASH")
    log("Command : %s" % " ".join(sys.argv), "CRASH")
    log("CWD     : %s" % os.getcwd(), "CRASH")
    log("Traceback:", "CRASH")
    log_block("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
    log_separator("!", "CRASH")


def _shutdown_log():
    """Flush and close the log file."""
    global _log_stream
    if _log_stream is not None:
        try:
            _log_stream.flush()
            _log_stream.close()
        except Exception:                                      # noqa: BLE001
            pass
        _log_stream = None


def _install_crash_handlers():
    """Catch unhandled exceptions AND hard crashes (faulthandler)."""
    def excepthook(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            log("Interrupted by user (Ctrl+C)", "WARN")
        else:
            _log_crash(exc_type, exc_value, exc_tb)
        _shutdown_log()
        os._exit(3)

    sys.excepthook = excepthook

    try:
        import faulthandler
        if _log_stream is not None:
            faulthandler.enable(file=_log_stream, all_threads=True)
        else:
            faulthandler.enable()
    except Exception:                                          # noqa: BLE001
        pass

    def _on_exit():
        log("Process exiting (log file: %s)" % _log_path)
        _shutdown_log()

    atexit.register(_on_exit)


def _prune_old_logs(keep_days):
    """Delete log files older than keep_days (0 disables pruning)."""
    if not keep_days or keep_days <= 0:
        return
    try:
        cutoff = time.time() - keep_days * 86400
        directory = os.path.dirname(_log_path) if _log_path else LOG_DIR
        for name in os.listdir(directory):
            if not (name.startswith(LOG_FILE_PREFIX) and name.endswith(".log")):
                continue
            full = os.path.join(directory, name)
            if full == _log_path:
                continue
            if os.path.isfile(full) and os.path.getmtime(full) < cutoff:
                os.remove(full)
                log("Removed expired log file: %s" % name)
    except Exception as exc:                                   # noqa: BLE001
        log("Log pruning skipped: %s" % exc, "WARN")


# ============================================================
# Environment diagnostics
# ============================================================

_user32 = ctypes.WinDLL("user32", use_last_error=True) if os.name == "nt" else None
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True) if os.name == "nt" else None

if _user32 is not None:
    _user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    _user32.FindWindowW.restype = wintypes.HWND
    _user32.GetSystemMetrics.argtypes = [ctypes.c_int]
    _user32.GetSystemMetrics.restype = ctypes.c_int
if _kernel32 is not None:
    _kernel32.GetTickCount64.restype = ctypes.c_ulonglong
    _kernel32.ProcessIdToSessionId.argtypes = [wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    _kernel32.ProcessIdToSessionId.restype = wintypes.BOOL


def get_uptime_seconds():
    """Seconds since Windows booted (None if unavailable)."""
    try:
        return _kernel32.GetTickCount64() / 1000.0
    except Exception:                                          # noqa: BLE001
        return None


def get_session_id():
    """Windows session id of the current process (0 = services/session 0)."""
    try:
        sid = wintypes.DWORD(0)
        if _kernel32.ProcessIdToSessionId(_kernel32.GetCurrentProcessId(), ctypes.byref(sid)):
            return sid.value
    except Exception:                                          # noqa: BLE001
        pass
    return None


def get_screen_size():
    """Primary screen resolution - needed to sanity-check WorkBuddy click coordinates."""
    try:
        return _user32.GetSystemMetrics(0), _user32.GetSystemMetrics(1)
    except Exception:                                          # noqa: BLE001
        return None, None


def shell_is_ready():
    """True when the interactive Windows shell (Explorer tray) exists in this session."""
    try:
        return bool(_user32.FindWindowW("Shell_TrayWnd", None))
    except Exception:                                          # noqa: BLE001
        return False


def log_environment(startup_mode):
    """Log everything we may need to diagnose a failure later."""
    log_separator()
    log("Auto Check-in Script Started%s" % (" (startup mode)" if startup_mode else ""))
    log_separator()
    log("Log file         : %s" % (_log_path or "<unavailable>"))
    log("Script           : %s" % SCRIPT_PATH)
    log("Project dir      : %s" % PROJECT_DIR)
    log("CWD              : %s" % os.getcwd())
    log("Command line     : %s" % " ".join(sys.argv))
    log("Config source    : %s" % CONFIG_SOURCE)
    if CONFIG_ERROR:
        log("Config import error: %s" % CONFIG_ERROR, "WARN")
    log("Python           : %s (%s)" % (sys.version.split()[0], sys.executable))
    log("Python (child)   : %s" % PYTHON_EXE)
    log("Node.js (child)  : %s -> %s" % (NODE_EXE, shutil.which(NODE_EXE) or "NOT FOUND"))
    log("OS               : %s %s" % (platform.system(), platform.release()))
    log("User             : %s" % os.environ.get("USERNAME", "<unknown>"))
    log("Session id       : %s" % get_session_id())
    log("Desktop shell    : %s" % ("ready" if shell_is_ready() else "NOT ready"))
    width, height = get_screen_size()
    log("Screen resolution: %sx%s" % (width, height))
    if (width, height) != tuple(WORKBUDDY_COORD_BASELINE):
        log("Screen is not the %sx%s that the WorkBuddy click coordinates were calibrated for."
            % tuple(WORKBUDDY_COORD_BASELINE), "WARN")
        log("The vendored WorkBuddy script clicks fixed pixels, so those clicks may miss their "
            "target and the check-in can silently do nothing - recalibrate if WorkBuddy fails.", "WARN")
    uptime = get_uptime_seconds()
    if uptime is None:
        log("System uptime    : <unavailable>")
    else:
        log("System uptime    : %.0f s (%.1f min) -> check-in started %.1f minutes after boot"
            % (uptime, uptime / 60.0, uptime / 60.0))


def wait_for_desktop_ready():
    """Wait until the desktop shell is usable - avoids GUI automation running too early."""
    if not WAIT_FOR_DESKTOP:
        log("Desktop readiness check disabled by configuration", "WARN")
        return True

    if os.name != "nt":
        return True

    if shell_is_ready():
        log("Desktop shell is already ready")
    else:
        log("Desktop shell not ready yet, waiting up to %ss..." % DESKTOP_READY_TIMEOUT)
        deadline = time.time() + DESKTOP_READY_TIMEOUT
        notified = 0.0
        while time.time() < deadline:
            if shell_is_ready():
                break
            if time.time() - notified >= 15:
                waited = DESKTOP_READY_TIMEOUT - max(0.0, deadline - time.time())
                log("Still waiting for desktop shell... (%.0fs elapsed)" % waited, "WARN")
                notified = time.time()
            time.sleep(max(0.5, DESKTOP_POLL_INTERVAL))
        else:
            log("Desktop shell did not become ready within %ss" % DESKTOP_READY_TIMEOUT, "ERROR")
            log("Session id is %s (session 0 means the task is NOT running on the user desktop)"
                % get_session_id(), "ERROR")
            return False

    if DESKTOP_SETTLE_SECONDS > 0:
        log("Desktop ready, settling %.0fs before starting GUI automation" % DESKTOP_SETTLE_SECONDS)
        time.sleep(DESKTOP_SETTLE_SECONDS)
    else:
        log("Desktop ready")
    return True


# ============================================================
# Path validation
# ============================================================

def check_path(path, name):
    """Check that a path exists; log the result (this is what caught the stale config bug)."""
    if path and os.path.exists(path):
        log("%s: OK -> %s" % (name, path))
        return True
    log("%s: NOT FOUND -> %s" % (name, path), "ERROR")
    return False


def check_all_paths():
    """Validate every external dependency up front, so failures are explainable."""
    log_separator("-")
    log("Validating paths and runtimes")
    log_separator("-")
    log("Config source: %s" % CONFIG_SOURCE)
    if CONFIG_ERROR:
        log("Config could not be imported (%s), using built-in default paths" % CONFIG_ERROR, "ERROR")

    results = {
        "trae_exe": check_path(TRAE_EXE, "Trae SOLO CN exe"),
        "workbuddy_exe": check_path(WORKBUDDY_EXE, "WorkBuddy exe"),
        "trae_script": check_path(TRAE_CHECKIN_SCRIPT, "Trae check-in script"),
        "workbuddy_script": check_path(WORKBUDDY_CHECKIN_SCRIPT, "WorkBuddy check-in script"),
    }

    if results["trae_exe"] and not results["trae_script"]:
        log("Trae app exists but its check-in script is missing - Trae check-in will fail", "WARN")
    if results["workbuddy_exe"] and not results["workbuddy_script"]:
        log("WorkBuddy app exists but its check-in script is missing - WorkBuddy check-in will fail", "WARN")

    return results


# ============================================================
# Check-in tasks
# ============================================================

def _child_env():
    """Child process env: force UTF-8 output so captured text decodes reliably."""
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _workbuddy_env():
    """Child env for the WorkBuddy script: inject the coordinates from config.py."""
    env = _child_env()
    env["WORKBUDDY_MENU_X"] = str(WORKBUDDY_MENU_X)
    env["WORKBUDDY_MENU_Y"] = str(WORKBUDDY_MENU_Y)
    env["WORKBUDDY_CHECKIN_X"] = str(WORKBUDDY_CHECKIN_X)
    env["WORKBUDDY_CHECKIN_Y"] = str(WORKBUDDY_CHECKIN_Y)
    env["WORKBUDDY_SKIP_MENU"] = "1" if WORKBUDDY_SKIP_MENU else "0"
    env["WORKBUDDY_VERIFY"] = "1" if WORKBUDDY_VERIFY else "0"
    env["WORKBUDDY_READY_TIMEOUT"] = str(WORKBUDDY_READY_TIMEOUT)
    env["WORKBUDDY_MAX_TRIES"] = str(WORKBUDDY_MAX_TRIES)
    env["WORKBUDDY_CLOSE_DELAY"] = str(WORKBUDDY_CLOSE_DELAY)
    return env


def run_command(cmd, timeout, label, env=None):
    """Run a command, log stdout/stderr/exit code, return the CompletedProcess (or None)."""
    log("Running %s: %s" % (label, subprocess.list2cmdline(cmd)))
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env if env is not None else _child_env(),
        )
    except subprocess.TimeoutExpired:
        log("%s timed out after %ss" % (label, timeout), "ERROR")
        return None
    except FileNotFoundError as exc:
        log("%s could not start: %s" % (label, exc), "ERROR")
        return None
    except Exception as exc:                                   # noqa: BLE001
        log("%s failed to run: %s: %s" % (label, type(exc).__name__, exc), "ERROR")
        return None

    log("%s exit code: %s" % (label, result.returncode))
    if result.stdout and result.stdout.strip():
        log("%s stdout:" % label)
        log_block(result.stdout)
    if result.stderr and result.stderr.strip():
        log("%s stderr:" % label, "WARN")
        log_block(result.stderr)
    return result


def run_trae_checkin():
    """Execute Trae SOLO CN check-in."""
    log_separator("-")
    log("Starting Trae SOLO CN check-in...")

    if not os.path.exists(TRAE_CHECKIN_SCRIPT):
        log("Trae check-in script missing, skipping: %s" % TRAE_CHECKIN_SCRIPT, "ERROR")
        return False

    result = run_command(
        [NODE_EXE, TRAE_CHECKIN_SCRIPT, "--force", "--close"],
        TRAE_TIMEOUT,
        "Trae check-in script",
    )

    if result is None:
        return False
    if result.returncode == 0:
        log("Trae check-in successful!", "SUCCESS")
        return True
    if result.returncode == 2:
        log("Trae already signed in today", "INFO")
        return True
    log("Trae check-in failed (exit code %s)" % result.returncode, "ERROR")
    return False


def run_workbuddy_checkin():
    """Execute WorkBuddy check-in."""
    log_separator("-")
    log("Starting WorkBuddy check-in...")

    if not os.path.exists(WORKBUDDY_CHECKIN_SCRIPT):
        log("WorkBuddy check-in script missing, skipping: %s" % WORKBUDDY_CHECKIN_SCRIPT, "ERROR")
        return False

    log("WorkBuddy click coordinates (from config.py): user menu=(%s, %s), check-in button=(%s, %s)"
        % (WORKBUDDY_MENU_X, WORKBUDDY_MENU_Y, WORKBUDDY_CHECKIN_X, WORKBUDDY_CHECKIN_Y))
    log("WorkBuddy flow: %s" % ("home page check-in (avatar menu skipped)" if WORKBUDDY_SKIP_MENU
                                else "avatar menu, then check-in button (upstream flow)"))
    log("WorkBuddy click verification: %s (max tries %s, ready timeout %ss)"
        % ("on" if WORKBUDDY_VERIFY else "off - upstream blind click",
           WORKBUDDY_MAX_TRIES, WORKBUDDY_READY_TIMEOUT))

    result = run_command(
        [PYTHON_EXE, WORKBUDDY_CHECKIN_SCRIPT],
        WORKBUDDY_TIMEOUT,
        "WorkBuddy check-in script",
        env=_workbuddy_env(),
    )

    if result is None:
        return False
    if result.returncode == 0:
        log("WorkBuddy check-in successful!", "SUCCESS")
        return True
    log("WorkBuddy check-in failed (exit code %s)" % result.returncode, "ERROR")
    return False


# ============================================================
# Main
# ============================================================

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Daily check-in for Trae SOLO CN and WorkBuddy")
    parser.add_argument("--startup", action="store_true",
                        help="started by the Windows scheduled task: wait for the desktop first")
    parser.add_argument("--no-desktop-wait", action="store_true",
                        help="skip the desktop readiness wait even in --startup mode")
    parser.add_argument("--target", choices=["all", "trae", "workbuddy"], default="all",
                        help="which check-in(s) to run: trae = Trae only, workbuddy = WorkBuddy "
                             "only, all = both (default)")
    return parser.parse_args(argv)


def run(startup_mode, skip_desktop_wait=False, target="all"):
    log_environment(startup_mode)
    _prune_old_logs(LOG_KEEP_DAYS)

    log("Check-in target    : %s" % target)

    want_trae = target in ("all", "trae")
    want_workbuddy = target in ("all", "workbuddy")

    paths = check_all_paths()
    trae_ready = want_trae and paths["trae_exe"] and paths["trae_script"]
    workbuddy_ready = want_workbuddy and paths["workbuddy_exe"] and paths["workbuddy_script"]

    if not trae_ready and not workbuddy_ready:
        log("No runnable check-in task (target=%s; missing application or script), cannot proceed"
            % target, "ERROR")
        return 1

    if startup_mode and not skip_desktop_wait:
        if not wait_for_desktop_ready():
            log("Aborting: desktop environment is not usable, check-in not attempted", "ERROR")
            return 1
    elif not startup_mode:
        log("Desktop readiness check skipped (manual run)")

    results = {"trae": False, "workbuddy": False}

    if trae_ready:
        results["trae"] = run_trae_checkin()
        log("Waiting %ss before the next task" % WAIT_BETWEEN_TASKS)
        time.sleep(WAIT_BETWEEN_TASKS)
    elif want_trae:
        log("Trae SOLO CN unavailable, skipped", "WARN")
    else:
        log("Trae SOLO CN not selected (target=%s), skipped" % target)

    if workbuddy_ready:
        results["workbuddy"] = run_workbuddy_checkin()
    elif want_workbuddy:
        log("WorkBuddy unavailable, skipped", "WARN")
    else:
        log("WorkBuddy not selected (target=%s), skipped" % target)

    def _status(key, ready, wanted):
        if results[key]:
            return "Success"
        if not wanted:
            return "Skipped (target=%s)" % target
        return "Failed" if ready else "Skipped (unavailable)"

    log_separator()
    log("Check-in Results Summary:")
    log("  Trae SOLO CN : %s" % _status("trae", trae_ready, want_trae))
    log("  WorkBuddy    : %s" % _status("workbuddy", workbuddy_ready, want_workbuddy))
    log_separator()

    success_count = sum(results.values())
    total_tasks = sum([trae_ready, workbuddy_ready])

    if success_count == total_tasks:
        log("All check-in tasks completed!", "SUCCESS")
        return 0
    if success_count > 0:
        log("Partial check-in tasks completed (%s/%s)" % (success_count, total_tasks), "WARN")
        return 0

    log("All check-in tasks failed", "ERROR")
    return 1


def main(argv=None):
    started = time.time()
    args = parse_args(argv)

    # Logging + crash handlers first, so even an early crash is recorded.
    _open_log_file()
    _install_crash_handlers()

    try:
        exit_code = run(args.startup, args.no_desktop_wait, args.target)
    except SystemExit:
        raise
    except BaseException as exc:                               # noqa: BLE001
        _log_crash(type(exc), exc, exc.__traceback__, "crash inside main()")
        return 3

    log("Finished with exit code %s after %.1fs" % (exit_code, time.time() - started))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())