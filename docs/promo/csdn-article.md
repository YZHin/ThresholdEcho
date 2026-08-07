# Python 开发 AI 电脑管家：从扫描到清理的完整实践（附开源代码）

> 关键词：Python 电脑管家 / Flask 系统工具 / AI Agent 本地应用 / PowerShell 扫描优化

## 前言

很多人问：「AI 除了聊天还能做什么？」这篇文章用一个真实项目回答：**用 Python 写一个能体检、能清理、能陪你聊天的电脑管家**。

项目名 **ThresholdEcho**，已在 GitHub 开源（MIT 协议），欢迎 Star。它主打 **轻量化 + 无捆绑无广告**：单文件免安装、无后台驻留、不弹窗不推广，同时与常用软件有机联动——Edge / Chrome / Firefox 缓存一键清理、联动 Windows Defender 安全中心、内置 OpenClaw Agent 对话操控电脑，是适合开发者的电脑管家。

## 一、整体架构

```
Web UI (HTML/JS)
    ↓
Flask 后端 (Python)
    ├── 扫描数据 API
    ├── 健康评分 API
    ├── 清理操作 API
    └── AI 对话 API
    ↓
PowerShell 扫描引擎
    └── 硬件/软件/进程/垃圾 9 类
```

## 二、核心实现

### 1. PowerShell 扫描引擎

```powershell
# 快速扫描（跳过垃圾）
param([switch]$SkipJunk, [string]$Output)

$result = @{
    hardware = Get-HardwareInfo
    storage  = Get-StorageInfo
    software = Get-SoftwareInfo
    system   = Get-SystemInfo
}

if (-not $SkipJunk) {
    $result.junk = Get-JunkInfo  # 9 类垃圾
}

$result | ConvertTo-Json -Depth 5 | Set-Content $Output -Encoding UTF8
```

### 2. 健康评分算法

6 个维度加权平均：

| 维度 | 权重 | 评分逻辑 |
|:--|:--|:--|
| 磁盘空间 | 25 | 使用率 <50% → 100 分 |
| 安全防护 | 25 | Defender 实时保护状态 |
| 垃圾文件 | 20 | 可清理体积 <1GB → 100 分 |
| 开机启动 | 10 | 启动项 <5 个 → 100 分 |
| 系统稳定性 | 10 | 24h 事件日志错误数 |
| CPU 负载 | 10 | 当前占用率 |

```python
overall = round(weighted_sum / total_weight)
grade = "A" if overall >= 90 else "B" if overall >= 75 else "C" if overall >= 60 else "D"
```

### 3. AI 对话接入

通过 OpenClaw 的 agent CLI 实现本地 AI 对话，支持自然语言操控：

```python
def _chat_via_cli(messages):
    oc = os.path.expandvars(r"%APPDATA%\npm\openclaw.cmd")
    r = subprocess.run(
        [oc, "agent", "--session-key", "agent:main:pc-manager",
         "--message", user_msg, "--json", "--timeout", "120"],
        capture_output=True, text=True, timeout=150
    )
    return json.loads(r.stdout)
```

## 三、踩坑记录

### 坑 1：`Get-ChildItem -Recurse` 太慢
扫一个 500GB 的磁盘要十几分钟。换成 `cmd /c dir /s` 只要 2-3 分钟。**Windows 文件统计用 cmd，不要用 PowerShell cmdlet。**

### 坑 2：中英文 locale 差异
`dir /s` 中文输出「个文件」，英文输出「File(s)」。正则要兼容：

```powershell
if ($line -match '(\d+)\s*个文件' -or $line -match '(\d+)\s*File\(s\)') {
    $count = $Matches[1]
}
```

### 坑 3：PyInstaller 打包路径
`--onefile` 模式下 `__file__` 指向 `_MEIPASS` 临时目录，模板和脚本路径要动态判断：

```python
if getattr(sys, 'frozen', False):
    BUNDLE_DIR = Path(sys._MEIPASS)
    app = Flask(__name__, template_folder=str(BUNDLE_DIR / "templates"))
```

## 四、效果展示

体检报告（6 维度评分 + 一键修复）：
- 清理临时文件 + 浏览器缓存 + 回收站，一次释放 2-3GB
- AI 对话：「帮我清垃圾」→ 自动预览 → 确认执行
- 点击任意进程/软件 → AI 气泡解释「是什么、安不安全、能不能动」

## 五、为什么适合开发者

1. **轻量无负担**：单文件约 58MB，无后台驻留，不占用开发机资源
2. **无捆绑无广告**：不开机弹窗、不全家桶，MIT 开源可审计
3. **AI 原生联动**：OpenClaw Agent 直连，对话就能操控电脑，支持点击即问
4. **本地优先**：数据不出本机，适合有隐私洁癖的开发者

## 六、获取源码

📦 GitHub：https://github.com/YZHin/ThresholdEcho

```bash
git clone https://github.com/YZHin/ThresholdEcho.git
cd ThresholdEcho/scripts/pc-manager
pip install flask pywebview
python desktop.py
```

## 总结

这个项目证明了：**Python + PowerShell + AI Agent 的组合，完全能做出实用的桌面工具**。代码量不大（核心后端 580 行 + 扫描脚本 350 行），但功能覆盖了商用管家的主要场景——还额外做到了轻量、无捆绑、无广告，与常用软件有机联动。

如果你也在写类似的系统工具，欢迎交流。

> 🏷️ #Python #Flask #AI #开源 #电脑管家 #Windows开发
