# ============================================================
#  PC Manager Scanner — 全量系统扫描
#  用法: powershell -File scan.ps1 [-Output scan.json]
#  输出: JSON 文件，含全部硬件/软件/存储/安全/网络/USB信息
# ============================================================
param(
    [string]$Output = "scan-result.json",
    [switch]$SkipJunk  # 快速模式：跳过垃圾扫描（仪表盘刷新用）
)

$ErrorActionPreference = "SilentlyContinue"

# ── 辅助函数 ──────────────────────────────────────────────
function Safe-Get { param($script, $fallback) try { & $script } catch { $fallback } }

function Format-Bytes($bytes) {
    if ($bytes -gt 1TB) { return "$([math]::Round($bytes/1TB,1)) TB" }
    if ($bytes -gt 1GB) { return "$([math]::Round($bytes/1GB,1)) GB" }
    if ($bytes -gt 1MB) { return "$([math]::Round($bytes/1MB,1)) MB" }
    return "$bytes B"
}

$scan = @{ timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss") }

# ════════════════════════════════════════════════════════════
#  1. 硬件信息
# ════════════════════════════════════════════════════════════
Write-Host "[1/7] 采集硬件信息..." -ForegroundColor Cyan

$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$gpu = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -notlike "*VirtualBox*" -and $_.Name -notlike "*Microsoft*" } | Select-Object -First 2
$ram = Get-CimInstance Win32_PhysicalMemory
$board = Get-CimInstance Win32_BaseBoard | Select-Object -First 1
$bios = Get-CimInstance Win32_BIOS | Select-Object -First 1
$system = Get-CimInstance Win32_ComputerSystem | Select-Object -First 1

$scan.hardware = @{
    cpu = @{
        name      = $cpu.Name -replace '\s+', ' '
        cores     = $cpu.NumberOfCores
        threads   = $cpu.NumberOfLogicalProcessors
        maxSpeed  = "$($cpu.MaxClockSpeed) MHz"
        socket    = $cpu.SocketDesignation
    }
    gpu = @($gpu | ForEach-Object {
        @{
            name   = $_.Name -replace '\s+', ' '
            driver = $_.DriverVersion
            vram   = Format-Bytes $_.AdapterRAM
        }
    })
    memory = @{
        total     = Format-Bytes $system.TotalPhysicalMemory
        sticks    = $ram.Count
        details   = @($ram | ForEach-Object {
            @{
                capacity = Format-Bytes $_.Capacity
                speed    = "$($_.Speed) MHz"
                slot     = $_.DeviceLocator
                type     = "DDR$($_.SMBIOSMemoryType)"
            }
        })
    }
    motherboard = @{ manufacturer = $board.Manufacturer; product = $board.Product }
    bios        = @{ vendor = $bios.Manufacturer; version = $bios.SMBIOSBIOSVersion; date = $bios.ReleaseDate }
}

# ════════════════════════════════════════════════════════════
#  2. 存储信息
# ════════════════════════════════════════════════════════════
Write-Host "[2/7] 采集存储信息..." -ForegroundColor Cyan

$volumes = Get-Volume | Where-Object { $_.DriveLetter -and $_.Size -gt 0 }
$physicalDisks = Get-PhysicalDisk -ErrorAction SilentlyContinue

$scan.storage = @{
    drives = @($volumes | ForEach-Object {
        $used = $_.Size - $_.SizeRemaining
        @{
            letter      = "$($_.DriveLetter):"
            label       = $_.FileSystemLabel
            fs          = $_.FileSystem
            total       = Format-Bytes $_.Size
            used        = Format-Bytes $used
            free        = Format-Bytes $_.SizeRemaining
            usedPercent = if ($_.Size -gt 0) { [math]::Round($used / $_.Size * 100, 1) } else { 0 }
        }
    })
    physical = @(if ($physicalDisks) { $physicalDisks | ForEach-Object {
        @{
            model        = $_.FriendlyName
            media        = $_.MediaType
            size         = Format-Bytes $_.Size
            health       = $_.HealthStatus
            temp         = "$($_.Temperature)°C"
            powerOnHours = $_.PowerOnHours
        }
    }})
}

# ── 大文件扫描（TOP 20 > 100MB，限制范围避免超慢）─────────
Write-Host "  │ 扫描大文件..." -ForegroundColor DarkGray
$searchPaths = @($env:USERPROFILE, "$env:SystemDrive\Program Files", "$env:SystemDrive\Program Files (x86)")
$bigFiles = @($searchPaths | ForEach-Object {
    Get-ChildItem $_ -Recurse -Depth 5 -File -ErrorAction SilentlyContinue
} | Where-Object { $_.Length -gt 100MB } |
    Sort-Object Length -Descending |
    Select-Object -First 20 |
    ForEach-Object {
        @{ path = $_.FullName; size = Format-Bytes $_.Length }
    })

