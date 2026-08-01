"""
 PC Manager Canvas Dashboard
 用法: python canvas_dashboard.py [scan.json]
 输出: ~/.openclaw/canvas/documents/pc-manager-dashboard/index.html
"""
import json, os, sys
from datetime import datetime
from pathlib import Path

SCAN_JSON = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "scan-result.json"
CANVAS_ROOT = Path.home() / ".openclaw" / "canvas" / "documents"
DOC_ID = "pc-manager-dashboard"
OUT_DIR = CANVAS_ROOT / DOC_ID
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════ 读取 & 评分 ═══════════
with open(SCAN_JSON, "r", encoding="utf-8-sig") as f:
    data = json.load(f)


def _fmt(size):
    for u in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024: return f"{size:.1f} {u}"
        size /= 1024
    return f"{size:.1f} PB"


def calc_score(data):
    items = []; tw = 0; ws = 0
    # 磁盘
    drives = (data.get("storage") or {}).get("drives") or []
    c = next((d for d in drives if d.get("letter", "").startswith("C")), None)
    if c:
        pct = c.get("usedPercent", 50)
        s = 100 if pct < 50 else 90 if pct < 60 else 80 if pct < 70 else 60 if pct < 80 else 30 if pct < 90 else 10
        items.append({"name": "磁盘空间", "score": s, "weight": 25, "detail": f"C盘已用 {pct}%",
                       "fix": "清理临时文件和回收站" if s < 70 else ""})
        tw += 25; ws += s * 25
    # 安全
    av = (data.get("security") or {}).get("antivirus") or {}
    if isinstance(av.get("enabled"), bool):
        s = 100 if (av.get("enabled") and av.get("realtimeProtection")) else 50 if av.get("enabled") else 10
    else: s = 40
    items.append({"name": "安全防护", "score": s, "weight": 25, "detail": "实时保护" + ("启用" if av.get("realtimeProtection") else "关闭"), "fix": ""})
    tw += 25; ws += s * 25
    # 启动项
    n = len((data.get("software") or {}).get("startup") or [])
    s = 100 if n <= 5 else 80 if n <= 10 else 60 if n <= 20 else 40 if n <= 30 else 20
    items.append({"name": "开机启动", "score": s, "weight": 10, "detail": f"共 {n} 个", "fix": ""})
    tw += 10; ws += s * 10
    # 垃圾
    jt = (data.get("junk") or {}).get("total", 0)
    s = 100 if jt < 1e9 else 80 if jt < 3e9 else 60 if jt < 5e9 else 40 if jt < 10e9 else 20
    items.append({"name": "垃圾清理", "score": s, "weight": 20, "detail": f"可清理 {(data.get('junk') or {}).get('totalText', '0 B')}", "fix": ""})
    tw += 20; ws += s * 20
    # CPU
    cu = (data.get("health") or {}).get("cpuUsage", 30)
    s = 100 if cu < 30 else 80 if cu < 60 else 50 if cu < 85 else 20
    items.append({"name": "CPU 负载", "score": s, "weight": 10, "detail": f"当前 {cu:.0f}%" if cu >= 0 else "未扫描", "fix": ""})
    tw += 10; ws += s * 10
    overall = round(ws / tw) if tw else 50
    grade = "A" if overall >= 90 else "B" if overall >= 75 else "C" if overall >= 60 else "D"
    emoji = "😱" if overall < 40 else "🤒" if overall < 60 else "😐" if overall < 75 else "😊" if overall < 90 else "🥳"
    for it in items:
        s = it["score"]; it["level"] = "critical" if s < 40 else "warning" if s < 70 else "good"
        it["barCls"] = "good" if s >= 80 else "warn" if s >= 50 else "danger"
        it["clr"] = "var(--green)" if s >= 80 else "var(--orange)" if s >= 50 else "var(--red)"
    suggestions = [i["fix"] for i in items if i.get("fix")]
    if not suggestions: suggestions.append("电脑状态不错，继续保持！")
    return {"overall": overall, "grade": grade, "emoji": emoji, "items": items, "suggestions": suggestions}


