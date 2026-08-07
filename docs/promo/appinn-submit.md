# ThresholdEcho — 轻量级 Windows AI 电脑管家（开源）

**一句话**：最适合开发者的电脑管家——轻量、无捆绑、无广告，体检/清理/进程管理全都有，还和常用软件有机联动，能聊天操控。

## 这是什么

ThresholdEcho 是一个开源的 Windows 电脑管家，基于 Flask + PowerShell + OpenClaw 构建。它有传统管家的所有功能（体检评分、垃圾清理、进程管理、安全中心），但多了一个 AI 核心——内置聊天控制台，直接对话就能操控电脑。

**和传统管家的区别：**

- 🪶 **轻量化**：单文件免安装，打包后约 58MB，无后台驻留、无常驻服务，不拖慢电脑
- 🚫 **无捆绑无广告**：不弹窗、不推广、不捆绑全家桶，MIT 开源可审计
- 🔗 **有机联动**：内置 OpenClaw Agent 对话操控；Edge / Chrome / Firefox 缓存联动清理；联动 Windows Defender 安全中心
- 🧑‍💻 **开发者向**：本地优先、数据不出本机，接口开放，随 fork 随改

## 特点

- 🏥 **一键体检**：6 维度健康评分（磁盘/安全/启动/垃圾/稳定/CPU），0-100 分 + A-D 等级
- 🧹 **垃圾清理**：9 类垃圾（临时文件/浏览器缓存/Win更新/日志等），分类预览，确认才删
- 🤖 **AI 对话操控**：「体检」「清垃圾」「C盘多大」——说话就行
- 🔗 **常用软件联动**：Edge / Chrome / Firefox 缓存一键清，OpenClaw Agent 直连操控
- 🔒 **本地优先**：数据不出本机，不弹窗、不捆绑、不偷数据
- 🖥️ **桌面应用**：打包后单文件约 58MB，免安装直接跑

## 运行截图

（这里放 2-3 张截图：仪表盘、体检报告、清理页面）

## 怎么用

```powershell
# 方式一：直接跑源码
git clone https://github.com/YZHin/ThresholdEcho.git
cd ThresholdEcho/scripts/pc-manager
pip install flask pywebview
python desktop.py

# 方式二：用打包好的 exe（见 GitHub Releases）
```

## 开源地址

https://github.com/YZHin/ThresholdEcho

MIT 协议，完全免费。独立开发者课余作品，求轻喷 😂 有 bug 欢迎提 Issue。
