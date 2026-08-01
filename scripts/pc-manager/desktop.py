"""
 PC Manager Desktop — 桌面应用入口
 用法: python desktop.py
 无 HTTP 端口暴露，纯本地窗口渲染
"""
import socket
import sys
import threading
from pathlib import Path

# ════════════════════════════════════════════════════════════
#  1. 找一个空闲端口（避免冲突）
# ════════════════════════════════════════════════════════════
def find_free_port(start=15000, end=16000):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    raise RuntimeError("no free port found")


PORT = find_free_port()
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# ════════════════════════════════════════════════════════════
#  2. 后台启动 Flask（127.0.0.1 仅本机可用）
# ════════════════════════════════════════════════════════════
from server import app

def run_flask():
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)

t = threading.Thread(target=run_flask, daemon=True)
t.start()

# ════════════════════════════════════════════════════════════
#  3. 用系统原生 WebView 打开窗口（无浏览器 UI）
# ════════════════════════════════════════════════════════════
import webview

URL = f"http://127.0.0.1:{PORT}"
WIDTH, HEIGHT = 1200, 780
TITLE = "ThresholdEcho"

print(f" 🖥️  {TITLE}")
print(f"    端口 {PORT}（仅 127.0.0.1）")

try:
    webview.create_window(TITLE, URL, width=WIDTH, height=HEIGHT,
                           min_size=(900, 600), resizable=True,
                           confirm_close=True, text_select=True)
    print("    GUI 窗口已打开 ✓")
    webview.start()
except Exception as e:
    print(f"    ⚠ GUI 不可用 ({e})，改用浏览器打开...")
    import webbrowser
    webbrowser.open(URL)
    print(f"    浏览器已打开 → {URL}")
    print("    按 Ctrl+C 退出")
    try:
        while True:  # 保持运行
            import time; time.sleep(1)
    except KeyboardInterrupt:
        print("    已退出")