score = calc_score(data)
hw = data.get("hardware", {})
st = data.get("storage", {})
sy = data.get("system", {})
se = data.get("security", {})
junk = data.get("junk", {})

# ═══════════ 预格式化所有数据 ═══════════
score_clr = "var(--green)" if score["overall"] >= 90 else "var(--blue)" if score["overall"] >= 75 else "var(--orange)" if score["overall"] >= 60 else "var(--red)"
score_badge = "badge-ok" if score["overall"] >= 75 else "badge-warn" if score["overall"] >= 60 else "badge-err"
score_msg = "状态极佳" if score["overall"] >= 90 else "良好" if score["overall"] >= 75 else "一般" if score["overall"] >= 60 else "需要优化"

score_rows = []
for it in score["items"]:
    lvl_badge = '<span class="badge badge-err">严重</span>' if it["level"] == "critical" else '<span class="badge badge-warn">建议</span>' if it["level"] == "warning" else '<span class="badge badge-ok">良好</span>'
    score_rows.append((lvl_badge, it["name"], it["detail"], it["score"], it["clr"], it["barCls"]))

sug_rows = "".join(f'<p style="padding:3px 0;font-size:13px">• {s}</p>' for s in score["suggestions"])

disk_rows = []
for d in st.get("drives", []):
    pct = d.get("usedPercent", 50)
    bar = "danger" if pct > 90 else "warn" if pct > 70 else "good"
    disk_rows.append((d.get("letter", "?"), d.get("used", "?"), d.get("total", "?"), d.get("free", "?"), pct, bar))

junk_cats = [(c.get("name", "?"), _fmt(c.get("size", 0))) for c in junk.get("categories", []) if c.get("size", 0) > 0]
proc_rows = [(p.get("name", "?"), str(p.get("pid", "?")), p.get("ram", "?")) for p in (sy.get("processes") or [])[:5]]

gpu_name = ""
for g in hw.get("gpu", []):
    if g.get("name"): gpu_name = g["name"][:35]; break

