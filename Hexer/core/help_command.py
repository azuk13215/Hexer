COMMAND_HELP_DICT = {
        "help": "Shows avaible commands and their description",
        "exit": "Exit the terminal",
        "time": "Show exact system time",
        "uptime": "Show system uptime",
        "mkdir": "Create a directory",
        "cd": "Change directory",
        "whoami": "Show username",
        "pwd": "Print working directory",
        "ls": "List directory contents",
        "touch": "Create an empty file",
        "echo": "Print text or write to file",
        "cat": "Show file contents",
        "rm": "Remove file/directory",
        "rename": "Rename file/directory",
        "cp": "Copy file",
        "mv": "Move (rename) file",
        "find": "Search for files",
        "grep": "Search text in files",
        "history": "Show command history",
        "sleep": "Pause for N seconds",
        "timer": "Start countdown timer",
        "ping": "Ping host",
        "ip": "Show IP information"
    }

def helpApp(cmd: str):
    def check_help(command, args):
        from core.help_command import COMMAND_HELP_DICT
        if "--help" in args or "-h" in args:
            if command in COMMAND_HELP_DICT:
                return ("info", f"Help for '{command}': \n{COMMAND_HELP_DICT[command]}", os.getcwd())
            else:
                return ("error", f"No help available for '{command}'")
    import os
    parts = cmd.strip().split()
    if not parts:
        return ("info", "", os.getcwd())

    command = parts[0].lower()

    if command != "help":
        return None

    list_help = """
        ===================== Hexer Help =====================

        help        - Show this help menu
        exit        - Exit the terminal
        time        - Show exact system time
        uptime      - Show system uptime
        mkdir       - Create a directory
        cd          - Change directory
        whoami      - Show username
        pwd         - Print working directory
        ls          - List directory contents
        touch       - Create an empty file
        echo        - Print text or write to file
        cat         - Show file contents
        rm          - Remove file/directory
        rename      - Rename file/directory
        cp          - Copy file
        mv          - Move (rename) file
        find        - Search for files
        grep        - Search text in files
        history     - Show command history
        sleep       - Pause for N seconds
        timer       - Start countdown timer
        ping        - Ping host
        ip          - Show IP information

        =======================================================
        """

    return ("info", list_help, os.getcwd())
