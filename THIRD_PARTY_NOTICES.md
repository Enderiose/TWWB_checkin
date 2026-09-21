# 第三方代码引用声明 / Third-Party Notices

本仓库（`TWWB_checkin`）以**未修改的上游副本**形式收录了以下第三方项目。
本仓库仅提供封装与调度层（`config.py`、`scripts/`、`*.bat`、`README.md`）；
所有签到实现的功能、算法与技术路线的著作权归上游作者所有。

This repository vendors the following upstream projects as **unmodified copies**.
Only the wrapper/scheduling layer (`config.py`, `scripts/`, `*.bat`, `README.md`)
is original to this project. All copyright in the check-in implementations
belongs to the respective upstream authors.

---

## 1. trae-daily-checkin

| 项目 / Item | 内容 / Value |
| --- | --- |
| 收录目录 / Vendored path | `trae-daily-checkin/` |
| 上游仓库 / Upstream | https://github.com/BlueChonk/trae-daily-checkin |
| 作者 / Author | Cecilia（见 `trae-daily-checkin/package.json` 的 `author` 字段） |
| 版本 / Version | 1.0.0（`package.json`） |
| 许可证 / License | MIT |
| 本地是否修改 / Local modifications | 无（原样收录） |

### 用途 / Purpose

Trae SOLO CN 每日签到自动化。通过启动参数开启 Chromium 远程调试端口，
再经由 Chrome DevTools Protocol (CDP) 操控页面 DOM 完成签到点击。

本仓库引用入口：`config.py` 的 `TRAE_CHECKIN_SCRIPT`
→ `trae-daily-checkin/src/auto-checkin.mjs`（由 `scripts/auto_checkin.py` 调用）。

### 许可证原文 / License text

上游 `package.json` 声明 `"license": "MIT"`，但仓库内未附 `LICENSE` 文件。
如上游后续补充许可证文件，以该文件为准。

MIT License（摘要）

> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

---

## 2. workbuddy-checkin

| 项目 / Item | 内容 / Value |
| --- | --- |
| 收录目录 / Vendored path | `workbuddy-checkin/` |
| 上游仓库 / Upstream | https://github.com/GitOfUser/workbuddy-checkin |
| 作者 / Author | GitOfUser |
| 收录提交 / Vendored commit | `cb9f5e21a1fc447a59d16c1184dc671727058656`（`fix(scripts/checkin_py): adjust checkin mouse coordinates`） |
| 许可证 / License | 上游未提供许可证文件，版权归原作者所有（All rights reserved） |
| 本地是否修改 / Local modifications | 无（原样收录；仅生成运行时缓存 `scripts/__pycache__/`） |

### 用途 / Purpose

WorkBuddy 每日签到自动化。通过 Windows Win32 API（Python `ctypes` / PowerShell）
模拟鼠标点击完成签到，另附 Linux/macOS 的 Playwright/shell 实现。

本仓库引用入口：`config.py` 的 `WORKBUDDY_CHECKIN_SCRIPT`
→ `workbuddy-checkin/scripts/checkin_py.py`（由 `scripts/auto_checkin.py` 调用）。

### 使用注意 / Usage notes

上游仓库未声明开源许可证，因此在未获得作者授权前：

- 请勿再分发、商用或以其名义发布衍生版本；
- 本仓库仅作个人本地使用的原样收录；
- 如需引用或分发，请先联系上游作者获取授权。

The upstream repository provides **no license file**. Until the author grants a
license, do **not** redistribute or use this code commercially. It is vendored
here for personal, local use only. Contact the upstream author for permission.

---

## 免责声明 / Disclaimer

- 本项目及其引用的第三方代码均为非官方的个人自动化脚本，与 Trae SOLO CN、WorkBuddy
  各自的开发/运营方无任何隶属或背书关系。
- 商标、产品名称（Trae、SOLO CN、WorkBuddy 等）归其各自所有者所有，仅用于说明用途。
- 自动化点击可能违反相关服务条款，使用者需自行承担风险。