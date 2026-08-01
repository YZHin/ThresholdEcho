"""
 ThresholdEcho Console — Flask 后端
 启动: python server.py [--port 5000]
 绑定: 127.0.0.1 仅本地访问
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request

# ── 路径 & 配置 ──────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
CREATE_NO_WINDOW = 0x08000000  # 子进程不弹终端窗口

# PyInstaller 打包后路径修正
if getattr(sys, 'frozen', False):
    BUNDLE_DIR = Path(sys._MEIPASS)
    # 模板和静态资源在打包目录
    app = Flask(__name__, template_folder=str(BUNDLE_DIR / "templates"))
    SCAN_SCRIPT = BUNDLE_DIR / "scan.ps1"
    # 扫描结果写到用户临时目录（exe 内不可写）
    SCAN_OUTPUT = Path(os.environ.get("TEMP", ".")) / "pc-manager-scan.json"
else:
    app = Flask(__name__)
    SCAN_SCRIPT = SCRIPT_DIR / "scan.ps1"
    SCAN_OUTPUT = SCRIPT_DIR / "scan-result.json"

# ── OpenClaw Gateway 配置 ──────────────────────────────
def _load_gateway_config():
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if config_path.exists():
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
        return {
            "token": cfg.get("gateway", {}).get("auth", {}).get("token", ""),
            "port": cfg.get("gateway", {}).get("port", 18789),
        }
    return {"token": "", "port": 18789}

GATEWAY = _load_gateway_config()

# ── 缓存 ──────────────────────────────────────────────────
_cache = {"data": None, "ts": 0.0}


def run_scan(force: bool = False) -> dict:
    """读取扫描数据：优先缓存文件，force=True 快速刷新（跳过垃圾扫描）"""
    # ── 有缓存文件直接读（秒开）────────────────────
    if not force and SCAN_OUTPUT.exists():
        try:
            data = json.loads(SCAN_OUTPUT.read_text(encoding="utf-8-sig"))
            _cache["data"] = data
            _cache["ts"] = time.time()
            return data
        except Exception:
            pass  # 缓存坏了就重新扫

    # ── 刷新时跳过垃圾扫描，秒级完成 ────────────────
    try:
        cmd = ["powershell", "-File", str(SCAN_SCRIPT), "-Output", str(SCAN_OUTPUT)]
        if force:
            cmd.append("-SkipJunk")  # 快速模式
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, shell=False, creationflags=CREATE_NO_WINDOW)
        if result.returncode != 0 or not SCAN_OUTPUT.exists():
            raise RuntimeError(result.stderr or "scan script failed")
        data = json.loads(SCAN_OUTPUT.read_text(encoding="utf-8-sig"))
        _cache["data"] = data
        _cache["ts"] = time.time()
        return data
    except subprocess.TimeoutExpired:
        return {"error": "扫描超时（>180s），请减少范围后重试"}
    except Exception as e:
        return {"error": str(e)}


def run_full_scan() -> dict:
    """完整扫描（含垃圾扫描），用于体检/清理页面"""
    try:
        result = subprocess.run(
            ["powershell", "-File", str(SCAN_SCRIPT), "-Output", str(SCAN_OUTPUT)],
            capture_output=True, text=True, timeout=180, shell=False, creationflags=CREATE_NO_WINDOW
        )
        if result.returncode != 0 or not SCAN_OUTPUT.exists():
            raise RuntimeError(result.stderr or "full scan failed")
        data = json.loads(SCAN_OUTPUT.read_text(encoding="utf-8-sig"))
        _cache["data"] = data
        _cache["ts"] = time.time()
        return data
    except subprocess.TimeoutExpired:
        return {"error": "完整扫描超时"}
    except Exception as e:
        return {"error": str(e)}


# ════════════════════════════════════════════════════════════
#  API — 只读查询
# ════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """控制台首页"""
    return render_template("index.html")


@app.route("/api/scan")
def api_scan():
    """全量扫描数据"""
    force = request.args.get("force", "0") == "1"
    return jsonify(run_scan(force=force))


@app.route("/api/hardware")
def api_hardware():
    data = run_scan()
    return jsonify(data.get("hardware", {}))


@app.route("/api/storage")
def api_storage():
    data = run_scan()
    return jsonify(data.get("storage", {}))


@app.route("/api/software")
def api_software():
    data = run_scan()
    return jsonify(data.get("software", {}))


@app.route("/api/usb")
def api_usb():
    data = run_scan()
    return jsonify(data.get("usb", {}))


@app.route("/api/security")
def api_security():
    data = run_scan()
    return jsonify(data.get("security", {}))


@app.route("/api/network")
def api_network():
    data = run_scan()
    return jsonify(data.get("network", {}))


@app.route("/api/system")
def api_system():
    data = run_scan()
    return jsonify(data.get("system", {}))


@app.route("/api/processes")
def api_processes():
    data = run_scan()
    return jsonify({"processes": data.get("system", {}).get("processes", [])})


# ════════════════════════════════════════════════════════════
#  API — 健康体检评分
# ════════════════════════════════════════════════════════════

@app.route("/api/health-score")
def api_health_score():
    """综合健康度评分（0-100），强制完整扫描以获取最新数据"""
    force = request.args.get("force", "1") == "1"
    if force:
        data = run_full_scan()
    else:
        data = run_scan()
    items = []
    total_weight = 0
    weighted_sum = 0

    # ── 磁盘健康（权重25）───────────────────────────
    drives = (data.get("storage") or {}).get("drives") or []
    c_drive = next((d for d in drives if d.get("letter","").startswith("C")), None)
    if c_drive:
        used_pct = c_drive.get("usedPercent", 50)
        if used_pct < 50:   disk_score = 100
        elif used_pct < 60: disk_score = 90
        elif used_pct < 70: disk_score = 80
        elif used_pct < 80: disk_score = 60
        elif used_pct < 90: disk_score = 30
        else:               disk_score = 10
        items.append({"id": "disk", "name": "磁盘空间", "score": disk_score, "weight": 25,
                       "detail": f"C盘已用 {used_pct}%",
                       "fix": "清理临时文件和回收站可释放空间" if disk_score < 70 else "",
                       "fixable": disk_score < 90,
                       "fixAction": "auto-clean"})
        total_weight += 25
        weighted_sum += disk_score * 25

    # ── 安全防护（权重25）───────────────────────────
    av = (data.get("security") or {}).get("antivirus") or {}
    if isinstance(av.get("enabled"), bool):
        if av.get("enabled") and av.get("realtimeProtection") and av.get("behaviorMonitor"):
            sec_score = 100
        elif av.get("enabled") and av.get("realtimeProtection"):
            sec_score = 70
        elif av.get("enabled"):
            sec_score = 50
        else:
            sec_score = 10
    else:
        sec_score = 40
    items.append({"id": "security", "name": "安全防护", "score": sec_score, "weight": 25,
                   "detail": "实时保护" + ("启用" if av.get("realtimeProtection") else "关闭"),
                   "fix": "请开启 Windows Defender 实时保护" if sec_score < 50 else "",
                   "fixable": False})
    total_weight += 25
    weighted_sum += sec_score * 25

    # ── 启动项（权重10）─────────────────────────────
    startup_count = len((data.get("software") or {}).get("startup") or [])
    if startup_count <= 5:    boot_score = 100
    elif startup_count <= 10: boot_score = 80
    elif startup_count <= 20: boot_score = 60
    elif startup_count <= 30: boot_score = 40
    else:                     boot_score = 20
    items.append({"id": "startup", "name": "开机启动", "score": boot_score, "weight": 10,
                   "detail": f"共 {startup_count} 个启动项",
                   "fix": "建议禁用不必要的启动项以加快开机速度" if boot_score < 60 else "",
                   "fixable": False})
    total_weight += 10
    weighted_sum += boot_score * 10

    # ── 垃圾文件（权重20）───────────────────────────
    junk = data.get("junk") or {}
    junk_total = junk.get("total", 0)
    if junk_total < 1_000_000_000:      junk_score = 100
    elif junk_total < 3_000_000_000:    junk_score = 80
    elif junk_total < 5_000_000_000:    junk_score = 60
    elif junk_total < 10_000_000_000:   junk_score = 40
    else:                                junk_score = 20
    items.append({"id": "junk", "name": "垃圾清理", "score": junk_score, "weight": 20,
                   "detail": f"可清理约 {junk.get('totalText', '0 B')}",
                   "fix": "一键清理可释放磁盘空间" if junk_score < 70 else "",
                   "fixable": junk_score < 90,
                   "fixAction": "auto-clean"})
    total_weight += 20
    weighted_sum += junk_score * 20

    # ── 系统稳定性（权重10）─────────────────────────
    health = data.get("health") or {}
    errors = health.get("eventErrors", 0)
    warnings = health.get("eventWarnings", 0)
    if errors < 0:
        sys_score = 60  # 未扫描
        stability_detail = "未扫描（需管理员权限）"
    elif errors == 0 and warnings < 5:    sys_score = 100
    elif errors < 3 and warnings < 10:  sys_score = 80
    elif errors < 10:                   sys_score = 50
    else:                               sys_score = 30
    if errors < 0:
        stability_detail = "未扫描（需管理员权限）"
    else:
        stability_detail = f"24h {errors} 错误, {warnings} 警告"
    items.append({"id": "stability", "name": "系统稳定性", "score": sys_score, "weight": 10,
                   "detail": stability_detail,
                   "fix": "检查事件日志排查频繁错误" if sys_score < 50 else "",
                   "fixable": False})
    total_weight += 10
    weighted_sum += sys_score * 10

    # ── CPU 负载（权重10）───────────────────────────
    cpu_usage = health.get("cpuUsage", -1)
    if cpu_usage < 0:   cpu_score = 60
    elif cpu_usage < 30: cpu_score = 100
    elif cpu_usage < 60: cpu_score = 80
    elif cpu_usage < 85: cpu_score = 50
    else:               cpu_score = 20
    items.append({"id": "cpu", "name": "CPU 负载", "score": cpu_score, "weight": 10,
                   "detail": f"当前 {cpu_usage:.0f}%" if cpu_usage >= 0 else "数据不可用",
                   "fix": "检查高占用进程" if cpu_score < 50 else "",
                   "fixable": False})
    total_weight += 10
    weighted_sum += cpu_score * 10

    # ── 归一化总分 ─────────────────────────────────
    overall = round(weighted_sum / total_weight) if total_weight > 0 else 50

    # ── 问题分级 & 统计 ───────────────────────────
    for it in items:
        s = it["score"]
        it["level"] = "critical" if s < 40 else "warning" if s < 70 else "good"

    issues = [it for it in items if it["fix"]]
    fixable = [it for it in items if it.get("fixable")]
    critical_count = sum(1 for it in items if it["level"] == "critical")
    warning_count = sum(1 for it in items if it["level"] == "warning")

    # ── 生成体检建议 ───────────────────────────────
    suggestions = [it["fix"] for it in items if it["fix"]]
    if not suggestions:
        suggestions.append("你的电脑状态不错，继续保持！🎉")

    grade = "A" if overall >= 90 else "B" if overall >= 75 else "C" if overall >= 60 else "D"

    return jsonify({
        "overall": overall,
        "grade": grade,
        "items": items,
        "issuesCount": len(issues),
        "criticalCount": critical_count,
        "warningCount": warning_count,
        "fixableCount": len(fixable),
        "suggestions": suggestions,
        "timestamp": data.get("timestamp", "")
    })


# ════════════════════════════════════════════════════════════
#  API — 一键修复
# ════════════════════════════════════════════════════════════

@app.route("/api/one-click-fix", methods=["POST"])
def api_one_click_fix():
    """一键修复：根据体检报告自动执行可修复项（temp + recycle + browser + wupdate）"""
    if not request.is_json:
        return jsonify({"error": "请求体需为 JSON"}), 400

    confirm = request.json.get("confirm", False)
    if not confirm:
        return jsonify({"error": "需设置 confirm: true 确认一键修复"}), 400

    fixes = ["temp", "recycle", "browser", "wupdate"]  # 安全可自动修复的类别
    results = {}
    total_freed = 0

    for cat in fixes:
        freed = 0
        try:
            if cat == "temp":
                freed = _clean_temp_files()
            elif cat == "recycle":
                freed = _clean_recycle_bin()
            elif cat == "browser":
                freed = _clean_browser_cache()
            elif cat == "wupdate":
                freed = _clean_windows_update_cache()
        except Exception as e:
            results[cat] = {"error": str(e)}
            continue
        results[cat] = {"freedBytes": freed, "freedText": _format_bytes(freed)}
        total_freed += freed

    # 修复后标记需要重新体检
    return jsonify({
        "totalFreed": total_freed,
        "totalFreedText": _format_bytes(total_freed),
        "results": results,
        "needRescan": True
    })


# ════════════════════════════════════════════════════════════
#  API — 垃圾清理
# ════════════════════════════════════════════════════════════

@app.route("/api/cleanup/preview")
def api_cleanup_preview():
    """预览可清理的垃圾文件（触发完整扫描）"""
    force = request.args.get("force", "1") == "1"
    if force:
        data = run_full_scan()
    else:
        data = run_scan()
    junk = data.get("junk") or {}
    categories = junk.get("categories") or []
    return jsonify({
        "totalText": junk.get("totalText", "0 B"),
        "totalBytes": junk.get("total", 0),
        "categories": [c for c in categories if c.get("size", 0) > 0]
    })


@app.route("/api/cleanup/execute", methods=["POST"])
def api_cleanup_execute():
    """执行垃圾清理（需传 categories 列表 + confirm:true）"""
    if not request.is_json:
        return jsonify({"error": "请求体需为 JSON"}), 400

    categories = request.json.get("categories", [])
    confirm = request.json.get("confirm", False)

    if not categories:
        return jsonify({"error": "缺少 categories 参数"}), 400
    if not confirm:
        return jsonify({"error": "需设置 confirm: true 确认清理", "preview": categories}), 400

    results = {}
    total_freed = 0

    for cat in categories:
        freed = 0
        try:
            if cat == "temp":
                freed = _clean_temp_files()
            elif cat == "recycle":
                freed = _clean_recycle_bin()
            elif cat == "browser":
                freed = _clean_browser_cache()
            elif cat == "wupdate":
                freed = _clean_windows_update_cache()
            elif cat == "thumbnail":
                freed = _clean_thumbnail_cache()
            elif cat == "logs":
                freed = _clean_logs()
            elif cat == "delivery":
                freed = _clean_delivery_optimization()
            elif cat == "wer":
                freed = _clean_wer()
        except Exception as e:
            results[cat] = {"error": str(e)}
            continue
        results[cat] = {"freedBytes": freed, "freedText": _format_bytes(freed)}
        total_freed += freed

    return jsonify({
        "totalFreed": total_freed,
        "totalFreedText": _format_bytes(total_freed),
        "results": results
    })


def _clean_temp_files():
    freed = _delete_dir_files(os.environ.get("TEMP", ""))
    freed += _delete_dir_files(r"C:\Windows\Temp")
    return freed

def _clean_recycle_bin():
    import ctypes
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
    except Exception:
        pass
    return 0

def _clean_browser_cache():
    freed = 0
    paths = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data", "Default", "Cache", "Cache_Data"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data", "Default", "Cache", "Cache_Data"),
    ]
    for p in paths:
        freed += _delete_dir_files(p)
    ff_base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Mozilla", "Firefox", "Profiles")
    if os.path.isdir(ff_base):
        for d in os.listdir(ff_base):
            freed += _delete_dir_files(os.path.join(ff_base, d, "cache2"))
    return freed

def _clean_windows_update_cache():
    return _delete_dir_files(r"C:\Windows\SoftwareDistribution\Download")

def _clean_thumbnail_cache():
    freed = 0
    base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Explorer")
    if os.path.isdir(base):
        for f in os.listdir(base):
            if "thumbcache" in f.lower():
                fp = os.path.join(base, f)
                try:
                    freed += os.path.getsize(fp)
                    os.remove(fp)
                except OSError:
                    pass
    return freed

def _clean_logs():
    freed = 0
    for lp in [r"C:\Windows\Logs\CBS", r"C:\Windows\Logs\DISM", r"C:\Windows\Debug"]:
        freed += _delete_dir_files(lp)
    return freed

def _clean_delivery_optimization():
    return _delete_dir_files(r"C:\Windows\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache")

def _clean_wer():
    freed = 0
    for wp in [
        r"C:\ProgramData\Microsoft\Windows\WER\ReportArchive",
        r"C:\ProgramData\Microsoft\Windows\WER\ReportQueue"
    ]:
        freed += _delete_dir_files(wp)
    return freed

def _delete_dir_files(path):
    """删除目录下所有文件，返回释放字节数"""
    freed = 0
    if not path or not os.path.isdir(path):
        return 0
    for root, dirs, files in os.walk(path, topdown=False, onerror=lambda e: None):
        for f in files:
            fp = os.path.join(root, f)
            try:
                freed += os.path.getsize(fp)
                os.remove(fp)
            except (OSError, PermissionError):
                pass
        for d in dirs:
            try:
                os.rmdir(os.path.join(root, d))
            except OSError:
                pass
    return freed


# ════════════════════════════════════════════════════════════
#  API — 操作端点（需确认的破坏性操作记录在 skill 层控制）
# ════════════════════════════════════════════════════════════

@app.route("/api/action/clean-temp", methods=["POST"])
def action_clean_temp():
    """清理临时文件（预览模式: 仅返回大小，不实际删除）"""
    dry_run = request.args.get("dry_run", "1") == "1"
    temp_paths = [os.environ.get("TEMP", ""), r"C:\Windows\Temp"]
    total = 0

    for tp in temp_paths:
        if not tp:
            continue
        for root, dirs, files in os.walk(tp, topdown=True):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                    if not dry_run:
                        os.remove(fp)
                except (OSError, PermissionError):
                    pass

    return jsonify({
        "dry_run": dry_run,
        "bytes": total,
        "readable": _format_bytes(total),
        "action": "would delete" if dry_run else "deleted"
    })


@app.route("/api/action/defender-scan", methods=["POST"])
def action_defender_scan():
    """触发 Windows Defender 快速扫描"""
    scan_type = request.json.get("type", "QuickScan") if request.is_json else "QuickScan"
    # 仅允许 QuickScan / FullScan
    if scan_type not in ("QuickScan", "FullScan"):
        return jsonify({"error": "scan type 仅支持 QuickScan / FullScan"}), 400

    try:
        result = subprocess.run(
            ["powershell", "-Command", f"Start-MpScan -ScanType {scan_type}"],
            capture_output=True, text=True, timeout=3600, shell=False, creationflags=CREATE_NO_WINDOW
        )
        return jsonify({
            "status": "started" if result.returncode == 0 else "failed",
            "scanType": scan_type,
            "output": result.stdout[:500]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/action/kill-process", methods=["POST"])
def action_kill_process():
    """结束进程（需显式 confirm 参数）"""
    if not request.is_json:
        return jsonify({"error": "请求体需为 JSON"}), 400

    pid = request.json.get("pid")
    confirm = request.json.get("confirm", False)

    if not pid:
        return jsonify({"error": "缺少 pid 参数"}), 400
    if not confirm:
        return jsonify({"error": "需设置 confirm: true 确认操作", "pid": pid}), 400

    try:
        subprocess.run(["taskkill", "/PID", str(pid), "/F"],
                       capture_output=True, timeout=10, creationflags=CREATE_NO_WINDOW)
        return jsonify({"status": "killed", "pid": pid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════
#  API — AI 聊天（通用 OpenAI 兼容接口）
# ════════════════════════════════════════════════════════════

CHAT_CONFIG = {
    "endpoint": f"http://127.0.0.1:{GATEWAY['port']}/v1/chat/completions",
    "api_key": GATEWAY.get("token", ""),
    "model": "deepseek/deepseek-v4-flash",
}
CHAT_BACKEND = "openclaw" if CHAT_CONFIG["api_key"] else "none"


def _chat_via_cli(messages):
    """通过 openclaw agent CLI 聊天"""
    user_msg = messages[-1].get("content", "") if messages else ""
    try:
        oc = os.path.expandvars(r"%APPDATA%\npm\openclaw.cmd")
        r = subprocess.run(
            [oc, "agent", "--session-key", "agent:main:pc-manager",
             "--message", user_msg, "--json", "--timeout", "120"],
            capture_output=True, text=True, timeout=150, creationflags=CREATE_NO_WINDOW
        )
        if r.returncode == 0 and r.stdout.strip():
            o = json.loads(r.stdout)
            return jsonify({"reply": o.get("result", {}).get("payloads", [{}])[0].get("text", "") or o.get("reply", "")})
    except Exception:
        pass
    return None  # 返回 None 表示失败，由调用方处理


@app.route("/api/chat/config", methods=["GET", "POST"])
def api_chat_config():
    """读取/更新 AI 聊天配置"""
    if request.method == "POST" and request.is_json:
        for k in ("endpoint", "api_key", "model"):
            if k in request.json and request.json[k]:
                CHAT_CONFIG[k] = request.json[k]
        safe = {**CHAT_CONFIG, "api_key": CHAT_CONFIG["api_key"][:4]+"***" if CHAT_CONFIG["api_key"] else ""}
        return jsonify({"ok": True, "config": safe})
    safe_cfg = {**CHAT_CONFIG, "api_key": (CHAT_CONFIG["api_key"][:4]+"***") if CHAT_CONFIG["api_key"] else ""}
    return jsonify({"config": safe_cfg, "backend": CHAT_BACKEND})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """通用 AI 聊天：OpenAI/OpenClaw/自定义 API + CLI 回退"""
    if not request.is_json:
        return jsonify({"error": "请求体需为 JSON"}), 400
    messages = request.json.get("messages", [])
    if not messages:
        return jsonify({"error": "缺少 messages 参数"}), 400

    # OpenClaw Gateway → 优先 CLI
    if CHAT_BACKEND == "openclaw" and CHAT_CONFIG["api_key"]:
        cli_resp = _chat_via_cli(messages)
        if cli_resp is not None:
            return cli_resp
        # CLI 失败，回退到 API

    # 自定义 API → 通用 OpenAI 格式
    if CHAT_CONFIG["api_key"]:
        try:
            payload = json.dumps({
                "model": CHAT_CONFIG["model"],
                "messages": messages,
                "stream": False,
                "max_tokens": 800
            }).encode()
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CHAT_CONFIG['api_key']}"
            }
            req = urllib.request.Request(CHAT_CONFIG["endpoint"], data=payload, headers=headers, method="POST")
            resp = urllib.request.urlopen(req, timeout=120)
            content = json.loads(resp.read()).get("choices", [{}])[0].get("message", {}).get("content", "")
            return jsonify({"reply": content or "（AI 无回复）"})
        except urllib.error.HTTPError as e:
            err = e.read().decode(errors="replace")[:300]
            return jsonify({"error": f"API {e.code}: {err}"}), 502
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "未配置 AI 后端。请在设置面板填入 API endpoint + key。\n支持: OpenAI / DeepSeek / OpenClaw Gateway / 任何 OpenAI 兼容 API"}), 500

#  辅助
# ════════════════════════════════════════════════════════════

def _format_bytes(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


# ════════════════════════════════════════════════════════════
#  入口
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f" 🖥️  PC Manager → http://127.0.0.1:{port}")
    print(f"    AI 聊天: OpenClaw Gateway @ {GATEWAY['port']}")
    print(f"    Ctrl+C 停止")
    app.run(host="127.0.0.1", port=port, debug=False)
