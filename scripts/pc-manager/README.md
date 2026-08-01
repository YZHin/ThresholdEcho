# ThresholdEcho

> 轻量级 Windows AI 电脑管家

[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.8%2B-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](#license)

**不弹窗、不捆绑、不偷数据**的开源电脑管家。结合 OpenClaw AI 框架，支持语音/对话/桌面三种操控方式。

---

## ✨ 功能

| 模块 | 说明 |
|:--|:--|
| 📊 **仪表盘** | CPU/内存/硬盘/GPU 实时概览 |
| 🏥 **一键体检** | 6 维度健康评分 + 问题分级（严重/建议/良好） |
| ✨ **一键修复** | 体检联动，自动清理临时文件/回收站/浏览器缓存 |
| 🧹 **垃圾清理** | 9 类垃圾扫描（临时文件/浏览器缓存/Win更新/日志等） |
| 🤖 **AI 聊天** | 内置 AI 助手，可对话操控管家、分析系统数据 |
| ⚙️ **进程管理** | TOP 15 内存进程 + 结束进程（需确认） |
| 🛡️ **安全中心** | Defender 状态/防火墙/最近威胁 |
| 📦 **软件清单** | 已安装软件列表 + 启动项管理 |

## 🚀 使用方式

### 方式一：独立桌面应用

```powershell
# 打包好的 exe（推荐）
.\dist\PC-Manager.exe

# 或从源码运行（需 pywebview）
pip install pywebview
python desktop.py
```

### 方式二：AI 对话操控（推荐）

PC Manager 兼容 [OpenClaw](https://github.com/openclaw) AI 框架：

```yaml
# 在 OpenClaw 聊天中
"体检"         → 跑扫描，显示健康评分
"清理垃圾"     → 预览 → 确认 → 执行
"C盘还有多少"  → 读缓存直接答
```

方式：把 `scripts/pc-manager/` 复制到 OpenClaw workspace 下的 `scripts/pc-manager/`。

### 方式三：Web 控制台（调试用）

```powershell
python server.py
# 浏览器打开 http://127.0.0.1:5000
```

## 📦 AI 聊天集成

PC Manager 内置聊天面板通过 `openclaw agent` CLI 与 OpenClaw 通信：

```
用户消息 → Flask /api/chat → openclaw agent --session-key ... → AI 回复
```

**前提：** 已安装 [OpenClaw](https://docs.openclaw.ai/start/quickstart)。无需额外配置，PC Manager 自动检测 Gateway。

## 🛡️ 安全设计

- 所有网络通信仅绑定 `127.0.0.1`（外网不可达）
- 破坏性操作（清理/结束进程）需用户弹窗确认
- 不收集用户数据，不连接任何远程服务器
- AI 对话走本地 OpenClaw Gateway，不上传数据

## 🏗️ 构建

```powershell
# 单文件 exe
pyinstaller --onefile --windowed --name "PC-Manager" \
  --add-data "templates;templates" \
  --add-data "scan.ps1;." \
  --hidden-import flask --hidden-import webview \
  desktop.py
```

## 📂 项目结构

```
scripts/pc-manager/
├── scan.ps1              # PowerShell 扫描引擎
├── server.py             # Flask 后端
├── desktop.py            # 桌面窗口入口
├── canvas_dashboard.py   # Canvas 仪表盘生成器
├── templates/
│   └── index.html        # 前端面板
└── dist/
    └── PC-Manager.exe    # 构建产物
```

## 📝 License

MIT
