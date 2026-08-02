# 我用 Flask + OpenClaw 写了个 AI 电脑管家（开源）

> 一个 AI Agent 时代的「电脑管家」应该长什么样？

大家好，我是 YuzuDev，一个喜欢折腾 AI 工具的独立开发者。

最近 AI Agent 特别火——OpenClaw、Claude Code、各种 agent 框架层出不穷。但大部分 agent 都是「帮你在终端里干活」的，有没有一个 agent 是「帮你管电脑本身」的？

于是我写了一个：**ThresholdEcho（阈限回响）**——一个轻量级的 Windows AI 电脑管家，目前已在 GitHub 开源。

## 先看效果

体检 → 评分 → 一键修复，全流程：

```text
🏥 健康评分: 92 分 (A)
├── 磁盘空间  100/100  C盘已用 38% ✅
├── 安全防护  100/100  实时保护已开启 ✅
├── 开机启动  80/100   共 8 个启动项
├── 垃圾清理  85/100   可清理 1.2GB
├── 系统稳定性 100/100 24h 0 错误 ✅
└── CPU 负载  100/100  当前 12% ✅

✨ 可一键修复: 临时文件 890MB + 浏览器缓存 310MB
```

## 为什么叫「ThresholdEcho」？

名字源于「阈限空间」（Liminal Space）的意象——电脑管家应该站在「正常」与「异常」的边界，倾听系统发出的每一声回响。

（好吧，我承认这名字有点中二，但反正代码是开源的，名字你们随便吐槽 😂）

## 技术架构

```
┌─────────────────────────────────────┐
│  Web UI (index.html)                │
│  ┌─────────┐  ┌───────────────────┐ │
│  │ 仪表盘   │  │ AI 聊天控制台      │ │
│  └────┬────┘  └─────────┬─────────┘ │
│       └───────┬─────────┘           │
└───────────────┼─────────────────────┘
                ▼
        Flask 后端 (server.py)
        ├── /api/scan          扫描数据
        ├── /api/health-score  健康评分
        ├── /api/cleanup/*     垃圾清理
        └── /api/chat          AI 对话
                │
                ▼
        PowerShell 扫描引擎 (scan.ps1)
        ├── 硬件/存储/软件/USB
        ├── 进程/网络/安全
        └── 9 类垃圾扫描
```

**技术选型：**

| 层 | 技术 | 为什么 |
|:--|:--|:--|
| 后端 | Flask | 轻量、生态好、一个文件搞定 |
| 扫描引擎 | PowerShell | 原生调 Windows API，最快最全 |
| 桌面壳 | pywebview | 原生窗口，无浏览器 UI，打包后 55MB |
| AI 接入 | OpenClaw | 本地 Agent 框架，支持对话操控 |

## 核心功能

### 🏥 健康评分（6 维度）

磁盘、安全、启动、垃圾、稳定、CPU——加权平均出 0-100 分 + A-D 等级。每个维度都有具体的修复建议，不是「健康」两个字的空话。

### 🧹 垃圾清理（9 类）

临时文件、浏览器缓存、Windows 更新缓存、缩略图、日志、交付优化缓存、WER 报告……每个类别单独统计大小，勾选确认后才删。

### 🤖 AI 聊天控制台

内置 AI 助手，能直接对话操控：
- 「体检」→ 跑扫描 → 出报告
- 「帮我清垃圾」→ 预览 → 确认 → 执行
- 「C盘还有多少空间」→ 直接读缓存回答

## 踩过的坑

### 1. PowerShell 扫描慢

一开始用 `Get-ChildItem -Recurse` 扫大目录，慢到怀疑人生。换成 `cmd dir /s` 后快了 5-10 倍。经验：**Windows 上统计文件体积，cmd 的原生工具永远比 PowerShell cmdlet 快**。

### 2. 中英文环境差异

`dir /s` 的输出在中文系统是「个文件」，英文系统是「File(s)」。正则必须兼容两种，否则统计会崩。

### 3. 打包后路径找不到

PyInstaller 打包后 `__file__` 指向临时解压目录，模板和扫描脚本的路径全乱。解决：检测 `sys.frozen`，用 `sys._MEIPASS` 修正。

## 未来规划

- [ ] 点击进程 → Agent 解释（点击即问）
- [ ] 开机自检报告（每天登录自动推送）
- [ ] 智能垃圾溯源（告诉你「谁产生了这些垃圾」）
- [ ] 容量预测（预估几天后会爆盘）

详见 [docs/WORKFLOW.md](https://github.com/YZHin/ThresholdEcho/blob/main/docs/WORKFLOW.md)

## 开源地址

📦 **GitHub**: [github.com/YZHin/ThresholdEcho](https://github.com/YZHin/ThresholdEcho)

```bash
git clone https://github.com/YZHin/ThresholdEcho.git
cd ThresholdEcho/scripts/pc-manager
pip install flask pywebview
python desktop.py
```

如果对你有帮助，点个 ⭐ 就是对我最大的鼓励！

---

*题外话：作为一个高中生，课余时间写代码真的很快乐。如果你也是学生开发者，欢迎来交流，我们一起折腾有意思的东西。*

---

> 🏷️ #AI #开源 #电脑管家 #Flask #OpenClaw #Windows工具
