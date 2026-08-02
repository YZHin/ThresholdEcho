/* ═══════════════════════════════════════════════════════════
   ThresholdEcho — 轻量 i18n（零依赖）
   用法：<span data-i18n="key">默认文本</span>
   动态文本用 t('key', params) 获取
   ═══════════════════════════════════════════════════════════ */
const I18N = {
  current: localStorage.getItem('te-lang') || 'zh',
  dicts: {
    zh: {
      'nav.dashboard': '仪表盘',
      'nav.hardware': '硬件',
      'nav.storage': '存储',
      'nav.software': '软件',
      'nav.usb': '外接设备',
      'nav.checkup': '一键体检',
      'nav.cleanup': '垃圾清理',
      'nav.security': '安全中心',
      'nav.network': '网络',
      'nav.processes': '进程',
      'nav.ai': 'AI 控制台',
      'status.online': '在线',
      'title.dashboard': '系统仪表盘',
      'btn.refresh': '刷新',
      'dash.topProcesses': '实时进程 TOP 5',
      'hw.title': '硬件详情',
      'storage.title': '磁盘分区',
      'storage.bigFiles': '大文件 TOP 10',
      'sw.title': '已安装软件',
      'sw.startup': '启动项',
      'usb.title': '当前 USB 设备',
      'usb.history': 'USB 历史记录',
      'usb.monitors': '显示器',
      'sec.defender': 'Windows Defender',
      'sec.quickScan': '快速扫描',
      'sec.fullScan': '全盘扫描 ⚠ 慢',
      'sec.threats': '威胁历史',
      'sec.firewall': '防火墙',
      'checkup.title': '一键体检',
      'checkup.recheck': '重新体检',
      'checkup.fix': '一键修复',
      'checkup.dims': '各维度评分',
      'checkup.suggestions': '优化建议',
      'cleanup.loading': '正在扫描垃圾文件...',
      'cleanup.total': '可清理垃圾文件总计',
      'cleanup.selectAll': '全选',
      'cleanup.deselect': '取消全选',
      'cleanup.details': '垃圾分类详情',
      'cleanup.execute': '清理选中项',
      'cleanup.note': '仅删除选中类别，不删重要文件',
      'ai.label': 'AI 控制台',
      'ai.hint': '你好！我是 AI 助手，可以帮你解读系统数据、提优化建议、回答电脑问题。有什么需要？',
      'bubble.echo': 'Echo',
      'bubble.analyzing': '正在分析...',
      'bubble.error': '连接失败',
      'chat.backend': '后端',
      'chat.settings': '设置',
      'chat.send': '发送',
      'chat.placeholder': '输入消息... (Enter 发送)',
      'chat.save': '保存',
      'chat.cancel': '取消',
      'common.noData': '无数据',
      'hw.cpu': 'CPU',
      'hw.gpu': 'GPU',
      'hw.memory': '内存',
      'hw.totalDisk': '磁盘总量',
      'hw.uptime': '运行时间',
      'hw.defender': 'Defender',
      'hw.enabled': '已启用',
      'hw.disabled': '未启用',
      'hw.protected': '实时保护中',
      'hw.check': '请检查',
      'hw.cores': '核',
      'hw.threads': '线程',
      'hw.sticks': '条',
      'hw.partitions': '个分区',
      'hw.motherboard': '主板',
      'hw.bios': 'BIOS',
      'hw.driver': '驱动',
      'hw.vram': '显存',
      'dash.noData': '无数据',
    },
    en: {
      'nav.dashboard': 'Dashboard',
      'nav.hardware': 'Hardware',
      'nav.storage': 'Storage',
      'nav.software': 'Software',
      'nav.usb': 'Devices',
      'nav.checkup': 'Checkup',
      'nav.cleanup': 'Cleanup',
      'nav.security': 'Security',
      'nav.network': 'Network',
      'nav.processes': 'Processes',
      'nav.ai': 'AI Console',
      'status.online': 'Online',
      'title.dashboard': 'System Dashboard',
      'btn.refresh': 'Refresh',
      'dash.topProcesses': 'Top 5 Processes',
      'hw.title': 'Hardware Details',
      'storage.title': 'Disk Partitions',
      'storage.bigFiles': 'Top 10 Large Files',
      'sw.title': 'Installed Software',
      'sw.startup': 'Startup Items',
      'usb.title': 'USB Devices',
      'usb.history': 'USB History',
      'usb.monitors': 'Monitors',
      'sec.defender': 'Windows Defender',
      'sec.quickScan': 'Quick Scan',
      'sec.fullScan': 'Full Scan ⚠ Slow',
      'sec.threats': 'Threat History',
      'sec.firewall': 'Firewall',
      'checkup.title': 'System Checkup',
      'checkup.recheck': 'Re-check',
      'checkup.fix': 'One-Click Fix',
      'checkup.dims': 'Score Details',
      'checkup.suggestions': 'Suggestions',
      'cleanup.loading': 'Scanning junk files...',
      'cleanup.total': 'Total Cleanable',
      'cleanup.selectAll': 'Select All',
      'cleanup.deselect': 'Deselect',
      'cleanup.details': 'Junk Categories',
      'cleanup.execute': 'Clean Selected',
      'cleanup.note': 'Only removes selected categories, never important files',
      'ai.label': 'AI Console',
      'ai.hint': 'Hi! I am the AI assistant. Ask me about your system data, optimization tips, or PC questions.',
      'bubble.echo': 'Echo',
      'bubble.analyzing': 'Analyzing...',
      'bubble.error': 'Connection failed',
      'chat.backend': 'Backend',
      'chat.settings': 'Settings',
      'chat.send': 'Send',
      'chat.placeholder': 'Type a message... (Enter to send)',
      'chat.save': 'Save',
      'chat.cancel': 'Cancel',
      'common.noData': 'No data',
      'hw.cpu': 'CPU',
      'hw.gpu': 'GPU',
      'hw.memory': 'Memory',
      'hw.totalDisk': 'Total Disk',
      'hw.uptime': 'Uptime',
      'hw.defender': 'Defender',
      'hw.enabled': 'Enabled',
      'hw.disabled': 'Disabled',
      'hw.protected': 'Active',
      'hw.check': 'Check',
      'hw.cores': 'cores',
      'hw.threads': 'threads',
      'hw.sticks': 'sticks',
      'hw.partitions': 'partitions',
      'hw.motherboard': 'Motherboard',
      'hw.bios': 'BIOS',
      'hw.driver': 'Driver',
      'hw.vram': 'VRAM',
      'dash.noData': 'No data',
    }
  },
  t(key, params) {
    let s = (this.dicts[this.current] && this.dicts[this.current][key]) || key;
    if (params) {
      Object.entries(params).forEach(([k, v]) => { s = s.replaceAll('{' + k + '}', v); });
    }
    return s;
  },
  apply() {
    document.documentElement.lang = this.current;
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      el.textContent = this.t(key);
    });
    document.querySelectorAll('[data-i18n-ph]').forEach(el => {
      const key = el.getAttribute('data-i18n-ph');
      el.placeholder = this.t(key);
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      el.title = this.t(key);
    });
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
      const key = el.getAttribute('data-i18n-html');
      el.innerHTML = this.t(key);
    });
  },
  setLang(lang) {
    this.current = lang;
    localStorage.setItem('te-lang', lang);
    this.apply();
    fetch('/api/lang', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({lang})
    }).catch(() => {});
  }
};
