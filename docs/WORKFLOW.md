# 🗺️ OpenClaw PC Manager — 长期工作流总控

> 最后更新：2026-08-01 · 当前阶段：Phase 4 待启动
> 
> ⚠️ **阻塞项**：等待 Hin 宝给出最终 GitHub 仓库命名方案

---

## 📋 三阶段总览

```
Phase 4 (2026-08 第1-2周)    Phase 5 (第3-4周)          Phase 6 (第5周起)
┌──────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
│ 🥇 点击进程→Agent解释  │  │ 🥈 智能垃圾溯源          │  │ 🥉 异常行为时序分析      │
│ 🥇 开机自检报告        │  │ 🥈 容量预测+趋势         │  │ 🥉 根因推理引擎          │
│ 🥇 点击软件→Agent解释  │  │ 🥈 安全周报自动化         │  │ 🥉 崩溃自动诊断          │
│ 🥇 游戏/场景联动       │  │ 🥈 软件安装顾问          │  │ 🥉 知识库自学习          │
│                      │  │                        │  │ 🥉 服务依赖图分析        │
└──────────────────────┘  └────────────────────────┘  └────────────────────────┘
```

## 🔧 当前任务状态

| # | 任务 | 阶段 | 状态 | 负责人 |
|:--:|:--|:--:|:--:|:--:|
| 1 | Agent API 中间层 `/api/agent/explain-*` | Phase 4 | ⬜ 未开始 | 🤖 |
| 2 | 前端「点击即问」UI（气泡组件） | Phase 4 | ⬜ 未开始 | 🤖 |
| 3 | 点击进程 → Agent 解释 | Phase 4 | ⬜ 未开始 | 🤖 |
| 4 | 开机自检报告 | Phase 4 | ⬜ 未开始 | 🤖 |
| 5 | 点击软件 → Agent 解释 | Phase 4 | ⬜ 未开始 | 🤖 |
| 6 | 游戏模式联动 | Phase 4 | ⬜ 未开始 | 🤖 |
| 7 | GitHub 仓库创建 + 初始 push | 基础建设 | ⏸️ 阻塞（等命名） | 👤 Hin |
| 8 | GitHub Actions CI（PyInstaller 自动打包） | 基础建设 | ⬜ 未开始 | 🤖 |
| 9 | ClawHub 发布技能包 | 基础建设 | ⬜ 未开始 | 🤖 |
| 10 | 智能垃圾溯源 | Phase 5 | ⬜ 未开始 | 🤖 |
| 11 | 容量预测 + 趋势分析 | Phase 5 | ⬜ 未开始 | 🤖 |
| 12 | 安全周报自动化 | Phase 5 | ⬜ 未开始 | 🤖 |

## ⏰ 自动化任务（Cron）

| Cron 名称 | 频率 | 用途 | 状态 |
|:--|:--|:--|:--:|
| `midnight-self-optimize` | 每天 00:00 | 自优化记忆压缩 | ✅ 启用 |
| `kkrb-daily-report` | 每天 15:00 | KKRB 日报 | ✅ 启用 |
| `daily-balance-check` | 每天 17:00 | DeepSeek 额度检查 | ✅ 启用 |
| `bilibili-archive` | 每天 19:05 | B站热梗归档 | ✅ 启用 |
| `bilibili-study` | 每天 19:00 | B站热梗学习 | ✅ 启用 |
| `pc-manager-phase4-daily-review` | 每天 10:00 | Phase 4 每日进度追踪 | ⏸️ 待启用 |
| `pc-manager-weekly-security-report` | 每周一 09:00 | PC安全周报 | ⏸️ 待启用 |

## 🐙 GitHub 准备清单

- [x] 本地 git init + 初始 commit（54 files, 6913 lines）
- [x] `.gitignore` 配置（排除 secrets/memory/binaries）
- [x] GitHub Skills 安装（github-api-tool + github-cli-tool）
- [x] GITHUB_TOKEN 已配置（环境变量 `github_pat_...`）
- [x] GitHub Desktop 已安装
- [ ] **⏸️ 等 Hin 宝给仓库名** → 创建 GitHub repo + push
- [ ] 创建 `README.md`（展示用）
- [ ] 设置 GitHub Actions CI（自动 PyInstaller 打包 `.exe`）
- [ ] 打 Release tag + 发布 v2.0 版本
- [ ] 发布到 ClawHub 中文镜像站

## 🔑 技术路线（Phase 4 核心）

### 数据流
```
PC Manager UI 点击 
    → POST /api/agent/explain-{type} 
    → server.py 收集上下文数据 + 拼 Agent prompt
    → openclaw agent CLI 推理
    → 自然语言结果 
    → 前端气泡组件渲染
```

### 新增文件
| 文件 | 用途 |
|:--|:--|
| `server.py` 新增 | `/api/agent/explain-*` 端点（8个） |
| `server.py` 新增 | `call_agent()` 通用 Agent 调用函数 |
| `index.html` 新增 | 可点击气泡组件 CSS/JS |
| `index.html` 修改 | 表格行加 `data-*` 属性 + `onclick` 绑定 |

### 后端新增端点
| 端点 | 输入 | 输出 |
|:--|:--|:--|
| `POST /api/agent/explain-process` | `{pid, name, cpu, memory}` | Agent 自然语言回复 |
| `POST /api/agent/explain-software` | `{name, version, install_date}` | Agent 自然语言回复 |
| `POST /api/agent/explain-startup` | `{name, command, impact}` | Agent 自然语言回复 |
| `POST /api/agent/explain-device` | `{name, driver_ver}` | Agent 自然语言回复 |
| `POST /api/agent/startup-report` | 自动触发 | 开机自检报告 |

---

## 📝 变更日志

| 日期 | 变更 |
|:--|:--|
| 2026-08-01 | 初始工作流文档创建；git repo 初始化（54 files）；GitHub Skills 安装 |
| 2026-08-01 | 📊 Excel 分析文档完成（20场景 + API设计 + 路线图） |
