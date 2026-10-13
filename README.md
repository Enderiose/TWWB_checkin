# TWWB_check / 自动化签到工具

[English](#English) · [简体中文](#简体中文)

---

<a id="English"></a>

## English

Automatically complete daily check-in for Trae SOLO CN and WorkBuddy.

### Features

- **Dual Program Support**: Trae SOLO CN + WorkBuddy
- **Auto Start on Logon**: Runs ~2 minutes after Windows user logon (never during logon, so the desktop is ready)
- **Detailed Logging**: Timestamp and status for each operation, written to a daily log file
- **Crash Logging**: Unhandled exceptions are logged with a full traceback and exit code 3

### Prerequisites

- Windows OS
- Python 3.x
- Node.js 18+
- Trae SOLO CN and WorkBuddy installed

### Quick Start

#### 1. Validate Paths
```cmd
python scripts\test_paths.py
```

#### 2. Install Auto Check-in Task
```cmd
install_startup_task.bat
```

The installer asks what the task should check in (15s timeout, default = both):

| Choice | Meaning |
|--------|---------|
| `[1]` | Trae only |
| `[2]` | WorkBuddy only |
| `[3]` | Both (default) |

The choice can also be passed on the command line (unattended):
```cmd
install_startup_task.bat workbuddy quiet
```
Accepted values: `trae`, `workbuddy`, `all` (or `both`), `1`, `2`, `3`.

#### 3. Test Check-in
```cmd
python scripts\auto_checkin.py
```

### Project Structure

```
auto_sign/
├── config.py                  # Configuration
├── logs/                      # Daily log files (auto-created, not in git)
│   └── auto_checkin_YYYY-MM-DD.log
├── scripts/
│   ├── auto_checkin.py        # Main check-in script (logging + crash handling)
│   ├── test_paths.py          # Path validation
│   ├── diagnose_workbuddy.py  # Screenshot-only WorkBuddy diagnostics (never clicks)
│   └── full_test.py           # System test
├── patches/                   # Local patch snapshot for the vendored submodule
├── trae-daily-checkin/        # Trae library (3rd-party, see THIRD_PARTY_NOTICES.md)
├── workbuddy-checkin/         # WorkBuddy library (3rd-party, see THIRD_PARTY_NOTICES.md)
├── install_startup_task.bat   # Install task (logon + 2 min delay)
├── uninstall_startup_task.bat # Uninstall task
├── test_checkin.bat           # Test check-in
└── info.bat                   # Show info
```

### Logs and Exit Codes

Every run appends to `logs/auto_checkin_YYYY-MM-DD.log` (UTF-8, 30 days kept).
Each entry records the environment (session id, screen resolution, uptime after boot,
resolved paths), every sub-process command with its stdout/stderr and exit code, and
any unhandled exception with a full traceback.

| Exit code | Meaning |
| --- | --- |
| `0` | All check-ins done, or at least one of them |
| `1` | All check-ins failed / application or script not found |
| `3` | Unexpected crash - see the `[CRASH]` block in the log |

The last exit code of the scheduled run is also visible in Task Scheduler
(`schtasks /Query /TN AutoCheckinOnStartup /V /FO LIST`, field *Last Result*).

### Configuration

Edit `config.py`:
```python
TRAE_EXE = r"Your Trae path"
WORKBUDDY_EXE = r"Your WorkBuddy path"
TRAE_TIMEOUT = 120
WORKBUDDY_TIMEOUT = 60
```

### Commands

| Command | Description |
|---------|-------------|
| `python scripts\test_paths.py` | Test paths |
| `python scripts\auto_checkin.py` | Manual check-in (both) |
| `python scripts\auto_checkin.py --target trae` | Manual check-in, Trae only (`trae`/`workbuddy`/`all`) |
| `python scripts\full_test.py` | System test |
| `install_startup_task.bat` | Install task (asks for the target) |
| `install_startup_task.bat workbuddy` | Install task for WorkBuddy only (no prompt) |
| `uninstall_startup_task.bat` | Uninstall task |

### Troubleshooting

1. **Path error**: Edit `config.py` - and read the log, it names the exact missing path
2. **Check-in failed**: Ensure apps are logged in
3. **Task not running**: Check Python/Node.js in PATH
4. **Any unexplained failure**: open `logs\auto_checkin_YYYY-MM-DD.log`; it contains the
   full environment dump, every sub-process exit code and any crash traceback
5. **WorkBuddy clicks do nothing**: its click coordinates are hard-coded for 1920x1080,
   the script logs a warning when the screen differs
6. **WorkBuddy "no change" / check-in not visible**: run `python scripts\diagnose_workbuddy.py`,
   look at the generated screenshots and correct `WORKBUDDY_CHECKIN_X/Y` in `config.py`
7. **The installer seems to do nothing**: open `logs\install_task.log` - it records the
   elevation state, the resolved Python/Node paths, and the exact `schtasks` command with
   its output and exit code. A cancelled UAC prompt now reports an explicit error instead
   of closing the window silently. The task itself only fires AT LOGON, so nothing happens
   until the next logon or reboot.

### Technical Details

- **Trae**: Chrome DevTools Protocol (CDP) + Node.js
- **WorkBuddy**: Win32 API (ctypes) + Python

### Notes

- The check-in runs **2 minutes after user logon** (adjustable: `STARTUP_DELAY` at the
  top of `install_startup_task.bat`, then re-run it)
- The scheduled command starts in `C:\Windows\System32`; all paths are resolved from the
  project directory, never from the current directory
- WorkBuddy click coordinates live in `config.py` (`WORKBUDDY_MENU_X/Y`, `WORKBUDDY_CHECKIN_X/Y`)
  and are injected into the vendored script as environment variables. They were measured on
  this machine's screen (2560x1440) - the shipped defaults assume 1920x1080, so recalibrate
  them after a screen/scale change (the log prints a warning when the resolution differs)
- `WORKBUDDY_SKIP_MENU = True` makes WorkBuddy check in straight from the home page,
  skipping the "click the avatar, wait for the menu" steps
- The WorkBuddy step is self-verifying (`WORKBUDDY_VERIFY = True`): it waits for the white
  check-in button to render, makes sure the window is really in the foreground, clicks, then
  compares before/after screenshots and retries (up to `WORKBUDDY_MAX_TRIES`) when nothing
  changed. If no button is found it reports "already checked in today" and exits 0 instead of
  clicking blindly, so a missing button is never mistaken for a successful check-in
- `python scripts\diagnose_workbuddy.py` takes screenshots of the real WorkBuddy window with a
  crosshair drawn at the configured coordinates - it never clicks, so use it whenever the
  check-in fails or after a screen/scale change
- To re-measure a coordinate, hover the mouse over the target and run:
  `python -c "import ctypes,ctypes.wintypes as w,time; u=ctypes.windll.user32; time.sleep(5); p=w.POINT(); u.GetCursorPos(ctypes.byref(p)); print(p.x, p.y)"`
  (use `python`, not PowerShell - PowerShell is DPI-unaware and reports scaled coordinates)
- First use requires manual login
- Trae debug port only listens on 127.0.0.1

### Third-Party Code and Attribution

This repository vendors two upstream projects. All credit for the check-in implementations belongs to their authors; only the wrapper/scheduling layer (`config.py`, `scripts/`, `*.bat`) is original to this project. `trae-daily-checkin/` carries three small documented local fixes (waiting for the CDP page target, polling for the account UI, and making `--close` actually control whether Trae is closed); `workbuddy-checkin/` carries two small documented local patches (click coordinates and a flow switch, both driven by environment variables so they stay configurable from `config.py`).

| Directory | Upstream repository | Author | License |
| --- | --- | --- | --- |
| `trae-daily-checkin/` | [BlueChonk/trae-daily-checkin](https://github.com/BlueChonk/trae-daily-checkin) | Cecilia | MIT |
| `workbuddy-checkin/` | [GitOfUser/workbuddy-checkin](https://github.com/GitOfUser/workbuddy-checkin) | GitOfUser | Upstream provides no license file (all rights reserved by the author) |

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for version/commit details and trademark notes.

### License

The original parts of this project — the wrapper and scheduling layer (`config.py`, `scripts/`, `*.bat`) — are released under the [MIT License](LICENSE).

The vendored third-party code keeps the copyright and license of its respective authors (see the table above); the MIT License does not apply to it. In particular, `workbuddy-checkin/` ships without any upstream license file, so all rights to that code remain with its author.

---

<a id="简体中文"></a>

## 简体中文

自动完成 Trae SOLO CN 和 WorkBuddy 的每日签到。

### 功能特点

- **双程序签到**：同时支持 Trae SOLO CN 和 WorkBuddy
- **登录后自启**：登录后约 2 分钟才执行（不在登录瞬间运行，桌面环境已就绪）
- **详细日志**：每一步都带时间戳写入按天分割的日志文件
- **崩溃日志**：未捕获异常会完整记录堆栈并以退出码 3 结束

### 前提条件

- Windows 操作系统
- Python 3.x
- Node.js 18+
- Trae SOLO CN 和 WorkBuddy 已安装

### 快速开始

#### 1. 验证路径
```cmd
python scripts\test_paths.py
```

#### 2. 安装自动签到任务
```cmd
install_startup_task.bat
```

安装时会询问任务要签到哪些应用（15 秒无操作默认全签）：

| 选项 | 含义 |
|------|------|
| `[1]` | 仅 Trae |
| `[2]` | 仅 WorkBuddy |
| `[3]` | 两者都签（默认） |

也可以直接在命令行传入（用于无人值守）：
```cmd
install_startup_task.bat workbuddy quiet
```
可选值：`trae`、`workbuddy`、`all`（或 `both`）、`1`、`2`、`3`。

#### 3. 测试签到
```cmd
python scripts\auto_checkin.py
```

### 项目结构

```
auto_sign/
├── config.py                  # 配置文件
├── logs/                      # 按天日志目录（自动创建，不纳入 git）
│   └── auto_checkin_YYYY-MM-DD.log
├── scripts/
│   ├── auto_checkin.py        # 主签到脚本（含日志/崩溃捕获）
│   ├── test_paths.py          # 路径验证
│   ├── diagnose_workbuddy.py  # WorkBuddy 诊断（只截图不点击）
│   └── full_test.py           # 系统测试
├── patches/                   # 第三方子模块的本地补丁快照
├── trae-daily-checkin/        # Trae 库（第三方，见 THIRD_PARTY_NOTICES.md）
├── workbuddy-checkin/         # WorkBuddy 库（第三方，见 THIRD_PARTY_NOTICES.md）
├── install_startup_task.bat   # 安装任务（登录 + 2 分钟延迟）
├── uninstall_startup_task.bat # 卸载任务
├── test_checkin.bat           # 测试签到
└── info.bat                   # 显示信息
```

### 日志与退出码

每次运行都会追加写入 `logs\auto_checkin_YYYY-MM-DD.log`（UTF-8，保留 30 天）。
日志包含：运行环境（会话 ID、屏幕分辨率、开机后经过时间、各路径解析结果）、
每个子进程的完整命令与 stdout/stderr 和退出码、以及任何异常的完整堆栈。

| 退出码 | 含义 |
| --- | --- |
| `0` | 全部签到成功，或至少一个成功 |
| `1` | 全部签到失败 / 应用或脚本路径不存在 |
| `3` | 脚本异常崩溃（日志中有 `[CRASH]` 段落） |

计划任务的上次退出码也可在任务计划程序中查看
（`schtasks /Query /TN AutoCheckinOnStartup /V /FO LIST` 的“上次结果”字段）。

### 配置说明

编辑 `config.py`：
```python
TRAE_EXE = r"你的Trae路径"
WORKBUDDY_EXE = r"你的WorkBuddy路径"
TRAE_TIMEOUT = 120
WORKBUDDY_TIMEOUT = 60
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `python scripts\test_paths.py` | 测试路径 |
| `python scripts\auto_checkin.py` | 手动签到（全部） |
| `python scripts\auto_checkin.py --target trae` | 手动签到，仅 Trae（`trae`/`workbuddy`/`all`） |
| `python scripts\full_test.py` | 系统测试 |
| `install_startup_task.bat` | 安装任务（会询问签到目标） |
| `install_startup_task.bat workbuddy` | 仅安装 WorkBuddy 签到任务（不询问） |
| `uninstall_startup_task.bat` | 卸载任务 |

### 故障排除

1. **路径错误**：编辑 `config.py` —— 日志里会明确写出缺失的路径
2. **签到失败**：确保应用已登录
3. **任务不执行**：检查 Python/Node.js 在 PATH 中
4. **任何无法解释的失败**：打开 `logs\auto_checkin_YYYY-MM-DD.log`，
   里面有完整环境信息、每个子进程退出码和崩溃堆栈
5. **WorkBuddy 点击无反应**：它的点击坐标是按 1920x1080 硬编码的，
   分辨率不一致时脚本会输出 WARN 提示
6. **WorkBuddy 提示"界面无变化"或界面上看不到签到结果**：运行
   `python scripts\diagnose_workbuddy.py`，查看生成的截图并修正 `config.py` 的
   `WORKBUDDY_CHECKIN_X/Y`
7. **安装脚本看起来没生效**：打开 `logs\install_task.log`，里面有提权状态、解析到的
   Python/Node 路径、以及完整的 `schtasks` 命令与输出/退出码。UAC 被取消时现在会明确
   报错，不再静默关窗。另外计划任务只在**登录时**触发，所以未重新登录/重启前不会执行。

### 技术细节

- **Trae**：Chrome DevTools Protocol (CDP) + Node.js
- **WorkBuddy**：Win32 API (ctypes) + Python

### 注意事项

- 签到在**用户登录后 2 分钟**执行（可改：`install_startup_task.bat` 顶部的
  `STARTUP_DELAY`，改完重新运行该脚本）
- 计划任务的工作目录是 `C:\Windows\System32`，所有路径都基于项目目录解析，
  与当前目录无关
- WorkBuddy 坐标在 `config.py`（`WORKBUDDY_MENU_X/Y`、`WORKBUDDY_CHECKIN_X/Y`）中配置，
  由 `scripts/auto_checkin.py` 以环境变量注入到第三方脚本中。当前值是在本机屏幕
  （2560x1440）上实测得到的（上游默认值按 1920x1080 校准）；换屏或改缩放后需重新校准，
  否则点击会落空（分辨率不一致时日志会输出 WARN）
- `WORKBUDDY_SKIP_MENU = True` 表示直接点首页的签到按钮，跳过头像菜单流程
- WorkBuddy 签到自带校验（`WORKBUDDY_VERIFY = True`）：先等白色签到按钮渲染出来，
  确认窗口真的在前台，再点击，然后对比点击前后的截图，界面没变化就重试
  （最多 `WORKBUDDY_MAX_TRIES` 次）。若找不到按钮就按"今天已签到"处理并返回 0，
  绝不盲点，因此"没点到"不会再被误报成成功
- `python scripts\diagnose_workbuddy.py` 会截取真实 WorkBuddy 窗口并在配置坐标处画十字，
  **全程不点击**；签到失败或换屏后用它定位问题
- 重新校准坐标：把鼠标悬停在目标上，然后执行
  `python -c "import ctypes,ctypes.wintypes as w,time; u=ctypes.windll.user32; time.sleep(5); p=w.POINT(); u.GetCursorPos(ctypes.byref(p)); print(p.x, p.y)"`
  （用 `python` 而不是 PowerShell —— PowerShell 不感知 DPI，取到的坐标会被缩放）
- 首次使用需手动登录
- Trae 调试端口仅监听 127.0.0.1

### 第三方代码引用声明

本仓库收录以下两个开源项目。签到实现的所有功劳归上游作者所有；本项目原创部分仅为封装与调度层（`config.py`、`scripts/`、`*.bat`）。`trae-daily-checkin/` 带 3 处本地修复（等待 CDP page target、轮询账户 UI、让 `--close` 真正生效）；`workbuddy-checkin/` 带有少量本地补丁（点击坐标与签到流程开关均支持环境变量覆盖，从而可由 `config.py` 统一配置），详见 THIRD_PARTY_NOTICES.md。

| 目录 | 上游仓库 | 作者 | 许可证 |
| --- | --- | --- | --- |
| `trae-daily-checkin/` | [BlueChonk/trae-daily-checkin](https://github.com/BlueChonk/trae-daily-checkin) | Cecilia | MIT |
| `workbuddy-checkin/` | [GitOfUser/workbuddy-checkin](https://github.com/GitOfUser/workbuddy-checkin) | GitOfUser | 上游未提供许可证文件（版权归原作者所有） |

版本与提交信息、商标说明详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

---

## License / 许可证

本项目原创部分（封装与调度层）采用 MIT License。
收录的第三方代码版权归各自作者所有，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