# ═══════════ HTML ═══════════
html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenClaw PC Manager</title><style>
:root{{--bg:#0d1117;--bg-card:#161b22;--border:#30363d;--text:#c9d1d9;--text-dim:#8b949e;--accent:#a371f7;--green:#3fb950;--red:#f85149;--orange:#d2991d;--blue:#58a6ff;--radius:10px;--shadow:0 2px 12px rgba(0,0,0,.4)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:var(--bg);color:var(--text);font-family:"Segoe UI","Microsoft YaHei",system-ui;padding:18px 22px;max-width:920px;margin:0 auto}}
h2{{font-size:15px;color:var(--accent);margin-bottom:10px;padding-bottom:5px;border-bottom:1px solid var(--border)}}
.card{{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:14px 18px;margin-bottom:12px;box-shadow:var(--shadow)}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px;margin-bottom:12px}}
.mini{{font-size:11px;color:var(--text-dim)}}
.bar-wrap{{background:var(--bg);border-radius:5px;height:5px;margin:3px 0;overflow:hidden}}
.bar-fill{{height:100%;border-radius:5px}}.good{{background:var(--green)}}.warn{{background:var(--orange)}}.danger{{background:var(--red)}}
.badge{{display:inline-block;padding:1px 7px;border-radius:9px;font-size:10px;font-weight:500}}
.badge-ok{{background:#1a3a2a;color:var(--green)}}.badge-warn{{background:#3a2a1a;color:var(--orange)}}.badge-err{{background:#3a1a1a;color:var(--red)}}
.row{{display:flex;justify-content:space-between;align-items:center;padding:3px 0;font-size:12px}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{text-align:left;padding:5px 8px;color:var(--text-dim);font-weight:500;border-bottom:1px solid var(--border)}}
td{{padding:5px 8px;border-bottom:1px solid var(--border)}}
</style></head><body>

<h1 style="font-size:17px;font-weight:600;margin-bottom:2px">OpenClaw PC Manager</h1>
<p class="mini" style="margin-bottom:14px">体检: {data.get('timestamp','?')} · {sy.get('os','?')} Build {sy.get('build','?')} · 运行 {sy.get('uptime','?')}</p>

<div class="card" style="text-align:center;padding:22px">
  <div style="font-size:44px">{score['emoji']}</div>
  <div style="font-size:34px;font-weight:700;margin:6px 0;color:{score_clr}">{score['overall']}分</div>
  <span class="badge {score_badge}" style="font-size:13px;padding:3px 14px">{score['grade']} · {score_msg}</span>
</div>

<div class="card"><h2>各维度评分</h2>{"".join(f'''
  <div style="margin-bottom:8px">
    <div class="row"><span>{r[0]} <strong>{r[1]}</strong></span><span class="mini">{r[2]}</span><strong style="color:{r[4]}">{r[3]}分</strong></div>
    <div class="bar-wrap"><div class="bar-fill {r[5]}" style="width:{r[3]}%"></div></div>
  </div>''' for r in score_rows)}</div>

<div class="card"><h2>优化建议</h2>{sug_rows}</div>

<div class="cards">
  <div class="card"><p class="mini">CPU</p><p style="font-weight:600;font-size:13px">{(hw.get('cpu') or {}).get('name','?')[:35]}</p><p class="mini">{(hw.get('cpu') or {}).get('cores','?')}核 {(hw.get('cpu') or {}).get('threads','?')}线程</p></div>
  <div class="card"><p class="mini">内存</p><p style="font-weight:600;font-size:13px">{(hw.get('memory') or {}).get('total','?')}</p><p class="mini">{(hw.get('memory') or {}).get('sticks','?')}条</p></div>
  <div class="card"><p class="mini">GPU</p><p style="font-weight:600;font-size:13px">{gpu_name or '?'}</p><p class="mini">{(hw.get('gpu') or [{}])[0].get('vram','?') if hw.get('gpu') else '?'}</p></div>
  <div class="card"><p class="mini">Defender</p><p style="font-weight:600;font-size:13px">{"✅ 启用" if (se.get('antivirus') or {}).get('enabled') else "⚠ 关闭"}</p><p class="mini">实时保护{("中" if (se.get('antivirus') or {}).get('realtimeProtection') else "关")}</p></div>
</div>

<div class="card"><h2>磁盘分区</h2>{"".join(f'''
  <div style="margin-bottom:6px"><div class="row"><strong>{d[0]}</strong><span>{d[1]} / {d[2]}</span><span class="mini">剩{d[3]}</span></div>
  <div class="bar-wrap"><div class="bar-fill {d[5]}" style="width:{d[4]}%"></div></div></div>''' for d in disk_rows)}</div>

<div class="card"><h2>垃圾文件</h2>
  <p style="font-size:13px;font-weight:600;margin-bottom:6px">可清理 <span style="color:var(--accent)">{junk.get('totalText','0 B')}</span></p>
  <table><tr><th>类别</th><th>大小</th></tr>
  {"".join(f'<tr><td>{c[0]}</td><td>{c[1]}</td></tr>' for c in junk_cats) or '<tr><td colspan="2" style="color:var(--text-dim)">无可清理垃圾</td></tr>'}
  </table></div>

<div class="card"><h2>进程 TOP 5</h2>
  <table><tr><th>进程</th><th>PID</th><th>内存</th></tr>
  {"".join(f'<tr><td>{p[0]}</td><td>{p[1]}</td><td>{p[2]}</td></tr>' for p in proc_rows)}
  </table></div>

<p class="mini" style="text-align:center;margin-top:14px">OpenClaw PC Manager · OpenClaw · {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
</body></html>"""

(OUT_DIR / "index.html").write_text(html, encoding="utf-8")
print(f"✅ Dashboard OK  →  ref: {DOC_ID}")
print(f"   评分: {score['overall']} / {score['grade']}")
print(f"   路径: {OUT_DIR}")
