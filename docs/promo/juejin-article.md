# 装一个管家软件送你三个全家桶，我干脆自己写了个 AI 电脑管家（开源）

这软件是我 7 月底开始写的，断断续续写到现在，快两个星期了。正好赶上放暑假，白天不用上课，就多写了一点。

起因是想给电脑找个清理工具。结果装了几个"电脑管家"，一个比一个离谱：开机弹窗、广告推送，卸载的时候还跟你玩捉迷藏，装一个顺手送你三个"兄弟软件"。删都删不干净。

我寻思这些东西的功能我也不是不会写，干脆自己搞一个，至少不恶心自己。于是就有了 ThresholdEcho。

## 目前长这样

打开是一个体检报告页，磁盘、安全、启动项、垃圾、稳定性、CPU 六项打分：

```text
🏥 健康评分: 92 分 (A)
├── 磁盘空间  100/100  C盘已用 38% ✅
├── 安全防护  100/100  实时保护已开启 ✅
├── 开机启动  80/100   共 8 个启动项
├── 垃圾清理  85/100   可清理 1.2GB
├── 系统稳定性 100/100 24h 0 错误 ✅
└── CPU 负载  100/100  当前 12% ✅
```

垃圾清理有 9 类：临时文件、浏览器缓存、Windows 更新缓存、缩略图、日志。每类单独统计大小，勾选确认才删，不会上来就咔咔给你清。

AI 对话是后加的。最开始只有扫描和清理，后来把 OpenClaw 接进去，就能直接说"帮我清垃圾""C盘还有多少空间"。再后来加了点击即问——点一下进程名，它告诉你这是什么、安不安全、能不能结束。

对了，它还认得 Edge、Chrome、Firefox 的缓存，能直接清理；Windows Defender 的状态也能读到。数据都在本机。

## 技术栈没什么好说的

Flask 后端，PowerShell 扫描，pywebview 桌面壳，OpenClaw 做 AI。

选型思路就一个：怎么省事怎么来。毕竟白天还要上课，没时间研究那些花里胡哨的。比如扫描引擎，一开始想用 Python 的 psutil，后来发现 Windows 上很多信息还是调系统命令最直接，干脆全用 PowerShell 写，Python 只负责起服务。

## 坑倒是踩了不少

**1. PowerShell 扫描慢到怀疑人生**

一开始 `Get-ChildItem -Recurse` 扫大目录，慢得离谱。换成 `cmd dir /s`，快了 5-10 倍。Windows 上统计文件体积，cmd 的原生工具永远比 PowerShell cmdlet 快，这是真话。

**2. 中英文系统的正则地狱**

`dir /s` 的输出，中文系统是"个文件"，英文系统是"File(s)"。正则不兼容两种就崩，我一开始就踩了这个坑。

**3. PyInstaller 打包路径全乱**

打包后 `__file__` 指向临时解压目录，模板和扫描脚本的路径全找不到。解决方法是检测 `sys.frozen`，用 `sys._MEIPASS` 修正。

**4. CLI 子进程输出混进启动 banner**

调 OpenClaw 的时候，stdout 会混入启动日志，JSON 直接解析崩。最后是把输出重定向到文件再读，才干净。

## 接下来想做的

开机自检报告、智能垃圾溯源（告诉你"谁产生了这些垃圾"）、容量预测（预估几天后会爆盘）。

立几个 flag，做不做得到另说。

## 开源地址

GitHub: [github.com/YZHin/ThresholdEcho](https://github.com/YZHin/ThresholdEcho)

```bash
git clone https://github.com/YZHin/ThresholdEcho.git
cd ThresholdEcho/scripts/pc-manager
pip install flask pywebview
python desktop.py
```

有啥问题欢迎提 Issue，有建议也欢迎唠。开学之后更新可能就慢了，提前说一声哈。