$scan.storage.bigFiles = $bigFiles

# ── 临时文件统计（dir 快速估算，不递归）─────────────────
$tempSize = 0
$tempDirs = @($env:TEMP, "$env:SystemRoot\Temp")
foreach ($td in $tempDirs) {
    if (Test-Path $td) {
        $sizeOutput = & cmd.exe /c "dir `"$td`" /s /a-d 2>nul" 2>$null | Select-String -Pattern "个文件" -AllMatches
        if ($sizeOutput) {
            $match = [regex]::Match($sizeOutput, '([\d,]+)\s*字节')
            if ($match.Success) { $tempSize += [long]($match.Groups[1].Value -replace ',','') }
        }
    }
}
if ($tempSize -eq 0) {
    # 回退：快速取样
    Get-ChildItem $env:TEMP -File -Depth 1 -ErrorAction SilentlyContinue | ForEach-Object { $tempSize += $_.Length }
}
$scan.storage.tempSize = Format-Bytes $tempSize

# ════════════════════════════════════════════════════════════
#  3. 软件信息
# ════════════════════════════════════════════════════════════
Write-Host "[3/7] 采集软件清单..." -ForegroundColor Cyan

$regPaths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

$apps = $regPaths | ForEach-Object {
    Get-ItemProperty $_ -ErrorAction SilentlyContinue
} | Where-Object { $_.DisplayName -and $_.DisplayName -ne "" } |
    Sort-Object DisplayName -Unique |
    ForEach-Object {
        @{
            name       = $_.DisplayName
            version    = $_.DisplayVersion
            publisher  = $_.Publisher
            installDate = $_.InstallDate
        }
    }

$scan.software = @{
    count   = $apps.Count
    apps    = @($apps)
    startup = @(Get-CimInstance Win32_StartupCommand | ForEach-Object {
        @{ name = $_.Name; command = $_.Command; location = $_.Location }
    })
}

# ════════════════════════════════════════════════════════════
#  4. 外接设备（USB/蓝牙/显示器）
# ════════════════════════════════════════════════════════════
Write-Host "[4/7] 采集外接设备..." -ForegroundColor Cyan

$usbCurrent = Get-PnpDevice -Class USB -ErrorAction SilentlyContinue |
    Where-Object { $_.Status -eq "OK" } |
    ForEach-Object { @{ name = $_.FriendlyName; id = $_.InstanceId } }

# USB 历史（曾经插入过的设备）
$usbHistory = @(Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Enum\USB\*\*" -ErrorAction SilentlyContinue |
    ForEach-Object {
        $name = $_.DeviceDesc
        if (-not $name) { $name = $_.FriendlyName }
        @{ name = $name; hardwareId = $_.HardwareID }
    } | Where-Object { $_.name } | Select-Object -Unique -First 20)

$monitors = @(Get-CimInstance WmiMonitorID -Namespace root\wmi -ErrorAction SilentlyContinue |
    ForEach-Object {
        $nameBytes = if ($_.UserFriendlyName -and $_.UserFriendlyName.Count -gt 0) { $_.UserFriendlyName } else { $_.ManufacturerName }
        $name = [System.Text.Encoding]::ASCII.GetString($nameBytes).TrimEnd([char]0)
        @{ name = $name; serial = $_.SerialNumberID }
    })

$scan.usb = @{
    current = @($usbCurrent)
    history = @($usbHistory)
    monitors = @($monitors)
}

# ════════════════════════════════════════════════════════════
#  5. 安全信息（Windows Defender）
# ════════════════════════════════════════════════════════════
Write-Host "[5/7] 采集安全状态..." -ForegroundColor Cyan

try {
    $mp = Get-MpComputerStatus -ErrorAction Stop
    $threats = Get-MpThreatDetection -ErrorAction SilentlyContinue
    $firewall = Get-NetFirewallProfile -ErrorAction SilentlyContinue |
        Select-Object Name, Enabled

    $scan.security = @{
        antivirus = @{
            enabled             = $mp.AntivirusEnabled
            signatureUpdated    = $mp.AntivirusSignatureLastUpdated
            behaviorMonitor     = $mp.BehaviorMonitorEnabled
            realtimeProtection  = $mp.RealTimeProtectionEnabled
        }
        threats = @($threats | Where-Object { $_.ThreatName } | ForEach-Object {
            @{
                name     = $_.ThreatName
                severity = if ($_.Severity) { $_.Severity.ToString() } else { "?" }
                action   = if ($_.Action) { $_.Action.ToString() } else { "?" }
                path     = $_.Resources
            }
        } | Select-Object -Last 10)
        firewall = @($firewall | ForEach-Object {
            @{ profile = $_.Name; enabled = $_.Enabled }
        })
    }
} catch {
    Write-Host "  ⚠ Defender 数据需要管理员权限" -ForegroundColor Yellow
    $scan.security = @{ antivirus = @{ enabled = "⚠ 权限不足" }; threats = @(); firewall = @() }
}

# ════════════════════════════════════════════════════════════
#  6. 网络信息
# ════════════════════════════════════════════════════════════
Write-Host "[6/7] 采集网络信息..." -ForegroundColor Cyan

$adapters = @(Get-NetAdapter -ErrorAction SilentlyContinue |
    Where-Object { $_.Status -eq "Up" -and $_.Name } |
    ForEach-Object {
        @{
            name    = $_.Name
            speed   = if ($_.LinkSpeed) { "$([math]::Round($_.LinkSpeed/1e6)) Mbps" } else { "-" }
            mac     = $_.MacAddress
        }
    })

$scan.network = @{
    adapters    = if ($adapters.Count -gt 0) { $adapters } else { @() }
    hostname    = $env:COMPUTERNAME
}

# ════════════════════════════════════════════════════════════
#  7. 系统 & 进程信息
# ════════════════════════════════════════════════════════════
Write-Host "[7/7] 采集系统信息..." -ForegroundColor Cyan

$os = Get-CimInstance Win32_OperatingSystem | Select-Object -First 1
$uptime = (Get-Date) - $os.LastBootUpTime

$topProcesses = Get-Process | Sort-Object WorkingSet64 -Descending |
    Select-Object -First 15 |
    ForEach-Object {
        @{
            name = $_.ProcessName
            pid  = $_.Id
            ram  = Format-Bytes $_.WorkingSet64
            cpu  = [math]::Round($_.CPU, 2)
        }
    }

$scan.system = @{
    os           = $os.Caption
    version      = [System.Environment]::OSVersion.VersionString
    build        = "$($os.BuildNumber)"
    installDate  = $os.InstallDate.ToString("yyyy-MM-dd")
    lastBoot     = $os.LastBootUpTime.ToString("yyyy-MM-dd HH:mm")
    uptime       = "$($uptime.Days)d $($uptime.Hours)h $($uptime.Minutes)m"
    totalRAM     = Format-Bytes $system.TotalPhysicalMemory
    processes    = @($topProcesses)
}

# ════════════════════════════════════════════════════════════
#  8. 健康体检 & 垃圾文件扫描（可跳过）
# ════════════════════════════════════════════════════════════
if ($SkipJunk) {
    Write-Host "[8/8] ⏭ 跳过垃圾扫描（快速模式）" -ForegroundColor DarkGray
    $scan.junk = @{ total = 0; totalText = "未扫描（请进入体检页）"; categories = @(); details = @{} }
    $scan.health = @{
        cpuUsage       = -1
        eventErrors    = -1
        eventWarnings  = -1
        windowsUpdate  = @{ lastCheck = "未扫描"; pendingCount = -1; autoUpdate = "未知" }
    }
} else {
    Write-Host "[8/8] 采集体检 & 垃圾数据..." -ForegroundColor Cyan

# ── 快速目录大小（dir /s，比 Get-ChildItem -Recurse 快5-10倍）─
function Get-DirSizeSafe($path) {
    if (-not (Test-Path $path)) { return 0 }
    $out = & cmd.exe /c "dir `"$path`" /s /a-d 2>nul" 2>$null | Select-String -Pattern "(个文件|File\(s\))" | Select-Object -Last 1
    if ($out) {
        $m = [regex]::Match($out, '([\d,]+)\s*字节')
        if ($m.Success) { return [long]($m.Groups[1].Value -replace ',','') }
    }
    return 0
}

# ── 回收站大小（各盘符）─────────────────────────────────
$recycleSizes = @{}; $recycleTotal = 0
$driveLetters = (Get-Volume | Where-Object { $_.DriveLetter -and $_.Size -gt 0 }).DriveLetter
foreach ($dl in $driveLetters) {
    $rbPath = "${dl}:\`$Recycle.Bin"
    $rbSize = Get-DirSizeSafe $rbPath
    if ($rbSize -gt 0) { $recycleSizes["$dl"] = $rbSize; $recycleTotal += $rbSize }
}
Write-Host "  │ 回收站: $(Format-Bytes $recycleTotal)" -ForegroundColor DarkGray

# ── 浏览器缓存 ────────────────────────────────────────
$browserCaches = @{Edge=0; Chrome=0; Firefox=0}
$browserCaches.Edge   = Get-DirSizeSafe "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache\Cache_Data"
$browserCaches.Chrome = Get-DirSizeSafe "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache\Cache_Data"
$ffProfiles = "$env:LOCALAPPDATA\Mozilla\Firefox\Profiles"
if (Test-Path $ffProfiles) {
    Get-ChildItem $ffProfiles -Directory -ErrorAction SilentlyContinue | Select-Object -First 3 | ForEach-Object {
        $browserCaches.Firefox += Get-DirSizeSafe (Join-Path $_.FullName "cache2")
    }
}
Write-Host "  │ 浏览器缓存: Edge $(Format-Bytes $browserCaches.Edge) / Chrome $(Format-Bytes $browserCaches.Chrome) / Firefox $(Format-Bytes $browserCaches.Firefox)" -ForegroundColor DarkGray

# ── Windows Update 缓存 ─────────────────────────────────
$wuCacheSize = Get-DirSizeSafe "$env:SystemRoot\SoftwareDistribution\Download"
Write-Host "  │ WinUpdate缓存: $(Format-Bytes $wuCacheSize)" -ForegroundColor DarkGray

# ── 缩略图缓存 ──────────────────────────────────────────
$thumbSize = 0
$thumbDir = "$env:LOCALAPPDATA\Microsoft\Windows\Explorer"
if (Test-Path $thumbDir) {
    Get-ChildItem $thumbDir -Filter "*thumbcache*" -File -ErrorAction SilentlyContinue | ForEach-Object { $thumbSize += $_.Length }
}

# ── 系统日志 ───────────────────────────────────────────
$logSize = 0
"$env:SystemRoot\Logs\CBS", "$env:SystemRoot\Logs\DISM", "$env:SystemRoot\Debug" | ForEach-Object { $logSize += Get-DirSizeSafe $_ }

# ── 传递优化 ───────────────────────────────────────────
$doSize = Get-DirSizeSafe "$env:SystemRoot\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache"

# ── Windows 错误报告 ──────────────────────────────────
$werSize = 0
"$env:ProgramData\Microsoft\Windows\WER\ReportArchive", "$env:ProgramData\Microsoft\Windows\WER\ReportQueue" | ForEach-Object { $werSize += Get-DirSizeSafe $_ }

# ── Windows.old ───────────────────────────────────────
$winOldSize = Get-DirSizeSafe "$env:SystemDrive\Windows.old"

# ── CPU 实时使用率 ─────────────────────────────────────
try { $cpuUsage = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average } catch { $cpuUsage = -1 }

# ── 汇总 junk ─────────────────────────────────────────
$browserTotal = 0; foreach ($bc in $browserCaches.Values) { $browserTotal += $bc }
$junkTotal = 0
$junkCategories = @(
    @{ id="temp";       name="临时文件";         size=$tempSize;       description="用户临时文件 + Windows Temp" },
    @{ id="recycle";    name="回收站";           size=$recycleTotal;    description="各盘符回收站内容" },
    @{ id="browser";    name="浏览器缓存";       size=$browserTotal;     description="Edge + Chrome + Firefox 缓存" },
    @{ id="wupdate";    name="Windows更新缓存";   size=$wuCacheSize;      description="SoftwareDistribution\Download" },
    @{ id="thumbnail";  name="缩略图缓存";       size=$thumbSize;        description="文件资源管理器缩略图缓存" },
    @{ id="logs";       name="系统日志";         size=$logSize;          description="CBS / DISM / Debug 日志" },
    @{ id="delivery";   name="传递优化文件";     size=$doSize;           description="Windows Update P2P 缓存" },
    @{ id="wer";        name="错误报告";         size=$werSize;          description="Windows 错误报告归档" },
    @{ id="winold";     name="Windows.old";      size=$winOldSize;       description="旧版 Windows 安装残留" }
)
foreach ($jc in $junkCategories) { $junkTotal += $jc.size }
Write-Host "  │ 垃圾总计: $(Format-Bytes $junkTotal)" -ForegroundColor Yellow

$scan.junk = @{
    total       = $junkTotal
    totalText   = Format-Bytes $junkTotal
    categories  = @($junkCategories)
    details     = @{
        recycleBin   = $recycleSizes
        browsers     = $browserCaches
        restorePoint = "未扫描(需管理员)"
    }
}

$scan.health = @{
    cpuUsage       = $cpuUsage
    eventErrors    = -1
    eventWarnings  = -1
    windowsUpdate  = @{ lastCheck = "未扫描"; pendingCount = -1; autoUpdate = "未知" }
}
}

# ════════════════════════════════════════════════════════════
#  输出
# ════════════════════════════════════════════════════════════
$json = $scan | ConvertTo-Json -Depth 4
$json | Out-File -FilePath $Output -Encoding UTF8
Write-Host ""
Write-Host "✅ 扫描完成 → $Output" -ForegroundColor Green
Write-Host "   文件大小: $(Format-Bytes (Get-Item $Output).Length)" -ForegroundColor Green
Write-Host ""

# 返回路径给调用者
return $Output
