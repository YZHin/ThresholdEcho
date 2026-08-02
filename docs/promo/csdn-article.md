# Python 开发 AI 电脑管家：从扫描到清理的完整实践（附开源代码）

> 关键词：Python 电脑管家 / Flask 系统工具 / AI Agent 本地应用 / PowerShell 扫描优化

## 前言

很多人问：「AI 除了聊天还能做什么？」这篇文章用一个真实项目回答：**用 Python 写一个能体检、能清理、能陪你聊天的电脑管家**。

项目名 **ThresholdEcho**，已在 GitHub 开源（MIT 协议），欢迎 Star。

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

## 五、获取源码

📦 GitHub：https://github.com/YZHin/ThresholdEcho

```bash
git clone https://github.com/YZHin/ThresholdEcho.git
cd ThresholdEcho/scripts/pc-manager
pip install flask pywebview
python desktop.py
```

## 总结

这个项目证明了：**Python + PowerShell + AI Agent 的组合，完全能做出实用的桌面工具**。代码量不大（核心后端 580 行 + 扫描脚本 350 行），但功能覆盖了商用管家的主要场景。

如果你也在写类似的系统工具，欢迎交流。

> 🏷️ #Python #Flask #AI #开源 #电脑管家 #Windows开发
