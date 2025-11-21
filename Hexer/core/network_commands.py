import subprocess
import os

def netApp(cmd: str):
    parts = cmd.strip().split()
    if not parts:
        return ("info", "", os.getcwd())

    command = parts[0].lower()
    args = parts[1:]

    def check_help(command, args):
        from core.help_command import COMMAND_HELP_DICT
        if "--help" in args or "-h" in args:
            if command in COMMAND_HELP_DICT:
                return ("info", f"Help for '{command}': \n{COMMAND_HELP_DICT[command]}", os.getcwd())
            else:
                return ("error", f"No help available for '{command}'")

    if command == "ping":
    
        if len(args) == 0:
            return ("error", "Usage: ping <host> [-c count]", os.getcwd())
    
        host = args[0]
        count = 4  # default packets
    
        # parse -c flag
        for i, arg in enumerate(args):
            if arg == "-c":
                try:
                    count = int(args[i+1])
                except:
                    return ("error", "Invalid packet count", os.getcwd())
    
        try:
            # Linux/macOS format:
            # ping -c 4 google.com
            result = subprocess.run(
                ["ping", "-c", str(count), host],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
    
            if result.returncode != 0:
                return ("error", result.stderr.strip(), os.getcwd())
    
            return ("info", result.stdout, os.getcwd())
    
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
    
    if command == "ip":
        try:
            import socket

            hostname = socket.gethostname()

            local_ip = socket.gethostbyname(hostname)

            text = (
                f"Hostname: {hostname}\n"
                f"Local IP: {local_ip}"
            )

            return ("info", text, os.getcwd())

        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())

    return None