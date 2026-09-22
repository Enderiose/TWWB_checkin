#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WorkBuddy 签到诊断工具（只截图，不点击，安全）

用途：看清 WorkBuddy 窗口在最大化后到底是什么样子，以及 config.py 里配置的
      签到坐标究竟落在界面哪个位置。

用法：
    python scripts/diagnose_workbuddy.py                # 默认：最大化后 1s、5s 各截一张
    python scripts/diagnose_workbuddy.py --waits 1,3,8  # 自定义截图时机（秒）
    python scripts/diagnose_workbuddy.py --no-launch    # 不自动启动 WorkBuddy
    python scripts/diagnose_workbuddy.py --no-maximize  # 只在当前窗口状态下截图

输出：logs/diag_workbuddy_<时间戳>_<等待秒数>s.png（整屏，带十字标记）
      logs/diag_workbuddy_<时间戳>_<等待秒数>s_zoom.png（签到坐标附近放大图）
"""

import argparse
import ctypes
import os
import subprocess
import sys
import time
from ctypes import wintypes
from datetime import datetime

SCRIPT_PATH = os.path.abspath(__file__)
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_PATH))
sys.path.insert(0, PROJECT_DIR)

try:
    from config import (
        PROJECT_DIR as _CONFIG_PROJECT_DIR, WORKBUDDY_EXE, LOG_DIR,
        WORKBUDDY_MENU_X, WORKBUDDY_MENU_Y,
        WORKBUDDY_CHECKIN_X, WORKBUDDY_CHECKIN_Y,
        WORKBUDDY_SKIP_MENU,
    )
    CONFIG_SOURCE = "config.py"
except Exception as exc:                                       # noqa: BLE001
    CONFIG_SOURCE = "built-in defaults (%s)" % exc
    WORKBUDDY_EXE = r"C:\Users\Administrator\AppData\Local\Programs\WorkBuddy\WorkBuddy.exe"
    LOG_DIR = os.path.join(PROJECT_DIR, "logs")
    WORKBUDDY_MENU_X, WORKBUDDY_MENU_Y = 207, 983
    WORKBUDDY_CHECKIN_X, WORKBUDDY_CHECKIN_Y = 112, 487
    WORKBUDDY_SKIP_MENU = False

WINDOW_TITLE = "WorkBuddy"

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowW.restype = wintypes.HWND
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetWindowRect.restype = wintypes.BOOL
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype = wintypes.BOOL
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.GetSystemMetrics.argtypes = [ctypes.c_int]
user32.GetSystemMetrics.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int


def log(message, level="INFO"):
    print("[%s] [%s] %s" % (datetime.now().strftime("%H:%M:%S"), level, message), flush=True)


def find_window():
    return user32.FindWindowW(None, WINDOW_TITLE)


def window_rect(hwnd):
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None
    return rect.left, rect.top, rect.right, rect.bottom


def rect_text(rect):
    if not rect:
        return "<unknown>"
    left, top, right, bottom = rect
    return "(%d,%d)-(%d,%d) size %dx%d" % (left, top, right, bottom, right - left, bottom - top)


def launch_workbuddy():
    log("WorkBuddy 未运行，正在启动: %s" % WORKBUDDY_EXE)
    if not os.path.exists(WORKBUDDY_EXE):
        log("可执行文件不存在", "ERROR")
        return False
    try:
        subprocess.Popen(
            ["cmd", "/c", "start", "", WORKBUDDY_EXE],
            shell=True,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        return True
    except Exception as exc:                                   # noqa: BLE001
        log("启动失败: %s" % exc, "ERROR")
        return False


def wait_for_window(timeout=45):
    log("等待 WorkBuddy 窗口出现（最多 %ds）..." % timeout)
    start = time.time()
    while time.time() - start < timeout:
        hwnd = find_window()
        if hwnd and user32.IsWindowVisible(hwnd):
            log("窗口已出现 (handle=%s)，用时 %.1fs" % (hwnd, time.time() - start))
            return hwnd
        time.sleep(1)
    return 0


def capture(tag, mark_points, zoom_point=None):
    """截图（整屏 + 可选放大图），并在指定坐标画十字标记。"""
    try:
        from PIL import ImageGrab, ImageDraw
    except Exception as exc:                                   # noqa: BLE001
        log("Pillow 不可用，无法截图: %s" % exc, "ERROR")
        return None

    # 说明：SetCursorPos / mouse_event 使用"虚拟桌面"坐标，多屏时原点可能不是 (0,0)
    origin_x = user32.GetSystemMetrics(76)   # SM_XVIRTUALSCREEN
    origin_y = user32.GetSystemMetrics(77)   # SM_YVIRTUALSCREEN
    image = ImageGrab.grab(all_screens=True)
    draw = ImageDraw.Draw(image)

    for (x, y), label, color in mark_points:
        px, py = x - origin_x, y - origin_y
        draw.line([(px - 60, py), (px + 60, py)], fill=color, width=3)
        draw.line([(px, py - 60), (px, py + 60)], fill=color, width=3)
        draw.ellipse([px - 18, py - 18, px + 18, py + 18], outline=color, width=3)
        draw.text((px + 24, py - 34), label, fill=color)

    os.makedirs(LOG_DIR, exist_ok=True)
    path = os.path.join(LOG_DIR, "diag_workbuddy_%s_%s.png" % (tag, datetime.now().strftime("%H%M%S")))
    image.save(path)
    log("整屏截图: %s  (%dx%d, 虚拟桌面原点 %d,%d)" % (path, image.width, image.height, origin_x, origin_y))

    if zoom_point:
        x, y = zoom_point
        px, py = x - origin_x, y - origin_y
        box = (max(0, px - 300), max(0, py - 220), min(image.width, px + 300), min(image.height, py + 220))
        zoom = image.crop(box)
        zoom = zoom.resize((zoom.width * 2, zoom.height * 2))
        zoom_path = os.path.join(LOG_DIR, "diag_workbuddy_%s_%s_zoom.png"
                                 % (tag, datetime.now().strftime("%H%M%S")))
        zoom.save(zoom_path)
        log("放大截图: %s  (区域 %s)" % (zoom_path, str(box)))
    return path


def main():
    parser = argparse.ArgumentParser(description="WorkBuddy 签到诊断（只截图，不点击）")
    parser.add_argument("--waits", default="1,5",
                        help="最大化后截图时机，逗号分隔的秒数，默认 1,5")
    parser.add_argument("--no-launch", action="store_true", help="不自动启动 WorkBuddy")
    parser.add_argument("--no-maximize", action="store_true", help="不最大化窗口")
    args = parser.parse_args()

    log("=" * 70)
    log("WorkBuddy 诊断（只截图，绝不点击）")
    log("配置来源: %s" % CONFIG_SOURCE)
    log("配置坐标: 用户菜单=(%s, %s)  签到按钮=(%s, %s)  首页直签=%s"
        % (WORKBUDDY_MENU_X, WORKBUDDY_MENU_Y, WORKBUDDY_CHECKIN_X, WORKBUDDY_CHECKIN_Y,
           WORKBUDDY_SKIP_MENU))
    log("=" * 70)

    hwnd = find_window()
    if not hwnd and not args.no_launch:
        if not launch_workbuddy():
            return 1
        hwnd = wait_for_window()
    if not hwnd:
        log("找不到 WorkBuddy 窗口（若它在运行但标题变了，请把真实标题告诉我）", "ERROR")
        return 1

    log("窗口 handle = %s" % hwnd)
    log("最大化前窗口位置: %s" % rect_text(window_rect(hwnd)))

    if not args.no_maximize:
        user32.ShowWindow(hwnd, 3)          # SW_MAXIMIZE
        time.sleep(1.0)
        user32.SetForegroundWindow(hwnd)
        user32.BringWindowToTop(hwnd)
        log("最大化后窗口位置: %s" % rect_text(window_rect(hwnd)))

    marks = []
    if WORKBUDDY_SKIP_MENU:
        marks.append(((WORKBUDDY_CHECKIN_X, WORKBUDDY_CHECKIN_Y), "CHECKIN config", (255, 0, 0)))
    else:
        marks.append(((WORKBUDDY_MENU_X, WORKBUDDY_MENU_Y), "MENU config", (255, 0, 0)))
        marks.append(((WORKBUDDY_CHECKIN_X, WORKBUDDY_CHECKIN_Y), "CHECKIN config", (0, 0, 255)))

    for raw in args.waits.split(","):
        try:
            seconds = float(raw.strip())
        except ValueError:
            continue
        log("等待 %.1fs 后截图..." % seconds)
        time.sleep(seconds)
        capture("%gs" % seconds, marks, zoom_point=(WORKBUDDY_CHECKIN_X, WORKBUDDY_CHECKIN_Y))
        log("窗口位置: %s" % rect_text(window_rect(hwnd)))

    log("完成：没有执行任何点击。请查看上面的截图路径。")
    return 0


if __name__ == "__main__":
    sys.exit(main())