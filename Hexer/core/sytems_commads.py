import os
import shlex
import datetime
import json
import getpass

def sysApp(cmd: str):
    parts = shlex.split(cmd.strip())
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

    HISTORY_FILE = os.path.expanduser("/home/andriy/Hexer/Hexer/data/hexer_history.json")

    # --- load history ---
    def load_history():
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    
    # --- save history ---
    def save_history(history):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4)
        except:
            pass

    # Always load and update history
    command_history = load_history()

    command_history.append({
        "id": len(command_history) + 1,
        "command": str(cmd)
    })
    save_history(command_history)

    # --- tree ---
    if command == "tree":
        start_dir = os.getcwd()
        tree_output = []

        try:
            for root, dirs, files in os.walk(start_dir):
                level = root.replace(start_dir, "").count(os.sep)
                indent = "   " * level
                folder_name = os.path.basename(root)
                tree_output.append(f"{indent}{folder_name}/")

                sub_indent = "   " * (level + 1)
                for f in files:
                    tree_output.append(f"{sub_indent}{f}")

            result_text = "\n".join(tree_output)
            return ("info", result_text, os.getcwd())

        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
    
    # --- date ---
    if command == "date":
        try:
            now = datetime.datetime.now()
            result = now.strftime("%Y-%m-%d %H:%M:%S")
            return ("info", result, os.getcwd())
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
        
    # --- sysinfo ---
    if command == "sysinfo":
        try:
            import platform
            import psutil

            info = []

            if not args:
                info.append(f"OS: {platform.system()} {platform.release()}")
                info.append(f"Machine: {platform.machine()}")
                info.append(f"Processor: {platform.processor()}")
                info.append(f"Python: {platform.python_version()}")
                info.append(
                    f"CPU cores: {psutil.cpu_count(logical=True)} logical / "
                    f"{psutil.cpu_count(logical=False)} physical"
                )

                ram = psutil.virtual_memory()
                info.append(f"RAM: {round(ram.total / (1024**3), 2)} GB")

                return ("info", "\n".join(info), os.getcwd())

            flag = args[0]

            # OS only
            if flag == "--os":
                info.append(f"OS: {platform.system()} {platform.release()}")
                return ("info", "\n".join(info), os.getcwd())

            # CPU only
            if flag == "--cpu":
                info.append(
                    f"CPU cores: {psutil.cpu_count(logical=True)} logical / "
                    f"{psutil.cpu_count(logical=False)} physical"
                )
                info.append(f"Processor: {platform.processor()}")
                return ("info", "\n".join(info), os.getcwd())

            # RAM only
            if flag == "--ram":
                ram = psutil.virtual_memory()
                info.append(f"RAM: {round(ram.total / (1024**3), 2)} GB")
                return ("info", "\n".join(info), os.getcwd())

            # Unknown flag
            return ("error", f"Unknown flag: {flag}", os.getcwd())

        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())

        
    # --- cwd ---
    if command == "cwd":
        try:
            current = os.getcwd()
            return ("info", current, current)
        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
        
    # --- history ---
    if command == "history":
        try:
            history = load_history()

            if len(history) == 0:
                return ("info", "History is empty", os.getcwd())

            show_json = False
            clear_history = False
            n = None

            # Parse flags
            for i, arg in enumerate(args):
                if arg == "-c":
                    clear_history = True
                elif arg == "--json":
                    show_json = True
                elif arg == "-n":
                    try:
                        n = int(args[i+1])
                    except (IndexError, ValueError):
                        return ("error", "Invalid usage of -n flag", os.getcwd())

            if clear_history:
                save_history([])
                return ("success", "History cleared", os.getcwd())

            if n is not None:
                history = history[-n:]

            if show_json:
                return ("success", json.dumps(history, indent=4), os.getcwd())

            # Standard readable output
            text = "\n".join(
                f"{item['id']} command = {item['command']}"
                for item in history
            )

            return ("info", text, os.getcwd())

        except Exception as e:
            return ("error", f"Error: {e}", os.getcwd())
        
    if command == "whoami":
        try:
            user = getpass.getuser()
        except Exception:
            user = os.getenv("USER", "unknown")
        return ("info", f"Current user: {user}", os.getcwd())

    return None
