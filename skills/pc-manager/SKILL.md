---
name: pc-manager
description: ThresholdEcho — 阈限回响。二次元×后室的 AI 电脑守护者，扫描/体检/清理/进程管理/一键修复。
metadata: { "openclaw": { "emoji": "🌫️" } }
---

# ThresholdEcho — 阈限回响

## 安装

### 方式一：ClawHub（推荐）
```
openclaw skill install pc-manager
```

### 方式二：手动安装
把本项目 `skills/pc-manager/` 复制到 OpenClaw 的 skills 目录：
```powershell
# Windows
cp -Recurse skills/pc-manager $env:USERPROFILE\.openclaw\skills\pc-manager

# macOS / Linux
cp -r skills/pc-manager ~/.openclaw/skills/pc-manager
```

### 方式三：独立桌面应用（无需 OpenClaw）
```powershell
python scripts/pc-manager/desktop.py
# 或直接双击 dist/PC-Manager.exe
```

## 概述
本地电脑管家技能。AI 可直接调用脚本完成诊断/巡检/优化，结果渲染在 OpenClaw Canvas 或对话中。
**破坏性操作一律需用户确认。**

## 脚本路径

> 所有脚本路径相对于 workspace 根目录。安装 skill 后 `{workspace}/scripts/pc-manager/` 即包含以下文件。

| 文件 | 路径 | 用途 |
|:--|:--|:--|
| scan.ps1 | `scripts/pc-manager/scan.ps1` | 全量扫描引擎 |
| canvas_dashboard.py | `scripts/pc-manager/canvas_dashboard.py` | Canvas 仪表盘生成 |
| server.py | `scripts/pc-manager/server.py` | Web 控制台（可选） |
| desktop.py | `scripts/pc-manager/desktop.py` | 桌面窗口（可选） |

## 启动方式

### 🤖 对话操作（推荐 / OpenClaw 原生）
直接在聊天中指挥 AI 助手，无需端口/窗口/浏览器：
```
"体检"            → 跑快速扫描 → 评分 + 建议 + Canvas 看板
"帮我清垃圾"       → 预览 → 确认 → 执行
"C盘还有多少空间"  → 读缓存直接答
"内存占用多少"     → 分析进程列表
```

### 🖥️ 桌面应用（可选）
```powershell
# 原生窗口（需 pywebview：pip install pywebview）
python scripts/pc-manager/desktop.py

# 打包好的 exe
scripts\pc-manager\dist\PC-Manager.exe
```

### 📡 命令行扫描
```powershell
# 快速扫描（10s）
powershell -File scripts/pc-manager/scan.ps1 -SkipJunk

# 完整扫描（含垃圾扫描）
powershell -File scripts/pc-manager/scan.ps1

# 生成 Canvas 仪表盘
python scripts/pc-manager/canvas_dashboard.py
```

## AI 标准工作流

### 体检流程
```
1. 用户说"体检"或"扫描"
2. AI 执行: powershell -File scan.ps1 -SkipJunk
3. AI 执行: python canvas_dashboard.py
4. AI 读 JSON 分析数据 → 先文字总结评分 + 关键发现
5. 展示 Canvas: [embed ref="pc-manager-dashboard" title="PC Manager" height="720"]
6. 如有可修复项，询问用户是否一键修复
```

### 垃圾清理流程
```
1. 用户说"清垃圾"
2. AI 执行: powershell -File scan.ps1（完整扫描）
3. AI 执行: python canvas_dashboard.py（更新 Canvas）
4. AI 告知可清理总量 + 分类明细
5. 用户确认后 → python server.py 的 cleanup API 或直接用 PowerShell 清理
```

## 功能清单

| 功能 | 指令 | 安全 |
|:--|:--|:--:|
| 全量扫描 | `scan` 或 "体检" | ✅ 只读 |
| Canvas 看板 | `canvas` 或生成仪表盘 | ✅ 只读 |
| 垃圾预览 | "看看有什么垃圾" | ✅ 只读 |
| 清理垃圾 | "清理垃圾" | ⚠️ 需确认 |
| 硬件查询 | cpu / gpu / memory | ✅ 只读 |
| 软件清单 | "装了哪些软件" | ✅ 只读 |
| 进程管理 | "在跑什么" | ✅ 只读 |
| 结束进程 | "杀掉 xxx" | ⚠️ 必须确认 |

## 安全约束

### ⚠️ 必须确认
- 清理/删除操作
- 结束进程
- 触发 Defender 扫描

### ✅ 可自主执行
- 所有只读查询
- 预览统计
- 生成 Canvas 看板

## 依赖
- **PowerShell**: 5.1+（Windows 自带）
- **Python 3.8+**: 仅 Canvas 生成需要
- **权限**: 扫描可不管理员，Defender 详细数据需管理员

## 维护者
OpenClaw PC Manager · v2 · 2026-08-01
