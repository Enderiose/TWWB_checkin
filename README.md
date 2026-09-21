# TWWB_check / 自动化签到工具

[English](#English) · [简体中文](#简体中文)

---

<a id="English"></a>

## English

Automatically complete daily check-in for Trae SOLO CN and WorkBuddy.

### Features

- **Dual Program Support**: Trae SOLO CN + WorkBuddy
- **Auto Start on Boot**: Execute on Windows user logon
- **Detailed Logging**: Timestamp and status for each operation
- **Easy Configuration**: Modify paths in `config.py`

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

#### 3. Test Check-in
```cmd
python scripts\auto_checkin.py
```

### Project Structure

```
auto_sign/
├── config.py                  # Configuration
├── scripts/
│   ├── auto_checkin.py        # Main check-in script
│   ├── test_paths.py          # Path validation
│   └── full_test.py           # System test
├── trae-daily-checkin/        # Trae library (3rd-party, see THIRD_PARTY_NOTICES.md)
├── workbuddy-checkin/         # WorkBuddy library (3rd-party, see THIRD_PARTY_NOTICES.md)
├── install_startup_task.bat   # Install task
├── uninstall_startup_task.bat # Uninstall task
├── test_checkin.bat           # Test check-in
└── info.bat                   # Show info
```

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
| `python scripts\auto_checkin.py` | Manual check-in |
| `python scripts\full_test.py` | System test |
| `install_startup_task.bat` | Install task |
| `uninstall_startup_task.bat` | Uninstall task |

### Troubleshooting

1. **Path error**: Edit `config.py`
2. **Check-in failed**: Ensure apps are logged in
3. **Task not running**: Check Python/Node.js in PATH

### Technical Details

- **Trae**: Chrome DevTools Protocol (CDP) + Node.js
- **WorkBuddy**: Win32 API (ctypes) + Python

### Notes

- WorkBuddy coordinates optimized for 1920x1080
- First use requires manual login
- Trae debug port only listens on 127.0.0.1

### Third-Party Code and Attribution

This repository vendors two upstream projects as **unmodified copies**. All credit for the check-in implementations belongs to their authors; only the wrapper/scheduling layer (`config.py`, `scripts/`, `*.bat`) is original to this project.

| Directory | Upstream repository | Author | License |
| --- | --- | --- | --- |
| `trae-daily-checkin/` | [BlueChonk/trae-daily-checkin](https://github.com/BlueChonk/trae-daily-checkin) | Cecilia | MIT |
| `workbuddy-checkin/` | [GitOfUser/workbuddy-checkin](https://github.com/GitOfUser/workbuddy-checkin) | GitOfUser | Upstream provides no license file (all rights reserved by the author) |

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for version/commit details and trademark notes.

---

<a id="简体中文"></a>

## 简体中文

自动完成 Trae SOLO CN 和 WorkBuddy 的每日签到。

### 功能特点

- **双程序签到**：同时支持 Trae SOLO CN 和 WorkBuddy
- **开机自启**：用户登录后自动执行
- **详细日志**：记录签到过程和结果
- **易于配置**：修改 `config.py` 即可

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

#### 3. 测试签到
```cmd
python scripts\auto_checkin.py
```

### 项目结构

```
auto_sign/
├── config.py                  # 配置文件
├── scripts/
│   ├── auto_checkin.py        # 主签到脚本
│   ├── test_paths.py          # 路径验证
│   └── full_test.py           # 系统测试
├── trae-daily-checkin/        # Trae 库（第三方，见 THIRD_PARTY_NOTICES.md）
├── workbuddy-checkin/         # WorkBuddy 库（第三方，见 THIRD_PARTY_NOTICES.md）
├── install_startup_task.bat   # 安装任务
├── uninstall_startup_task.bat # 卸载任务
├── test_checkin.bat           # 测试签到
└── info.bat                   # 显示信息
```

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
| `python scripts\auto_checkin.py` | 手动签到 |
| `python scripts\full_test.py` | 系统测试 |
| `install_startup_task.bat` | 安装任务 |
| `uninstall_startup_task.bat` | 卸载任务 |

### 故障排除

1. **路径错误**：编辑 `config.py`
2. **签到失败**：确保应用已登录
3. **任务不执行**：检查 Python/Node.js 在 PATH 中

### 技术细节

- **Trae**：Chrome DevTools Protocol (CDP) + Node.js
- **WorkBuddy**：Win32 API (ctypes) + Python

### 注意事项

- WorkBuddy 坐标针对 1920x1080 优化
- 首次使用需手动登录
- Trae 调试端口仅监听 127.0.0.1

### 第三方代码引用声明

本仓库以**未修改的上游副本**形式收录以下两个开源项目。签到实现的所有功劳归上游作者所有；本项目原创部分仅为封装与调度层（`config.py`、`scripts/`、`*.bat`）。

| 目录 | 上游仓库 | 作者 | 许可证 |
| --- | --- | --- | --- |
| `trae-daily-checkin/` | [BlueChonk/trae-daily-checkin](https://github.com/BlueChonk/trae-daily-checkin) | Cecilia | MIT |
| `workbuddy-checkin/` | [GitOfUser/workbuddy-checkin](https://github.com/GitOfUser/workbuddy-checkin) | GitOfUser | 上游未提供许可证文件（版权归原作者所有） |

版本与提交信息、商标说明详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

---

## License / 许可证

本项目原创部分（封装与调度层）采用 MIT License。
收录的第三方代码版权归各自作者所有，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
