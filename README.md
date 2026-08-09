# 🌫️ ThresholdEcho

> 轻量级 Windows AI 电脑管家

> 🎒 *Built by a high school student with 💜 — 一个高中生的 AI 管家梦*

[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)](https://github.com/YZHin/ThresholdEcho)
[![Python](https://img.shields.io/badge/python-3.8%2B-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
[![Release](https://img.shields.io/badge/release-v2.0-a371f7)](https://github.com/YZHin/ThresholdEcho/releases)

---

## ✨ 功能

| 模块 | 说明 |
|:--|:--|
| 📊 **仪表盘** | CPU / 内存 / 硬盘 / GPU 实时概览 |
| 🏥 **一键体检** | 6 维度健康评分 + 问题分级（严重/建议/良好） |
| ✨ **一键修复** | 体检联动，自动清理临时文件/回收站/浏览器缓存 |
| 🧹 **垃圾清理** | 9 类垃圾扫描（临时文件/浏览器缓存/Win更新/日志等） |
| 🤖 **AI 聊天** | 内置 AI 助手，可对话操控管家、分析系统数据 |
| ⚙️ **进程管理** | TOP 15 内存进程 + 结束进程 |
| 🛡️ **安全中心** | Defender 状态 / 防火墙 / 最近威胁 |
| 📦 **软件清单** | 已安装软件列表 + 启动项管理 |

## 🎬 功能演示

![ThresholdEcho 演示](scripts/pc-manager/docs/te_demo.gif)

*仪表盘 · 一键体检 · 垃圾清理 · AI 控制台*

## 🚀 快速开始

### 桌面应用

```powershell
# 安装依赖
pip install flask pywebview

# 启动
python scripts/pc-manager/desktop.py
```

### 命令行扫描

```powershell
# 快速扫描（~10s）
powershell -File scripts/pc-manager/scan.ps1 -SkipJunk

# 完整扫描（含垃圾）
powershell -File scripts/pc-manager/scan.ps1
```

### 打包为 exe

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "templates;templates" scripts/pc-manager/desktop.py
```

## 🏗️ 项目结构

```
ThresholdEcho/
├── scripts/pc-manager/
│   ├── server.py              # Flask 后端
│   ├── desktop.py             # 桌面窗口入口
│   ├── scan.ps1               # 扫描引擎
│   ├── canvas_dashboard.py    # Canvas 仪表盘
│   ├── templates/
│   │   └── index.html         # Web 控制台
│   └── README.md
├── skills/pc-manager/
│   └── SKILL.md               # OpenClaw Skill 定义
└── docs/
    ├── pc-manager-agent-integration.md   # Agent 联动设计
    └── WORKFLOW.md                      # 长期工作流
```

## 🔮 路线图

- [x] v2.0 — 健康评分 + 垃圾清理 + 一键修复 + AI 聊天
- [ ] Phase 4 — 点击即问（进程/软件→Agent 解释）+ 开机自检
- [ ] Phase 5 — 智能垃圾溯源 + 容量预测 + 安全周报
- [ ] Phase 6 — 异常检测 + 根因推理 + 崩溃诊断

详见 `docs/WORKFLOW.md`

## 📄 许可

MIT License — 详见 [LICENSE](scripts/pc-manager/LICENSE)

---

<p align="center">
  <sub>🌫️ ThresholdEcho</sub>
</p>
